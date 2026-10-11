"""Distribuidor (hub): recebe UM fluxo MPEG-TS do encoder e repassa os mesmos bytes a N destinos. NAO recodifica.

- Cada destino (sender) entra num quadro-chave, com PAT/PMT em cache, entao o video e valido desde o primeiro quadro.
- Fila POR TEMPO: o limite e  bitrate_medido x buffer_seconds  (e nao um numero fixo de bytes, que a 25 Mbps eram so 2,7 s).
- Fila enchendo: ATENCAO (50%) -> CRITICO (80%) -> descarte controlado (ressincroniza no proximo quadro-chave).
  Se ressincronizar 3x em 60 s, desconecta o destino (ele reconecta sozinho). Nunca cresce sem limite.
"""
import socket, threading, time
from collections import deque

TS = 188
PID_PAT, PID_PMT, PID_VIDEO = 0, 0x1000, 0x100     # fixados no encoder (-mpegts_start_pid 256 / -mpegts_pmt_start_pid 4096)
MIN_QUEUE, MAX_QUEUE = 2 * 1024 * 1024, 256 * 1024 * 1024


def _is_key(pkt):
    if ((pkt[1] & 0x1F) << 8 | pkt[2]) != PID_VIDEO:
        return False
    afc = (pkt[3] >> 4) & 3
    return afc in (2, 3) and pkt[4] > 0 and bool(pkt[5] & 0x40)


class _Sub:
    def __init__(self, sock):
        self.sock = sock; self.dq = deque(); self.size = 0; self.cv = threading.Condition()
        self.waiting = True; self.dead = False; self.resyncs = []; self.total_resyncs = 0; self.limit = MIN_QUEUE
        threading.Thread(target=self._writer, daemon=True).start()

    def put(self, data, limit):
        """True ok | 'resync' (descartou a fila) | False (destino removido)."""
        with self.cv:
            if self.dead:
                return False
            self.limit = limit; self.dq.append(data); self.size += len(data)
            if self.size > limit:
                self.dq.clear(); self.size = 0; self.waiting = True; self.total_resyncs += 1
                now = time.time(); self.resyncs = [t for t in self.resyncs if now - t < 60] + [now]
                if len(self.resyncs) >= 3:
                    self._close_locked(); return False
                return "resync"
            self.cv.notify()
        return True

    def fill(self):
        return self.size / float(self.limit or 1)

    def _writer(self):
        while True:
            with self.cv:
                while not self.dq and not self.dead:
                    self.cv.wait(0.5)
                if self.dead:
                    break
                data = self.dq.popleft(); self.size -= len(data)
            try:
                self.sock.sendall(data)
            except OSError:
                break
        self.close()

    def _close_locked(self):
        self.dead = True
        try: self.sock.close()
        except OSError: pass
        self.cv.notify_all()

    def close(self):
        with self.cv:
            self._close_locked()


class Channel:
    """Um perfil de saida: porta onde o encoder escreve + porta onde os senders leem."""

    def __init__(self, buffer_seconds=20.0):
        self.buffer_seconds = float(buffer_seconds)
        self.enc_srv, self.sub_srv = self._listen(), self._listen()
        self.enc_port, self.sub_port = self.enc_srv.getsockname()[1], self.sub_srv.getsockname()[1]
        self.subs = []; self.lock = threading.Lock(); self.psi = {}; self.closed = False
        self.bytes_in = 0; self.joins = 0; self.removed = 0; self.resyncs = 0; self.encoder_connected = False
        self.rate = 0.0; self._t = time.time(); self._b = 0     # bytes/s (media movel)
        threading.Thread(target=self._accept_subs, daemon=True).start()
        threading.Thread(target=self._read_encoder, daemon=True).start()

    @staticmethod
    def _listen():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.bind(("127.0.0.1", 0)); s.listen(8); return s

    def limit_bytes(self):
        return int(max(MIN_QUEUE, min(MAX_QUEUE, self.rate * self.buffer_seconds)))

    def _accept_subs(self):
        while not self.closed:
            try:
                c, _ = self.sub_srv.accept()
            except OSError:
                return
            try:   # buffer do SO pequeno: a pressao aparece na NOSSA fila (controlada por tempo), nao escondida no kernel
                c.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
            except OSError:
                pass
            with self.lock:
                self.subs.append(_Sub(c)); self.joins += 1

    def _update_rate(self, n):
        self._b += n; now = time.time(); dt = now - self._t
        if dt >= 1.0:
            inst = self._b / dt; self.rate = inst if self.rate == 0 else 0.7 * self.rate + 0.3 * inst
            self._t, self._b = now, 0

    def _read_encoder(self):
        try:
            c, _ = self.enc_srv.accept()
        except OSError:
            return
        self.encoder_connected = True; buf = b""
        while not self.closed:
            try:
                d = c.recv(65536)
            except OSError:
                break
            if not d:
                break
            self.bytes_in += len(d); self._update_rate(len(d)); buf += d
            while len(buf) >= TS and buf[0] != 0x47:
                i = buf.find(b"\x47", 1); buf = buf[i:] if i > 0 else b""
            n = (len(buf) // TS) * TS
            if n == 0:
                continue
            chunk, buf = buf[:n], buf[n:]
            key_at = None
            for off in range(0, n, TS):
                pkt = chunk[off:off + TS]; pid = (pkt[1] & 0x1F) << 8 | pkt[2]
                if pid in (PID_PAT, PID_PMT):
                    self.psi[pid] = pkt
                if key_at is None and _is_key(pkt):
                    key_at = off
            header = self.psi.get(PID_PAT, b"") + self.psi.get(PID_PMT, b""); limit = self.limit_bytes()
            with self.lock:
                for s in list(self.subs):
                    if s.dead:
                        self.subs.remove(s); self.removed += 1; continue
                    if s.waiting:
                        if key_at is not None and header:
                            with s.cv:
                                s.waiting = False
                            r = s.put(header + chunk[key_at:], limit)
                        else:
                            continue
                    else:
                        r = s.put(chunk, limit)
                    if r == "resync":
                        self.resyncs += 1
                    elif r is False:
                        self.subs.remove(s); self.removed += 1

    def status(self):
        with self.lock:
            fills = [s.fill() for s in self.subs if not s.dead]
        worst = max(fills) if fills else 0.0
        level = "CRITICO" if worst >= .8 else ("ATENCAO" if worst >= .5 else "OK")
        return {"kbps": int(self.rate * 8 / 1000), "buffer_s": self.buffer_seconds, "limit_MB": round(self.limit_bytes() / 1e6, 1),
                "fila_max_%": int(worst * 100), "nivel": level, "destinos_ativos": len(fills), "entradas": self.joins,
                "removidos": self.removed, "ressincronizacoes": self.resyncs, "MB_recebidos": round(self.bytes_in / 1e6, 2),
                "encoder_conectou": self.encoder_connected}

    def subscribers(self):
        with self.lock:
            return sum(1 for s in self.subs if not s.dead)

    def close(self):
        self.closed = True
        for s in (self.enc_srv, self.sub_srv):
            try: s.close()
            except OSError: pass
        with self.lock:
            for s in self.subs:
                s.close()


class Hub:
    def __init__(self, n, buffer_seconds=20.0):
        self.channels = [Channel(buffer_seconds) for _ in range(n)]

    @property
    def enc_ports(self):
        return [c.enc_port for c in self.channels]

    @property
    def sub_ports(self):
        return [c.sub_port for c in self.channels]

    def stats(self):
        return [dict(canal=i, **c.status()) for i, c in enumerate(self.channels)]

    def close(self):
        for c in self.channels:
            c.close()
