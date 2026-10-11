"""Motor de transmissao V08.

  CAMERA --> [ENCODER: 1 FFmpeg, camera aberta 1x, 1 codificacao por PERFIL distinto]
                 | MPEG-TS por TCP local (1 canal por perfil)
                 v
             [HUB: repassa bytes, fila por tempo, entra em quadro-chave]
                 |--> [ENVIO destino A: -c copy -> RTMP(S)]  reconecta sozinho (5,10,20,40,60 s), failover p/ servidor de backup
                 '--> [ENVIO destino B: -c copy -> RTMP(S)]  idem. Falha de um destino NUNCA derruba o outro.

Estados de cada destino: IDLE, CONNECTING, CONNECTED, STREAMING, RECONNECTING, ERROR, STOPPING, STOPPED.
"""
import platform, re, threading, time
from collections import deque
from . import ffcmd
from .errors import classify
from .hub import Hub
from .logs import LogHub
from .proc import popen
from .validation import build_url, parse_url

STATS_ENC = re.compile(r"frame=\s*(\d+)\s+fps=\s*([\d.]+).*?speed=\s*([\d.]+)x", re.I)
DROP = re.compile(r"drop=\s*(\d+)", re.I)
STATS_SND = re.compile(r"time=\s*(\S+).*?bitrate=\s*([\d.]+)\s*kbits/s", re.I)
NOISE = re.compile(r"^\[(libx264|aac) @ [^\]]+\]\s+(frame|mb|coded|i16|i4|i8c|ref|weighted|kb/s|using|profile|consecutive|SSE|Qavg|8x8|final)|^\[out#\d+/\w+ @|^(video|audio):|update header|^Output #|^Input #|^\s*(Stream #|Metadata|Side data|encoder\s*:|cpb:|Duration|Stream mapping|Press|Program)", re.I)
IMPORTANT = re.compile(r"error|fail|could not|cannot|unable|invalid|refused|broken pipe|reset|warning|no such|not found|unknown|denied|busy|overrun|dropp", re.I)

STATES = ("IDLE", "CONNECTING", "CONNECTED", "STREAMING", "RECONNECTING", "ERROR", "STOPPING", "STOPPED")
ESPERAS = (5, 10, 20, 40, 60)       # backoff; depois de MAX_FALHAS a reconexao automatica e suspensa (botao REINICIAR)
MAX_FALHAS = 8


