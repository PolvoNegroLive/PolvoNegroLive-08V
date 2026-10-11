"""ComponentManager: acha o FFmpeg que JA existe, valida (versao, arquitetura, roda, encoders, protocolos). Nao instala nada sozinho."""
import os, re, shutil
from pathlib import Path
from .paths import APP_DIR, data_dir
from .proc import run

COMMON = (r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe", r"C:\ProgramData\chocolatey\bin\ffmpeg.exe")


class Component:
    def __init__(self, name):
        self.name, self.found, self.path, self.version, self.arch = name, False, "", "", ""
        self.ok, self.detail = False, ""
        self.encoders, self.out_protocols, self.muxers, self.demuxers = [], set(), set(), set()

    def summary(self):
        return "%s: %s | versão %s | %s | %s" % (self.name, "ENCONTRADO" if self.found else "NÃO ENCONTRADO", self.version or "-", self.arch or "-",
                                                    ("OK" if self.ok else "PROBLEMA: " + self.detail) if self.found else self.detail)


def candidates(override=""):
    c = []
    if override:
        c.append(override)
    w = shutil.which("ffmpeg")
    if w:
        c.append(w)
    for base in (APP_DIR, APP_DIR / "components", data_dir() / "components"):
        c += [str(base / "ffmpeg" / "bin" / "ffmpeg.exe"), str(base / "ffmpeg" / "ffmpeg.exe"), str(base / "FFMPEG" / "bin" / "ffmpeg.exe")]
    c += list(COMMON)
    seen, out = set(), []
    for x in c:
        if x and x.lower() not in seen and Path(x).exists():
            seen.add(x.lower()); out.append(x)
    return out


def parse_version(text):
    m = re.search(r"ffmpeg version\s+(\S+)", text)
    return m.group(1) if m else ""


def parse_arch(text):
    cfg = re.search(r"configuration:(.*)", text)
    c = cfg.group(1) if cfg else ""
    for pat, name in ((r"--arch=(x86_64|amd64)", "64 bits (x64)"), (r"--arch=(aarch64|arm64)", "ARM64"), (r"--arch=(x86|i686|i386)\b", "32 bits (x86)")):
        if re.search(pat, c):
            return name
    return "64 bits (x64)" if "x86_64" in text or "mingw" in c else ""


def parse_section(text, section):
    """-protocols imprime 'Input:' e 'Output:' seguidos de nomes."""
    out, on = set(), False
    for line in text.splitlines():
        s = line.strip()
        if s.endswith(":") and s[:-1] in ("Input", "Output"):
            on = (s[:-1] == section); continue
        if on and s and not s.startswith("Supported"):
            out.add(s)
    return out


def inspect(path):
    c = Component("FFmpeg"); c.path = path
    code, text = run([path, "-version"], 10)
    if code != 0 or "ffmpeg version" not in text:
        c.detail = "não executou (%s)" % (text.strip().splitlines() or ["sem saída"])[-1][:80]; c.found = True; return c
    c.found = True; c.version, c.arch = parse_version(text), parse_arch(text)
    code, enc = run([path, "-hide_banner", "-encoders"], 15)
    c.encoders = sorted({m.group(1) for m in re.finditer(r"^\s*V\S*\s+(\S*264\S*|\S*hevc\S*|\S*av1\S*)\s", enc, re.M)})
    c.out_protocols = parse_section(run([path, "-hide_banner", "-protocols"], 10)[1], "Output")
    mux = run([path, "-hide_banner", "-muxers"], 10)[1]
    c.muxers = {m.group(1) for m in re.finditer(r"^\s*E\S*\s+(\S+)", mux, re.M)}
    dem = run([path, "-hide_banner", "-demuxers"], 10)[1]
    c.demuxers = {m.group(1) for m in re.finditer(r"^\s*D\S*\s+(\S+)", dem, re.M)}
    missing = []
    if "libx264" not in c.encoders: missing.append("encoder libx264")
    if "rtmp" not in c.out_protocols: missing.append("protocolo rtmp")
    for m in ("flv", "mpegts"):
        if m not in c.muxers: missing.append("muxer " + m)
    if os.name == "nt" and "dshow" not in c.demuxers: missing.append("captura DirectShow (dshow)")
    c.ok = not missing
    c.detail = "faltando: " + ", ".join(missing) if missing else ""
    if "32 bits" in c.arch: c.detail = "FFmpeg de 32 bits (use o de 64 bits)"; c.ok = False
    return c


def find_ffmpeg(override=""):
    """Primeiro candidato que RODA e atende aos requisitos; senao o primeiro que existe (com o problema descrito)."""
    first = None
    for p in candidates(override):
        c = inspect(p)
        if c.ok:
            return c
        first = first or c
    if first:
        return first
    c = Component("FFmpeg"); c.detail = "não encontrado no PATH nem nas pastas do programa. Instale o FFmpeg (64 bits) ou coloque ffmpeg.exe em ffmpeg\\bin\\."
    return c


def capabilities(c):
    """O que este FFmpeg consegue (para a tela Diagnostico)."""
    return {"RTMP": "rtmp" in c.out_protocols, "RTMPS (TLS)": "rtmps" in c.out_protocols or "tls" in c.out_protocols,
            "SRT (libsrt)": "srt" in c.out_protocols, "WHIP": "whip" in c.muxers}
