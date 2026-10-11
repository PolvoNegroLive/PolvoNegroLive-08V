"""Launcher do Polvo Negro Live. Duplo clique em INICIAR_POLVO_NEGRO_LIVE.bat (ou: python POLVO_NEGRO_LIVE.py)."""
import os, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))


def prepare_windows():
    if os.name != "nt":
        return
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DiegoBotelhoPereira.PolvoNegroLive.8")   # icone proprio na barra de tarefas
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)                                                           # nitidez em telas com escala 125-200%
    except Exception:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except Exception: pass


def main():
    prepare_windows()
    import tkinter as tk
    from app.ui.panel import App
    root = tk.Tk(); App(root); root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        try:
            from app.paths import data_dir
            (data_dir() / "logs" / "crash.log").open("a", encoding="utf-8").write("[%s]\n%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), tb))
        except Exception:
            pass
        try:
            import tkinter as tk
            from tkinter import messagebox
            r = tk.Tk(); r.withdraw(); messagebox.showerror("Polvo Negro Live", "O programa fechou por um erro.\n\nO detalhe foi salvo em logs\\crash.log\n\n" + tb[-600:]); r.destroy()
        except Exception:
            print(tb)
        sys.exit(1)
