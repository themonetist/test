"""Gesaeuse-Siegel: Varianten im 155x80 rendern, Vergleichsbild + Detailcrops nach out/gesaeuse-varianten/."""
import os, re
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import fmt, label_v2 as L

OUT = "out/gesaeuse-varianten/"
VARIANTEN = [("E", "qr",        "QR | URL | Gesaeuse (vorher)"),
             ("F", "qr-unter",  "URL unter dem QR, Gesaeuse rechts"),
             ("G", "qr-text",   "Story wieder da, kleiner, Gesaeuse rechts"),
             ("H", "qr-breit",  "QR groesser, URL darunter gleich breit"),
             ("I", "qr-rechts", "gespiegelt: Gesaeuse links, QR + URL rechts")]

def run():
    os.makedirs(OUT, exist_ok=True)
    cfg = dict(fmt.FORMATE["155x80"])
    band = fmt.band_for(cfg["trim_w"] + 2*cfg["bleed"])
    crops = []
    for key, mode, desc in VARIANTEN:
        L.configure(band_png=band, bg_tone="gelb", gs_mode=mode, **cfg)
        svg = fmt.layered(False)
        stem = OUT + f"variante-{key}-{mode}"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + ".png", output_width=2400)
        g = re.search(r'<g id="gesaeuse-partner"[^>]*translate\(([\d.]+),([\d.]+)\) scale\(([\d.]+)\)', svg)
        tx, ty, sc = map(float, g.groups())
        vx0, vy0 = tx + L.GS_BOX[0]*sc, ty + L.GS_BOX[1]*sc
        vx1, vy1 = tx + L.GS_BOX[2]*sc, ty + L.GS_BOX[3]*sc
        print(f"{key} {mode:10s} Logo {vx1-vx0:.2f} x {vy1-vy0:.2f} mm, "
              f"x {vx0-L.OX:.2f}..{vx1-L.OX:.2f}, y {vy0-L.OY:.2f}..{vy1-L.OY:.2f} (ab Schnittkante), "
              f"Abstand Schnitt links {vx0-L.OX:.2f} / unten {L.OY+L.TRIM_H-vy1:.2f}")
        im = Image.open(stem + ".png"); px = im.width / L.W
        c = im.crop((0, round(24*px), round(52*px), round(54*px))) if not mode.startswith('qr') else \
            im.crop((round(106*px), round(24*px), round(158*px), round(54*px)))
        c.save(stem + "-detail.png"); crops.append((key, desc, c))
    # Vergleichsblatt
    cw, ch = crops[0][2].size
    sheet = Image.new("RGB", (cw, (ch + 60) * len(crops)), "white")
    d = ImageDraw.Draw(sheet)
    try: f = ImageFont.truetype("fonts/Oswald-500.ttf", 34)
    except OSError: f = None
    for i, (key, desc, c) in enumerate(crops):
        y = i * (ch + 60)
        d.text((12, y + 10), f"{key}: {desc}", fill="#2E3524", font=f)
        sheet.paste(c, (0, y + 60))
    sheet.save(OUT + "vergleich.png")

if __name__ == "__main__":
    run()
