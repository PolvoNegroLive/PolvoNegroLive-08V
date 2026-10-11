"""Migracao de configuracoes entre versoes.

- CONFIG_SCHEMA_VERSION identifica o formato do arquivo (nao e a versao do programa).
- Antes de qualquer migracao e feito BACKUP.
- Schema 0 = nada salvo ainda OU arquivos soltos das versoes V04-V07 (config\\youtube.json etc. ao lado do programa).
  Eles sao importados uma unica vez e as chaves passam a ser guardadas protegidas (DPAPI).
- Para criar a V09: aumente CONFIG_SCHEMA_VERSION e adicione a funcao em MIGRATIONS[8].
"""
import json, re
from pathlib import Path
from . import CONFIG_SCHEMA_VERSION
from .paths import APP_DIR


def _legacy_dirs():
    found = [APP_DIR / "config"]
    parent = APP_DIR.parent
    try:
        sib = sorted((p for p in parent.glob("POLVO_NEGRO_LIVE_V0*") if p.is_dir() and p != APP_DIR), key=lambda p: p.name, reverse=True)
        found += [p / "config" for p in sib]
    except OSError:
        pass
    return [d for d in found if (d / "youtube.json").exists() or (d / "tiktok.json").exists()]


def _kind_of(server):
    s = (server or "").lower()
    return "restream" if "restream.io" in s else ("youtube" if "youtube.com" in s else None)


def from_legacy(st, notes, legacy_dir=None):
    dirs = [Path(legacy_dir)] if legacy_dir else _legacy_dirs()
    if not dirs:
        return
    d0 = dirs[0]; imported = []
    for fname, kind in (("youtube.json", "youtube"), ("tiktok.json", "tiktok")):
        try:
            old = json.loads((d0 / fname).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        k = _kind_of(old.get("server")) or kind
        d = st.new_destination(k)
        d["name"] = {"youtube": "YouTube", "tiktok": "TikTok"}[kind] if k == kind else d["name"]
        d.update({"enabled": bool(old.get("enabled", True)), "server": old.get("server", d["server"]), "stream_key": old.get("stream_key", ""),
                  "width": int(old.get("width", d["width"])), "height": int(old.get("height", d["height"])), "fps": int(old.get("fps", d["fps"])),
                  "video_bitrate": str(old.get("video_bitrate", d["video_bitrate"])), "encoder": old.get("encoder", "libx264"), "fit": old.get("fit", d["fit"])})
        if kind == "tiktok":
            d["id"] = "tiktok"
        st.destinations.append(d); imported.append(d["name"])
    try:
        cam = json.loads((d0 / "camera.json").read_text(encoding="utf-8"))
        st.capture.update({k: v for k, v in cam.items() if k in st.capture})
    except (OSError, ValueError):
        pass
    if imported:
        notes.append("Configurações antigas importadas de %s (%s). As chaves agora ficam protegidas." % (d0, ", ".join(imported)))


def _noop(st, notes):
    pass


MIGRATIONS = {0: from_legacy, 1: _noop, 2: _noop, 3: _noop, 4: _noop, 5: _noop, 6: _noop, 7: _noop}


def run(st, had_files):
    """Executa a cadeia de migracoes necessaria. Retorna lista de avisos para o usuario."""
    ver = int(st.app.get("schema", 0)) if had_files else 0
    if ver >= CONFIG_SCHEMA_VERSION:
        return []
    notes = []
    b = st.backup("antes_da_migracao_schema_%d" % ver) if had_files else None
    if b:
        notes.append("Backup criado antes de migrar: %s" % b)
    for v in range(ver, CONFIG_SCHEMA_VERSION):
        fn = MIGRATIONS.get(v)
        if fn:
            fn(st, notes)
    st.app["legacy_imported"] = True
    st.save()
    return notes
