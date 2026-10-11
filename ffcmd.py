"""Montagem dos comandos FFmpeg (puro, sem efeitos colaterais: facil de testar)."""
import re


def _even(n):
    n = int(n); return n - (n % 2)


def encoder_args(enc, bitrate, fps, preset="veryfast"):
    br = str(bitrate); n = re.match(r"(\d+)", br); bufsize = "%dk" % (int(n.group(1)) * 2) if n else "4000k"
    gop = ["-g", str(int(fps) * 2), "-keyint_min", str(int(fps) * 2)]          # keyframe a cada 2 s (YouTube: recomendado 2, maximo 4)
    base = ["-c:v", enc, "-pix_fmt", "yuv420p", "-b:v", br, "-maxrate", br, "-bufsize", bufsize] + gop
    if enc == "libx264":
        return base + ["-preset", preset or "veryfast", "-tune", "zerolatency", "-profile:v", "main", "-minrate", br, "-x264-params", "nal-hrd=cbr:force-cfr=1"]
    if enc == "h264_nvenc":
        return base + ["-preset", "p3", "-rc", "cbr", "-bf", "0"]
    if enc == "h264_qsv":
        return base + ["-preset", "veryfast", "-look_ahead", "0", "-bf", "0"]
    if enc == "h264_amf":
        return base + ["-usage", "lowlatency", "-rc", "cbr"]
    return base


def branch_filter(d):
    """fit: cortar (preenche o quadro, sem barras) | ajustar (barras pretas) | esticar."""
    W, H, F = _even(d["width"]), _even(d["height"]), int(d["fps"]); fit = d.get("fit", "cortar")
    if fit == "ajustar":
        return "fps=%d,scale=%d:%d:force_original_aspect_ratio=decrease:flags=bicubic,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" % (F, W, H, W, H)
    if fit == "esticar":
        return "fps=%d,scale=%d:%d:flags=bicubic,setsar=1" % (F, W, H)
    crop = "crop=w='if(gt(iw/ih,%d/%d),ih*%d/%d,iw)':h='if(gt(iw/ih,%d/%d),ih,iw*%d/%d)'" % (W, H, W, H, W, H, H, W)   # h = iw*H/W (corrigido)
    return "fps=%d,%s,scale=%d:%d:flags=bicubic,setsar=1" % (F, crop, W, H)


def pre_filter(cap):
    parts = []
    if cap.get("mirror"):
        parts.append("hflip")
    parts += {90: ["transpose=1"], 180: ["hflip", "vflip"], 270: ["transpose=2"]}.get(int(cap.get("rotate", 0) or 0), [])
    return ",".join(parts)


def input_args(cap):
    """Entrada DirectShow. ATENCAO: sem aspas no nome (video=Nome), pois nao passa por shell."""
    a = ["-f", "dshow"]
    if cap.get("format_opt") and cap.get("format") and cap["format"] != "auto":
        a += ["-" + cap["format_opt"], cap["format"]]
    if cap.get("width") and cap.get("height"):
        a += ["-video_size", "%dx%d" % (int(cap["width"]), int(cap["height"]))]
    if cap.get("fps"):
        a += ["-framerate", str(cap["fps"])]
    if cap.get("audio") and int(cap.get("audio_rate") or 0) > 0:
        a += ["-sample_rate", str(int(cap["audio_rate"]))]
    a += ["-thread_queue_size", "512", "-rtbufsize", str(cap.get("rtbufsize", "256M"))]
    src = "video=" + cap["video"] + ((":audio=" + cap["audio"]) if cap.get("audio") else "")
    return a + ["-i", src]


def profile_key(d):
    return (int(d["width"]), int(d["height"]), int(d["fps"]), str(d["video_bitrate"]), d.get("encoder") or "libx264", d.get("fit", "cortar"),
            d.get("preset") or "veryfast", d.get("audio_bitrate", "128k"))


def group_profiles(dests):
    """Destinos com perfil IDENTICO dividem 1 codificacao. Cada destino ganha d['pid']."""
    keys, profiles = {}, []
    for d in dests:
        k = profile_key(d)
        if k not in keys:
            keys[k] = len(profiles); profiles.append(dict(d))
        d["pid"] = keys[k]
    return profiles


def _graph(cap, profiles):
    pre = pre_filter(cap); n = len(profiles)
    if n == 1:
        return "[0:v]" + (pre + "," if pre else "") + branch_filter(profiles[0]) + "[o0]"
    chains = ["[0:v]" + (pre + "," if pre else "") + "split=%d%s" % (n, "".join("[s%d]" % i for i in range(n)))]
    chains += ["[s%d]%s[o%d]" % (i, branch_filter(p), i) for i, p in enumerate(profiles)]
    return ";".join(chains)


def _outputs(cap, profiles, sink):
    cmd, has_audio = [], bool(cap.get("audio"))
    for i, p in enumerate(profiles):
        cmd += ["-map", "[o%d]" % i] + (["-map", cap.get("audio_map", "0:a:0")] if has_audio else [])
        cmd += encoder_args(p.get("encoder") or "libx264", p["video_bitrate"], p["fps"], p.get("preset", "veryfast"))
        if has_audio:
            cmd += ["-c:a", "aac", "-b:a", p.get("audio_bitrate", "128k"), "-ar", "44100", "-ac", "2", "-af", "aresample=async=1:first_pts=0"]
        cmd += sink(i)
    return cmd


def build_encoder(ff, in_args, cap, profiles, enc_ports):
    """1 FFmpeg, camera aberta 1x, 1 saida MPEG-TS por perfil enviada ao hub (que escuta; o encoder e cliente)."""
    head = [ff, "-hide_banner", "-nostdin", "-loglevel", "info", "-stats"] + in_args + ["-filter_complex", _graph(cap, profiles)]
    sink = lambda i: ["-f", "mpegts", "-mpegts_flags", "+resend_headers", "-mpegts_start_pid", "256", "-mpegts_pmt_start_pid", "4096",
                      "-flush_packets", "1", "tcp://127.0.0.1:%d" % enc_ports[i]]
    return head + _outputs(cap, profiles, sink)


def build_test(ff, in_args, cap, profiles, seconds):
    """Mesmo caminho de codificacao, mas jogando fora a saida (-f null): mede velocidade/CPU sem publicar nada."""
    head = [ff, "-hide_banner", "-nostdin", "-loglevel", "info", "-stats"] + in_args + ["-t", str(seconds), "-filter_complex", _graph(cap, profiles)]
    return head + _outputs(cap, profiles, lambda i: ["-f", "null", "-"])


def build_sender(ff, hub_port, url):
    return [ff, "-hide_banner", "-nostdin", "-y", "-loglevel", "info", "-stats", "-analyzeduration", "1500000", "-probesize", "500000",
            "-f", "mpegts", "-i", "tcp://127.0.0.1:%d" % hub_port, "-c", "copy", "-bsf:a", "aac_adtstoasc", "-flvflags", "no_duration_filesize",
            "-rw_timeout", "15000000", "-f", "flv", url]


def lavfi_source(realtime=True):
    """Fonte sintetica (sem camera) para testes."""
    return (["-re"] if realtime else []) + ["-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100"], \
           {"video": "teste", "audio": "sintetico", "audio_map": "1:a:0", "width": 1280, "height": 720, "fps": 30}
