"""Validacao de URL/chave/video ANTES de iniciar. Separa VALOR ESCOLHIDO de VALOR SUPORTADO.
Niveis: 'erro' (pede confirmacao: corrigir automaticamente ou usar mesmo assim) e 'aviso' (so informa)."""
import re

URL_RE = re.compile(r"^(?P<scheme>rtmps?)://(?P<host>[^/:?\s]+)(?::(?P<port>\d+))?(?P<path>/[^?\s]*)?(?:\?(?P<query>\S*))?$", re.I)

# faixas recomendadas de bitrate H.264 (kbps) por lado menor da imagem e FPS (<=30 / >30). Referencia: YouTube Live / guias; apenas AVISO.
BITRATES = {360: ((400, 1000), (600, 1500)), 480: ((1000, 2000), (1500, 3000)), 720: ((2500, 4000), (3500, 5000)),
            1080: ((4500, 6000), (6000, 9000)), 1440: ((9000, 13000), (13000, 20000)), 2160: ((20000, 30000), (30000, 51000))}


def parse_url(server):
    m = URL_RE.match((server or "").strip())
    if not m:
        return None
    g = m.groupdict(); scheme = g["scheme"].lower()
    port = int(g["port"]) if g["port"] else (443 if scheme == "rtmps" else 1935)
    return {"scheme": scheme, "host": g["host"].lower(), "port": port, "explicit_port": g["port"], "path": (g["path"] or "").rstrip("/"), "query": g["query"] or ""}


def build_url(server, key):
    """server + chave. Trata '?backup=1' do YouTube: vira .../live2/CHAVE?backup=1 (nunca .../live2?backup=1/CHAVE)."""
    p = parse_url(server)
    if not p:
        return (server or "").rstrip("/") + "/" + (key or "").lstrip("/")
    base = "%s://%s%s%s" % (p["scheme"], p["host"], (":" + p["explicit_port"]) if p["explicit_port"] else "", p["path"])
    url = base + "/" + (key or "").lstrip("/")
    if p["query"]:
        url += ("&" if "?" in url else "?") + p["query"]
    return url


def recommended_bitrate(w, h, fps):
    short = min(int(w), int(h)); fps = int(fps)
    step = min(BITRATES, key=lambda k: abs(k - short))
    lo, hi = BITRATES[step][0 if fps <= 30 else 1]
    if fps <= 20:
        lo, hi = int(lo * .6), int(hi * .7)
    return lo, hi


def kbps(v):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([kKmM]?)", str(v))
    if not m:
        return 0
    n = float(m.group(1)); return int(n * 1000) if m.group(2).lower() == "m" else int(n)


def endpoint_id(d):
    p = parse_url(d.get("server", ""))
    return ("%s%s" % (p["host"], p["path"]) if p else (d.get("server", "").lower()), d.get("stream_key", ""))


def issue(level, code, msg, dest=None, fix=None):
    return {"level": level, "code": code, "msg": msg, "dest": dest, "fix": fix or {}}


