"""Configuracoes persistentes (app.json, capture.json, destinations.json) com chaves protegidas, backup e migracao."""
import json, os, re, shutil, time
from pathlib import Path
from . import CONFIG_SCHEMA_VERSION, APP_VERSION
from .paths import data_dir
from . import secrets

APP_DEFAULT = {"schema": CONFIG_SCHEMA_VERSION, "app_version": APP_VERSION, "mode": "automatico", "quality": 60, "reserve": 25,
               "low_priority": True, "watermark": 10, "ffmpeg_path": "", "buffer_seconds": 20, "legacy_imported": False}
CAPTURE_DEFAULT = {"video": "", "audio": "", "format": "auto", "format_opt": "", "width": 1280, "height": 720, "fps": 30,
                   "rtbufsize": "256M", "mirror": False, "rotate": 0, "audio_rate": 0, "audio_map": "0:a:0"}
KIND_DEFAULTS = {
    "youtube": {"name": "YouTube", "server": "rtmps://a.rtmps.youtube.com:443/live2", "backup_server": "rtmps://b.rtmps.youtube.com:443/live2?backup=1",
                "width": 854, "height": 480, "fps": 30, "video_bitrate": "2000k", "fit": "ajustar"},
    "tiktok": {"name": "TikTok", "server": "", "backup_server": "", "width": 480, "height": 854, "fps": 30, "video_bitrate": "1800k", "fit": "cortar"},
    "restream": {"name": "Restream", "server": "", "backup_server": "", "width": 854, "height": 480, "fps": 30, "video_bitrate": "2000k", "fit": "ajustar"},
    "custom": {"name": "Servidor personalizado", "server": "", "backup_server": "", "width": 854, "height": 480, "fps": 30, "video_bitrate": "2000k", "fit": "ajustar"},
}
DEST_COMMON = {"enabled": True, "stream_key": "", "audio_bitrate": "128k", "encoder": "libx264", "preset": "veryfast",
               "fps_conversion": False, "locks": []}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "", text.lower()) or "destino"


class Settings:
    def __init__(self, base=None):
        self.base = Path(base) if base else data_dir()
        for s in ("config", "profiles", "logs", "backups", "cache"):
            (self.base / s).mkdir(parents=True, exist_ok=True)
        self.cfg = self.base / "config"
        self.app, self.capture, self.destinations = dict(APP_DEFAULT), dict(CAPTURE_DEFAULT), []
        self.notes, self.key_errors = [], []

    # ---------- arquivos ----------
    def _read(self, name):
        try:
            return json.loads((self.cfg / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _write(self, name, data):
        tmp = self.cfg / (name + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.cfg / name)

    # ---------- destinos ----------
    def new_destination(self, kind="custom"):
        d = dict(DEST_COMMON); d.update(KIND_DEFAULTS.get(kind, KIND_DEFAULTS["custom"])); d["kind"] = kind; d["locks"] = []
        base = slug(kind if kind != "custom" else "custom"); ids = {x["id"] for x in self.destinations}; n, i = base, 1
        while n in ids:
            i += 1; n = "%s%d" % (base, i)
        d["id"] = n
        return d

    def load(self):
        from . import migration
        a = self._read("app.json")
        if a is not None:
            self.app = {**APP_DEFAULT, **a}
        c = self._read("capture.json")
        if c is not None:
            self.capture = {**CAPTURE_DEFAULT, **c}
        raw = self._read("destinations.json")
        self.destinations, self.key_errors = [], []
        for d in (raw or {}).get("destinations", []):
            key, ok = secrets.unprotect(d.get("stream_key_enc", d.get("stream_key", "")))
            if not ok:
                self.key_errors.append(d.get("name", d.get("id", "?")))
            item = {**DEST_COMMON, **d}; item.pop("stream_key_enc", None); item["stream_key"] = key
            self.destinations.append(item)
        self.notes = migration.run(self, had_files=(a is not None))
        if not self.destinations:                       # primeira execucao: dois destinos de exemplo
            self.destinations = [self.new_destination("youtube"), self.new_destination("tiktok")]
        return self

    def save(self):
        self.app.update({"schema": CONFIG_SCHEMA_VERSION, "app_version": APP_VERSION})
        self._write("app.json", self.app); self._write("capture.json", self.capture)
        out = []
        for d in self.destinations:
            x = dict(d); x["stream_key_enc"] = secrets.protect(x.pop("stream_key", "")); out.append(x)
        self._write("destinations.json", {"schema": CONFIG_SCHEMA_VERSION, "destinations": out})

    # ---------- backup ----------
    def backup(self, label="manual"):
        dst = self.base / "backups" / ("config_%s_%s" % (time.strftime("%Y%m%d_%H%M%S"), slug(label)))
        if any(self.cfg.glob("*.json")):
            shutil.copytree(self.cfg, dst)           # as chaves continuam protegidas pelo DPAPI
            olds = sorted((self.base / "backups").glob("config_*"))
            for o in olds[:-10]:
                shutil.rmtree(o, ignore_errors=True)
            return dst
        return None

    def secret_values(self):
        return [d.get("stream_key", "") for d in self.destinations if d.get("stream_key")]
