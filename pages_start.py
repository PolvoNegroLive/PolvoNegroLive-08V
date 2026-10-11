"""Paginas Inicio e Captura."""
import tkinter as tk
from tkinter import ttk
from . import theme as T
from ..devices import list_devices, list_modes, best_default, list_audio_modes, guess_audio_for

NOAUDIO = "(sem áudio)"


class StartPages:
    # ---------------- INICIO ----------------
    def make_card(self, parent, title):
        f = tk.Frame(parent, bg=T.CARD, highlightthickness=1, highlightbackground=T.BORDER, padx=12, pady=10)
        tk.Label(f, text=title, bg=T.CARD, fg=T.MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        row = tk.Frame(f, bg=T.CARD); row.pack(anchor="w", fill="x", pady=(4, 0))
        dot = tk.Label(row, text="●", bg=T.CARD, fg=T.MUTED, font=("Segoe UI", 14)); dot.pack(side="left")
        st = tk.Label(row, text="PARADO", bg=T.CARD, fg=T.FG, font=("Segoe UI", 12, "bold")); st.pack(side="left", padx=6)
        tx = tk.Label(f, text="", bg=T.CARD, fg=T.MUTED, font=("Segoe UI", 9), justify="left", wraplength=250, anchor="w"); tx.pack(anchor="w", fill="x")
        return {"frame": f, "dot": dot, "state": st, "text": tx}

    def build_inicio(self, p):
        top = ttk.Frame(p); top.pack(fill="x")
        self.fixed = {}
        for key, title in (("capture", "CAPTURA"), ("encoder", "ENCODER"), ("audio", "ÁUDIO")):
            c = self.make_card(top, title); c["frame"].pack(side="left", padx=4, fill="x", expand=True); self.fixed[key] = c
        ttk.Label(p, text="DESTINOS", style="H.TLabel").pack(anchor="w", pady=(12, 4))
        self.dest_frame = ttk.Frame(p); self.dest_frame.pack(fill="x")
        bar = ttk.Frame(p); bar.pack(fill="x", pady=12)
        self.btn_start = ttk.Button(bar, text="▶  INICIAR LIVE", style="Accent.TButton", command=self.start_live); self.btn_start.pack(side="left")
        self.btn_stop = ttk.Button(bar, text="■  PARAR", style="Danger.TButton", command=self.stop_live, state="disabled"); self.btn_stop.pack(side="left", padx=8)
        self.lbl_enc = ttk.Label(p, text="Captura: --", font=("Consolas", 10)); self.lbl_enc.pack(anchor="w")
        self.lbl_hub = ttk.Label(p, text="Distribuidor: --", style="Muted.TLabel", font=("Consolas", 9)); self.lbl_hub.pack(anchor="w", pady=(2, 6))
        self.log_box = T.text_widget(p, height=9); self.log_box.pack(fill="both", expand=True)
        self.wm = tk.Label(p, bg=T.BG, bd=0); self.wm.place(relx=1.0, rely=1.0, anchor="se", x=-4, y=-4); self.wm.lower()
        self.rebuild_cards()

    def rebuild_cards(self):
        for w in self.dest_frame.winfo_children():
            w.destroy()
        self.dcard = {}
        for i, d in enumerate(self.st.destinations):
            c = self.make_card(self.dest_frame, d["name"].upper() + ("" if d["enabled"] else "  (desativado)"))
            c["frame"].grid(row=i // 3, column=i % 3, padx=4, pady=4, sticky="nsew"); self.dest_frame.columnconfigure(i % 3, weight=1)
            c["btn"] = ttk.Button(c["frame"], text="REINICIAR", command=lambda did=d["id"]: self.restart_dest(did))
            self.dcard[d["id"]] = c
            self.paint_card(c, "IDLE" if d["enabled"] else "STOPPED", "" if d["enabled"] else "Ative na aba Destinos.")

    def paint_card(self, c, state, text, suspended=False):
        c["dot"].config(fg=T.STATE_COLOR.get(state, T.MUTED)); c["state"].config(text=T.STATE_WORD.get(state, state), fg=T.STATE_COLOR.get(state, T.FG)); c["text"].config(text=text)
        b = c.get("btn")
        if b is not None:
            if suspended:
                b.pack(anchor="w", pady=(6, 0))
            else:
                b.pack_forget()

    def refresh_wm(self):
        img = self.img.watermark(int(self.st.app.get("watermark", 10)))
        self.wm.config(image=img or ""); self.wm.image = img

    # ---------------- CAPTURA ----------------
    def build_captura(self, p):
        f = ttk.LabelFrame(p, text="Fonte (qualquer câmera, webcam ou placa de captura DirectShow)", padding=12); f.pack(fill="x"); f.columnconfigure(1, weight=1)
        ttk.Label(f, text="Vídeo").grid(row=0, column=0, sticky="w", pady=4)
        self.cb_video = ttk.Combobox(f, textvariable=self.sv("video"), state="readonly"); self.cb_video.grid(row=0, column=1, sticky="ew", padx=8)
        self.cb_video.bind("<<ComboboxSelected>>", lambda e: self.read_modes())
        ttk.Label(f, text="Áudio").grid(row=1, column=0, sticky="w", pady=4)
        self.cb_audio = ttk.Combobox(f, textvariable=self.sv("audio", NOAUDIO), state="readonly"); self.cb_audio.grid(row=1, column=1, sticky="ew", padx=8)
        self.cb_audio.bind("<<ComboboxSelected>>", lambda e: self.on_audio())
        self.lbl_audio = ttk.Label(f, text="", foreground=T.ORANGE); self.lbl_audio.grid(row=2, column=1, sticky="w", padx=8)
        self.btn_sugg = ttk.Button(f, text="Usar sugestão", command=self.use_suggestion)
        r = ttk.Frame(f); r.grid(row=3, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Label(r, text="Formato").pack(side="left"); self.cb_fmt = ttk.Combobox(r, textvariable=self.sv("format", "auto"), width=11, values=["auto"]); self.cb_fmt.pack(side="left", padx=(4, 12))
        self.cb_fmt.bind("<<ComboboxSelected>>", lambda e: self.fill_res())
        ttk.Label(r, text="Resolução").pack(side="left"); self.cb_res = ttk.Combobox(r, textvariable=self.sv("res", "1280x720"), width=11); self.cb_res.pack(side="left", padx=(4, 12))
        self.cb_res.bind("<<ComboboxSelected>>", lambda e: self.fill_fps())
        ttk.Label(r, text="FPS").pack(side="left"); self.cb_fps = ttk.Combobox(r, textvariable=self.sv("fps", "30"), width=6); self.cb_fps.pack(side="left", padx=(4, 12))
        ttk.Label(r, text="Taxa do áudio").pack(side="left"); self.cb_rate = ttk.Combobox(r, textvariable=self.sv("audio_rate", "auto"), width=8, values=["auto"]); self.cb_rate.pack(side="left", padx=(4, 12))
        ttk.Label(r, text="Buffer").pack(side="left"); ttk.Entry(r, textvariable=self.sv("rtbufsize", "256M"), width=7).pack(side="left", padx=4)
        r2 = ttk.Frame(f); r2.grid(row=4, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(r2, text="Espelhar", variable=self.bv("mirror")).pack(side="left")
        ttk.Label(r2, text="   Rotação").pack(side="left"); ttk.Combobox(r2, textvariable=self.sv("rotate", "0"), width=5, state="readonly", values=["0", "90", "180", "270"]).pack(side="left", padx=4)
        bt = ttk.Frame(p); bt.pack(fill="x", pady=10)
        ttk.Button(bt, text="Atualizar dispositivos", command=self.refresh_devices).pack(side="left")
        ttk.Button(bt, text="Ler modos da câmera", command=self.read_modes).pack(side="left", padx=6)
        ttk.Button(bt, text="Testar câmera (3 s)", command=self.test_camera).pack(side="left")
        self.lbl_modes = ttk.Label(bt, text="Modos: --", style="Muted.TLabel"); self.lbl_modes.pack(side="left", padx=10)
        ttk.Label(p, wraplength=760, style="Muted.TLabel", text=("Formato, resolução e FPS listam só o que a câmera informou ao Windows. MJPEG costuma ser o mais leve para USB; "
                                                                  "YUY2 não é comprimido e limita o FPS em resoluções altas. A saída de cada destino nunca passa do que a captura entrega.")).pack(anchor="w")

    def refresh_devices(self):
        if not self.ff:
            self.log("FFmpeg não encontrado. Veja Configurações."); return
        self.bg(lambda: list_devices(self.ff), self.after_devices)

    def after_devices(self, r):
        if isinstance(r, Exception):
            self.log("Erro ao listar dispositivos: %s" % r); return
        videos, audios, raw = r; self.videos, self.audios = videos, audios
        self.cb_video["values"] = videos; self.cb_audio["values"] = [NOAUDIO] + audios
        if self.v["video"].get() not in videos:
            self.v["video"].set(videos[0] if videos else "")
        if self.v["audio"].get() not in [NOAUDIO] + audios:
            self.v["audio"].set(NOAUDIO)
        self.log("Dispositivos: %d vídeo, %d áudio." % (len(videos), len(audios)))
        if videos:
            self.read_modes(keep=True)
        self.on_audio()

    def on_audio(self):
        a = self.v["audio"].get()
        if a in ("", NOAUDIO):
            self.lbl_audio.config(text="VÍDEO DISPONÍVEL — ÁUDIO NÃO SELECIONADO. A live sairá sem som.")
            self.sugg = guess_audio_for(self.v["video"].get(), self.audios)
            if self.sugg:
                self.btn_sugg.config(text="Usar sugestão: " + self.sugg[:40]); self.btn_sugg.grid(row=2, column=1, sticky="e", padx=8)
            else:
                self.btn_sugg.grid_remove()
        else:
            self.lbl_audio.config(text=""); self.btn_sugg.grid_remove()
            if self.ff:
                def done(r):
                    if isinstance(r, Exception): return
                    m = r[0]; self.cb_rate["values"] = ["auto"] + [str(x) for x in m["rates"]]
                self.bg(lambda: list_audio_modes(self.ff, a), done)

    def use_suggestion(self):
        if getattr(self, "sugg", None):
            self.v["audio"].set(self.sugg); self.on_audio()

    def read_modes(self, keep=False):
        dev = self.v["video"].get()
        if not (self.ff and dev):
            return
        self.lbl_modes.config(text="Lendo modos...")
        def done(r):
            if isinstance(r, Exception):
                self.lbl_modes.config(text="Erro"); self.log("Erro ao ler modos: %s" % r); return
            self.modes, self.raw_modes = r; self.lbl_modes.config(text="Modos: %d" % len(self.modes))
            self.cb_fmt["values"] = ["auto"] + sorted({m["fmt"] for m in self.modes})
            if not self.modes:
                self.log("A câmera não informou modos (ou está em uso por outro programa). Veja Diagnóstico."); return
            ok = any(m["fmt"] == self.v["format"].get() and "%dx%d" % (m["w"], m["h"]) == self.v["res"].get() for m in self.modes)
            if keep and ok:
                self.fill_res(); self.fill_fps(); return
            b = best_default(self.modes); self.v["format"].set(b["fmt"]); self.fill_res(); self.v["res"].set("%dx%d" % (b["w"], b["h"])); self.fill_fps()
            self.v["fps"].set(str(30 if 30 in b["fps"] else max(b["fps"])))
            self.log("Modo sugerido: %s %dx%d @ %s (troque se quiser)." % (b["fmt"], b["w"], b["h"], self.v["fps"].get()))
        self.bg(lambda: list_modes(self.ff, dev), done)

    def fill_res(self):
        f = self.v["format"].get()
        res = sorted({(m["w"], m["h"]) for m in self.modes if f == "auto" or m["fmt"] == f}, key=lambda s: s[0] * s[1])
        self.cb_res["values"] = ["%dx%d" % s for s in res]
        if res and self.v["res"].get() not in self.cb_res["values"]:
            self.v["res"].set(self.cb_res["values"][-1])
        self.fill_fps()

    def fill_fps(self):
        f, r = self.v["format"].get(), self.v["res"].get(); fps = set()
        for m in self.modes:
            if (f == "auto" or m["fmt"] == f) and "%dx%d" % (m["w"], m["h"]) == r:
                fps |= set(m["fps"])
        vals = sorted(fps); self.cb_fps["values"] = [str(x) for x in vals]
        if vals and self.v["fps"].get() not in self.cb_fps["values"]:
            self.v["fps"].set(str(30 if 30 in vals else vals[-1]))
