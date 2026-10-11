"""Execucao de processos sem janela preta, com prioridade baixa opcional (para o Windows respirar)."""
import os, subprocess, socket

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
BELOW_NORMAL = 0x00004000 if os.name == "nt" else 0


def flags(low_priority=True):
    return NOWIN | (BELOW_NORMAL if low_priority else 0)


def run(cmd, timeout=15):
    """(codigo, texto stdout+stderr). Nunca levanta excecao."""
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=NOWIN)
        return r.returncode, r.stdout or ""
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return -9, out + "\n[tempo esgotado]"
    except Exception as e:
        return -1, "ERRO: %s" % e


def popen(cmd, low_priority=True):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                            creationflags=flags(low_priority))


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p
