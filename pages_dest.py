"""Paginas Destinos e Qualidade."""
import tkinter as tk
from tkinter import ttk, messagebox
from . import theme as T
from .. import performance as P
from ..conntest import test_connection
from ..secrets import mask_key
from ..settings import KIND_DEFAULTS
from ..validation import validate_destination, kbps

KINDS = {"youtube": "YouTube", "tiktok": "TikTok", "restream": "Restream", "custom": "Personalizado"}
LOCKS = {"res": ("width", "height"), "fps": ("fps",), "br": ("video_bitrate",), "enc": ("encoder",)}


class DestPages:
    # ---------------- DESTINOS ----------------
    def build_destinos(self, p):
        left = ttk.Frame(p); left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="Destinos", style="H.TLabel").pack(anchor="w")
        self.lb = tk.Listbox(left, width=24, height=12, bg=T.CARD, fg=T.FG, selectbackground=T.ACCENT, selectforeground="#04121f", relief="flat", highlightthickness=1, highlightbackground=T.BORDER, exportselection=False)
        self.lb.pack(fill="y", pady=4); self.lb.bind("<<ListboxSelect>>", lambda e: self.on_select())
        self.add_kind = tk.StringVar(value="Personalizado"); ttk.Combobox(left, textvariable=self.add_kind, values=list(KINDS.values()), state="readonly", width=21).pack(pady=(6, 2))
        ttk.Button(left, text="＋ Adicionar destino", command=self.add_dest).pack(fill="x"); ttk.Button(left, text="－ Remover selecionado", command=self.remove_dest).pack(fill="x", pady=4)
        right = ttk.Frame(p); right.pack(side="left", fill="both", expand=True); right.columnconfigure(1, weight=1)
        fv, r = self.fv, 0
        def row(label, widget_factory, span=3):
            nonlocal r
            ttk.Label(right, text=label).grid(row=r, column=0, sticky="w", pady=3); w = widget_factory(); w.grid(row=r, column=1, columnspan=span, sticky="ew", padx=8); r += 1; return w
        for k in ("name", "kind", "server", "backup", "key", "w", "h", "fps", "br", "fit", "enc", "preset", "abr"):
            fv[k] = tk.StringVar()
        fv["enabled"], fv["fpsconv"] = tk.BooleanVar(), tk.BooleanVar()
        for k in LOCKS:
            fv["lock_" + k] = tk.BooleanVar()
        row("Nome", lambda: ttk.Entry(right, textvariable=fv["name"]))
        row("Tipo", lambda: ttk.Combobox(right, textvariable=fv["kind"], values=list(KINDS.values()), state="readonly"))
        row("", lambda: ttk.Checkbutton(right, text="Destino ativo nesta live", variable=fv["enabled"]))
        row("Servidor", lambda: ttk.Entry(right, textvariable=fv["server"]))
        row("Servidor de backup", lambda: ttk.Entry(right, textvariable=fv["backup"]))
        kf = ttk.Frame(right); ttk.Label(right, text="Chave").grid(row=r, column=0, sticky="w", pady=3); kf.grid(row=r, column=1, sticky="ew", padx=8); r += 1
        kf.columnconfigure(0, weight=1); self.key_entry = ttk.Entry(kf, textvariable=fv["key"], show="•"); self.key_entry.grid(row=0, column=0, sticky="ew")
        ttk.Button(kf, text="Mostrar", width=9, command=lambda: self.key_entry.config(show="" if self.key_entry.cget("show") else "•")).grid(row=0, column=1, padx=(6, 0))
        self.lbl_key = ttk.Label(right, text="", style="Muted.TLabel"); self.lbl_key.grid(row=r, column=1, sticky="w", padx=8); r += 1
        g = ttk.LabelFrame(right, text="Vídeo e áudio deste destino", padding=8); g.grid(row=r, column=0, columnspan=4, sticky="ew", pady=8); r += 1
        self.mw = {k: [] for k in ("res", "fps", "br", "enc", "preset", "fit", "fpsconv", "abr")}
        def put(col, label, widget, grp, lock=None):
            ttk.Label(g, text=label).grid(row=0, column=col * 2, sticky="w", padx=(0, 4)); widget.grid(row=0, column=col * 2 + 1, padx=(0, 10)); self.mw[grp].append(widget)
        put(0, "Largura", ttk.Entry(g, textvariable=fv["w"], width=6), "res"); put(1, "Altura", ttk.Entry(g, textvariable=fv["h"], width=6), "res")
        put(2, "FPS", ttk.Entry(g, textvariable=fv["fps"], width=5), "fps"); put(3, "Bitrate", ttk.Entry(g, textvariable=fv["br"], width=8), "br")
        g2 = ttk.Frame(g); g2.grid(row=1, column=0, columnspan=8, sticky="w", pady=(8, 0))
        def put2(label, widget, grp):
            ttk.Label(g2, text=label).pack(side="left", padx=(0, 4)); widget.pack(side="left", padx=(0, 10)); self.mw[grp].append(widget)
        put2("Enquadramento", ttk.Combobox(g2, textvariable=fv["fit"], values=["cortar", "ajustar", "esticar"], state="readonly", width=9), "fit")
        self.cb_enc = ttk.Combobox(g2, textvariable=fv["enc"], values=self.enc_values(), state="readonly", width=12); put2("Encoder", self.cb_enc, "enc")
        put2("Preset", ttk.Combobox(g2, textvariable=fv["preset"], values=P.PRESETS, state="readonly", width=10), "preset")
        put2("Áudio", ttk.Combobox(g2, textvariable=fv["abr"], values=["64k", "96k", "128k", "160k", "192k"], state="readonly", width=6), "abr")
        cb = ttk.Checkbutton(g2, text="Conversão de FPS (duplicar quadros de propósito)", variable=fv["fpsconv"]); cb.pack(side="left"); self.mw["fpsconv"].append(cb)
        lk = ttk.Frame(g); lk.grid(row=2, column=0, columnspan=8, sticky="w", pady=(8, 0)); ttk.Label(lk, text="Fixar (o Automático não altera):", style="Muted.TLabel").pack(side="left")
        for k, t in (("res", "resolução"), ("fps", "FPS"), ("br", "bitrate"), ("enc", "encoder")):
            ttk.Checkbutton(lk, text=t, variable=fv["lock_" + k], command=self.apply_mode_state).pack(side="left", padx=6)
        self.lbl_issues = tk.Label(right, text="", bg=T.BG, fg=T.ORANGE, justify="left", anchor="w", wraplength=520); self.lbl_issues.grid(row=r, column=0, columnspan=4, sticky="ew"); r += 1
        bt = ttk.Frame(right); bt.grid(row=r, column=0, columnspan=4, sticky="w", pady=6)
        ttk.Button(bt, text="Salvar destino", command=self.save_dest).pack(side="left")
        ttk.Button(bt, text="TESTAR CONEXÃO (rede)", command=self.conn_test).pack(side="left", padx=6)
        ttk.Button(bt, text="TESTAR PUBLICAÇÃO (envia 5 s)", command=lambda: self.conn_test(True)).pack(side="left")
        self.conn_out = T.text_widget(right, height=7); self.conn_out.grid(row=r + 1, column=0, columnspan=4, sticky="nsew")
        self.refresh_dest_list()

    def enc_values(self):
        return ["libx264"] + [e for e, ok in self.enc_cache.items() if ok and e != "libx264"]

    def refresh_dest_list(self, keep=None):
        self.lb.delete(0, "end")
        for d in self.st.destinations:
            self.lb.insert("end", ("● " if d["enabled"] else "○ ") + d["name"])
        if self.st.destinations:
            i = keep if keep is not None and keep < len(self.st.destinations) else 0
            self.lb.selection_clear(0, "end"); self.lb.selection_set(i); self.sel = i; self.dest_to_form()

    def on_select(self):
        s = self.lb.curselection()
        if s:
            self.form_to_dest(); self.sel = s[0]; self.dest_to_form()

    def cur(self):
        return self.st.destinations[self.sel] if 0 <= getattr(self, "sel", -1) < len(self.st.destinations) else None

    def dest_to_form(self):
        d, fv = self.cur(), self.fv
        if not d: return
        fv["name"].set(d["name"]); fv["kind"].set(KINDS.get(d["kind"], "Personalizado")); fv["enabled"].set(d["enabled"]); fv["server"].set(d["server"]); fv["backup"].set(d.get("backup_server", ""))
        fv["key"].set(d["stream_key"]); fv["w"].set(d["width"]); fv["h"].set(d["height"]); fv["fps"].set(d["fps"]); fv["br"].set(d["video_bitrate"]); fv["fit"].set(d["fit"])
        fv["enc"].set(d["encoder"]); fv["preset"].set(d["preset"]); fv["abr"].set(d["audio_bitrate"]); fv["fpsconv"].set(d.get("fps_conversion", False))
        for k, names in LOCKS.items():
            fv["lock_" + k].set(any(n in d.get("locks", []) for n in names))
        self.lbl_key.config(text=("Chave salva: " + mask_key(d["stream_key"])) if d["stream_key"] else "Nenhuma chave informada."); self.apply_mode_state(); self.show_issues()

    def form_to_dest(self):
        d, fv = self.cur(), self.fv
        if not d or not fv["name"].get() and not fv["server"].get() and not fv["w"].get(): return
        inv = {v: k for k, v in KINDS.items()}
        d.update(name=fv["name"].get().strip() or d["name"], kind=inv.get(fv["kind"].get(), "custom"), enabled=bool(fv["enabled"].get()), server=fv["server"].get().strip(),
                 backup_server=fv["backup"].get().strip(), stream_key=fv["key"].get().strip(), fit=fv["fit"].get() or "cortar", encoder=fv["enc"].get() or "libx264",
                 preset=fv["preset"].get() or "veryfast", audio_bitrate=fv["abr"].get() or "128k", fps_conversion=bool(fv["fpsconv"].get()), video_bitrate=fv["br"].get().strip() or "2000k")
        for k, key in (("w", "width"), ("h", "height"), ("fps", "fps")):
            try: d[key] = int(fv[k].get())
            except ValueError: pass
        d["locks"] = [n for k, names in LOCKS.items() if fv["lock_" + k].get() for n in names]

    def save_dest(self):
        self.form_to_dest(); self.st.save(); self.refresh_dest_list(self.sel); self.rebuild_cards(); self.log("Destino salvo (chave protegida).")

    def add_dest(self):
        self.form_to_dest(); inv = {v: k for k, v in KINDS.items()}; d = self.st.new_destination(inv.get(self.add_kind.get(), "custom"))
        self.st.destinations.append(d); self.refresh_dest_list(len(self.st.destinations) - 1); self.rebuild_cards()

    def remove_dest(self):
        d = self.cur()
        if d and messagebox.askyesno("Remover", "Remover o destino '%s'?" % d["name"]):
            self.st.destinations.remove(d); self.refresh_dest_list(0); self.rebuild_cards(); self.st.save()

    def apply_mode_state(self):
        mode = self.mode.get()
        for grp, widgets in self.mw.items():
            locked = self.fv.get("lock_" + grp) is not None and self.fv["lock_" + grp].get()
            on = mode == "avancado" or (mode == "manual" and grp in ("res", "fps", "br", "fit")) or (mode == "automatico" and locked)
            for w in widgets:
                try: w.config(state=("readonly" if isinstance(w, ttk.Combobox) else "normal") if on else "disabled")
                except tk.TclError: pass

    def show_issues(self):
        d = self.cur()
        if not d: return
        self.form_to_dest()
        issues = validate_destination(d, self.cap_dict(), set(self.enc_values()))
        self.lbl_issues.config(text="\n".join(("✖ " if i["level"] == "erro" else "⚠ ") + i["msg"] for i in issues[:6]), fg=T.SALMON if any(i["level"] == "erro" for i in issues) else T.ORANGE)

    def conn_test(self, publish=False):
        self.form_to_dest(); d = self.cur()
        if not d: return
        if publish and not messagebox.askyesno("Testar publicação", "Isto ENVIA 5 segundos de imagem de teste ao servidor real.\nSe a sua live já estiver no ar nessa plataforma, os espectadores verão a imagem de teste.\n\nContinuar?"):
            return
        self.conn_out.delete("1.0", "end"); self.conn_out.insert("end", "Testando %s...\n" % d["name"])
        def job(): return test_connection(d["server"], d["stream_key"], d["kind"], self.ff, publish)
        def done(r):
            self.conn_out.delete("1.0", "end")
            if isinstance(r, Exception): self.conn_out.insert("end", "Erro: %s\n" % r); return
            verdict, stages = r
            for s in stages: self.conn_out.insert("end", "%s %-11s %s\n" % ("✓" if s["ok"] else "✗", s["stage"], s["detail"]))
            self.conn_out.insert("end", "\nRESULTADO: %s\n" % verdict)
            if not publish: self.conn_out.insert("end", "(Este teste não valida a chave: ela só é validada ao publicar.)\n")
        self.bg(job, done)

    # ---------------- QUALIDADE ----------------
    def build_qualidade(self, p):
        top = ttk.LabelFrame(p, text="Modo", padding=10); top.pack(fill="x")
        for v, t in (("automatico", "Automático (o sistema escolhe)"), ("manual", "Manual (resolução/FPS/bitrate)"), ("avancado", "Avançado (tudo)")):
            ttk.Radiobutton(top, text=t, value=v, variable=self.mode, command=self.on_mode).pack(side="left", padx=8)
        q = ttk.LabelFrame(p, text="Qualidade ↔ Desempenho", padding=10); q.pack(fill="x", pady=8)
        row = ttk.Frame(q); row.pack(fill="x")
        ttk.Label(row, text="MAIS DESEMPENHO").pack(side="left"); self.sc_q = ttk.Scale(row, from_=0, to=100, variable=self.quality, command=lambda v: self.update_preview()); self.sc_q.pack(side="left", fill="x", expand=True, padx=10)
        ttk.Label(row, text="MAIS QUALIDADE").pack(side="left"); self.lbl_q = ttk.Label(q, text="", style="H.TLabel"); self.lbl_q.pack(anchor="center")
        row2 = ttk.Frame(q); row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="Reserva do Windows").pack(side="left"); self.sc_r = ttk.Scale(row2, from_=0, to=50, variable=self.reserve, command=lambda v: self.update_preview()); self.sc_r.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_r = ttk.Label(row2, text=""); self.lbl_r.pack(side="left")
        ttk.Checkbutton(q, text="Prioridade baixa do encoder (deixa o Windows respirar)", variable=self.lowprio).pack(anchor="w", pady=(8, 0))
        self.prev = T.text_widget(p, height=7); self.prev.pack(fill="x", pady=6)
        bt = ttk.Frame(p); bt.pack(fill="x")
        ttk.Button(bt, text="APLICAR aos destinos", style="Accent.TButton", command=self.apply_plan).pack(side="left")
        ttk.Button(bt, text="TESTAR CONFIGURAÇÃO (10 s)", command=self.test_config).pack(side="left", padx=8)
        self.btn_accept = ttk.Button(bt, text="Aceitar sugestão mais leve", command=self.accept_suggestion)
        self.pb = ttk.Progressbar(p, maximum=100); self.pb.pack(fill="x", pady=(8, 2))
        self.res_lbl = tk.Label(p, text="", bg=T.BG, fg=T.FG, justify="left", anchor="w", wraplength=760, font=("Segoe UI", 10)); self.res_lbl.pack(fill="x")
        ttk.Label(p, wraplength=760, style="Muted.TLabel", text=("O controle escolhe resolução, FPS, bitrate e preset dentro do que a câmera entrega e das faixas recomendadas; nunca sobe FPS acima da captura. "
                                                                  "A reserva do Windows é um orçamento de planejamento (o teste mede a CPU de verdade).")).pack(anchor="w", pady=4)
        self.update_preview()

    def on_mode(self):
        self.st.app["mode"] = self.mode.get(); self.apply_mode_state()

    def lock_names(self, d):
        return list(d.get("locks", []))

    def plan_for(self, d):
        return P.plan(self.quality.get(), self.cap_dict(), d["height"] > d["width"], int(self.reserve.get()), self.lock_names(d), d)

    def update_preview(self):
        self.lbl_q.config(text="%d%%" % int(self.quality.get())); self.lbl_r.config(text="%d%%" % int(self.reserve.get()))
        self.prev.delete("1.0", "end"); cap = self.cap_dict()
        self.prev.insert("end", "Captura: %sx%s @ %s fps\n" % (cap["width"], cap["height"], cap["fps"]))
        for d in self.st.destinations:
            if d["enabled"]:
                p = self.plan_for(d); self.prev.insert("end", "• %-14s → %dx%d @ %d fps, %s, preset %s%s\n" % (d["name"], p["width"], p["height"], p["fps"], p["video_bitrate"], p["preset"], "  (com itens fixados)" if d.get("locks") else ""))

    def apply_plan(self):
        self.form_to_dest()
        for d in self.st.destinations:
            if d["enabled"]:
                p = self.plan_for(d); d.update(width=p["width"], height=p["height"], fps=p["fps"], video_bitrate=p["video_bitrate"], preset=p["preset"])
        self.st.app.update(quality=int(self.quality.get()), reserve=int(self.reserve.get())); self.st.save(); self.dest_to_form(); self.update_preview(); self.log("Plano de qualidade aplicado aos destinos.")

    def test_config(self):
        from .. import ffcmd
        if self.streamer or not self.ff:
            self.res_lbl.config(text="Pare a live (ou configure o FFmpeg) antes de testar.", fg=T.ORANGE); return
        self.form_to_dest(); cap = self.cap_dict(); dests = [dict(d) for d in self.st.destinations if d["enabled"]]
        if not dests:
            self.res_lbl.config(text="Ative pelo menos um destino.", fg=T.ORANGE); return
        synthetic = not cap.get("video")
        if synthetic:
            ia, scap = ffcmd.lavfi_source(realtime=False); cap = {**cap, **scap}
        else:
            ia = ffcmd.input_args(cap)
        self.pb["value"] = 0; self.res_lbl.config(text="Testando por 10 s com o mesmo caminho da live (nada é publicado)%s..." % (" — SEM câmera, fonte sintética" if synthetic else ""), fg=T.FG)
        def prog(frac, fps, sp): self.q.put(("call", lambda _: self.pb.config(value=frac * 100), None))
        def job(): return P.run_test(self.ff, ia, cap, dests, 10, bool(self.lowprio.get()), prog, realtime_source=not synthetic)
        def done(r):
            self.pb["value"] = 100
            if isinstance(r, Exception): self.res_lbl.config(text="Erro no teste: %s" % r, fg=T.SALMON); return
            budget = 100 - int(self.reserve.get()); verdict, why = P.evaluate(r, budget, not synthetic)
            color = {"RECOMENDADA": T.GREEN, "PESADA": T.ORANGE}.get(verdict, T.SALMON)
            self.res_lbl.config(text="%s\n%s\nFPS %.1f | velocidade %.2fx | quadros perdidos %d | CPU média %.0f%%" % (verdict, why, r["fps"], r["speed"], r["drops"], r["cpu_avg"]), fg=color)
            self.suggest = {}
            if verdict != "RECOMENDADA":
                for d in dests:
                    s = P.step_down({"width": d["width"], "height": d["height"], "fps": d["fps"]}, self.cap_dict(), d["height"] > d["width"])
                    if s: self.suggest[d["id"]] = s
            if self.suggest: self.btn_accept.pack(side="left")
            else: self.btn_accept.pack_forget()
        self.bg(job, done)

    def accept_suggestion(self):
        for d in self.st.destinations:
            s = getattr(self, "suggest", {}).get(d["id"])
            if s: d.update(width=s["width"], height=s["height"], fps=s["fps"], video_bitrate=s["video_bitrate"])
        self.st.save(); self.dest_to_form(); self.update_preview(); self.btn_accept.pack_forget(); self.log("Sugestão mais leve aplicada. Rode o teste de novo.")
