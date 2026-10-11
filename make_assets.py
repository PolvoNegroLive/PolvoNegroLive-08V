"""Gera todas as imagens derivadas da logo original (transparente). Uso: python tools/make_assets.py
Precisa do Pillow SOMENTE para gerar os arquivos. O programa em si NAO precisa de Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/logo/source/Polvo_Negro_Live_original.png"
OUT = ROOT / "assets/logo"
BG = (13, 17, 23)            # mesmo fundo do painel (theme.py)
BLUE = (82, 164, 220); RED = (225, 29, 46)


def load_master():
    im = Image.open(SRC).convert("RGBA")
    a = np.array(im)
    alpha = a[..., 3].astype(float)
    a[..., 3] = np.clip(alpha * (255.0 / max(alpha.max(), 1)), 0, 255).astype("uint8")   # alpha maximo vira 255
    im = Image.fromarray(a)
    box = Image.fromarray((a[..., 3] > 20).astype("uint8") * 255).getbbox()
    im = im.crop(box)
    s = max(im.size); sq = Image.new("RGBA", (s, s), (0, 0, 0, 0)); sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    return sq


def glow(canvas_size, logo, color, radius, strength):
    a = logo.split()[3]
    big = Image.new("L", canvas_size, 0); big.paste(a, ((canvas_size[0] - logo.width) // 2, (canvas_size[1] - logo.height) // 2))
    g = big.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, int(v * strength)))
    layer = Image.new("RGBA", canvas_size, color + (0,)); layer.putalpha(g); return layer


def variants(master, size):
    pad = max(6, round(size * 0.12)); cs = (size + 2 * pad, size + 2 * pad)
    def place(logo_img, extra=None):
        c = Image.new("RGBA", cs, (0, 0, 0, 0))
        if extra is not None:
            c.alpha_composite(extra)
        c.alpha_composite(logo_img, ((cs[0] - logo_img.width) // 2, (cs[1] - logo_img.height) // 2)); return c
    base = master.resize((size, size), Image.LANCZOS)
    out = {"": place(base)}
    out["_hover"] = place(base, glow(cs, base, BLUE, pad * 0.55, 1.6))
    pr = master.resize((round(size * 0.94),) * 2, Image.LANCZOS); out["_pressed"] = place(pr)
    out["_live"] = place(base, glow(cs, base, RED, pad * 0.55, 1.7))
    return out


def icon_image(master_src, size=512):
    im = Image.open(SRC).convert("RGBA"); S = size * 4
    head = im.crop((330, 70, 930, 670)).resize((S, S), Image.LANCZOS)
    bg = Image.new("RGBA", (S, S), (11, 26, 48, 255)); bg.alpha_composite(head)
    m = Image.new("L", (S, S), 0); box = (int(S * .04),) * 2 + (int(S * .96),) * 2; ImageDraw.Draw(m).ellipse(box, fill=255)
    o = Image.new("RGBA", (S, S), (0, 0, 0, 0)); o.paste(bg, (0, 0), m)
    ImageDraw.Draw(o).ellipse(box, outline=BLUE + (255,), width=max(4, int(S * .045)))
    return o.resize((size, size), Image.LANCZOS)


def main():
    master = load_master(); master.resize((512, 512), Image.LANCZOS).save(OUT / "logo_512.png", optimize=True)
    for s in (72, 108, 144, 160):
        for suf, img in variants(master, s).items():
            img.save(OUT / ("logo_%d%s.png" % (s, suf)), optimize=True)
    ic = icon_image(master)
    for s in (32, 64, 256):
        ic.resize((s, s), Image.LANCZOS).save(OUT / ("icone_%d.png" % s), optimize=True)
    ic.save(OUT / "polvonegro.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    # marca d'agua: ja misturada com o fundo do painel (Tk nao faz alpha entre widgets)
    for pct in (5, 10, 15):
        m = master.resize((380, 380), Image.LANCZOS); bg = Image.new("RGBA", (380, 380), BG + (255,))
        a = m.split()[3].point(lambda v, p=pct: int(v * p / 100)); m.putalpha(a); bg.alpha_composite(m)
        bg.convert("RGB").save(OUT / ("marca_dagua_%02d.png" % pct), optimize=True)
    # imagens do instalador (Inno Setup)
    for name, (w, h), lsz in (("wizard_large.bmp", (164, 314), 150), ("wizard_small.bmp", (55, 58), 50)):
        c = Image.new("RGBA", (w, h), (11, 26, 48, 255)); l = master.resize((lsz, lsz), Image.LANCZOS)
        c.alpha_composite(l, ((w - lsz) // 2, (h - lsz) // 2 if h < 100 else 24)); c.convert("RGB").save(OUT / name)
    print("assets gerados em", OUT)


if __name__ == "__main__":
    main()
