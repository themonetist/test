"""X'Eistee 80 mm label, v2 layout: one baseline grid, one margin system, real marks.

Grid: 2.4 mm baseline grid, 5 mm side margins, shared top baseline y=9.6 mm across
all three panels, shared bottom edge y=44.0 mm for every panel's last element.
"""
import re, base64, math
import PIL.Image as I
import variants as V
import label_ink as L          # copy + helpers (left_text, wrap_text, palette)
import qr_brand, ean_brand
import marks
MARK_STYLE = 'brushfill'
# --- per-format knobs, set by configure() ---
EAN_BAR, MARK_D, QR_S = 11.0, 9.4, 9.0
CAP_V = 1.45     # freiwilliger Text (Hinweise, Story, URL)
EAN_GAP = 3.0
BG_TONE = 'gelb'                 # 'gelb' | 'gold'
GS_MODE = 'mhd'                  # Gesaeuse-Siegel: 'mhd' | 'qr' | 'qr-unter' | 'qr-breit' | 'qr-rechts' | 'qr-text' | 'siegel' | 'ean-unten' | 'ean-oben'
GLOW = {'gelb': ("#EFCF70", "#EED490", "#EDDCB8", "#ECDFC9"),
        'gold': ("#D6B37D", "#DDC299", "#E6D5BB", "#EADDCA")}

def configure(trim_w=177.0, trim_h=80.0, bleed=3.0, *, ean_bar=11.0, mark_d=9.4,
              qr_s=9.0, cap_b=1.70, cap_s=1.70, cap_h=2.3, base=2.4,
              top=6.6, bottom=47.0, band_png=None, bg_tone='gelb', margin=5.0,
              cap_v=1.45, ean_gap=3.0, gs_mode='mhd'):
    """Set the label format. Everything derived is recomputed here."""
    global TRIM_W, TRIM_H, BLEED, W, H, OX, OY, SIDE_W
    global FRONT_X0, FRONT_X1, CXF, LEFT_X0, RIGHT_X1
    global EAN_BAR, MARK_D, QR_S, CAP_B, CAP_S, CAP_H, BASE, TOP, BOTTOM
    global BAND_PNG, BG_TONE, M, CAP_V, EAN_GAP, GS_MODE
    TRIM_W, TRIM_H, BLEED = trim_w, trim_h, bleed
    W, H = TRIM_W + 2*BLEED, TRIM_H + 2*BLEED
    OX = OY = BLEED
    SIDE_W = (TRIM_W - PANEL_W)/2
    FRONT_X0 = OX + SIDE_W; FRONT_X1 = FRONT_X0 + PANEL_W
    CXF = (FRONT_X0 + FRONT_X1)/2
    LEFT_X0, RIGHT_X1 = OX, OX + TRIM_W
    EAN_BAR, MARK_D, QR_S = ean_bar, mark_d, qr_s
    CAP_B, CAP_S, CAP_H, BASE, M = cap_b, cap_s, cap_h, base, margin
    CAP_V = cap_v
    EAN_GAP = ean_gap
    TOP, BOTTOM = OY + top, OY + bottom
    BG_TONE = bg_tone
    GS_MODE = gs_mode
    if band_png: BAND_PNG = band_png
# PLACEHOLDER values - typical for a herbal drink with apple juice + sugar. Replace with the
# LK Steiermark calculation before print. Rounding per LMIV Annex-XV guidance.
NAEHRWERT = [   # final figures from the calculation, Sep 14 2026
    ("Brennwert",                   "103 kJ / 24 kcal", False),
    ("Fett",                        "0 g",              False),
    ("davon gesättigte Fettsäuren", "0 g",              True),
    ("Kohlenhydrate",               "6,0 g",            False),
    ("davon Zucker",                "5,9 g",            True),
    ("Eiweiß",                      "0,1 g",            False),
    ("Salz",                        "0 g",              False),
]
HINWEISE = ["Flasche vor Gebrauch schütteln.",
            "Kühl und dunkel lagern und nach dem Öffnen alsbald verbrauchen!",
            "Pfandflasche."]
STORY = ["Bergkräuter aus dem Gesäuse.",
         "Vom Bio-Bergbauernhof in Landl."]