def validate_destination(d, cap, tested_encoders=None):
    out, n = [], d.get("name", d.get("id", "?")); i = d.get("id")
    p = parse_url(d.get("server", ""))
    if not d.get("server"):
        out.append(issue("erro", "NO_SERVER", "%s: servidor não informado." % n, i))
    elif not p:
        out.append(issue("erro", "BAD_URL", "%s: o servidor precisa começar com rtmp:// ou rtmps:// (ex.: rtmps://servidor:443/app)." % n, i))
    else:
        if p["scheme"] == "rtmps" and p["port"] == 1935:
            out.append(issue("aviso", "PORT_MISMATCH", "%s: RTMPS na porta 1935 é incomum. Use exatamente o endereço RTMPS que a plataforma mostra." % n, i))
        if p["scheme"] == "rtmp" and p["port"] == 443:
            out.append(issue("aviso", "PORT_MISMATCH", "%s: RTMP (sem TLS) na porta 443 é incomum; talvez seja RTMPS." % n, i))
        if d.get("kind") == "youtube" and p["scheme"] != "rtmps":
            out.append(issue("aviso", "YT_NOT_RTMPS", "%s: o YouTube recomenda RTMPS (conexão criptografada)." % n, i))
    if not d.get("stream_key"):
        out.append(issue("erro", "NO_KEY", "%s: chave da transmissão não informada." % n, i))
    try:
        w, h, f = int(d["width"]), int(d["height"]), int(d["fps"])
        if min(w, h, f) <= 0:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        out.append(issue("erro", "BAD_VIDEO", "%s: resolução/FPS inválidos." % n, i)); return out
    cf, cw, ch = int(cap.get("fps") or 30), int(cap.get("width") or 0), int(cap.get("height") or 0)
    if f > cf and not d.get("fps_conversion"):
        out.append(issue("erro", "FPS_ABOVE_CAPTURE", "%s: %d FPS é mais do que a captura entrega (%d). Isso só duplicaria quadros, sem ganho. Para duplicar de propósito, marque 'Conversão de FPS'." % (n, f, cf), i, {"fps": cf}))
    elif f > 60:
        out.append(issue("aviso", "FPS_HIGH", "%s: %d FPS é raro em plataformas (limite comum: 60)." % (n, f), i))
    if cw and ch and max(w, h) > max(cw, ch) * 1.02:
        out.append(issue("aviso", "UPSCALE", "%s: a saída (%dx%d) é maior que a captura (%dx%d); ampliar não melhora a imagem." % (n, w, h, cw, ch), i))
    ar = max(w, h) / min(w, h)
    if not any(abs(ar - x) < 0.06 for x in (16 / 9, 4 / 3, 1.0, 3 / 2, 21 / 9)):
        out.append(issue("aviso", "ODD_ASPECT", "%s: proporção incomum (%dx%d). Plataformas esperam 16:9 (horizontal) ou 9:16 (vertical)." % (n, w, h), i))
    br = kbps(d.get("video_bitrate", ""))
    lo, hi = recommended_bitrate(w, h, f)
    if br <= 0:
        out.append(issue("erro", "BAD_BITRATE", "%s: bitrate inválido (ex.: 2000k)." % n, i))
    elif br > hi * 3 or (br > 20000 and br > hi * 2):
        out.append(issue("erro", "BITRATE_ABSURD", "%s: %d kbps é muito acima do recomendado (%d–%d kbps para %dx%d@%d). Pode estourar o seu upload e a plataforma." % (n, br, lo, hi, w, h, f), i, {"video_bitrate": "%dk" % ((lo + hi) // 2)}))
    elif br > hi * 1.3:
        out.append(issue("aviso", "BITRATE_HIGH", "%s: %d kbps acima da faixa recomendada (%d–%d)." % (n, br, lo, hi), i))
    elif br < lo * 0.5:
        out.append(issue("aviso", "BITRATE_LOW", "%s: %d kbps abaixo da faixa recomendada (%d–%d); a imagem pode ficar ruim." % (n, br, lo, hi), i))
    enc = d.get("encoder") or "libx264"
    if enc != "libx264" and tested_encoders is not None and enc not in tested_encoders:
        out.append(issue("aviso", "ENCODER_UNTESTED", "%s: o encoder %s ainda não foi testado neste PC (Diagnóstico > Testar encoders)." % (n, enc), i, {"encoder": "libx264"}))
    return out


def validate_set(dests, cap, tested_encoders=None):
    """Valida todos os destinos ATIVOS e os conflitos entre eles."""
    act = [d for d in dests if d.get("enabled")]; out = []
    if not cap.get("video"):
        out.append(issue("erro", "NO_CAPTURE", "Nenhuma câmera/placa de captura selecionada."))
    if not act:
        out.append(issue("erro", "NO_DEST", "Ative pelo menos um destino."))
    for d in act:
        out += validate_destination(d, cap, tested_encoders)
    seen = {}
    for d in act:
        if not (d.get("server") and d.get("stream_key")):
            continue
        seen.setdefault(endpoint_id(d), []).append(d)
    for k, grp in seen.items():
        if len(grp) > 1:
            names = ", ".join(x["name"] for x in grp)
            out.append(issue("erro", "DUP_ENTRY", "Possível destino duplicado: %s usam a mesma entrada (servidor + chave). Muitos serviços aceitam só UMA conexão por chave: a outra será recusada (\"End of file\")." % names))
    bykey = {}
    for d in act:
        if d.get("stream_key"):
            bykey.setdefault(d["stream_key"], []).append(d)
    for k, grp in bykey.items():
        if len(grp) > 1 and endpoint_id(grp[0]) != endpoint_id(grp[1]):
            out.append(issue("erro", "DUP_KEY", "A mesma chave está em mais de um destino (%s), mesmo com servidores diferentes. Cada plataforma tem a sua chave: normalmente só uma conexão por chave é aceita." % ", ".join(x["name"] for x in grp)))
    rs = [d for d in act if "restream.io" in (d.get("server") or "").lower()]
    if len(rs) > 1 and len({d.get("stream_key") for d in rs}) > 1:
        out.append(issue("aviso", "RESTREAM_MULTI", "Mais de um destino aponta para o Restream. Confira se o seu plano aceita mais de uma entrada simultânea."))
    if not cap.get("audio"):
        out.append(issue("aviso", "AUDIO_NONE", "VÍDEO DISPONÍVEL — ÁUDIO NÃO SELECIONADO. A live sairá sem som (algumas plataformas reclamam)."))
    return out


def apply_fixes(dests, issues):
    """Aplica os 'fix' das issues no destino correspondente. Retorna quantos ajustes foram feitos."""
    n = 0
    for it in issues:
        if it.get("fix") and it.get("dest"):
            for d in dests:
                if d.get("id") == it["dest"]:
                    d.update(it["fix"]); n += 1
    return n
