"""Deteccao de cameras/audio DirectShow e dos modos REAIS que cada camera oferece."""
import re
from .proc import run

STD_SIZES = [(160, 120), (320, 240), (640, 360), (640, 480), (800, 600), (854, 480), (960, 540),
             (1024, 768), (1280, 720), (1280, 960), (1600, 900), (1920, 1080)]
STD_FPS = [5, 10, 15, 20, 24, 25, 30, 50, 60]


def list_devices(ff):
    code, text = run([ff, "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"], 12)
    videos, audios, section = [], [], None
    for line in text.splitlines():
        if "Alternative name" in line:
            continue
        if "DirectShow video devices" in line:
            section = "video"; continue
        if "DirectShow audio devices" in line:
            section = "audio"; continue
        m = re.search(r'"([^"]+)"\s*\((video|audio|none)\)', line)
        if m:
            name, kind = m.group(1), m.group(2)
        else:
            m = re.search(r'"([^"]+)"', line)
            if not (m and section):
                continue
            name, kind = m.group(1), section
        if kind == "video" and name not in videos:
            videos.append(name)
        elif kind == "audio" and name not in audios:
            audios.append(name)
    return videos, audios, text


_MODE = re.compile(r"(pixel_format|vcodec)=(\S+)\s+min s=(\d+)x(\d+) fps=([\d.]+)\s+max s=(\d+)x(\d+) fps=([\d.]+)", re.I)


def list_modes(ff, device):
    """Consulta o DirectShow. Retorna (lista de modos, texto bruto)."""
    code, text = run([ff, "-hide_banner", "-list_options", "true", "-f", "dshow", "-i", "video=" + device], 20)
    return parse_modes(text), text


def parse_modes(text):
    modes, index = [], {}
    for line in text.splitlines():
        m = _MODE.search(line)
        if not m:
            continue
        opt, fmt = m.group(1).lower(), m.group(2).lower()
        w0, h0, f0 = int(m.group(3)), int(m.group(4)), float(m.group(5))
        w1, h1, f1 = int(m.group(6)), int(m.group(7)), float(m.group(8))
        if (w0, h0) == (w1, h1):
            sizes = [(w1, h1)]
        else:  # camera aceita uma faixa: oferece as resolucoes padrao dentro dela
            sizes = [s for s in STD_SIZES if w0 <= s[0] <= w1 and h0 <= s[1] <= h1]
            if (w1, h1) not in sizes:
                sizes.append((w1, h1))
        lo, hi = int(round(f0)), int(round(f1))
        fps = sorted({f for f in STD_FPS if lo <= f <= hi} | {hi})
        for w, h in sizes:
            k = (opt, fmt, w, h)
            if k in index:
                index[k]["fps"] = sorted(set(index[k]["fps"]) | set(fps))
            else:
                index[k] = {"opt": opt, "fmt": fmt, "w": w, "h": h, "fps": list(fps)}
                modes.append(index[k])
    return modes


def best_default(modes):
    """Padrao leve: prefere MJPEG (menos banda USB), ate 720p, com 30 fps se existir."""
    if not modes:
        return None
    def score(m):
        return (m["fmt"] == "mjpeg", m["h"] <= 720, max(m["fps"]) >= 30, m["w"] * m["h"] if m["h"] <= 720 else -m["w"] * m["h"])
    return max(modes, key=score)


# ---------------- audio ----------------
_A_RANGE = re.compile(r"min ch=\s*(\d+),?\s*bits=\s*(\d+),?\s*rate=\s*(\d+)\s+max ch=\s*(\d+),?\s*bits=\s*(\d+),?\s*rate=\s*(\d+)", re.I)
_A_ONE = re.compile(r"ch=\s*(\d+),\s*bits=\s*(\d+),\s*rate=\s*(\d+)", re.I)
STD_RATES = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000]


def parse_audio_modes(text):
    """Retorna {'rates': [...], 'channels': [...]} realmente informados pelo dispositivo."""
    rates, chans = set(), set()
    for line in text.splitlines():
        m = _A_RANGE.search(line)
        if m:
            r0, r1 = int(m.group(3)), int(m.group(6))
            rates |= {r for r in STD_RATES if r0 <= r <= r1} | {r1}; chans |= {int(m.group(1)), int(m.group(4))}
            continue
        m = _A_ONE.search(line)
        if m:
            rates.add(int(m.group(3))); chans.add(int(m.group(1)))
    return {"rates": sorted(rates), "channels": sorted(chans)}


def list_audio_modes(ff, device):
    code, text = run([ff, "-hide_banner", "-list_options", "true", "-f", "dshow", "-i", "audio=" + device], 15)
    return parse_audio_modes(text), text


def guess_audio_for(video, audios):
    """Tenta achar o audio da MESMA placa de captura (ex.: 'USB Video' <-> 'Digital Audio Interface (USB Digital Audio)')."""
    words = lambda t: {w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in ("video", "audio", "device", "the", "interface", "digital", "input", "microphone")}
    vw = words(video); best, score = None, 0
    for a in audios:
        s = len(vw & words(a)) + (2 if ("hdmi" in a.lower() and "hdmi" in video.lower()) else 0)
        if s > score:
            best, score = a, s
    return best
