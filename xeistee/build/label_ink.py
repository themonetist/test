#!/usr/bin/env python3
"""X'Eistee wrap label, v5 - zoned, with the wrapping silhouette band.

    |seam|      FRONT      | side A |       BACK        | side B |
    0    8               68.4     97.5                157.9    187

FRONT  : the Kalbling + XEISTEE, nothing else.
side A : Zutaten.
BACK   : Nährwertdeklaration + producer + QR.
side B : Bio marks, Gesäuse-Partner, EAN.

Type is outlined at build time; only the illustration is raster. What you see
is the file that goes to the printer.
"""
import math, random
import variants as V
EAN_SHIFT = 0.0
GES_SHIFT = 0.0
VAL_W_MM = 22.0
QR_HOOK = None
SIDE_HOOK = lambda: ''

TRIM_W, TRIM_H = 187.0, 100.0
BLEED = 3.0
W, H = TRIM_W + 2*BLEED, TRIM_H + 2*BLEED
OX, OY = BLEED, BLEED

# The FRONT sits in the middle of the flat artwork and the seam falls at the two
# ends, i.e. round the back of the bottle - which is where a seam belongs.
PANEL_W  = 60.4                        # = bottle diameter, the face seen head-on
SIDE_W   = (TRIM_W - PANEL_W) / 2      # 63.3 each

FRONT_X0 = OX + SIDE_W
FRONT_X1 = FRONT_X0 + PANEL_W
LEFT_X0  = OX
LEFT_X1  = FRONT_X0
RIGHT_X0 = FRONT_X1
RIGHT_X1 = OX + TRIM_W
CXF = (FRONT_X0 + FRONT_X1) / 2

P = dict(V.PALETTE)
P["cream"] = "#ECE0D0"
P["band"]  = "#3A4030"
P["ink"]   = "#2E3524"

# --- copy. Placeholders are marked; nothing here is invented as fact.
ZUTATEN = ("Wasser, Auszug aus Pfefferminze* und Bohnenkraut*. Holunderbeeren*, "
           "Apfelsaft*, Biozucker. Säuerungsmittel: Zitronensäure.")
BIO_NOTE = "* aus kontrolliert biologischer Landwirtschaft"
HINWEISE = [
    "Flasche vor Gebrauch schütteln.",
    "Kühl und dunkel lagern und nach dem Öffnen alsbald verbrauchen!",
    "Bis 1:1 verdünnbar",
]
ERZEUGER = [
    "Sandra Stangl · T: 0664/73839445",
    "Lainbach 25, 8921 Landl",
    "www.kraeuterbergbauer.at",
]
BIO_CODE = "AT-BIO-402"
BIO_ORIGIN = "Österreich-Landwirtschaft"
EAN = "9 120048 938668"

# (label, value, indented?)  Values are placeholders until the lab figures exist.
NAEHRWERT = [
    ("Brennwert",                   "–– kJ / –– kcal", False),
    ("Fett",                        "–– g",            False),
    ("davon gesättigte Fettsäuren", "–– g",            True),
    ("Kohlenhydrate",               "–– g",            False),
    ("davon Zucker",                "–– g",            True),
    ("Eiweiß",                      "–– g",            False),
    ("Salz",                        "–– g",            False),
]


def wrap_text(text, path, cap, max_w):
    """Greedy wrap using the real outline metrics, so it never overflows."""
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if V.natural_w(t, path, cap) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines


def left_text(txt, path, cap, x, baseline, fill, tracking=0.0):
    gl, wtot = V.glyphs(txt, path, cap, tracking)
    if V.LIVE_TEXT:
        f = V._font(path)
        upm = f["head"].unitsPerEm
        capH = getattr(f["OS/2"], "sCapHeight", 0) or int(0.72*upm)
        size = cap * upm / capH
        esc = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return ((f'<text x="{x:.4f}" y="{baseline:.4f}" fill="{fill}" '
                 f'font-family="{V._font_family(path)}" font-size="{size:.4f}" '
                 f'letter-spacing="{tracking:.4f}" '
                 f'xml:space="preserve">{esc}</text>'), wtot)
    parts = [f'<path d="{d}" transform="translate({x+dx:.4f},{baseline:.4f}) '
             f'scale({sc:.6f},{-sc:.6f})"/>' for d, dx, sc in gl]
    return f'<g fill="{fill}">' + "".join(parts) + "</g>", wtot