def roundel(x, y, d, top, bottom, fill, paper):
    """Own small claim mark: ink disc, two lines of paper-coloured caps."""
    r = d/2; cx, cy = x + r, y + r
    out = [f'<g inkscape:label="Marke {top} {bottom or ""}"><circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{fill}"/>']
    if bottom:
        cap, inner = d*0.17, d*0.80
        for t2 in (top, bottom):
            w2 = _VM.natural_w(t2, _VM.TEXT_FONTS[600], cap) + 0.12*(len(t2)-1)
            if w2 > inner: cap *= inner/w2
        out.append(V.text_block(top,    V.TEXT_FONTS[600], cap, cx, cy - d*0.04, paper, tracking=0.12))
        out.append(V.text_block(bottom, V.TEXT_FONTS[600], cap, cx, cy + d*0.19, paper, tracking=0.12))
    else:
        out.append(V.text_block(top, V.TEXT_FONTS[600], d*0.2, cx, cy + d*0.08, paper, tracking=0.15))
    return "".join(out) + "</g>"

wrap_text = L.wrap_text
def _lab(name):
    return (name[:60].replace('&','&amp;').replace('"','&quot;')
            .replace('<','&lt;').replace('>','&gt;'))
def left_text(txt, path, cap, x, baseline, fill, tracking=0.0):
    t, w = L.left_text(txt, path, cap, x, baseline, fill, tracking)
    return f'<g inkscape:label="{_lab(txt)}">{t}</g>', w
import variants as _VM
class _V:
    def __getattr__(self, k): return getattr(_VM, k)
    def text_block(self, text, *a, **kw):
        return f'<g inkscape:label="{_lab(text)}">{_VM.text_block(text, *a, **kw)}</g>'
V = _V()
P, T = L.P, V.TEXT_FONTS
INK, CREAM, RED = P["ink"], P["cream"], "#C00015"
EU = "eu/euzip/logo_eps/EU_Organic_Logo_Colour_54x36mm.svg"
GS = "eu/gs_partner.svg"
LACON = "eu/lacon.png"

TRIM_W, TRIM_H, BLEED = 177.0, 80.0, 3.0
W, H = TRIM_W + 2*BLEED, TRIM_H + 2*BLEED
OX, OY = BLEED, BLEED
PANEL_W = 60.4
SIDE_W = (TRIM_W - PANEL_W)/2
FRONT_X0 = OX + SIDE_W; FRONT_X1 = FRONT_X0 + PANEL_W; CXF = (FRONT_X0+FRONT_X1)/2
LEFT_X0, RIGHT_X1 = OX, OX + TRIM_W

# ---- the system
M      = 5.0        # side margin inside the trim
BASE   = 2.4        # baseline grid
TOP    = OY + 6.6   # first baseline (9.6 mm from the bleed edge)
BOTTOM = OY + 47.0  # bottom edge of the side panels' content (50.0); band starts at 56
CAP_H  = 2.3        # headings
CAP_B  = 1.6        # body
CAP_S  = 1.45       # small print
BAND_H = 30.0
BAND_PNG = 'art/bandF-wide.png'   # 1.5x wide (mirrored ends), natural height 37.6 mm at label width
BAND_OVER = 4.6    # band 3 mm hoeher: unterste Beere bekommt 3 mm Luft zur Schnittkante
MTN_H  = 36.0

def _inner(svg_text):
    return svg_text[svg_text.index(">", svg_text.index("<svg"))+1:svg_text.rindex("</svg>")]

def svg_place(path, x, y, w, h=None, lid=None):
    """Place an SVG file's content scaled into a w x h box (uniform scale)."""
    s = open(path, encoding="utf-8").read()
    m = re.search(r'viewBox="([\d.\-eE ]+)"', s)
    vx, vy, vw, vh = map(float, m.group(1).split())
    sc = w / vw
    if h is None: h = vh*sc
    else: sc = min(sc, h/vh)
    ox = x + (w - vw*sc)/2; oy = y + (h - vh*sc)/2
    body = _inner(s)
    # potrace / pdftocairo wrap their content in their own transforms - keep as is
    return (f'<g id="{lid or "placed"}" inkscape:label="{lid or "placed"}" transform="translate({ox:.4f},{oy:.4f}) scale({sc:.6f})">'
            f'<g transform="translate({-vx},{-vy})">{body}</g></g>'), vh*sc

