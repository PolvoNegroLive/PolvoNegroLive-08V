# -*- mode: python ; coding: utf-8 -*-
# PyInstaller (onedir, sem console). Rodar na raiz do projeto:  py -3 -m PyInstaller --noconfirm --clean installer\PolvoNegroLive.spec
import glob, os
ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
datas = [(f, "assets/logo") for f in glob.glob(os.path.join(ROOT, "assets", "logo", "*")) if os.path.isfile(f)]   # sem a pasta 'source' (2 MB)
a = Analysis([os.path.join(ROOT, "POLVO_NEGRO_LIVE.py")], pathex=[ROOT], binaries=[], datas=datas, hiddenimports=[], hookspath=[], runtime_hooks=[],
             excludes=["numpy", "PIL", "matplotlib", "scipy", "pandas"], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="PolvoNegroLive", console=False, disable_windowed_traceback=False,
          icon=os.path.join(ROOT, "assets", "logo", "polvonegro.ico"), version=os.path.join(ROOT, "installer", "version_info.txt"))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="PolvoNegroLive")
