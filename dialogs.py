import tkinter as tk
from tkinter import ttk
from . import theme as T

BLOCKING = {"NO_CAPTURE", "NO_DEST", "NO_SERVER", "BAD_URL", "NO_KEY", "BAD_VIDEO", "BAD_BITRATE"}   # impedem iniciar


def ask_issues(parent, issues, title="Conferência antes de iniciar"):
    """Mostra os problemas. Retorna 'fix' (corrigir automaticamente), 'force' (usar mesmo assim) ou 'cancel'."""
    win = tk.Toplevel(parent); win.title(title); win.configure(bg=T.BG); win.transient(parent); win.grab_set(); win.geometry("760x460")
    res = {"v": "cancel"}
    blocking = any(i["code"] in BLOCKING for i in issues)
    ttk.Label(win, text="Encontrei %d ponto(s) para você conferir:" % len(issues), style="H.TLabel").pack(anchor="w", padx=14, pady=(12, 6))
    box = T.text_widget(win, height=14); box.pack(fill="both", expand=True, padx=14)
    box.tag_config("erro", foreground=T.SALMON); box.tag_config("aviso", foreground=T.ORANGE); box.tag_config("fix", foreground=T.GREEN)
    for i in issues:
        box.insert("end", ("✖ " if i["level"] == "erro" else "⚠ ") + i["msg"] + "\n", i["level"])
        if i.get("fix"):
            box.insert("end", "    ↳ correção automática: %s\n" % ", ".join("%s=%s" % kv for kv in i["fix"].items()), "fix")
        box.insert("end", "\n")
    box.config(state="disabled")
    bar = ttk.Frame(win); bar.pack(fill="x", padx=14, pady=12)
    def done(v):
        res["v"] = v; win.destroy()
    if blocking:
        ttk.Label(bar, text="Há itens que impedem iniciar. Corrija e tente de novo.", foreground=T.SALMON).pack(side="left")
    else:
        if any(i.get("fix") for i in issues):
            ttk.Button(bar, text="Corrigir automaticamente", style="Accent.TButton", command=lambda: done("fix")).pack(side="left")
        ttk.Button(bar, text="Usar mesmo assim", command=lambda: done("force")).pack(side="left", padx=8)
    ttk.Button(bar, text="Cancelar", command=lambda: done("cancel")).pack(side="right")
    parent.wait_window(win)
    return res["v"]
