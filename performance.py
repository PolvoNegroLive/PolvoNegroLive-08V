"""Controle QUALIDADE <-> DESEMPENHO: transforma 1 numero (0-100) num ORCAMENTO realista de resolucao, FPS, bitrate e preset,
sempre limitado pelo que a captura entrega. O 'Teste de configuracao' mede o PC de verdade (velocidade do encoder, quadros perdidos, CPU)."""
import re, subprocess, threading, time
from . import ffcmd
from .ffcmd import group_profiles
from .hardware import CpuSampler
from .proc import popen
from .validation import recommended_bitrate

LADDER = [(360, 15), (360, 30), (480, 30), (720, 30), (720, 60), (1080, 30), (1080, 60)]     # (lado menor, fps)
PRESETS = ["ultrafast", "superfast", "veryfast", "faster", "fast"]                              # 'medium' fica de fora: pesado demais p/ PC fraco
STATS = re.compile(r"frame=\s*(\d+)\s+fps=\s*([\d.]+).*?speed=\s*([\d.]+)x", re.I)
DROP = re.compile(r"drop=\s*(\d+)", re.I)


def dims(short, vertical):
    long_ = int(round(short * 16 / 9 / 2.0) * 2)
    return (short, long_) if vertical else (long_, short)


def allowed_steps(cap):
    """Perfis que a captura consegue alimentar sem ampliar a imagem.

    A escada usa o lado menor (360/480/720/1080), mas isso sozinho nao
    basta: por exemplo, uma captura 800x600 nao deve sugerir 854x480,
    porque a largura de saida seria ampliada. Comparamos os dois lados.
    """
    cw = max(1, int(cap.get("width") or 1280))
    ch = max(1, int(cap.get("height") or 720))
    cap_long, cap_short = max(cw, ch), min(cw, ch)
    cf = max(1, int(cap.get("fps") or 30))
    steps = [s for s in LADDER
             if s[0] <= cap_short and int(round(s[0] * 16 / 9)) <= cap_long
             and s[1] <= cf]
    # Se a captura for menor que 360p ou tiver FPS muito baixo, mantem o
    # menor perfil historico como fallback; a validacao continua avisando.
    return steps or [LADDER[0]]


def plan(slider, cap, vertical=False, reserve=0, locks=None, current=None):
    """Retorna dict(width,height,fps,video_bitrate,preset) para o ponto do controle. 'locks' (nomes) preservam o valor de 'current'."""
    steps = allowed_steps(cap); slider = max(0, min(100, int(slider)))
    idx = round(slider / 100.0 * (len(steps) - 1))
    if reserve >= 35:
        idx = max(0, idx - 1)                    # reserva alta para o Windows: um degrau mais leve
    short, fps = steps[idx]; w, h = dims(short, vertical); lo, hi = recommended_bitrate(w, h, fps)
    out = {"width": w, "height": h, "fps": fps, "video_bitrate": "%dk" % max(500, int(lo + (hi - lo) * slider / 100.0)),
           "preset": PRESETS[min(len(PRESETS) - 1, 0 if slider <= 10 else 1 if slider <= 30 else 2 if slider <= 60 else 3 if slider <= 80 else 4)]}
    for k in (locks or []):
        if current and k in current:
            out[k] = current[k]
    return out


def step_down(p, cap, vertical=False):
    """Um degrau mais leve (usado quando o teste diz que o PC nao acompanha)."""
    steps = allowed_steps(cap); short = min(p["width"], p["height"])
    cur = min(range(len(steps)), key=lambda i: (abs(steps[i][0] - short), abs(steps[i][1] - p["fps"])))
    if cur == 0:
        return None
    s, f = steps[cur - 1]; w, h = dims(s, vertical); lo, hi = recommended_bitrate(w, h, f)
    q = dict(p); q.update(width=w, height=h, fps=f, video_bitrate="%dk" % ((lo + hi) // 2)); return q


def evaluate(res, budget_pct, realtime_source=True):
    if res.get("error"):
        return "NÃO SUPORTADA", "O teste falhou: %s" % res["error"]
    sp, dr, cpu = res["speed"], res["drops"], res["cpu_avg"]
    need = 0.97 if realtime_source else 1.2
    if sp < need or dr > 5:
        return "NÃO SUPORTADA", "Velocidade do encoder %.2fx (precisa de pelo menos %.2fx) e %d quadros perdidos: haveria atraso/travadas." % (sp, need, dr)
    if cpu > budget_pct:
        return "PESADA", "CPU média %.0f%% passa do orçamento de %.0f%% (reserva do Windows). Funciona, mas sem folga." % (cpu, budget_pct)
    return "RECOMENDADA", "Velocidade %.2fx, CPU média %.0f%% (orçamento %.0f%%), %d quadros perdidos." % (sp, cpu, budget_pct, dr)


def run_test(ff, in_args, cap, dests, seconds=10, low_priority=True, on_progress=None, realtime_source=True):
    """Roda o MESMO pipeline da live (descartando a saida) e mede. Nao publica nada."""
    profiles = group_profiles([dict(d) for d in dests])
    cmd = ffcmd.build_test(ff, in_args, cap, profiles, seconds)
    cpu, speeds, drops, last_fps, tail = CpuSampler(), [], 0, 0.0, []
    samples, done = [], threading.Event()
    def sampler():
        while not done.wait(1.0):
            samples.append(cpu.percent())
    threading.Thread(target=sampler, daemon=True).start()
    p = popen(cmd, low_priority); t0 = time.time()
    for line in p.stdout:
        line = line.strip()
        m = STATS.search(line)
        if m:
            last_fps = float(m.group(2)); speeds.append(float(m.group(3)))
            d = DROP.search(line); drops = int(d.group(1)) if d else drops
            if on_progress:
                on_progress(min(1.0, (time.time() - t0) / float(seconds)), last_fps, speeds[-1])
        elif line:
            tail.append(line); tail = tail[-6:]
    code = p.wait(); done.set()
    steady = speeds[len(speeds) // 3:] or speeds           # ignora a partida
    res = {"seconds": seconds, "code": code, "fps": last_fps, "speed": (sum(steady) / len(steady)) if steady else 0.0, "drops": drops,
           "cpu_avg": (sum(samples[1:]) / len(samples[1:])) if len(samples) > 1 else (samples[0] if samples else 0.0), "error": ""}
    if code != 0 or not speeds:
        res["error"] = " / ".join(tail[-3:]) or "o FFmpeg terminou com código %s" % code
    return res