def eu_leaf(x, y, w, green="#4A7729", star="#ECE0D0"):
    """Stand-in for the EU organic leaf at its legal minimum, 13.5 x 9 mm.

    The real mark is prescribed artwork (Reg. (EU) 2018/848, Annex V) and must
    be dropped in as the official EPS before printing. This draws the correct
    footprint and the 12-star leaf so the layout can be judged.
    """
    h = w * 9.0 / 13.5
    out = [f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
           f'rx="{h*0.10:.2f}" fill="{green}"/>']
    # 12 stars: a leaf outline - stem running up-right, blade curving left
    pts = [(0.30,0.80),(0.38,0.72),(0.46,0.64),(0.54,0.56),(0.62,0.48),(0.70,0.40),
           (0.62,0.32),(0.52,0.30),(0.42,0.34),(0.34,0.42),(0.30,0.53),(0.30,0.66)]
    r = h*0.075
    for fx, fy2 in pts:
        cx, cy = x + fx*w, y + fy2*h
        d = []
        for i in range(10):
            ang = math.radians(-90 + i*36)
            rr = r if i % 2 == 0 else r*0.42
            d.append(f"{cx+rr*math.cos(ang):.3f},{cy+rr*math.sin(ang):.3f}")
        out.append(f'<path d="M {" L ".join(d)} Z" fill="{star}"/>')
    return "".join(out)


def qr_block(x, y, size, fill, seed=11, PAPER="#ECE0D0"):
    """A stand-in QR: real modules can only be generated once the URL exists."""
    rnd = random.Random(seed)
    n = 21
    m = size / n
    out = []
    def finder(fx, fy):
        s = 7*m
        out.append(f'<rect x="{fx:.2f}" y="{fy:.2f}" width="{s:.2f}" height="{s:.2f}" fill="{fill}"/>')
        out.append(f'<rect x="{fx+m:.2f}" y="{fy+m:.2f}" width="{5*m:.2f}" '
                   f'height="{5*m:.2f}" fill="{PAPER}"/>')
        out.append(f'<rect x="{fx+2*m:.2f}" y="{fy+2*m:.2f}" width="{3*m:.2f}" height="{3*m:.2f}" fill="{fill}"/>')
    for r in range(n):
        for c in range(n):
            if (r < 8 and c < 8) or (r < 8 and c > n-9) or (r > n-9 and c < 8):
                continue
            if rnd.random() < 0.45:
                out.append(f'<rect x="{x+c*m:.3f}" y="{y+r*m:.3f}" '
                           f'width="{m:.3f}" height="{m:.3f}" fill="{fill}"/>')
    finder(x, y); finder(x + (n-7)*m, y); finder(x, y + (n-7)*m)
    return "".join(out)


