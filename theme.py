"""Tema escuro do Polvo Negro Live + carregamento das imagens (logo) por escala de tela. So biblioteca padrao."""
import tkinter as tk
from tkinter import ttk
from ..paths import asset

BG, CARD, PANEL = "#0d1117", "#111a2b", "#0b1a30"
FG, MUTED, ACCENT = "#e6edf3", "#8b98a9", "#52a4dc"
RED, ORANGE, GREEN, SALMON = "#e11d2e", "#d29922", "#2ea043", "#ff7b72"
BORDER, BTN, BTN_HOVER = "#1f2b3d", "#1b2a41", "#25405f"
FONT = ("Segoe UI", 10)
STATE_COLOR = {"IDLE": MUTED, "CONNECTING": ORANGE, "CONNECTED": ORANGE, "STREAMING": RED, "RECONNECTING": ORANGE, "ERROR": SALMON, "STOPPING": MUTED, "STOPPED": MUTED}
STATE_WORD = {"IDLE": "PARADO", "CONNECTING": "CONECTANDO", "CONNECTED": "CONECTADO", "STREAMING": "AO VIVO", "RECONNECTING": "RECONECTANDO", "ERROR": "ERRO",
              "STOPPING": "PARANDO", "STOPPED": "PARADO"}


def apply(root):
    root.configure(bg=BG)
    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass
    s.configure(".", background=BG, foreground=FG, fieldbackground=CARD, bordercolor=BORDER, lightcolor=BG, darkcolor=BG, troughcolor=CARD, focuscolor=ACCENT, font=FONT)
    s.configure("TFrame", background=BG); s.configure("Card.TFrame", background=CARD, relief="flat")
    s.configure("TLabel", background=BG, foreground=FG); s.configure("Card.TLabel", background=CARD, foreground=FG)
    s.configure("Muted.TLabel", background=BG, foreground=MUTED); s.configure("Title.TLabel", background=BG, foreground=FG, font=("Segoe UI", 18, "bold"))
    s.configure("H.TLabel", background=BG, foreground=ACCENT, font=("Segoe UI", 12, "bold"))
    s.configure("TLabelframe", background=BG, bordercolor=BORDER); s.configure("TLabelframe.Label", background=BG, foreground=ACCENT, font=("Segoe UI", 10, "bold"))
    s.configure("TButton", background=BTN, foreground=FG, padding=(12, 6), borderwidth=0)
    s.map("TButton", background=[("disabled", "#141c28"), ("active", BTN_HOVER)], foreground=[("disabled", "#566274")])
    s.configure("Accent.TButton", background=ACCENT, foreground="#04121f", font=("Segoe UI", 11, "bold"), padding=(18, 9))
    s.map("Accent.TButton", background=[("disabled", "#2b4a63"), ("active", "#74b9e8")])
    s.configure("Danger.TButton", background="#7a1520", foreground="#ffffff", padding=(14, 9))
    s.map("Danger.TButton", background=[("disabled", "#2a1418"), ("active", "#a11c2b")])
    s.configure("TEntry", fieldbackground=CARD, foreground=FG, insertcolor=FG, bordercolor=BORDER); s.map("TEntry", fieldbackground=[("disabled", "#0f1520")], foreground=[("disabled", "#566274")])
    s.configure("TCombobox", fieldbackground=CARD, background=BTN, foreground=FG, arrowcolor=ACCENT, bordercolor=BORDER, selectbackground=CARD, selectforeground=FG)
    s.map("TCombobox", fieldbackground=[("readonly", CARD), ("disabled", "#0f1520")], foreground=[("disabled", "#566274")], selectbackground=[("readonly", CARD)], selectforeground=[("readonly", FG)])
    s.configure("TCheckbutton", background=BG, foreground=FG); s.map("TCheckbutton", background=[("active", BG)], foreground=[("disabled", "#566274")])
    s.configure("TRadiobutton", background=BG, foreground=FG); s.map("TRadiobutton", background=[("active", BG)])
    s.configure("Horizontal.TScale", background=BG, troughcolor=CARD); s.configure("Horizontal.TProgressbar", troughcolor=CARD, background=ACCENT, bordercolor=BORDER)
    s.configure("TScrollbar", background=BTN, troughcolor=CARD, bordercolor=BORDER, arrowcolor=ACCENT)
    for k, v in (("Listbox.background", CARD), ("Listbox.foreground", FG), ("Listbox.selectBackground", ACCENT), ("Listbox.selectForeground", "#04121f")):
        root.option_add("*TCombobox*" + k, v)


def text_widget(parent, **kw):
    return tk.Text(parent, bg=CARD, fg=FG, insertbackground=FG, relief="flat", highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
                   font=("Consolas", 9), wrap="word", **kw)


class Images:
    """Carrega a logo na escala certa (72/108/144 px). Se o arquivo faltar devolve None: o painel mostra so o texto, sem travar."""

    def __init__(self, root):
        self.root, self._cache = root, {}
        try:
            sc = root.winfo_fpixels("1i") / 96.0
        except tk.TclError:
            sc = 1.0
        self.size = 72 if sc < 1.25 else (108 if sc < 1.75 else 144)

    def load(self, *parts):
        key = "/".join(parts)
        if key not in self._cache:
            try:
                self._cache[key] = tk.PhotoImage(file=str(asset(*parts)))
            except (tk.TclError, OSError):
                self._cache[key] = None
        return self._cache[key]

    def logo(self, variant=""):
        return self.load("logo", "logo_%d%s.png" % (self.size, variant))

    def watermark(self, pct):
        return self.load("logo", "marca_dagua_%02d.png" % pct) if pct in (5, 10, 15) else None
