"""Painel principal: cabecalho com logo clicavel, menu lateral, 7 paginas, eventos do motor. Toda chamada lenta roda em thread."""
import json, os, queue, re, threading, time, tkinter as tk
from tkinter import ttk, messagebox
from . import theme as T
from .dialogs import ask_issues
from .pages_dest import DestPages
from .pages_misc import MiscPages, open_folder
from .pages_start import StartPages, NOAUDIO
from .. import APP_NAME, APP_VERSION, AUTHOR, ffcmd, validation
from ..components import find_ffmpeg
from ..errors import classify
from ..logs import LogHub
from ..paths import asset
from ..proc import run
from ..settings import Settings
from ..streamer import Streamer

PAGES = [("inicio", "Início", "🏠"), ("captura", "Captura", "🎥"), ("destinos", "Destinos", "📡"), ("qualidade", "Qualidade", "⚖"),
         ("diag", "Diagnóstico", "🔧"), ("logs", "Logs", "📋"), ("config", "Configurações", "⚙")]


class App(StartPages, DestPages, MiscPages):
    def __init__(self, root):
        self.root = root; self.st = Settings().load(); self.q = queue.Queue(); self.streamer = None; self.last_streamer = None
        self.ff, self.comp, self.videos, self.audios, self.modes, self.raw_modes, self.sel = None, None, [], [], [], "", 0
        self.v, self.fv, self.suggest = {}, {}, {}
        self.logs = LogHub(self.st.base / "logs", keys=self.st.secret_values)
        try: self.enc_cache = json.loads((self.st.base / "cache" / "encoders.json").read_text(encoding="utf-8"))
        except (OSError, ValueError): self.enc_cache = {}
        T.apply(root); self.img = T.Images(root)
        root.title("%s %s" % (APP_NAME, APP_VERSION)); root.geometry("1160x800"); root.minsize(1020, 720)
        a = self.st.app; self.mode = tk.StringVar(value=a.get("mode", "automatico")); self.quality = tk.DoubleVar(value=a.get("quality", 60))
        self.reserve = tk.DoubleVar(value=a.get("reserve", 25)); self.lowprio = tk.BooleanVar(value=bool(a.get("low_priority", True)))
        self.build_header(); self.build_body(); self.load_ui(); self.set_icon(); self.apply_mode_state(); self.update_preview(); self.refresh_wm()
        root.protocol("WM_DELETE_WINDOW", self.close); root.after(120, self.pump); root.after(300, self.dark_titlebar)
        for n in self.st.notes: self.log(n)
        for n in self.st.key_errors: self.log("Não consegui ler a chave de '%s' (outro usuário/PC?). Digite-a de novo." % n)
        self.detect_ffmpeg()

    # ---------------- infraestrutura ----------------
    def sv(self, k, val=""):
        self.v[k] = tk.StringVar(value=str(val)); return self.v[k]

    def bv(self, k, val=False):
        self.v[k] = tk.BooleanVar(value=bool(val)); return self.v[k]

    def bg(self, fn, done=None):
        def w():
            try: r = fn()
            except Exception as e: r = e
            self.q.put(("call", done, r))
        threading.Thread(target=w, daemon=True).start()

    def log(self, msg):
        self.q.put(("log", msg, None))

    def pump(self):
        try:
            while True:
                kind, a, b = self.q.get_nowait()
                if kind == "call" and a: a(b)
                elif kind == "log":
                    self.log_box.insert("end", "%s  %s\n" % (time.strftime("%H:%M:%S"), a)); self.log_box.see("end"); self.logs.write("engine", a)
                elif kind == "ev": self.on_event(*b)
        except queue.Empty:
            pass
        self.root.after(120, self.pump)

    def set_icon(self):
        try:
            ic = self.img.load("logo", "icone_64.png")
            if ic: self.root.iconphoto(True, ic)
            if os.name == "nt": self.root.iconbitmap(str(asset("logo", "polvonegro.ico")))
        except Exception: pass

    def dark_titlebar(self):
        if os.name != "nt": return
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()); val = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(val), 4)
        except Exception: pass

    # ---------------- construcao ----------------
    def build_header(self):
        h = tk.Frame(self.root, bg=T.BG); h.pack(fill="x", padx=12, pady=(8, 0))
        self.logo_lbl = tk.Label(h, bg=T.BG, bd=0, cursor="hand2", takefocus=True, highlightthickness=0)
        self.logo_img = {}
        for v in ("", "_hover", "_pressed", "_live"): self.logo_img[v] = self.img.logo(v)
        self.logo_set(""); self.logo_lbl.pack(side="left")
        if not self.logo_img[""]: self.logo_lbl.config(text="POLVO NEGRO", fg=T.ACCENT, font=("Segoe UI", 16, "bold"))
        self.live_now = False
        for ev, fn in (("<Enter>", lambda e: self.logo_set("_hover")), ("<Leave>", lambda e: self.logo_set("")), ("<ButtonPress-1>", lambda e: self.logo_set("_pressed")),
                       ("<ButtonRelease-1>", self.logo_click), ("<Return>", lambda e: self.show_page("inicio")), ("<Button-3>", self.logo_menu)):
            self.logo_lbl.bind(ev, fn)
        self.tip = "Voltar ao início"
        t = tk.Frame(h, bg=T.BG); t.pack(side="left", padx=14)
        tk.Label(t, text="POLVO NEGRO LIVE", bg=T.BG, fg=T.FG, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(t, text="v%s  •  captura, transmite, conecta" % APP_VERSION, bg=T.BG, fg=T.MUTED, font=("Segoe UI", 10)).pack(anchor="w")
        c = tk.Frame(h, bg=T.BG); c.pack(side="right")
        self.chip_ff = tk.Label(c, text="FFmpeg: procurando...", bg=T.CARD, fg=T.MUTED, padx=10, pady=4); self.chip_ff.pack(side="left", padx=4)
        self.chip_enc = tk.Label(c, text="Encoder: --", bg=T.CARD, fg=T.MUTED, padx=10, pady=4); self.chip_enc.pack(side="left", padx=4)

    def logo_set(self, variant):
        if variant == "" and getattr(self, "live_now", False): variant = "_live"
        img = self.logo_img.get(variant) or self.logo_img.get("")
        if img: self.logo_lbl.config(image=img); self.logo_lbl.image = img

    def logo_click(self, e):
        self.show_page("inicio"); self.logo_set("_hover")

    def logo_menu(self, e):
        m = tk.Menu(self.root, tearoff=0, bg=T.CARD, fg=T.FG, activebackground=T.ACCENT, activeforeground="#04121f")
        m.add_command(label="Início", command=lambda: self.show_page("inicio")); m.add_command(label="Abrir pasta de logs", command=lambda: open_folder(self.st.base / "logs"))
        m.add_command(label="Abrir pasta de configuração", command=lambda: open_folder(self.st.base)); m.add_command(label="Diagnóstico", command=lambda: self.show_page("diag"))
        m.add_separator(); m.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "%s %s\nCriador: %s\nConfigurações em: %s" % (APP_NAME, APP_VERSION, AUTHOR, self.st.base)))
        m.tk_popup(e.x_root, e.y_root)

    def build_body(self):
        body = tk.Frame(self.root, bg=T.BG); body.pack(fill="both", expand=True, padx=12, pady=10)
        side = tk.Frame(body, bg=T.PANEL, width=190); side.pack(side="left", fill="y"); side.pack_propagate(False)
        self.nav = {}
        for key, title, ico in PAGES:
            l = tk.Label(side, text="  %s  %s" % (ico, title), bg=T.PANEL, fg=T.FG, anchor="w", padx=10, pady=11, cursor="hand2", font=("Segoe UI", 11))
            l.pack(fill="x"); l.bind("<Button-1>", lambda e, k=key: self.show_page(k))
            l.bind("<Enter>", lambda e, w=l: w.config(bg=T.BTN_HOVER) if w is not self.nav.get(self.cur_page) else None); l.bind("<Leave>", lambda e, w=l: w.config(bg=T.ACCENT if w is self.nav.get(self.cur_page) else T.PANEL))
            self.nav[key] = l
        self.cont = tk.Frame(body, bg=T.BG); self.cont.pack(side="left", fill="both", expand=True, padx=(14, 0))
        self.pages, self.cur_page = {}, None
        for key, title, ico in PAGES:
            f = ttk.Frame(self.cont, padding=4); self.pages[key] = f
            getattr(self, {"inicio": "build_inicio", "captura": "build_captura", "destinos": "build_destinos", "qualidade": "build_qualidade", "diag": "build_diag", "logs": "build_logs", "config": "build_config"}[key])(f)
        self.show_page("inicio")

    def show_page(self, key):
        if self.cur_page: self.pages[self.cur_page].pack_forget(); self.nav[self.cur_page].config(bg=T.PANEL, fg=T.FG)
        self.cur_page = key; self.pages[key].pack(fill="both", expand=True); self.nav[key].config(bg=T.ACCENT, fg="#04121f")
        if key == "logs": self.view_log()
        if key == "qualidade": self.update_preview()
        if key == "destinos": self.show_issues()

    def load_ui(self):
        c = self.st.capture; v = self.v
        v["video"].set(c["video"]); v["audio"].set(c["audio"] or NOAUDIO); v["format"].set(c["format"]); v["res"].set("%sx%s" % (c["width"], c["height"])); v["fps"].set(str(c["fps"]))
        v["rtbufsize"].set(c["rtbufsize"]); v["mirror"].set(bool(c["mirror"])); v["rotate"].set(str(c["rotate"])); v["audio_rate"].set(str(c["audio_rate"]) if c.get("audio_rate") else "auto")
        v["ffpath"].set(self.st.app.get("ffmpeg_path", "")); v["wm"].set(str(self.st.app.get("watermark", 10))); v["bufsec"].set(str(self.st.app.get("buffer_seconds", 20)))
        self.saved_opt = c.get("format_opt", "")

    # ---------------- captura -> dict ----------------
    def cap_dict(self):
        v, c = self.v, self.st.capture
        m = re.match(r"\s*(\d+)\s*[xX×]\s*(\d+)", v["res"].get()); w, h = (int(m.group(1)), int(m.group(2))) if m else (c["width"], c["height"])
        fmt = v["format"].get() or "auto"; opt = ""
        for md in self.modes:
            if md["fmt"] == fmt: opt = md["opt"]; break
        if not opt and fmt != "auto": opt = self.saved_opt if fmt == c.get("format") and self.saved_opt else ("vcodec" if fmt in ("mjpeg", "h264") else "pixel_format")
        try: fps = int(v["fps"].get())
        except ValueError: fps = int(c.get("fps") or 30)
        a = v["audio"].get(); r = v["audio_rate"].get()
        return {"video": v["video"].get(), "audio": "" if a in ("", NOAUDIO) else a, "format": fmt, "format_opt": opt, "width": w, "height": h, "fps": fps,
                "rtbufsize": v["rtbufsize"].get().strip() or "256M", "mirror": bool(v["mirror"].get()), "rotate": int(v["rotate"].get() or 0), "audio_rate": int(r) if r.isdigit() else 0, "audio_map": "0:a:0"}

    def save_all(self):
        self.form_to_dest(); self.st.capture = self.cap_dict(); self.saved_opt = self.st.capture["format_opt"]
        self.st.app.update(mode=self.mode.get(), quality=int(self.quality.get()), reserve=int(self.reserve.get()), low_priority=bool(self.lowprio.get())); self.st.save()

    # ---------------- ffmpeg ----------------
    def detect_ffmpeg(self):
        self.chip_ff.config(text="FFmpeg: procurando...", fg=T.MUTED)
        def done(c):
            if isinstance(c, Exception): self.log("Erro ao procurar o FFmpeg: %s" % c); return
            self.comp = c; self.ff = c.path if c.found else None
            if c.found and c.ok: self.chip_ff.config(text="FFmpeg %s ✓" % (c.version.split("-")[0][:10]), fg=T.GREEN); self.log("FFmpeg: %s (%s)" % (c.path, c.arch)); self.refresh_devices()
            elif c.found: self.chip_ff.config(text="FFmpeg com problema", fg=T.ORANGE); self.log("FFmpeg encontrado, mas: %s" % c.detail); self.refresh_devices()
            else: self.chip_ff.config(text="FFmpeg NÃO encontrado", fg=T.SALMON); self.log(c.detail)
        self.bg(lambda: find_ffmpeg(self.st.app.get("ffmpeg_path", "")), done)

    def test_camera(self):
        cap = self.cap_dict()
        if not (self.ff and cap["video"]): self.log("Escolha uma câmera primeiro."); return
        self.log("Testando a câmera por 3 segundos..."); 
        def job():
            cmd = [self.ff, "-hide_banner", "-nostdin", "-loglevel", "info", "-stats"] + ffcmd.input_args(cap) + ["-t", "3", "-map", "0:v:0"] + (["-map", "0:a:0"] if cap["audio"] else []) + ["-f", "null", "-"]
            return run(cmd, 25)
        def done(r):
            code, out = r if not isinstance(r, Exception) else (-1, str(r)); fr = re.findall(r"frame=\s*(\d+)", out)
            if code == 0 and fr and int(fr[-1]) > 0: self.log("✓ Câmera OK: %s quadros em 3 s (%s %dx%d @ %d)." % (fr[-1], cap["format"], cap["width"], cap["height"], cap["fps"]))
            else: c = classify(out); self.log("✗ %s — %s Ação: %s" % (c["title"], c["explanation"], c["action"]))
        self.bg(job, done)

    # ---------------- live ----------------
    def start_live(self):
        if self.streamer: return
        if not self.ff: messagebox.showerror("FFmpeg", "FFmpeg não encontrado. Veja Configurações."); return
        self.form_to_dest(); tested = set(self.enc_values()); issues = []
        for _ in range(3):
            cap = self.cap_dict(); issues = validation.validate_set(self.st.destinations, cap, tested)
            if not any(i["level"] == "erro" for i in issues): break
            choice = ask_issues(self.root, issues)
            if choice == "cancel": return
            if choice == "force": break
            if not validation.apply_fixes(self.st.destinations, issues): break
            self.dest_to_form()
        for i in issues:
            if i["level"] == "aviso": self.log("Aviso: " + i["msg"])
        self.save_all(); cap = self.cap_dict(); dests = [d for d in self.st.destinations if d["enabled"]]
        self.streamer = Streamer(self.ff, cap, dests, lambda k, n, d: self.q.put(("ev", None, (k, n, d))), str(self.st.base / "logs"), buffer_seconds=int(self.st.app.get("buffer_seconds", 20)),
                                 low_priority=bool(self.lowprio.get()), version=APP_VERSION)
        for d in self.st.destinations: self.paint_card(self.dcard[d["id"]], "CONNECTING" if d["enabled"] else "STOPPED", "Preparando..." if d["enabled"] else "Desativado")
        self.paint_card(self.fixed["capture"], "CONNECTING", "%s\n%dx%d @ %d fps (%s)" % (cap["video"], cap["width"], cap["height"], cap["fps"], cap["format"]))
        self.paint_card(self.fixed["audio"], "CONNECTED" if cap["audio"] else "IDLE", cap["audio"] or "Sem áudio")
        self.streamer.start(); self.btn_start.config(state="disabled"); self.btn_stop.config(state="normal")
        self.log("Iniciando: %s" % ", ".join(d["name"] for d in dests))

    def stop_live(self):
        if self.streamer:
            self.btn_stop.config(state="disabled"); threading.Thread(target=self.streamer.stop, daemon=True).start(); self.log("Parando...")

    def restart_dest(self, did):
        if self.streamer and self.streamer.restart(did): self.log("Reiniciando destino %s..." % did)

    def on_event(self, kind, name, data):
        if kind == "state":
            c = self.dcard.get(name)
            if c: self.paint_card(c, data["state"], data["text"][:260], data.get("suspended", False))
            if data["state"] in ("RECONNECTING", "ERROR") and data.get("error"): self.log("%s: %s" % (name, data["text"][:200]))
            self.live_now = bool(self.streamer) and any(self.streamer.rt[x]["state"] == "STREAMING" for x in self.streamer.rt); self.logo_set("")
        elif kind == "enc":
            warn = data["speed"] < 0.95
            self.lbl_enc.config(text="Captura: %.1f fps | perdidos %d | velocidade %.2fx%s" % (data["fps"], data["drop"], data["speed"], "   ⚠ o PC não está acompanhando (reduza resolução/FPS)" if warn else ""), foreground=T.SALMON if warn else T.FG)
            self.chip_enc.config(text="Encoder %.2fx" % data["speed"], fg=T.SALMON if warn else T.GREEN); self.paint_card(self.fixed["encoder"], "STREAMING" if not warn else "RECONNECTING", "%.1f fps • %.2fx • perdidos %d" % (data["fps"], data["speed"], data["drop"]))
            self.paint_card(self.fixed["capture"], "CONNECTED", self.fixed["capture"]["text"].cget("text"))
        elif kind == "hub":
            self.lbl_hub.config(text="Distribuidor: " + " | ".join("canal %d: %d kbps, fila %d%% (%s), %d destino(s)" % (s["canal"], s["kbps"], s["fila_max_%"], s["nivel"], s["destinos_ativos"]) for s in data))
        elif kind == "log": self.log("%s: %s" % (name, data))
        elif kind == "exit":
            if not data.get("user_stop"):
                if data.get("all_failed"): self.log("Todos os destinos falharam; captura encerrada.")
                else:
                    e = data.get("error") or classify("")
                    self.log("⚠ A captura terminou (código %s): %s — %s Ação: %s" % (data["code"], e["title"], e["explanation"], e["action"]))
            if self.streamer:
                self.last_streamer = self.streamer; self.log("Relatório salvo: %s" % self.streamer.write_report())
            self.streamer = None; self.live_now = False; self.logo_set("")
            self.btn_start.config(state="normal"); self.btn_stop.config(state="disabled"); self.lbl_enc.config(text="Captura: --", foreground=T.FG); self.chip_enc.config(text="Encoder: --", fg=T.MUTED)
            for k in ("capture", "encoder", "audio"): self.paint_card(self.fixed[k], "IDLE", "")

    def close(self):
        try:
            if self.streamer: self.streamer.stop()
            self.save_all()
        finally:
            self.root.destroy()