GS_BOX = (168, 104, 3068, 1928)    # sichtbare Kontur von gs_partner.svg in viewBox-Einheiten
GS_ASPECT = (GS_BOX[3] - GS_BOX[1]) / (GS_BOX[2] - GS_BOX[0])

def svg_place_visual(path, vx, vy, vw, lid, fill=None):
    """Place an SVG so its VISIBLE outline (GS_BOX) starts at vx, vy and is vw wide."""
    s = open(path, encoding="utf-8").read()
    if fill: s = s.replace('fill="#000000"', f'fill="{fill}"')
    sc = vw / (GS_BOX[2] - GS_BOX[0])
    return (f'<g id="{lid}" inkscape:label="{lid}" transform="translate({vx - GS_BOX[0]*sc:.4f},'
            f'{vy - GS_BOX[1]*sc:.4f}) scale({sc:.6f})">{_inner(s)}</g>')

def img(path, x, y, w, h, lid=None):
    tag = f'<image id="{lid}" inkscape:label="{lid}" ' if lid else "<image "
    return V.img_tag(path, x, y, w, h, preserve="none").replace("<image ", tag, 1)

def wm_bbox():
    im = I.open(V.WORDMARK); a = im.split()[-1].point(lambda v: 255 if v > 60 else 0)
    return a.getbbox(), im.size

