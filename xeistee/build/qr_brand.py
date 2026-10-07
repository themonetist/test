"""Styled QR for kraeuterbergbauer.at — vector SVG + PNG, verified with pyzbar."""
import qrcode, io, subprocess, sys
from qrcode.constants import ERROR_CORRECT_H
import cairosvg
from PIL import Image
from pyzbar.pyzbar import decode

URL = "https://www.kraeuterbergbauer.at"
INK = "#2E3524"
OUT = "/mnt/user-data/outputs/xeistee-band/assets/"

def matrix(url):
    q = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, border=0)
    q.add_data(url); q.make(fit=True)
    return q.get_matrix()

def svg(m, fill=INK, style="rounded", centre=False, quiet=2):
    n = len(m); size = n + 2*quiet
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
             f'width="{size*4}mm" height="{size*4}mm">']  # scale set by user in Inkscape
    def finder(i, j):  # top-left module of a 7x7 finder
        return (i < 7 and j < 7) or (i < 7 and j >= n-7) or (i >= n-7 and j < 7)
    cx = cy = size/2
    for i, row in enumerate(m):
        for j, v in enumerate(row):
            if not v or finder(i, j): continue
            x, y = j+quiet, i+quiet
            if centre and ((x+0.5-cx)**2+(y+0.5-cy)**2)**0.5 < n*0.115+0.75:
                continue
            if style == "rounded":
                parts.append(f'<rect x="{x+0.08:.2f}" y="{y+0.08:.2f}" width="0.84" height="0.84" rx="0.32" fill="{fill}"/>')
            elif style == "dots":
                parts.append(f'<circle cx="{x+0.5}" cy="{y+0.5}" r="0.44" fill="{fill}"/>')
    # finders: rounded outer ring + rounded inner square
    for (fi, fj) in [(0,0), (0,n-7), (n-7,0)]:
        x, y = fj+quiet, fi+quiet
        parts.append(f'<path fill-rule="evenodd" fill="{fill}" d="'
                     f'M{x+2},{y} h3 a2,2 0 0 1 2,2 v3 a2,2 0 0 1 -2,2 h-3 a2,2 0 0 1 -2,-2 v-3 a2,2 0 0 1 2,-2 z '
                     f'M{x+2.4},{y+1} h2.2 a1.4,1.4 0 0 1 1.4,1.4 v2.2 a1.4,1.4 0 0 1 -1.4,1.4 h-2.2 a1.4,1.4 0 0 1 -1.4,-1.4 v-2.2 a1.4,1.4 0 0 1 1.4,-1.4 z"/>')
        parts.append(f'<rect x="{x+2}" y="{y+2}" width="3" height="3" rx="1" fill="{fill}"/>')
    if centre:
        r = n*0.115
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" stroke="{fill}" stroke-width="0.5"/>')
        # small mountain mark inside: two peaks
        w = r*0.72; h = r*0.62; bx, by = cx, cy + h*0.5
        parts.append(f'<path fill="{fill}" d="M{bx-w:.2f},{by:.2f} L{bx-w*0.35:.2f},{by-h:.2f} L{bx-w*0.05:.2f},{by-h*0.55:.2f} '
                     f'L{bx+w*0.3:.2f},{by-h*0.85:.2f} L{bx+w:.2f},{by:.2f} Z"/>')
    parts.append('</svg>')
    return "\n".join(parts)

def check(svg_text, name):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=1200, background_color="white")
    im = Image.open(io.BytesIO(png)).convert("L")
    res = decode(im)
    ok = bool(res) and res[0].data.decode() == URL
    # also a small print test: 12 mm at 300 dpi ≈ 142 px
    small = im.resize((142,142), Image.LANCZOS)
    ok_small = bool(decode(small)) and decode(small)[0].data.decode() == URL
    print(f"{name}: decode@1200={ok} decode@142px={ok_small}")
    return ok and ok_small

if __name__ == "__main__":
    import os; os.makedirs(OUT, exist_ok=True)
    m = matrix(URL); print("modules:", len(m))
    for name, kw in {"qr-rounded": dict(style="rounded"),
                     "qr-rounded-mark": dict(style="rounded", centre=True),
                     "qr-dots-mark": dict(style="dots", centre=True)}.items():
        s = svg(m, **kw)
        if not check(s, name): print("  !! FAILED", name); continue
        open(OUT+name+".svg","w").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=OUT+name+".png", output_width=2400)          # transparent
        cairosvg.svg2png(bytestring=s.encode(), write_to=OUT+name+"-cream.png", output_width=2400, background_color="#ECE0D0")
