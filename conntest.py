"""Teste de conexao por ETAPAS: URL -> DNS -> TCP -> TLS -> (opcional) publicacao real de 5 s. Diz QUAL etapa falhou."""
import socket, ssl, time
from . import ffcmd
from .errors import classify
from .logs import redact
from .proc import run
from .validation import parse_url, build_url


def _stage(name, ok, detail, code=""):
    return {"stage": name, "ok": ok, "detail": detail, "code": code}


def test_connection(server, key, kind="custom", ff=None, publish=False, timeout=6.0):
    """Retorna (veredito, etapas). Sem publish=True nada e enviado a plataforma (so rede)."""
    st = []
    p = parse_url(server)
    if not p:
        st.append(_stage("URL", False, "Endereço inválido: use rtmp:// ou rtmps:// (ex.: rtmps://servidor:443/app).", "BAD_URL")); return "ENDEREÇO INVÁLIDO", st
    st.append(_stage("URL", True, "%s://%s:%d%s" % (p["scheme"], p["host"], p["port"], p["path"])))
    try:
        ip = socket.getaddrinfo(p["host"], p["port"], type=socket.SOCK_STREAM)[0][4][0]
        st.append(_stage("DNS", True, "%s → %s" % (p["host"], ip)))
    except OSError as e:
        st.append(_stage("DNS", False, "não resolveu %s (%s)" % (p["host"], e), "DNS_ERROR")); return "DNS FALHOU", st
    t0 = time.time()
    try:
        sock = socket.create_connection((ip, p["port"]), timeout)
        st.append(_stage("TCP", True, "porta %d aberta (%d ms)" % (p["port"], (time.time() - t0) * 1000)))
    except socket.timeout:
        st.append(_stage("TCP", False, "tempo esgotado na porta %d" % p["port"], "TIMEOUT")); return "TIMEOUT", st
    except ConnectionRefusedError:
        st.append(_stage("TCP", False, "a porta %d recusou a conexão" % p["port"], "CONNECTION_REFUSED")); return "CONEXÃO RECUSADA", st
    except OSError as e:
        st.append(_stage("TCP", False, str(e), "NETWORK_ERROR")); return "FALHA DE REDE", st
    if p["scheme"] == "rtmps":
        try:
            ctx = ssl.create_default_context(); tls = ctx.wrap_socket(sock, server_hostname=p["host"]); st.append(_stage("TLS", True, "%s, certificado válido" % tls.version())); tls.close()
        except ssl.SSLCertVerificationError as e:
            st.append(_stage("TLS", False, "certificado não confiável (%s)" % e.verify_message, "TLS_ERROR")); return "TLS FALHOU", st
        except (ssl.SSLError, OSError) as e:
            st.append(_stage("TLS", False, "handshake falhou (%s). Esta porta talvez não seja RTMPS." % e, "TLS_ERROR")); return "TLS FALHOU", st
    else:
        sock.close(); st.append(_stage("TLS", True, "não usado (RTMP sem criptografia)"))
    if not publish:
        return "REDE OK (chave ainda não testada)", st
    if not ff:
        st.append(_stage("PUBLICAÇÃO", False, "FFmpeg não encontrado", "ENCODER_ERROR")); return "FFMPEG AUSENTE", st
    url = build_url(server, key)
    cmd = [ff, "-hide_banner", "-nostdin", "-loglevel", "info", "-re", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=15", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-t", "5", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-pix_fmt", "yuv420p", "-b:v", "600k", "-g", "30", "-c:a", "aac", "-b:a", "64k", "-f", "flv", url]
    code, out = run(cmd, 35); out = redact(out, [key])
    if code == 0 and "Output #0" in out:
        st.append(_stage("PUBLICAÇÃO", True, "o servidor aceitou a chave e recebeu 5 s de teste")); return "CONEXÃO OK", st
    c = classify(out)
    st.append(_stage("PUBLICAÇÃO", False, "%s — %s" % (c["title"], c["explanation"]), c["code"]))
    return {"SERVER_CLOSED_CONNECTION": "SERVIDOR FECHOU A CONEXÃO", "AUTH_FAILURE": "CHAVE RECUSADA"}.get(c["code"], c["title"].upper()), st