def build(bg_png=None):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
         f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">']
    s.append('<!--LAYER:Hintergrund-->')
    if bg_png:
        s.append(img(bg_png, 0, 0, W, H, "bg"))
    else:
        c0, c1, c2, c3 = GLOW[BG_TONE]
        s.append(f'<defs><radialGradient id="sky" gradientUnits="userSpaceOnUse" '
                 f'cx="{0.725*W:.2f}" cy="{0.860*H:.2f}" r="{0.959*W:.2f}">'
                 f'<stop offset="0" stop-color="{c0}"/><stop offset="0.28" stop-color="{c1}"/>'
                 f'<stop offset="0.62" stop-color="{c2}"/><stop offset="1" stop-color="{c3}"/>'
                 f'</radialGradient></defs>'
                 f'<rect inkscape:label="Hintergrund Verlauf" width="{W}" height="{H}" fill="url(#sky)"/>')

    # ---- mountain + band (unchanged art)
    s.append('<!--LAYER:Berg-->')
    mi = I.open("art/mtn-flat-k.png"); mw = MTN_H*mi.width/mi.height
    base_y = OY + 0.985*TRIM_H - 3.0   # Berg mit dem Band mit nach oben, Gipfel bleibt gleich sichtbar
    s.append(img("art/mtn-flat-k.png", CXF - mw*0.5586, base_y - MTN_H, mw, MTN_H, "berg"))
    s.append('<!--LAYER:Band-->')
    # band at its NATURAL aspect (never squashed); it overlaps the bottom bleed and is cut off there
    bi = I.open(BAND_PNG); bh = (W + 1.0) * bi.height / bi.width
    s.append(img(BAND_PNG, -0.5, H + BAND_OVER - bh, W + 1.0, bh, "band"))

    # ================= FRONT =================
    s.append('<!--LAYER:Front-->')
    (bx0, by0, bx1, by1), (iw, ih) = wm_bbox()
    vis_w = 48.0                                   # visual width of the wordmark
    sc = vis_w / (bx1 - bx0)
    wm_w, wm_h = iw*sc, ih*sc
    wm_x = CXF - (bx0 + (bx1-bx0)/2)*sc
    wm_top = TOP + 3.0                             # 2.6 mm below the BIO baseline
    wm_y = wm_top - by0*sc
    s.append(img(V.WORDMARK, wm_x, wm_y, wm_w, wm_h, "wordmark"))
    wm_bottom = wm_y + by1*sc
    # BIO left, ℮ 330 ml right - same cap as the subtitle, on the shared top baseline,
    # flush with the wordmark's visual edges
    lx, rx = CXF - vis_w/2, CXF + vis_w/2
    FC = 2.8   # front caps: BIO and 330 ml; the ℮ is 3.0 mm (legal minimum), so it sits in line
    t, _ = left_text("BIO", T[600], FC, lx, TOP, INK, tracking=0.3); s.append(t)
    # ℮ must be >= 3 mm tall (Dir. 76/211/EEC): Oswald's glyph is 584/810 of cap height
    e_cap = 3.0 * 810/584
    wv = V.natural_w("330 ml", T[600], FC) + 0.3*5
    t, _ = left_text("330 ml", T[600], FC, rx - wv, TOP, INK, tracking=0.3); s.append(t)
    ew = V.natural_w("℮", T[600], e_cap)
    t, _ = left_text("℮", T[600], e_cap, rx - wv - 1.0 - ew, TOP, INK); s.append(t)
    # subtitle: fixed tracking, centred, two lines
    y1 = wm_bottom + 4.2
    s.append(V.text_block("KRÄUTERSAFTGETRÄNK", T[500], 1.85, CXF, y1, INK, tracking=0.5))
    s.append(V.text_block("AUS DEM GESÄUSE",     T[500], 1.85, CXF, y1 + 3.2, INK, tracking=0.5))

    # ================= LEFT : EAN | Zutaten =================
    s.append('<!--LAYER:Zutaten-->')
    # EAN, ladder orientation, outer edge, top on the grid
    ean_brand.X = 0.264; ean_brand.BAR_H = EAN_BAR; ean_brand.GUARD_EXT = 1.32
    ean_brand.TXT_H = 2.2; ean_brand.QL = 11*0.264; ean_brand.QR = 7*0.264
    full, var, (EW, EH) = ean_brand.build("912004893866")
    ev = var["ean-%s-vertical" % full]
    ex, ey = LEFT_X0 + M - 1.5, TOP - CAP_H
    s.append(f'<g id="ean" inkscape:label="EAN 9120048938668" transform="translate({ex:.3f},{ey:.3f})">{_inner(ev)}</g>')
    x = ex + EH + EAN_GAP
    maxw = FRONT_X0 - M - x
    y = TOP
    t, _ = left_text("ZUTATEN", T[600], CAP_H, x, y, INK, tracking=0.30); s.append(t)
    y += BASE*1.5
    for ln in wrap_text(L.ZUTATEN, T[300], CAP_B*1.1, maxw):
        t, _ = left_text(ln, T[300], CAP_B, x, y, INK); s.append(t); y += BASE
    t, _ = left_text(L.BIO_NOTE, T[300], CAP_S, x, y, INK); s.append(t); y += BASE*1.5
    # Hinweise sind freiwillig -> sie duerfen schrumpfen, damit der Pflichtteil
    # (Zutaten, MHD, Bio-Code) in jedem Format seine Groesse behaelt
    _cc0 = min(1.9, 1.8*13.5/V.natural_w(L.BIO_CODE, T[500], 1.8))
    _co0 = min(CAP_S, CAP_S*13.5/V.natural_w(L.BIO_ORIGIN, T[300], CAP_S))
    _mhdw = maxw - 13.5 - 2.2
    # feste Zeilen: "Los:" entfaellt, die Losnummer beginnt selbst mit "L" (RL 2011/91/EU)
    # 'siegel': MHD/Los volle Breite ueber einer Siegelreihe EU-Blatt + Gesaeuse
    if GS_MODE == 'siegel':
        _mhd, _mhdw = ['Mindestens haltbar bis Ende: 10/2028', 'L-202765071'], maxw
    else:
        _mhd = ['Mindestens', 'haltbar bis Ende:', '10/2028', 'L-202765071']
    for l in _mhd:
        assert V.natural_w(l, T[300], CAP_B) <= _mhdw, f"MHD-Zeile zu breit: {l}"
    _leaf_h = 9.0 + 1.0 + _cc0 + 0.7 + _co0
    _mhd_h = CAP_B + (len(_mhd) - 1)*BASE + 1.6 if GS_MODE == 'siegel' else 0.0
    # Platz fuer das Gesaeuse-Siegel reservieren - im engsten Format darf es
    # schrumpfen, bevor der freiwillige Text unleserlich klein wird.
    # Steht es in der Barcode-Spalte, braucht die MHD-Spalte keinen Platz dafuer.
    for _ges in ((0.0,) if GS_MODE in ('ean-unten', 'ean-oben', 'siegel') or GS_MODE.startswith('qr') else (6.2, 5.6, 5.0, 4.5)):
        blk_h = _mhd_h + _leaf_h if GS_MODE == 'siegel' else max(_leaf_h, len(_mhd)*BASE + 1.0 + _ges)
        avail = (BOTTOM - blk_h) - 1.3 - y
        cv, lead = CAP_V, 0.86*BASE
        for _ in range(14):
            lns = [l for h in HINWEISE for l in wrap_text(h, T[300], cv*1.1, maxw)]
            if len(lns)*lead <= avail or cv <= 1.18: break
            cv *= 0.96; lead = 0.86*BASE*(cv/CAP_V)
        if len(lns)*lead <= avail: break
    for ln in lns:
        t, _ = left_text(ln, T[300], cv, x, y, INK); s.append(t); y += lead
    # unterer Block, zweispaltig: links EU-Blatt + Code, rechts MHD/Los + Gesäuse
    lw, lh = 13.5, 9.0
    cc, co = _cc0, _co0
    by = BOTTOM - blk_h
    ty = by                                   # Oberkante des Textblocks
    by = by + _mhd_h                          # Oberkante EU-Blatt
    g, _ = svg_place(EU, x, by, lw, lh, "eu-leaf"); s.append(g)
    s.append(left_text(L.BIO_CODE,   T[500], cc, x, by + lh + 1.0 + cc, INK)[0])
    s.append(left_text(L.BIO_ORIGIN, T[300], co, x, by + lh + 1.0 + cc + 0.7 + co, INK)[0])

    rx = x + lw + 2.2
    rw = maxw - lw - 2.2
    mhd = _mhd
    mx, ry = (x, ty + CAP_B) if GS_MODE == 'siegel' else (rx, by + CAP_B)
    for ln in mhd:
        t, _ = left_text(ln, T[300], CAP_B, mx, ry, INK); s.append(t); ry += BASE
    # Gesaeuse-Siegel: ausgerichtet wird an der sichtbaren Kontur (GS_BOX), nicht am viewBox
    base_o = by + lh + 1.0 + cc + 0.7 + co            # Grundlinie "Österreich-Landwirtschaft"
    if GS_MODE.startswith('ean'):
        # Barcode-Spalte unter dem EAN: buendig mit den Balken links und den Ziffern rechts
        # (EH hat unter den Ziffern 0,5 mm Luft, gemessen am Render)
        vx0 = ex; vw = EH - 0.5
        vh = vw * GS_ASPECT
        vy0 = by if GS_MODE == 'ean-oben' else base_o - vh
    elif GS_MODE == 'siegel':
        # Siegelreihe: rechts neben dem EU-Blatt, Spaltenbreite, Oberkante = Oberkante Blatt
        vx0, vw = rx, rw
        vh = vw * GS_ASPECT
        vy0 = by
    else:
        # rechte Spalte: links buendig mit MHD, Unterkante auf der gemeinsamen Grundlinie
        vx0 = rx
        vh = min(BOTTOM - (ry - BASE + 1.4), rw * GS_ASPECT, 8.0)
        vw = vh / GS_ASPECT
        vy0 = BOTTOM - vh
    if not GS_MODE.startswith('qr'):
        s.append(svg_place_visual(GS, vx0, vy0, vw, "gesaeuse-partner", fill=INK))
    if y > ty - 1.0:
        print(f"  ! Zutatenspalte zu lang: {y:.1f} > {ty-1.0:.1f}")
    print(f"  Hinweise cap {cv:.2f} mm, {len(lns)} Zeilen")

    # ================= RIGHT : Nährwerte | Erzeuger | QR + Gesäuse =================
    s.append('<!--LAYER:Naehrwerte-->')
    x = FRONT_X1 + M
    maxw = RIGHT_X1 - M - x
    y = TOP
    wv = V.natural_w("pro 100 ml", T[300], CAP_B)
    _hc, _tr = CAP_H, 0.30
    _hw = lambda c, tr: V.natural_w("NÄHRWERTDEKLARATION", T[600], c) + tr*c/CAP_H*18
    while _hw(_hc, _tr) > maxw - wv - 2.0 and _hc > 1.7:
        _hc *= 0.97; _tr *= 0.97
    t, _ = left_text("NÄHRWERTDEKLARATION", T[600], _hc, x, y, INK, tracking=_tr); s.append(t)
    t, _ = left_text("pro 100 ml", T[300], CAP_B, x + maxw - wv, y, INK); s.append(t)
    y += BASE*0.6
    rule = lambda yy: (f'<line inkscape:label="Linie Nährwerttabelle" x1="{x:.2f}" y1="{yy:.2f}" x2="{x+maxw:.2f}" y2="{yy:.2f}" '
                       f'stroke="{INK}" stroke-width="0.25"/>')
    s.append(rule(y)); y += BASE*1.1
    for name, val, indent in NAEHRWERT:
        nf = T[300] if indent else T[400]
        t, _ = left_text(name, nf, CAP_B, x + (2.4 if indent else 0), y, INK); s.append(t)
        vw = V.natural_w(val, T[400], CAP_B)
        t, _ = left_text(val, T[400], CAP_B, x + maxw - vw, y, INK); s.append(t)
        y += BASE
    y -= BASE*0.4
    s.append(rule(y)); y += BASE*1.4
    addr = ["Sandra Stangl", "T: 0664/73839445", "Lainbach 25, 8921 Landl"]
    aw = max(V.natural_w(a, T[300], CAP_B) for a in addr)
    d = MARK_D; mgap = 1.0
    # passen Adresse und Markenreihe nebeneinander? sonst Adresse umbrechen,
    # und wenn es dann immer noch klemmt, die Marken verkleinern
    if aw + 2.5 + 3*d + 2*mgap > maxw:
        addr = ["Sandra Stangl", "T: 0664/73839445", "Lainbach 25", "8921 Landl"]
        aw = max(V.natural_w(a, T[300], CAP_B) for a in addr)
    while aw + 2.5 + 3*d + 2*mgap > maxw and d > 6.5:
        d *= 0.97
    y0 = y
    for ln in addr:
        t, _ = left_text(ln, T[300], CAP_B, x, y, INK); s.append(t); y += BASE
    cy_m = y0 - CAP_B/2 + BASE*(len(addr)-1)/2
    mx0 = x + maxw - 3*d - 2*mgap
    for i, nm in enumerate(("vegan", "ohne-koffein", "hofproduktion")):
        s.append(img(f"art/marks/mark-{nm}.png", mx0 + i*(d+mgap), cy_m - d/2, d, d, f"marke-{nm}"))

    # unterste Reihe: QR + Story + URL
    s.append('<!--LAYER:Codes-->')
    qs = QR_S
    q = qr_brand.svg(qr_brand.matrix(qr_brand.URL), style="rounded", centre=True, quiet=0)
    n = int(re.search(r'viewBox="0 0 (\d+)', q).group(1))
    tx = x + qs + 2.2
    tw = maxw - qs - 2.2
    URL = "kraeuterbergbauer.at"
    def gesaeuse(vw, cy):
        vh = vw * GS_ASPECT
        s.append(svg_place_visual(GS, x + maxw - vw, cy - vh/2, vw, "gesaeuse-partner", fill=INK))
        return vh
    def arrow(ay):
        s.append(f'<path inkscape:label="Pfeil zum QR" d="M{tx+2.2:.2f},{ay:.2f} H{tx+0.3:.2f} '
                 f'M{tx+0.9:.2f},{ay-0.6:.2f} L{tx+0.25:.2f},{ay:.2f} L{tx+0.9:.2f},{ay+0.6:.2f}" '
                 f'fill="none" stroke="{INK}" stroke-width="0.25" stroke-linecap="round" stroke-linejoin="round"/>')
    qy = BOTTOM - qs                          # Oberkante QR
    if GS_MODE == 'qr-unter':
        # URL unter dem QR (Grundlinie = gemeinsame Unterkante), Siegel rechts buendig,
        # mittig zum Block QR + URL - wie Adresse | Marken in der Reihe darueber
        uc = CAP_B
        qy = BOTTOM - uc - 1.2 - qs
        s.append(left_text(URL, T[600], uc, x, BOTTOM, INK)[0])
        gesaeuse(min(8.0 / GS_ASPECT, maxw - V.natural_w(URL, T[600], uc) - 3.0), (qy + BOTTOM)/2)
    elif GS_MODE == 'qr-breit':
        # QR so gross wie die Hoehe hergibt (1,5 mm Luft zu Adresse/Marken),
        # URL darunter exakt QR-breit
        k = V.natural_w(URL, T[600], 1.0)              # Breite pro mm Versalhoehe
        room = BOTTOM - (max(y - BASE, cy_m + d/2) + 1.5) - 1.0
        qs = room / (1 + 1/k)
        uc = qs / k
        qy = BOTTOM - uc - 1.0 - qs
        s.append(left_text(URL, T[600], uc, x, BOTTOM, INK)[0])
        gesaeuse(8.0 / GS_ASPECT, (qy + BOTTOM)/2)
        print(f"  QR {qs:.2f} mm, URL Versal {uc:.2f} mm")
    elif GS_MODE == 'qr-rechts':
        # gespiegelt zur Reihe darueber: Siegel links unter der Adresse,
        # QR rechts unter den Marken, URL darunter rechtsbuendig
        uc = CAP_B
        qy = BOTTOM - uc - 1.2 - qs
        uw = V.natural_w(URL, T[600], uc)
        s.append(left_text(URL, T[600], uc, x + maxw - uw, BOTTOM, INK)[0])
        vw = 8.0 / GS_ASPECT; vh = vw * GS_ASPECT
        s.append(svg_place_visual(GS, x, (qy + BOTTOM)/2 - vh/2, vw, "gesaeuse-partner", fill=INK))
        x_qr = x + maxw - qs
    elif GS_MODE == 'qr-text':
        # Story wieder da, kleiner; QR 7,5 mm (Modul 0,227 mm, nicht kleiner);
        # das Siegel bekommt die ganze Restbreite
        qs = 7.5; qy = BOTTOM - qs; tx = x + qs + 2.2
        sc = 1.18                                    # Untergrenze freiwilliger Text
        aw = max(V.natural_w(st, T[400], sc) for st in STORY)
        uc = min(CAP_B, CAP_B * (aw - 3.4) / V.natural_w(URL, T[600], CAP_B))
        lead = BASE*0.92*sc/CAP_V
        blk = len(STORY)*lead + 0.3 + uc
        sy = BOTTOM - qs + (qs - blk)/2 + sc
        for i, st in enumerate(STORY):
            s.append(left_text(st, T[400], sc, tx, sy + i*lead, INK)[0])
        uy = sy + len(STORY)*lead + 0.3
        arrow(uy - uc*0.5)
        s.append(left_text(URL, T[600], uc, tx + 3.4, uy, INK)[0])
        vw = maxw - qs - 2.2 - aw - 2.2
        vh = gesaeuse(vw, BOTTOM - qs/2)
        print(f"  QR {qs:.2f} mm, Story {sc:.2f} mm, URL {uc:.2f} mm, Siegel {vw:.2f} x {vh:.2f} mm")
    elif GS_MODE == 'qr':
        # ohne Story, URL mittig zum QR, Siegel rechts buendig in derselben Reihe
        uc = CAP_V
        uy = BOTTOM - qs/2 + uc/2
        arrow(uy - uc*0.5)
        s.append(left_text(URL, T[600], uc, tx + 3.4, uy, INK)[0])
        gesaeuse(min(tw - 3.4 - V.natural_w(URL, T[600], uc) - 2.5, qs / GS_ASPECT), BOTTOM - qs/2)
    else:
        lines = [ln for st in STORY for ln in wrap_text(st, T[400], CAP_V*1.1, tw)]
        blk = len(lines)*BASE*0.92 + 0.3 + CAP_B
        sy = BOTTOM - qs + (qs - blk)/2 + CAP_V
        for i, ln in enumerate(lines):
            t, _ = left_text(ln, T[400], CAP_V, tx, sy + i*BASE*0.92, INK); s.append(t)
        uy = sy + len(lines)*BASE*0.92 + 0.3
        arrow(uy - CAP_B*0.5)
        t, _ = left_text(URL, T[600], CAP_B, tx + 3.4, uy, INK); s.append(t)
    s.append(f'<g id="qr" inkscape:label="QR kraeuterbergbauer.at" '
             f'transform="translate({x_qr if GS_MODE == "qr-rechts" else x:.3f},{qy:.3f}) scale({qs/n:.5f})">{_inner(q)}</g>')
    print(f"  QR oben {qy-OY:.2f} mm, Adresse/Marken unten {max(y - BASE, cy_m + d/2)-OY:.2f} mm (ab Schnitt)")
    s.append("</svg>")
    return "".join(s)

def render(stem, bg_png=None, png_w=2200):
    import cairosvg
    svg = build(bg_png)
    open(stem + ".svg", "w", encoding="utf-8").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=stem + ".png", output_width=png_w)
    return svg

if __name__ == "__main__":
    import sys
    render("out/v2", "/mnt/user-data/outputs/xeistee-band/backgrounds/bg-13-glow-gold-4k.png")
