"""Paginas Diagnostico, Logs e Configuracoes."""
import json, os, platform, tkinter as tk
from tkinter import ttk, filedialog
from . import theme as T
from .. import APP_NAME, APP_VERSION, AUTHOR, CONFIG_SCHEMA_VERSION
from ..components import find_ffmpeg, capabilities
from ..devices import list_devices
from ..hardware import cpu_info, ram_info, gpu_list, graphics_libs, windows_name
from ..proc import run
from ..streamer import ESPERAS

import subprocess


def open_folder(path):
    try:
        if os.name == "nt":
            os.startfile(str(path))
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except Exception:
        return False


class MiscPages:
    # ---------------- DIAGNOSTICO ----------------
    def build_diag(self, p):
        bt = ttk.Frame(p); bt.pack(fill="x")
        ttk.Button(bt, text="Analisar PC", style="Accent.TButton", command=self.diagnose).pack(side="left")
        ttk.Button(bt, text="Componentes (FFmpeg)", command=self.show_components).pack(side="left", padx=6)
        ttk.Button(bt, text="Testar encoders", command=self.test_encoders).pack(side="left")
        ttk.Button(bt, text="Ver saída bruta dos modos", command=self.show_raw).pack(side="left", padx=6)
        self.diag = T.text_widget(p); self.diag.pack(fill="both", expand=True, pady=8)

    def put(self, s):
        self.diag.insert("end", s + "\n"); self.diag.see("end")

    def diagnose(self):
        self.diag.delete("1.0", "end"); self.put("Analisando... (alguns segundos)")
        def job():
            o = ["POLVO NEGRO LIVE %s — DIAGNÓSTICO" % APP_VERSION, "", "Sistema: " + windows_name()]
            c = cpu_info(); o.append("CPU: %s | %s núcleos / %s threads | %s MHz" % (c["name"], c["cores"], c["threads"], c["mhz"]))
            r = ram_info(); o.append("RAM: total %s GB | livre %s GB" % (r["total_gb"], r["free_gb"]))
            g = gpu_list(); o.append("GPUs:"); o += ["  - %s | driver %s | VRAM %s MB" % (x["name"], x["driver"], x["vram_mb"]) for x in g] or ["  (não foi possível consultar)"]
            gl = graphics_libs()
            if gl:
                o += ["", "Bibliotecas gráficas PRESENTES (isto NÃO significa que ajudem a codificar vídeo; só o teste de encoder diz):"] + ["  %s %s" % ("✓" if v else "✗", k) for k, v in gl.items()]
            return "\n".join(o)
        self.bg(job, lambda r: (self.diag.delete("1.0", "end"), self.put(str(r))))

    def show_components(self):
        self.diag.delete("1.0", "end"); self.put("Verificando o FFmpeg...")
        def job():
            c = find_ffmpeg(self.st.app.get("ffmpeg_path", "")); o = [c.summary(), "Caminho: %s" % (c.path or "-")]
            if c.found:
                o += ["", "Capacidades deste FFmpeg:"] + ["  %s %s" % ("✓" if v else "✗", k) for k, v in capabilities(c).items()]
                o += ["", "Encoders H.264/HEVC/AV1 que o build possui: " + (", ".join(c.encoders) or "nenhum"), "(constar na lista NÃO prova que funcione neste PC: use 'Testar encoders')"]
            return "\n".join(o)
        self.bg(job, lambda r: (self.diag.delete("1.0", "end"), self.put(str(r))))

    def test_encoders(self):
        if not self.ff: self.put("FFmpeg não encontrado."); return
        self.put("\nTestando encoders (cada um codifica 10 quadros)...")
        def job():
            res = {}
            for e in (self.comp.encoders if self.comp else []):
                if e.startswith("h264_") and e not in ("h264_v4l2m2m", "h264_vaapi", "h264_vulkan", "h264_omx", "h264_mf") or e == "libx264":
                    code, out = run([self.ff, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=30", "-frames:v", "10", "-pix_fmt", "yuv420p", "-c:v", e, "-f", "null", "-"], 25)
                    res[e] = (code == 0, "OK" if code == 0 else (out.strip().splitlines() or ["falhou"])[-1][:90])
            return res
        def done(r):
            if isinstance(r, Exception): self.put("Erro: %s" % r); return
            self.enc_cache = {k: v[0] for k, v in r.items()}
            try: (self.st.base / "cache" / "encoders.json").write_text(json.dumps(self.enc_cache), encoding="utf-8")
            except OSError: pass
            for k, (ok, msg) in r.items(): self.put("  %-14s %s" % (k, "FUNCIONA" if ok else "não funciona: " + msg))
            self.cb_enc["values"] = self.enc_values()
            self.put("Só os encoders que funcionam aparecem na aba Destinos.")
        self.bg(job, done)

    def show_raw(self):
        self.diag.delete("1.0", "end"); self.put(getattr(self, "raw_modes", "") or "Escolha uma câmera e clique 'Ler modos da câmera' na aba Captura.")

    # ---------------- LOGS ----------------
    def build_logs(self, p):
        bt = ttk.Frame(p); bt.pack(fill="x")
        self.log_sel = tk.StringVar(); self.cb_log = ttk.Combobox(bt, textvariable=self.log_sel, state="readonly", width=22); self.cb_log.pack(side="left"); self.cb_log.bind("<<ComboboxSelected>>", lambda e: self.view_log())
        ttk.Button(bt, text="Atualizar", command=self.view_log).pack(side="left", padx=6)
        ttk.Button(bt, text="Abrir pasta de logs", command=lambda: open_folder(self.st.base / "logs")).pack(side="left")
        ttk.Button(bt, text="Gerar relatório", command=self.save_report).pack(side="left", padx=6)
        self.log_view = T.text_widget(p); self.log_view.pack(fill="both", expand=True, pady=8)
        ttk.Label(p, style="Muted.TLabel", text="Os logs nunca contêm chaves (aparecem como ********). Um arquivo por destino, mais engine, encoder, network e errors.").pack(anchor="w")

    def view_log(self):
        names = self.logs.names(); self.cb_log["values"] = names
        if not self.log_sel.get() and names: self.log_sel.set("errors" if "errors" in names else names[0])
        self.log_view.delete("1.0", "end"); self.log_view.insert("end", self.logs.tail(self.log_sel.get()) or "(vazio)"); self.log_view.see("end")

    def save_report(self):
        s = self.streamer or self.last_streamer
        self.log("Relatório salvo: %s" % s.write_report() if s else "Ainda não há relatório: inicie uma live ou um teste.")

    # ---------------- CONFIGURACOES ----------------
    def build_config(self, p):
        f = ttk.LabelFrame(p, text="Componentes", padding=12); f.pack(fill="x"); f.columnconfigure(1, weight=1)
        ttk.Label(f, text="Caminho do FFmpeg").grid(row=0, column=0, sticky="w"); ttk.Entry(f, textvariable=self.sv("ffpath")).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(f, text="Procurar...", command=self.browse_ff).grid(row=0, column=2)
        ttk.Label(f, text="(vazio = procurar sozinho: PATH do Windows e pastas do programa)", style="Muted.TLabel").grid(row=1, column=1, sticky="w", padx=8)
        g = ttk.LabelFrame(p, text="Aparência e distribuidor", padding=12); g.pack(fill="x", pady=10)
        ttk.Label(g, text="Marca d'água (%)").grid(row=0, column=0, sticky="w"); ttk.Combobox(g, textvariable=self.sv("wm", "10"), values=["0", "5", "10", "15"], state="readonly", width=6).grid(row=0, column=1, padx=8)
        ttk.Label(g, text="Buffer do distribuidor (s)").grid(row=0, column=2, sticky="w", padx=(18, 0)); ttk.Spinbox(g, from_=5, to=60, textvariable=self.sv("bufsec", "20"), width=6).grid(row=0, column=3, padx=8)
        h = ttk.LabelFrame(p, text="Dados e backup", padding=12); h.pack(fill="x")
        ttk.Label(h, text="Pasta de dados: %s" % self.st.base).pack(anchor="w")
        row = ttk.Frame(h); row.pack(anchor="w", pady=6)
        ttk.Button(row, text="Abrir pasta", command=lambda: open_folder(self.st.base)).pack(side="left")
        ttk.Button(row, text="Fazer backup agora", command=lambda: self.log("Backup criado: %s" % self.st.backup("manual"))).pack(side="left", padx=6)
        ttk.Button(p, text="Salvar configurações", style="Accent.TButton", command=self.save_config).pack(anchor="w", pady=10)
        ttk.Label(p, text="%s %s  •  esquema de configuração %d  •  %s" % (APP_NAME, APP_VERSION, CONFIG_SCHEMA_VERSION, AUTHOR), style="Muted.TLabel").pack(anchor="w")
        ttk.Label(p, text="Reconexão automática: espera %s s entre tentativas; suspende após 8 falhas (botão REINICIAR)." % "/".join(str(x) for x in ESPERAS), style="Muted.TLabel").pack(anchor="w")

    def browse_ff(self):
        f = filedialog.askopenfilename(title="Escolha o ffmpeg.exe", filetypes=[("ffmpeg", "ffmpeg*"), ("Todos", "*.*")])
        if f: self.v["ffpath"].set(f)

    def save_config(self):
        self.st.app.update(ffmpeg_path=self.v["ffpath"].get().strip(), watermark=int(self.v["wm"].get() or 10), buffer_seconds=int(self.v["bufsec"].get() or 20), low_priority=bool(self.lowprio.get()))
        self.st.save(); self.refresh_wm(); self.log("Configurações salvas."); self.detect_ffmpeg()
