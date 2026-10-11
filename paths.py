"""Caminhos. Nada de caminho absoluto do seu PC: tudo e relativo ao programa ou a pasta de dados do usuario.

Dados do usuario (configuracoes, chaves, logs, backups):
  - Windows:  %APPDATA%\\PolvoNegroLive\\
  - Portatil: crie um arquivo vazio 'portable.flag' ao lado do programa -> usa a pasta 'data' ao lado dele
  - Teste:    variavel de ambiente POLVO_DATA_DIR
Assim atualizar o programa (V08 -> V09...) nunca apaga as configuracoes.
"""
import os, sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)
APP_DIR = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent.parent
RES_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))          # onde o PyInstaller descompacta os recursos
ASSETS = RES_DIR / "assets"
SUBDIRS = ("config", "profiles", "logs", "backups", "cache")


def data_dir():
    env = os.environ.get("POLVO_DATA_DIR")
    if env:
        p = Path(env)
    elif (APP_DIR / "portable.flag").exists():
        p = APP_DIR / "data"
    elif os.name == "nt":
        p = Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming") / "PolvoNegroLive"
    else:
        p = Path.home() / ".polvonegrolive"
    for s in SUBDIRS:
        (p / s).mkdir(parents=True, exist_ok=True)
    return p


def asset(*parts):
    return ASSETS.joinpath(*parts)
