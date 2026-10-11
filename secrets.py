"""Protecao das chaves de transmissao.

Windows: DPAPI (CryptProtectData). So o SEU usuario do Windows, neste PC, consegue ler a chave salva.
Outros sistemas (so desenvolvimento/testes): base64 SEM seguranca, marcado como 'plain:'.
"""
import base64, os

PREFIX_DPAPI, PREFIX_PLAIN = "dpapi:", "plain:"


def _dpapi(data: bytes, protect: bool) -> bytes:
    import ctypes
    from ctypes import wintypes

    class BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    buf = ctypes.create_string_buffer(data, len(data))
    bin_ = BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    bout = BLOB()
    fn = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    if not fn(ctypes.byref(bin_), None, None, None, None, 0, ctypes.byref(bout)):
        raise OSError("DPAPI falhou (erro %d)" % ctypes.GetLastError())
    try:
        return ctypes.string_at(bout.pbData, bout.cbData)
    finally:
        kernel32.LocalFree(bout.pbData)


def protect(text: str) -> str:
    if not text:
        return ""
    raw = text.encode("utf-8")
    if os.name == "nt":
        try:
            return PREFIX_DPAPI + base64.b64encode(_dpapi(raw, True)).decode()
        except Exception:
            pass
    return PREFIX_PLAIN + base64.b64encode(raw).decode()


def unprotect(blob: str):
    """Retorna (texto, ok). Se nao conseguir ler (outro usuario/PC), devolve ('', False)."""
    if not blob:
        return "", True
    try:
        if blob.startswith(PREFIX_DPAPI):
            return _dpapi(base64.b64decode(blob[len(PREFIX_DPAPI):]), False).decode("utf-8"), True
        if blob.startswith(PREFIX_PLAIN):
            return base64.b64decode(blob[len(PREFIX_PLAIN):]).decode("utf-8"), True
    except Exception:
        return "", False
    return blob, True      # valor antigo em texto puro (sera protegido ao salvar)


def mask_key(key: str) -> str:
    """Para exibir na tela: so os 4 ultimos caracteres."""
    if not key:
        return ""
    return "*" * max(8, len(key) - 4) + key[-4:] if len(key) > 8 else "*" * len(key)
