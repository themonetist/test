#!/usr/bin/env python3
"""X'Eistee label - variant generator.

Every variant is a real print file: 70 x 125 mm trim + 3 mm bleed, type as
outlines, illustration placed as an embedded image. What you see IS the file
that goes to the printer - nothing is a mockup.

Only the ILLUSTRATION comes from ChatGPT. Type, layout, colour and copy are
built here, so a variant never changes appearance between preview and print.
"""
import base64, math, os
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

MM = 1.0
TRIM_W, TRIM_H = 187.0, 100.0   # WRAP. etivera longneck 330 ml: 60.4 mm dia -> 189.8 mm
                                # 170 leaves a ~3 mm gap. Height set per render (100 or 80).
PANEL_W = 60.4                  # front panel = bottle diameter
BLEED = 3.0
W, H = TRIM_W + 2*BLEED, TRIM_H + 2*BLEED
OX, OY = BLEED, BLEED
FLOOR_W = 0.20

PALETTE = {
    "cream":   "#EDE3D2",
    "ink":     "#2F3512",   # dark olive-black, measured off favorite.png
    "green":   "#146B21",   # brand green, from the old label
    "gold":    "#DEAF51",
    "rock":    "#7A7F5A",
    "red":     "#B11F34",   # brand red, from the old label
    "deep":    "#2F3720",
}

DISPLAY_FONTS = {
    "Oswald":        "fonts/Oswald-700.ttf",
    "Anton":         "fonts/cand-Anton.ttf",
    "BebasNeue":     "fonts/cand-BebasNeue.ttf",
    "FjallaOne":     "fonts/cand-FjallaOne.ttf",
    "BarlowCond":    "fonts/cand-BarlowCond-700.ttf",
    "ArchivoNarrow": "fonts/cand-ArchivoNarrow-700.ttf",
    "SairaCond":     "fonts/cand-SairaCond-700.ttf",
    "BigShoulders":  "fonts/cand-BigShoulders-700.ttf",
}
TEXT_FONTS = {500: "fonts/Oswald-500.ttf", 400: "fonts/Oswald-400.ttf",
              300: "fonts/Oswald-300.ttf", 600: "fonts/Oswald-600.ttf"}

_cache = {}
def _font(path):
    if path not in _cache:
        _cache[path] = TTFont(path)
    return _cache[path]

def glyphs(text, path, cap_mm, tracking=0.0):
    f = _font(path)
    upm = f["head"].unitsPerEm
    cap = getattr(f["OS/2"], "sCapHeight", 0) or int(0.72*upm)
    scale = cap_mm / cap
    cmap = f.getBestCmap(); gs = f.getGlyphSet(); hmtx = f["hmtx"]
    out, x = [], 0.0
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            x += 0.5*cap_mm + tracking; continue
        pen = SVGPathPen(gs); gs[gn].draw(pen)
        d = pen.getCommands(); adv = hmtx[gn][0]*scale
        if d: out.append((d, x, scale))
        x += adv + tracking
    return out, (x - tracking if text else 0.0)

def natural_w(text, path, cap_mm):
    return glyphs(text, path, cap_mm, 0.0)[1]

LIVE_TEXT = False          # True -> emit <text> instead of outlines


_FAMILY = {
    "fonts/Oswald-300.ttf": "Oswald Light",
    "fonts/Oswald-400.ttf": "Oswald",
    "fonts/Oswald-500.ttf": "Oswald Medium",
    "fonts/Oswald-600.ttf": "Oswald SemiBold",
    "fonts/Oswald-700.ttf": "Oswald",
    "fonts/cand-Anton.ttf": "Anton",
}


def _font_family(path):
    """Real family name from the font's own name table, so a design app
    resolves it after the user installs the two (free, SIL OFL) faces."""
    if path in _FAMILY:
        return _FAMILY[path]
    return _font(path)["name"].getDebugName(1)


def text_block(text, path, cap_mm, cx, baseline, fill, target_w=None, tracking=0.0):
    """Set text to target_w: track out if narrower, shrink if wider."""
    if target_w is not None:
        w0 = natural_w(text, path, cap_mm)
        if w0 > target_w:
            cap_mm = cap_mm * target_w / w0
            tracking = 0.0
        else:
            tracking = (target_w - w0) / max(1, len(text)-1)
    gl, wtot = glyphs(text, path, cap_mm, tracking)
    x0 = cx - wtot/2
    if LIVE_TEXT:
        f = _font(path)
        upm = f["head"].unitsPerEm
        cap = getattr(f["OS/2"], "sCapHeight", 0) or int(0.72*upm)
        size = cap_mm * upm / cap
        esc = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        return (f'<text x="{x0:.4f}" y="{baseline:.4f}" fill="{fill}" '
                f'font-family="{_font_family(path)}" font-size="{size:.4f}" '
                f'letter-spacing="{tracking:.4f}" '
                f'xml:space="preserve">{esc}</text>')
    parts = [f'<path d="{d}" transform="translate({x0+dx:.4f},{baseline:.4f}) '
             f'scale({sc:.6f},{-sc:.6f})"/>' for d, dx, sc in gl]
    return f'<g fill="{fill}">' + "".join(parts) + "</g>"

