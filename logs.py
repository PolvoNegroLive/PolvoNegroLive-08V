"""Logs separados (engine, encoder, um por destino, errors) com mascara de chaves e rotacao simples."""
import re, threading, time
from pathlib import Path

URL_RE = re.compile(r"(rtmps?://[^\s/]+/)\S+", re.I)


def redact(text, keys=()):
    for k in keys:
        if k and len(k) >= 4:
            text = text.replace(k, "********")
    return URL_RE.sub(r"\1********", text)


class LogHub:
    MAX_BYTES = 2 * 1024 * 1024

    def __init__(self, logdir, keys=lambda: ()):
        self.dir = Path(logdir); self.dir.mkdir(parents=True, exist_ok=True)
        self.keys = keys; self.lock = threading.Lock()

    def clean(self, text):
        return redact(text, self.keys())

    def write(self, name, msg, level="INFO"):
        line = "[%s] [%s] [%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), name.upper(), level, self.clean(str(msg)).rstrip())
        p = self.dir / (name.lower() + ".log")
        with self.lock:
            try:
                if p.exists() and p.stat().st_size > self.MAX_BYTES:
                    p.replace(p.with_suffix(".1.log"))
                with open(p, "a", encoding="utf-8") as f:
                    f.write(line)
            except OSError:
                pass

    def error(self, dest, process, code, error_class, message, action):
        """errors.log: cada erro com timestamp, destino, processo, codigo de saida, classe e acao tomada."""
        self.write("errors", "dest=%s proc=%s exit=%s class=%s | %s | acao: %s" % (dest, process, code, error_class, message, action), "ERROR")

    def tail(self, name, lines=300):
        p = self.dir / (name + ".log")
        try:
            return "".join(p.read_text(encoding="utf-8", errors="replace").splitlines(True)[-lines:])
        except OSError:
            return ""

    def names(self):
        return sorted(x.stem for x in self.dir.glob("*.log") if ".1" not in x.name)
