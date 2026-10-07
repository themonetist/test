"""GS1-layout EAN-13 as clean vector SVG (+PNG), horizontal and vertical, verified with pyzbar."""
import barcode, io, cairosvg
from PIL import Image
from pyzbar.pyzbar import decode

OUT = "/mnt/user-data/outputs/xeistee-band/assets/"
INK, CREAM = "#2E3524", "#ECE0D0"
X = 0.33                      # module width mm (100 % GS1 nominal)
BAR_H = 22.85                 # bar height mm (nominal)
GUARD_EXT = 1.65              # guard bars extend 5 modules into the text zone
TXT_H = 2.75                  # digit height mm (GS1 OCR-B nominal)
QL, QR = 11*X, 7*X            # quiet zones (left 11 modules, right 7)

def build(num12):
    e = barcode.get('ean13', num12)
    full = e.get_fullcode()
    bits = e.build()[0]                       # 95-char string of 1/0
    assert len(bits) == 95
    W = QL + 95*X + QR
    H = BAR_H + GUARD_EXT + TXT_H*0.35 + 0.6
    guard_idx = set(range(0,3)) | set(range(45,50)) | set(range(92,95))
    rects = []
    i = 0
    while i < 95:
        if bits[i] == '1':
            j = i
            while j < 95 and bits[j] == '1' and ((j in guard_idx) == (i in guard_idx)): j += 1
            h = BAR_H + (GUARD_EXT if i in guard_idx else 0)
            rects.append(f'<rect x="{QL+i*X:.3f}" y="0" width="{(j-i)*X:.3f}" height="{h:.3f}" fill="{INK}"/>')
            i = j
        else: i += 1
    ty = BAR_H + GUARD_EXT + 0.15 + TXT_H*0.35    # baseline slightly below extended guards
    font = f'font-family="OCR-B, OCRB, DejaVu Sans Mono, monospace" font-size="{TXT_H*1.32:.2f}" fill="{INK}"'
    def digits(s, x0, x1):
        # spread digits evenly over [x0,x1]
        n = len(s); step = (x1-x0)/n
        return "".join(f'<text x="{x0+step*(k+0.5):.3f}" y="{ty:.3f}" text-anchor="middle" {font}>{c}</text>'
                       for k,c in enumerate(s))
    text = (f'<text x="{QL-0.7:.3f}" y="{ty:.3f}" text-anchor="end" {font}>{full[0]}</text>'
            + digits(full[1:7], QL+3*X, QL+45*X)
            + digits(full[7:], QL+50*X, QL+92*X))
    def svg(bg, rot=False):
        w, h = (H, W) if rot else (W, H)
        tr = f' transform="rotate(-90) translate(-{W:.3f} 0)"' if rot else ''
        bgr = f'<rect width="{w:.3f}" height="{h:.3f}" fill="{CREAM}"/>' if bg else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}mm" height="{h:.3f}mm" viewBox="0 0 {w:.3f} {h:.3f}">'
                f'{bgr}<g{tr}>{"".join(rects)}{text}</g></svg>')
    return full, {"ean-%s-cream"%full: svg(True), "ean-%s"%full: svg(False),
                  "ean-%s-cream-vertical"%full: svg(True, True), "ean-%s-vertical"%full: svg(False, True)}, (W,H)

if __name__ == "__main__":
    full, variants, (W,H) = build("912004893866")
    print(full, f"{W:.2f} x {H:.2f} mm")
    for n, s in variants.items():
        open(OUT+n+".svg","w").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=OUT+n+".png", output_width=2400 if "vertical" not in n else 1800)
        im = Image.open(OUT+n+".png").convert("RGBA")
        bg = Image.new("RGBA", im.size, CREAM); bg.alpha_composite(im); g = bg.convert("L")
        r = decode(g); small = decode(g.resize((g.width//5, g.height//5), Image.LANCZOS))
        print(n, im.size, r[0].data if r else "NO DECODE", "| small:", small[0].data if small else "NO")