class Streamer:
    """on_event(kind, name, data) em threads: kind in state|enc|hub|log|exit. A UI deve enfileirar e tratar na thread dela."""

    def __init__(self, ff, cap, dests, on_event, logdir, in_args=None, buffer_seconds=20, low_priority=True, version="", esperas=None, max_falhas=None):
        self.ff, self.cap, self.on = ff, cap, on_event
        self.dests = [dict(d) for d in dests]
        self.in_args = in_args if in_args is not None else ffcmd.input_args(cap)
        self.buffer_seconds, self.low_priority, self.version = buffer_seconds, low_priority, version
        self.esperas, self.max_falhas = tuple(esperas or ESPERAS), max_falhas or MAX_FALHAS
        self.profiles = ffcmd.group_profiles(self.dests)
        self.logs = LogHub(logdir, keys=lambda: [x for d in self.dests for x in (d.get("stream_key", ""),) if x])
        self.procs, self.hub, self.stopping, self.all_failed = {}, None, False, False
        self.rt = {d["id"]: {"state": "IDLE", "text": "", "pid": None, "started": None, "restarts": 0, "last_error": None, "server": "principal", "attempt": 0, "suspended": False}
                   for d in self.dests}
        self.history, self.codes, self.cmds, self.tails, self.enc_last = [], {}, {}, {}, None
        self.t0 = time.time(); self.lock = threading.Lock(); self._loops = {}

    # ---------- utilidades ----------
    def _set(self, did, state, text="", error=None):
        r = self.rt[did]
        if r["state"] != state or (state in ("RECONNECTING", "ERROR") and r["text"] != text):
            self.history.append((round(time.time() - self.t0, 1), did, state, text))
            self.logs.write(did, "%s %s" % (state, text))
        r.update(state=state, text=text)
        if error is not None:
            r["last_error"] = error
        self.on("state", did, {"state": state, "text": text, "error": r["last_error"], "attempt": r["attempt"], "restarts": r["restarts"],
                               "server": r["server"], "suspended": r["suspended"], "pid": r["pid"]})

    def _line(self, log, text, tail_key):
        clean = self.logs.clean(text).rstrip()
        if not clean:
            return None
        if not STATS_ENC.search(clean) and not STATS_SND.search(clean) and not NOISE.search(clean):
            self.logs.write(log, clean); self.tails.setdefault(tail_key, deque(maxlen=25)).append(clean)
        return clean

    def _log_err(self, did, process, code, c, msg, action):
        self.logs.error(did, process, code, c["code"], msg, action)

    # ---------- ciclo de vida ----------
    def start(self):
        self.logs.write("engine", "START v%s | destinos: %s | perfis de saída: %d" % (self.version, ", ".join(d["id"] for d in self.dests), len(self.profiles)))
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self._run_inner()
        except Exception as e:
            self.logs.write("engine", "falha ao iniciar: %s" % e, "ERROR")
            self.on("exit", "encoder", {"code": -1, "user_stop": self.stopping, "error": classify(str(e)), "tail": [str(e)]}); self.stop()

    def _run_inner(self):
        self.hub = Hub(len(self.profiles), self.buffer_seconds)
        cmd = ffcmd.build_encoder(self.ff, self.in_args, self.cap, self.profiles, self.hub.enc_ports); self.cmds["ENCODER"] = cmd
        self.logs.write("encoder", "comando: " + " ".join(cmd))
        enc = popen(cmd, self.low_priority); self.procs["encoder"] = enc
        self.on("log", "ENCODER", "Captura iniciada (câmera aberta uma única vez). Perfis de saída: %d | destinos: %s" % (len(self.profiles), ", ".join(d["name"] for d in self.dests)))
        for d in self.dests:
            self._start_loop(d)
        threading.Thread(target=self._hub_monitor, daemon=True).start()
        tail, last_stat = [], 0.0
        for line in enc.stdout:
            c = self._line("encoder", line, "ENCODER")
            if not c:
                continue
            m = STATS_ENC.search(c)
            if m:
                dr = DROP.search(c)
                self.enc_last = {"frames": int(m.group(1)), "fps": float(m.group(2)), "speed": float(m.group(3)), "drop": int(dr.group(1)) if dr else 0}
                self.on("enc", "encoder", self.enc_last)
                if time.time() - last_stat > 10:
                    self.logs.write("encoder", "stats " + str(self.enc_last)); last_stat = time.time()
            else:
                tail.append(c); tail = tail[-8:]
                if IMPORTANT.search(c) and not NOISE.search(c):
                    self.on("log", "ENCODER", c)
        code = enc.wait(); self.codes["ENCODER"] = code
        user = self.stopping and not self.all_failed
        err = None if user else classify("\n".join(tail))
        if err and not self.all_failed:
            self._log_err("-", "encoder", code, err, " / ".join(tail[-2:]), "captura encerrada")
        self.on("exit", "encoder", {"code": code, "user_stop": user, "error": err, "all_failed": self.all_failed, "tail": [] if self.all_failed else tail[-3:]})
        self.stop()

    def _hub_monitor(self):
        last = {}
        while not self.stopping and self.hub:
            time.sleep(2.0)
            try:
                st = self.hub.stats()
            except Exception:
                return
            self.on("hub", "hub", st)
            for s in st:
                if s["nivel"] != "OK" and time.time() - last.get(s["canal"], 0) > 10:
                    self.logs.write("network", "fila do canal %d em %s (%d%% de %.1f MB, %d kbps)" % (s["canal"], s["nivel"], s["fila_max_%"], s["limit_MB"], s["kbps"]), "WARNING")
                    last[s["canal"]] = time.time()

    # ---------- destinos ----------
    def _start_loop(self, d):
        th = threading.Thread(target=self._sender_loop, args=(d,), daemon=True); self._loops[d["id"]] = th; th.start()

    def restart(self, did):
        """Botao REINICIAR: retoma um destino cuja reconexao automatica foi suspensa (ou que caiu)."""
        d = next((x for x in self.dests if x["id"] == did), None)
        if not d or self.stopping or (self._loops.get(did) and self._loops[did].is_alive()):
            return False
        self.rt[did].update(suspended=False, attempt=0); self.all_failed = False
        self._start_loop(d); return True

    def _server_for(self, d, falhas):
        """Failover: depois de 2 falhas no principal usa o de backup (se houver), alternando a cada 2 falhas."""
        b = d.get("backup_server") or ""
        if b and parse_url(b) and (falhas // 2) % 2 == 1:
            return b, "backup"
        return d["server"], "principal"

    def _sender_loop(self, d):
        did, falhas, rt = d["id"], 0, self.rt[d["id"]]
        port = self.hub.sub_ports[d["pid"]]
        while not self.stopping:
            rt["attempt"] += 1; server, which = self._server_for(d, falhas); rt["server"] = which
            if which == "backup" and falhas % 2 == 0:
                pass
            if rt["attempt"] > 1:
                rt["restarts"] += 1
            self._set(did, "CONNECTING" if rt["attempt"] == 1 else "RECONNECTING",
                      "Conectando ao servidor%s..." % (" de backup" if which == "backup" else "") if rt["attempt"] == 1 else "Reconectando (tentativa %d)%s..." % (rt["attempt"], " no servidor de backup" if which == "backup" else ""))
            url = build_url(server, d["stream_key"])
            cmd = ffcmd.build_sender(self.ff, port, url); self.cmds[did.upper()] = cmd
            p = popen(cmd, False); self.procs[did] = p; rt["pid"] = p.pid; rt["started"] = time.time()
            self.logs.write(did, "processo iniciado PID %s (%s)" % (p.pid, which))
            connected, t0, last_stat = threading.Event(), time.time(), 0.0
            killer = threading.Timer(30, lambda p=p, ev=connected: (p.kill() if (p.poll() is None and not ev.is_set()) else None)); killer.daemon = True; killer.start()
            tail = []
            for line in p.stdout:
                c = self._line(did, line, did.upper())
                if not c:
                    continue
                if "Output #0" in c and not connected.is_set():
                    connected.set(); self._set(did, "CONNECTED", "Conectado ao servidor. Enviando...")
                m = STATS_SND.search(c)
                if m and connected.is_set():
                    self._set(did, "STREAMING", "%d kbps | %s%s" % (int(float(m.group(2))), m.group(1).split(".")[0], " (reconectou)" if rt["attempt"] > 1 else ""))
                    if time.time() - last_stat > 10:
                        self.logs.write(did, "stats %s kbps t=%s" % (int(float(m.group(2))), m.group(1))); last_stat = time.time()
                elif not m:
                    tail.append(c); tail = tail[-8:]
            killer.cancel(); code = p.wait(); self.codes[did.upper()] = code; rt["pid"] = None
            if self.stopping:
                return
            text = "\n".join(tail) if tail else ""
            err = classify(text if connected.is_set() or text else "timeout")
            if not connected.is_set() and not text:
                err = classify("timed out")
            if connected.is_set() and time.time() - t0 > 20:
                falhas = 0
            falhas += 1
            msg = "%s — %s" % (err["title"], err["explanation"])
            self._log_err(did, "sender", code, err, " / ".join(tail[-2:]) or "sem saída", "reconectar em breve" if falhas < self.max_falhas else "reconexão suspensa")
            if falhas >= self.max_falhas:
                rt["suspended"] = True
                self._set(did, "ERROR", "Reconexão automática suspensa após %d tentativas. %s Ação: %s  [REINICIAR]" % (falhas, msg, err["action"]), err)
                if all(self.rt[x["id"]]["suspended"] for x in self.dests) and not self.all_failed:
                    self.all_failed = True
                    self.on("log", "SISTEMA", "Todos os destinos falharam. Encerrando a captura."); threading.Thread(target=self.stop, daemon=True).start()
                return
            espera = self.esperas[min(falhas - 1, len(self.esperas) - 1)]
            self._set(did, "RECONNECTING", "Caiu: %s Nova tentativa em %ds (%d/%d). Ação: %s" % (msg, espera, falhas, self.max_falhas, err["action"]), err)
            end = time.time() + espera
            while time.time() < end and not self.stopping:
                time.sleep(0.2)

    # ---------- relatorio / parada ----------
    def report_text(self):
        keys = [d.get("stream_key", "") for d in self.dests]
        L = ["POLVO NEGRO LIVE %s - RELATÓRIO (sem chaves)" % self.version, time.strftime("%Y-%m-%d %H:%M:%S"), "Sistema: %s | FFmpeg: %s" % (platform.platform(), self.ff), "",
             "Captura: %s" % {k: v for k, v in self.cap.items()}]
        for d in self.dests:
            r = self.rt[d["id"]]
            L.append("Destino %s (%s): %dx%d @ %dfps %s encoder=%s preset=%s perfil#%d servidor=%s | estado=%s tentativas=%d reinícios=%d" % (
                d["id"], d.get("kind"), d["width"], d["height"], d["fps"], d["video_bitrate"], d.get("encoder"), d.get("preset"), d.get("pid", -1), d["server"], r["state"], r["attempt"], r["restarts"]))
        L += ["Perfis de saída (encodes): %d" % len(self.profiles), "Hub: %s" % (self.hub.stats() if self.hub else "não iniciou"),
              "Último status do encoder: %s" % (self.enc_last or "nunca rodou"), "Códigos de saída: %s" % (self.codes or "processos ainda ativos"), "", "Linha do tempo (s desde o início):"]
        L += ["  %6.1fs  %-10s %-13s %s" % h for h in self.history]
        for name, tl in self.tails.items():
            L += ["", "--- últimas linhas de %s ---" % name] + list(tl)
        L += ["", "--- comandos (chaves mascaradas) ---"] + ["%s: %s" % (k, " ".join(v)) for k, v in self.cmds.items()]
        return self.logs.clean("\n".join(L))

    def write_report(self):
        try:
            p = self.logs.dir / "relatorio.txt"; p.write_text(self.report_text(), encoding="utf-8"); return str(p)
        except OSError:
            return ""

    def stop(self):
        if self.stopping:
            return
        self.stopping = True
        for d in self.dests:
            self._set(d["id"], "STOPPING", "Parando...")
        for p in list(self.procs.values()):
            try:
                if p.poll() is None: p.terminate()
            except Exception:
                pass
        for p in list(self.procs.values()):          # espera o encerramento REAL antes de liberar um novo START
            try:
                p.wait(timeout=5)
            except Exception:
                try: p.kill(); p.wait(timeout=3)
                except Exception: pass
        try:
            if self.hub: self.hub.close()
        except Exception:
            pass
        for d in self.dests:
            self._set(d["id"], "STOPPED", "Parado")
        self.logs.write("engine", "STOP")