def build(display="Anton", band=None, mtn=None, mtn_summit=0.558,
          bio="line", title_scale=1.0, herbs=None, herb_base=0.985,
          eu=True, eu_y=0.505, side_herbs=None, side_caption=None,
          spiral=None, spiral_w=74.0, spiral_y=0.045,
          ground=None, title_col=None, desc_col=None, title_mode='type',
          desc_drop=0.0, title_y=0.250, bio_y=0.065, bio_cap=3.0,
          mtn_h=44.0, mtn_base=0.735, band_h=None, guides=False, trim_h=None, ground_defs=None):
    global TRIM_H, H
    if trim_h:
        TRIM_H = trim_h; H = TRIM_H + 2*BLEED
    Hh = TRIM_H
    fy = lambda f: OY + f*Hh
    CREAM, INK, BAND = P["cream"], P["ink"], P["band"]
    if ground: CREAM = ground
    if title_col: TITLE_C = title_col
    else: TITLE_C = INK
    T = V.TEXT_FONTS

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         (ground_defs or '') + f'<rect width="{W}" height="{H}" fill="{CREAM}"/>']

    s.append('<!--LAYER:Berg-->')
    # ---- mountain, behind everything, on the front panel only
    if mtn:
        import PIL.Image as _I
        mi = _I.open(mtn)
        mw = mtn_h * mi.width / mi.height
        s.append(V.img_tag(mtn, CXF - mw*mtn_summit, fy(mtn_base) - mtn_h,
                           mw, mtn_h, preserve="none"))

    s.append('<!--LAYER:Band-->')
    # ---- the band wraps the whole label and hides the mountain's foot
    if band:
        import PIL.Image as _I
        bi = _I.open(band)
        bh = band_h if band_h else (W + 1.0) * bi.height / bi.width
        s.append(V.img_tag(band, -0.5, H + 0.5 - bh, W + 1.0, bh, preserve="none"))

    # ---- the two ingredient herbs, flanking the mountain, in front of the band
    if herbs:
        import PIL.Image as _I
        for path, hx, hh in herbs:
            hi = _I.open(path)
            hw = hh * hi.width / hi.height
            s.append(V.img_tag(path, hx - hw/2, fy(herb_base) - hh, hw, hh,
                               preserve="none"))

    # ---- small captioned herb vignettes in the clear cream beside the peak
    if side_herbs:
        import PIL.Image as _I
        for path, hx, hy, hh, name in side_herbs:
            hi = _I.open(path)
            hw = hh * hi.width / hi.height
            s.append(V.img_tag(path, hx - hw/2, hy - hh, hw, hh, preserve="none"))
            if name:
                s.append(V.text_block(name, T[400], 1.45, hx, hy + 2.9, INK,
                                      target_w=min(19.0, max(hw, 13.0))))
    if side_caption:
        cx0, cy0, txt, cw = side_caption
        s.append(V.text_block(txt, T[400], 1.5, cx0, cy0, INK, target_w=cw))

    # ---- the Kräuterbergbauer fiddlehead spiral, wrapped round the wordmark.
    #      Lifted from the parent-brand logo, so it is the real curve.
    if spiral:
        import PIL.Image as _I
        si = _I.open(spiral)
        sw = spiral_w
        shh = sw * si.height / si.width
        s.append(V.img_tag(spiral, CXF - sw*0.52, fy(spiral_y), sw, shh,
                           preserve="none"))

    s.append('<!--LAYER:Front-->')
    # ================= FRONT =================
    if title_mode == "wordmark":
        import PIL.Image as _I
        wm_w = (PANEL_W - 8.0)*title_scale*1.06
        iw, ih = _I.open(V.WORDMARK).size
        wm_h = wm_w*ih/iw
        s.append(V.img_tag(V.WORDMARK, CXF - wm_w/2, fy(title_y) - wm_h*0.78,
                           wm_w, wm_h, preserve="xMidYMid meet"))
    else:
        s.append(V.text_block("XEISTEE", V.DISPLAY_FONTS[display], 0.150*Hh*title_scale,
                              CXF, fy(title_y), TITLE_C,
                              target_w=(PANEL_W - 8.0)*title_scale))
    if bio == "line":
        l1 = "BIO KRÄUTERSAFTGETRÄNK"
        w1 = 0.97
    else:
        l1 = "KRÄUTERSAFTGETRÄNK"
        w1 = 0.93
    s.append(V.text_block(l1, T[500], 0.021*Hh, CXF, fy(0.310+desc_drop), desc_col or INK,
                          target_w=(PANEL_W - 8.0)*w1))
    s.append(V.text_block("AUS DEM GESÄUSE", T[500], 0.021*Hh, CXF,
                          fy(0.350+desc_drop), desc_col or INK, target_w=(PANEL_W - 8.0)*0.74))

    # EU organic leaf + control code, front of pack, in the clear cream left of
    # the mountain. Legal minimum 13.5 x 9 mm; the code and the origin have to
    # sit in the same visual field as the mark.
    if eu:
        lw = 13.5
        lh = lw * 9.0 / 13.5
        lx = FRONT_X0 + 3.5
        ly = fy(eu_y)
        s.append(eu_leaf(lx, ly, lw, green=INK, star=CREAM))
        t, _ = left_text(BIO_CODE, T[500], 1.7, lx, ly + lh + 2.6, INK)
        s.append(t)
        t, _ = left_text(BIO_ORIGIN, T[300], 1.45, lx, ly + lh + 5.0, INK)
        s.append(t)
    if bio in ("toprow", "toprow_red"):
        col = P["red"] if bio == "toprow_red" else INK
        # natural letterfit, only a hair of tracking - target_w was forcing
        # these apart into a gappy line
        s.append(V.text_block("BIO", T[600], bio_cap, FRONT_X0 + 9.0, fy(bio_y), col,
                              tracking=bio_cap*0.05))
        s.append(V.text_block("℮ 330 ml", T[400], bio_cap, FRONT_X1 - 12.5, fy(bio_y),
                              INK, tracking=bio_cap*0.05))
    if bio == "octagon":
        cx0, cy0, r = FRONT_X0 + 11.5, fy(0.735), 8.2
        pts = [(cx0 + r*math.cos(math.radians(a + 22.5)),
                cy0 + r*math.sin(math.radians(a + 22.5))) for a in range(0, 360, 45)]
        d = "M " + " L ".join(f"{a:.2f},{b:.2f}" for a, b in pts) + " Z"
        s.append(f'<path d="{d}" fill="{P["red"]}"/>')
        s.append(V.text_block("BIO", T[600], 3.6, cx0, cy0 + 1.3, CREAM, target_w=10.4))
    if bio == "roundel":
        cx0 = FRONT_X1 - 9.5
        cy0 = fy(eu_y) + 4.5
        s.append(f'<circle cx="{cx0:.2f}" cy="{cy0:.2f}" r="7.2" fill="{INK}"/>')
        s.append(V.text_block("BIO", T[600], 3.4, cx0, cy0 + 1.2, CREAM,
                              target_w=9.4))
    if bio == "mark":
        s.append(V.bio_hex(CXF, fy(0.095), 4.4, INK))

    s.append('<!--LAYER:Zutaten-->')
    # ================= LEFT : Zutaten, Hinweise, Bio =================
    x = LEFT_X0 + 5.0 + EAN_SHIFT
    maxw = SIDE_W - 11.0 - EAN_SHIFT
    y = fy(0.095)
    t, _ = left_text("ZUTATEN", T[600], 2.2, x, y, INK, tracking=0.30)
    s.append(t); y += 3.4
    for ln in wrap_text(ZUTATEN, T[300], 1.85, maxw):
        t, _ = left_text(ln, T[300], 1.65, x, y, INK); s.append(t); y += 2.4
    y += 0.6
    t, _ = left_text(BIO_NOTE, T[300], 1.6, x, y, INK); s.append(t); y += 4.2
    for h in HINWEISE:
        for ln in wrap_text(h, T[300], 1.75, maxw):
            t, _ = left_text(ln, T[300], 1.55, x, y, INK); s.append(t); y += 2.3
        y += 0.5

    # EU organic leaf + control code, on the same face as the BIO claim
    y += 0.6
    s.append(V.bio_hex(x + 4.6, y + 3.4, 4.0, INK))
    t, _ = left_text(BIO_CODE, T[400], 1.75, x + 11.0, y + 2.6, INK)
    s.append(t)
    t, _ = left_text(BIO_ORIGIN, T[300], 1.5, x + 11.0, y + 5.4, INK)
    s.append(t)
    s.append(f'<ellipse cx="{x + 38.0:.2f}" cy="{y + 3.4:.2f}" rx="6.4" ry="4.6" '
             f'fill="none" stroke="{INK}" stroke-width="0.28"/>')
    t, _ = left_text("lacon", T[400], 1.7, x + 34.0, y + 4.0, INK)
    s.append(t)
    y += 9.5
    t, _ = left_text("Mindestens haltbar bis Ende:", T[300], 1.4, x, y + 1.6, INK)
    s.append(t)
    t, _ = left_text("siehe Aufdruck · Los: siehe Aufdruck", T[300], 1.4, x, y + 4.0, INK)
    s.append(t)
    t, _ = left_text("Pfandflasche · ℮ 330 ml", T[400], 1.6, x, y + 7.0, INK)
    s.append(t)

    s.append('<!--LAYER:Naehrwerte-->')
    # ================= RIGHT : Nährwerte + Erzeuger + QR =================
    x = RIGHT_X0 + 6.0
    maxw = SIDE_W - 14.0 - GES_SHIFT
    y = fy(0.090)
    t, _ = left_text("NÄHRWERTDEKLARATION", T[600], 2.2, x, y, INK, tracking=0.30)
    s.append(t); y += 3.3
    t, _ = left_text("pro 100 ml Fertiggetränk", T[300], 1.75, x, y, INK)
    s.append(t); y += 2.2

    # One hairline over the table and one under it. Nothing between the rows -
    # alignment does that job, rules just add noise at this size.
    VAL_W  = VAL_W_MM                       # fixed right-hand column
    LEAD   = 2.45                       # single leading for every row
    rule = lambda yy: (f'<line x1="{x:.2f}" y1="{yy:.2f}" x2="{x+maxw:.2f}" '
                       f'y2="{yy:.2f}" stroke="{INK}" stroke-width="0.28"/>')
    s.append(rule(y))
    y += 3.0
    for name, val, indent in NAEHRWERT:
        nf  = T[300] if indent else T[400]
        cap = 1.55
        nx  = x + (2.2 if indent else 0.0)
        # never let the label run into the value column
        avail = maxw - VAL_W - (nx - x)
        nw = V.natural_w(name, nf, cap)
        t, _ = left_text(name, nf, cap * min(1.0, avail / nw), nx, y, INK)
        s.append(t)
        vw = V.natural_w(val, T[400], cap)
        t2, _ = left_text(val, T[400], cap, x + maxw - vw, y, INK)
        s.append(t2)
        y += LEAD
    y -= LEAD - 1.5
    s.append(rule(y))
    y += 3.0
    for ln in ERZEUGER:
        t, _ = left_text(ln, T[300], 1.55, x, y, INK); s.append(t); y += 2.25

    # QR and the Gesäuse-Partner mark, in the clear cream above the band
    qs = 8.5
    qy = y + 1.2
    s.append('<!--LAYER:Codes-->')
    s.append(QR_HOOK(x, qy, qs))
    gx = x + qs + 3.0
    t, _ = left_text("mehr erfahren · kraeuterbergbauer.at", T[300], 1.45, gx, qy + 2.6, INK)
    s.append(t)
    s.append(SIDE_HOOK())

    if guides:
        for gx, lbl, col in ((OX, "ZUTATEN  (halbe Rückseite)", "#9AA089"),
                             (FRONT_X0, "FRONT", "#3E7CA8"),
                             (FRONT_X1, "NÄHRWERTE  (halbe Rückseite)", "#9AA089"),
                             (OX+TRIM_W, "", "#C0563C")):
            s.append(f'<line x1="{gx:.2f}" y1="{OY:.2f}" x2="{gx:.2f}" y2="{OY+TRIM_H:.2f}" '
                     f'stroke="{col}" stroke-width="0.3" stroke-dasharray="2,1.5"/>')
            if lbl:
                t, _ = left_text(lbl, T[500], 2.2, gx + 2.0, OY + 3.4, col)
                s.append(t)
        s.append(f'<rect x="{OX}" y="{OY}" width="{TRIM_W}" height="{TRIM_H}" fill="none" '
                 f'stroke="#C0563C" stroke-width="0.3"/>')
    s.append("</svg>")
    return "".join(s)


def render(stem, **kw):
    import cairosvg
    svg = build(**kw)
    open(stem + ".svg", "w", encoding="utf-8").write(svg)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=stem + ".pdf")
    cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + ".png",
                     output_width=int(W/25.4*300))
    return stem
