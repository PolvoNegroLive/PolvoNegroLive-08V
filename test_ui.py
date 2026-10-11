"""Teste de fumaca da interface (pula se nao houver Tk/tela)."""
import os, sys, tempfile, time, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import tkinter as tk
    os.environ.setdefault("POLVO_DATA_DIR", tempfile.mkdtemp())
    _r = tk.Tk(); _r.destroy(); HAS_TK = True
except Exception:
    HAS_TK = False


@unittest.skipUnless(HAS_TK, "sem Tk/tela")
class TestUI(unittest.TestCase):
    def test_abre_todas_as_paginas_e_valida_antes_de_iniciar(self):
        from tkinter import messagebox
        from app.ui import dialogs, panel
        shown = []
        messagebox.showerror = lambda t, m, **k: shown.append(m)
        dialogs_ask = panel.ask_issues; panel.ask_issues = lambda parent, issues, **k: (shown.append([i["code"] for i in issues]) or "cancel")
        root = tk.Tk(); app = panel.App(root)
        end = time.time() + 1.5
        while time.time() < end: root.update(); time.sleep(0.03)
        for p in app.pages: app.show_page(p); root.update()
        app.ff = app.ff or "ffmpeg"                         # sem camera: deve ser BLOQUEADO pela validacao
        app.start_live(); root.update()
        self.assertIsNone(app.streamer)
        self.assertTrue(any("NO_CAPTURE" in x for x in shown if isinstance(x, list)))
        root.destroy(); panel.ask_issues = dialogs_ask


if __name__ == "__main__":
    unittest.main()
