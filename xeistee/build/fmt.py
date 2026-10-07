"""Build the Xeistee label in several trim formats.

The band is never scaled: it is cropped out of the 1.5x wide master at the
same px/mm, so the trees keep exactly the size they have on the 177 version.
"""
import os, re, shutil, base64, io
import cairosvg
from PIL import Image
import variants as V
import label_v2 as L

OUT = "out/formate/"
BAND_MASTER = "art/bandF-wide.png"
BAND_PX_PER_MM = 6516 / 184.0          # scale of the accepted 177 x 80 label

FORMATE = {
    # name          trim_w  bleed  ean_bar mark_d qr_s  margin
    "177x80": dict(trim_w=177.0, bleed=3.0, ean_bar=11.0, mark_d=9.4, qr_s=9.0, margin=5.0),
    "170x80": dict(trim_w=170.0, bleed=1.5, ean_bar=10.0, mark_d=9.0, qr_s=8.6, margin=4.5),
    "155x80": dict(trim_w=155.0, bleed=1.5, ean_bar=8.5,  mark_d=8.2, qr_s=8.0, margin=4.0,
                   top=5.2, bottom=48.3, cap_v=1.34, ean_gap=2.0),
}


def band_for(artboard_w):
    """Centre-crop the wide band so it covers the artboard at the original scale."""
    need = int(round((artboard_w + 1.0) * BAND_PX_PER_MM))
    im = Image.open(BAND_MASTER)
    assert need <= im.width, f"band master too narrow: need {need}, have {im.width}"
    x0 = (im.width - need) // 2
    p = f"art/_band_{artboard_w:.0f}.png"
    im.crop((x0, 0, x0 + need, im.height)).save(p)
    return p


def layer(name, inner, hidden=False, locked=False, lid=None):
    st = ' style="display:none"' if hidden else ''
    lk = ' sodipodi:insensitive="true"' if locked else ''
    return (f'<g inkscape:groupmode="layer" inkscape:label="{name}" id="{lid or name}"{st}{lk}>'
            f'{inner}</g>')


NAMES = {"Hintergrund": "Hintergrund", "Berg": "Berg", "Band": "Band (Kräuter)",
         "Front": "Front", "Zutaten": "Zutaten + EAN + Bio + Gesäuse",
         "Naehrwerte": "Nährwerte + Erzeuger", "Codes": "QR + Marken"}


def layered(live):
    import variants as _VM
    _VM.LIVE_TEXT = live
    svg = L.build(None)
    head, rest = svg.split(">", 1)
    head += (' xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd">'
             '<sodipodi:namedview id="nv" inkscape:document-units="mm" units="mm" showgrid="false"/>')
    rest = rest[:rest.rindex("</svg>")]
    parts = re.split(r"<!--LAYER:(\w+)-->", rest)
    out = [head]
    for i in range(1, len(parts), 2):
        out.append(layer(NAMES[parts[i]], parts[i + 1], lid=parts[i]))
    g = (f'<rect x="{L.OX}" y="{L.OY}" width="{L.TRIM_W}" height="{L.TRIM_H}" fill="none" '
         f'stroke="#C0563C" stroke-width="0.25"/>'
         f'<rect x="{L.OX+3}" y="{L.OY+3}" width="{L.TRIM_W-6}" height="{L.TRIM_H-6}" fill="none" '
         f'stroke="#3E7CA8" stroke-width="0.2" stroke-dasharray="1.5,1"/>'
         f'<line x1="{L.FRONT_X0}" y1="0" x2="{L.FRONT_X0}" y2="{L.H}" stroke="#3E7CA8" '
         f'stroke-width="0.2" stroke-dasharray="1.5,1"/>'
         f'<line x1="{L.FRONT_X1}" y1="0" x2="{L.FRONT_X1}" y2="{L.H}" stroke="#3E7CA8" '
         f'stroke-width="0.2" stroke-dasharray="1.5,1"/>')
    out.append(layer("Beschnitt + Sicherheitszone (nicht drucken)", g, hidden=True,
                     locked=True, lid="guides"))
    out.append("</svg>")
    return "".join(out)


def a4_proof(name, png_path, trim_w, trim_h, bleed, copies=3):
    """1:1 sheet to print and cut - the outer edge IS the cut line."""
    im = Image.open(png_path)
    px = im.width / (trim_w + 2 * bleed)
    im = im.crop((round(bleed * px), round(bleed * px),
                  round((bleed + trim_w) * px), round((bleed + trim_h) * px)))
    buf = io.BytesIO(); im.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    x0 = (210 - trim_w) / 2; y = 8.0
    p = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         'width="210mm" height="297mm" viewBox="0 0 210 297"><rect width="210" height="297" fill="white"/>']
    for _ in range(copies):
        p.append(f'<image x="{x0}" y="{y}" width="{trim_w}" height="{trim_h}" '
                 f'preserveAspectRatio="none" xlink:href="data:image/png;base64,{b64}"/>')
        for cx, cy, sx, sy in ((x0, y, -1, -1), (x0 + trim_w, y, 1, -1),
                               (x0, y + trim_h, -1, 1), (x0 + trim_w, y + trim_h, 1, 1)):
            p.append(f'<path d="M{cx+sx*1},{cy} h{sx*4} M{cx},{cy+sy*1} v{sy*4}" '
                     f'stroke="#444" stroke-width="0.15" fill="none"/>')
        y += trim_h + 8.0
    p.append(f'<text x="{x0}" y="{y+2}" font-family="Oswald, Arial, sans-serif" font-size="2.8" '
             f'fill="#777">Xeistee {name} - 1:1, bei 100 % drucken. '
             f'Außenkante = Schnittkante {trim_w:.0f} x {trim_h:.0f} mm.</text></svg>')
    return "".join(p)


def build_one(name, tone="gelb", **kw):
    cfg = dict(FORMATE[name]); cfg.update(kw)
    aw = cfg["trim_w"] + 2 * cfg["bleed"]
    L.configure(band_png=band_for(aw), bg_tone=tone, **cfg)
    d = OUT + name + "/"
    os.makedirs(d, exist_ok=True)
    stem = f"xeistee-{name}-{tone}"
    for live, suf in ((False, "outlines"), (True, "livetext")):
        open(d + f"{stem}-{suf}.svg", "w", encoding="utf-8").write(layered(live))
    svg = open(d + f"{stem}-outlines.svg", encoding="utf-8").read()
    cairosvg.svg2png(bytestring=svg.encode(), write_to=d + f"{stem}.png", output_width=2400)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=d + f"{stem}-print.pdf")
    proof = svg.replace('id="guides" style="display:none"', 'id="guides"')
    cairosvg.svg2png(bytestring=proof.encode(), write_to=d + f"{stem}-beschnitt.png", output_width=2400)
    cairosvg.svg2pdf(bytestring=a4_proof(name, d + f"{stem}.png", cfg["trim_w"], 80.0,
                                         cfg["bleed"]).encode(),
                     write_to=d + f"{stem}-A4-1zu1.pdf")
    return d, stem, cfg


if __name__ == "__main__":
    import sys
    for n in (sys.argv[1:] or ["170x80", "155x80"]):
        d, stem, cfg = build_one(n)
        print(n, "->", d, f"Seitenfläche {(cfg['trim_w']-L.PANEL_W)/2:.1f} mm")
