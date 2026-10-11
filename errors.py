"""Classificacao de erros do FFmpeg/rede em categorias com explicacao humana.
Importante: 'End of file' ao abrir a saida NAO significa FFmpeg quebrado - normalmente o SERVIDOR fechou a conexao."""
import re

# (classe, titulo, explicacao, acao sugerida, padrao). A ordem importa: o primeiro que casar vence.
RULES = [
    ("LOCAL_HUB_RESET", "Conexão local interrompida", "O envio perdeu a ligação com o distribuidor interno (fila cheia ou encerramento).",
     "Reconecta sozinho. Se repetir, reduza o bitrate.", r"in#0/mpegts.*(10054|reset)|demuxing.*10054.*mpegts"),
    ("CAPTURE_ERROR", "Falha na captura", "A câmera/placa de captura não abriu ou não aceitou o modo escolhido.",
     "Feche outros programas que usam a câmera e escolha um modo da lista.", r"Could not find video device|Could not set video options|Could not set video size|Could not run graph|Error opening input.*dshow|dshow.*I/O error|device is in use|Cannot open video"),
    ("AUDIO_ERROR", "Falha no áudio", "O dispositivo de áudio escolhido não abriu.", "Escolha outro dispositivo de áudio ou transmita sem áudio.",
     r"Could not find audio|audio=.*(I/O error|not found)|Could not set audio options"),
    ("ENCODER_ERROR", "Falha no encoder", "O encoder escolhido não iniciou neste computador.", "Use libx264 (CPU) ou rode Diagnóstico > Testar encoders.",
     r"Unknown encoder|Encoder .* not found|Error initializing output stream|OpenEncodeSessionEx|No NVENC|Error while opening encoder|MFX|Cannot load nvcuda|Error submitting a packet to the muxer: Invalid argument"),
    ("DNS_ERROR", "Falha de DNS", "Não foi possível encontrar o endereço do servidor.", "Confira o endereço do servidor e a internet.",
     r"Name or service not known|getaddrinfo|Could not resolve|nodename nor servname|10 ?0?1 ?0?4|11001|Temporary failure in name resolution"),
    ("TLS_ERROR", "Falha de TLS/RTMPS", "A conexão segura (RTMPS) falhou.", "Use exatamente o endereço RTMPS (e porta) informado pela plataforma; confira data/hora do Windows.",
     r"\btls\b|\bssl\b|certificate|handshake failed|SSL routines"),
    ("CONNECTION_REFUSED", "Conexão recusada", "O servidor ou a porta recusou a conexão.", "Confira servidor e porta; firewall/antivírus podem estar bloqueando.",
     r"Connection refused|10061|ECONNREFUSED"),
    ("TIMEOUT", "Tempo esgotado", "O servidor não respondeu a tempo.", "Confira a internet e o endereço do servidor.",
     r"timed out|timeout|10060|ETIMEDOUT|Operation timed out"),
    ("NETWORK_ERROR", "Rede indisponível", "Não há caminho de rede até o servidor.", "Confira cabo/Wi-Fi e a internet.",
     r"Network is unreachable|10051|10065|No route to host|ENETUNREACH"),
    ("CONNECTION_RESET", "Conexão encerrada (reset)", "A conexão caiu no meio da transmissão.", "Normalmente é internet instável ou o servidor derrubou. Reconecta sozinho.",
     r"10054|Connection reset|ECONNRESET|Broken pipe|10053|Software caused connection abort"),
    ("AUTH_FAILURE", "Chave/autenticação recusada", "O servidor recusou a publicação (chave inválida, expirada ou sem permissão).",
     "Gere/copie a chave de novo na plataforma. No TikTok a chave muda a cada live.",
     r"Server error|BadName|Publish\.Denied|Unauthorized|Forbidden|rejected|401|403|NetStream\.Publish"),
    ("SERVER_CLOSED_CONNECTION", "Servidor fechou a conexão", "O servidor encerrou a conexão logo ao abrir a saída (\"End of file\"). Costuma ser: chave já em uso por outra transmissão, chave inválida/expirada ou endereço errado.",
     "Confira se outro destino usa a mesma chave/entrada e se a chave é da live atual.", r"Error opening output.*End of file|Error opening output file|End of file"),
]
UNKNOWN = ("UNKNOWN_ERROR", "Erro não identificado", "O FFmpeg terminou com um erro que não reconheço.", "Veja o log do destino e o relatório.")


def classify(text):
    """Retorna dict(code, title, explanation, action)."""
    for code, title, expl, action, pat in RULES:
        if re.search(pat, text or "", re.I):
            return {"code": code, "title": title, "explanation": expl, "action": action}
    c, t, e, a = UNKNOWN
    return {"code": c, "title": t, "explanation": e, "action": a}