def img_tag(path, x, y, w, h, preserve="xMidYMid slice", opacity=1.0):
    ext = os.path.splitext(path)[1].lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return (f'<image x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'opacity="{opacity}" preserveAspectRatio="{preserve}" '
            f'xlink:href="data:{mime};base64,{b64}"/>')

def polyline(pts, stroke, w):
    w = max(w, FLOOR_W)
    d = "M " + " L ".join(f"{a:.3f},{b:.3f}" for a, b in pts)
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w:.3f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')

def leaf(cx, cy, h, colour):
    w = h*0.52
    d = (f"M {cx:.3f},{cy-h/2:.3f} C {cx+w/2:.3f},{cy-h*0.18:.3f} {cx+w/2:.3f},{cy+h*0.20:.3f} "
         f"{cx:.3f},{cy+h/2:.3f} C {cx-w/2:.3f},{cy+h*0.20:.3f} {cx-w/2:.3f},{cy-h*0.18:.3f} "
         f"{cx:.3f},{cy-h/2:.3f} Z")
    p = [f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{FLOOR_W*1.1:.3f}"/>',
         polyline([(cx, cy-h/2), (cx, cy+h/2)], colour, FLOOR_W)]
    for k in (-1, 0, 1):
        yy = cy + k*h*0.17
        for s in (-1, 1):
            p.append(polyline([(cx, yy-h*0.06), (cx+s*w*0.36, yy+h*0.10)], colour, FLOOR_W*0.9))
    return "".join(p)

def bio_hex(cx, cy, r, colour):
    pts = [(cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a)))
           for a in range(-90, 271, 60)]
    d = "M " + " L ".join(f"{a:.3f},{b:.3f}" for a, b in pts) + " Z"
    t = text_block("BIO", TEXT_FONTS[600], r*0.52, cx, cy + r*0.18, colour, target_w=r*1.05)
    return (f'<path d="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{max(FLOOR_W, 0.28):.3f}" stroke-linejoin="round"/>' + t)

# --------------------------------------------------------------- copy
# ONLY what the real bottle carries: BIO, e 330 ml, the xeistee mark,
# Kraeutersaftgetraenk, and the Kraeuterbergbauer logo. Nothing invented.
WORDMARK = "art/wordmark-hi.png"
KB_LOGO  = "assets/kb-logo-trans.png"

def build(display="Anton", title_mode="type", title_colour="ink",
          mountain=None, foreground=None, cream="cream", ink="ink",
          logo_pos=None, sach="KRÄUTERSAFTGETRÄNK", sach_y=0.430, sach_colour="ink",
          mtn_top=0.560, mtn_h=0.440, fg_top=0.740, fg_h=0.260):
    P = PALETTE
    CREAM, INK, TITLE = P[cream], P[ink], P[title_colour]
    Hh, cx = TRIM_H, OX + TRIM_W/2
    inner = PANEL_W - 2*3.5
    fy = lambda f: OY + f*Hh
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{CREAM}"/>']

    # ---- illustration: runs the full wrap and BLEEDS off the bottom edge
    if mountain:
        s.append(img_tag(mountain, -0.5, fy(mtn_top), W+1.0, (1.0-mtn_top)*Hh + BLEED + 1.0,
                         preserve="xMidYMax slice"))
    if foreground:
        s.append(img_tag(foreground, -0.5, fy(fg_top), W+1.0, (1.0-fg_top)*Hh + BLEED + 1.0,
                         preserve="xMidYMax slice"))

    # ---- top row: BIO left, estimated sign + volume right
    s.append(text_block("BIO", TEXT_FONTS[600], 0.020*Hh, cx-PANEL_W/2+8.5, fy(0.055), INK,
                        target_w=10.5))
    s.append(text_block("℮ 330 ml", TEXT_FONTS[400], 0.020*Hh, cx+PANEL_W/2-12.5,
                        fy(0.055), INK, target_w=19.0))

    # ---- product name
    if title_mode == "wordmark":
        wm_w = inner*0.98
        import PIL.Image as _I
        iw, ih = _I.open(WORDMARK).size
        wm_h = wm_w*ih/iw
        s.append(img_tag(WORDMARK, cx-wm_w/2, fy(0.360)-wm_h*0.72, wm_w, wm_h,
                         preserve="xMidYMid meet"))
    else:
        s.append(text_block("XEISTEE", DISPLAY_FONTS[display], 0.131*Hh, cx,
                            fy(0.360), TITLE, target_w=inner*1.0))

    # ---- Sachbezeichnung, under the illustration
    if sach:
        s.append(text_block(sach, TEXT_FONTS[500], 0.0215*Hh, cx, fy(sach_y),
                            PALETTE[sach_colour], target_w=inner*0.86))

    # ---- brand logo
    if logo_pos:
        import PIL.Image as _I
        lw = inner*(0.62 if logo_pos == "bottom" else 0.38)
        iw, ih = _I.open(KB_LOGO).size
        lh = lw*ih/iw
        ly = (fy(0.985) - lh) if logo_pos == "bottom" else fy(0.040)
        s.append(img_tag(KB_LOGO, cx-lw/2, ly, lw, lh, preserve="xMidYMid meet"))

    s.append("</svg>")
    return "".join(s)

def render(stem, **kw):
    import cairosvg
    svg = build(**kw)
    open(f"{stem}.svg", "w", encoding="utf-8").write(svg)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=f"{stem}.pdf")
    cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{stem}.png",
                     output_width=int(W/25.4*300))
    return stem
