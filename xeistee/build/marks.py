"""Claim marks for the Xeistee label: VEGAN / OHNE KOFFEIN / HOFPRODUKTION.

Drawn as vector at the size they print (9 mm), so they stay crisp. Icons are
built from simple shapes - anything finer than ~0.15 mm stroke disappears in
flexo print at this scale.
"""
import variants as V

INK, CREAM = "#2E3524", "#ECE0D0"
T = V.TEXT_FONTS


# ---------- icons, drawn in a unit box (-1..1), returned as one path group ----------
def ico_leaf(fill, sw):
    return (f'<path d="M0,-1 C0.78,-0.45 0.78,0.45 0,1 C-0.78,0.45 -0.78,-0.45 0,-1 Z" fill="{fill}"/>'
            f'<path d="M0,0.95 L0,-0.75" stroke="{"none"}" fill="none"/>')


def ico_leaf2(fill, sw, paper):
    # leaf with a cut-out midrib so it reads at 2 mm
    return (f'<path d="M0,-1 C0.78,-0.45 0.78,0.45 0,1 C-0.78,0.45 -0.78,-0.45 0,-1 Z" fill="{fill}"/>'
            f'<path d="M0,0.88 L0,-0.82 M0,-0.15 L0.42,-0.52 M0,0.3 L-0.42,-0.07" '
            f'stroke="{paper}" stroke-width="{sw}" fill="none" stroke-linecap="round"/>')


def ico_bean(fill, sw, paper):
    # coffee bean + slash
    return (f'<g transform="rotate(-22)">'
            f'<ellipse cx="0" cy="0" rx="0.62" ry="0.92" fill="{fill}"/>'
            f'<path d="M-0.06,-0.78 C0.30,-0.34 -0.30,0.34 0.06,0.78" stroke="{paper}" '
            f'stroke-width="{sw*1.1}" fill="none" stroke-linecap="round"/></g>'
            f'<path d="M-1.02,0.92 L1.02,-0.92" stroke="{paper}" stroke-width="{sw*2.6}" stroke-linecap="round"/>'
            f'<path d="M-1.02,0.92 L1.02,-0.92" stroke="{fill}" stroke-width="{sw*1.2}" stroke-linecap="round"/>')


def ico_hof(fill, sw, paper):
    # farmhouse: gable roof, body, door
    return (f'<path d="M-1.02,-0.12 L0,-0.95 L1.02,-0.12 Z" fill="{fill}"/>'
            f'<path d="M-0.76,-0.12 L0.76,-0.12 L0.76,0.92 L-0.76,0.92 Z" fill="{fill}"/>'
            f'<path d="M-0.17,0.92 L-0.17,0.28 L0.17,0.28 L0.17,0.92 Z" fill="{paper}"/>')


def ico_mtn(fill, sw, paper):
    # alt for Hofproduktion: hill with a house, ties to the band
    return (f'<path d="M-1.05,0.85 L-0.35,-0.25 L0.05,0.25 L0.5,-0.55 L1.05,0.85 Z" fill="{fill}"/>')


ICONS = {"vegan": ico_leaf2, "koffein": ico_bean, "hof": ico_hof}


def brush_ring(cx, cy, r, w, ink, a0=-2.55, sweep=0.955):
    """A single brush sweep round a circle: tapered ends, slightly uneven edge."""
    import math
    n, T = 240, 2*math.pi*sweep
    outer, inner = [], []
    for i in range(n+1):
        u = i/n; t = a0 + u*T
        rr = r * (1 + 0.012*math.sin(2.7*t + 1.3) + 0.007*math.sin(5.3*t + 0.4))
        ww = w * (0.30 + 0.70*math.sin(math.pi*u)**0.55) * (1 + 0.16*math.sin(4.1*t))
        outer.append((cx + (rr+ww/2)*math.cos(t), cy + (rr+ww/2)*math.sin(t)))
        inner.append((cx + (rr-ww/2)*math.cos(t), cy + (rr-ww/2)*math.sin(t)))
    d = "M" + " L".join(f"{a:.3f},{b:.3f}" for a, b in outer)
    d += " L" + " L".join(f"{a:.3f},{b:.3f}" for a, b in reversed(inner)) + " Z"
    return f'<path d="{d}" fill="{ink}"/>'


def brush_blob(cx, cy, r, ink):
    """Filled disc with a painted, slightly uneven edge."""
    import math
    n = 240
    pts = []
    for i in range(n):
        t = 2*math.pi*i/n
        rr = r * (1 + 0.020*math.sin(2.3*t + 0.7) + 0.012*math.sin(4.7*t + 2.1)
                  + 0.007*math.sin(7.9*t))
        pts.append((cx + rr*math.cos(t), cy + rr*math.sin(t)))
    return '<path d="M' + " L".join(f"{a:.3f},{b:.3f}" for a, b in pts) + ' Z" fill="%s"/>' % ink


def mark(style, x, y, d, icon, lines, ink=INK, paper=CREAM):
    """One claim mark, top-left at (x, y), diameter d."""
    r = d / 2
    cx, cy = x + r, y + r
    on_ink = style in ("disc", "seal", "brushfill")
    fg = paper if on_ink else ink
    bg = ink if on_ink else paper
    out = [f'<g inkscape:label="Marke {" ".join(lines)}">']

    if style == "disc":
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{ink}"/>')
    elif style == "seal":
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{ink}"/>')
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r-d*0.085:.3f}" fill="none" '
                   f'stroke="{paper}" stroke-width="{d*0.028:.3f}"/>')
    elif style == "ring":
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r-d*0.02:.3f}" fill="none" '
                   f'stroke="{ink}" stroke-width="{d*0.04:.3f}"/>')
    elif style == "brush":
        out.append(brush_ring(cx, cy, r - d*0.055, d*0.075, ink))
    elif style == "brushfill":
        out.append(brush_blob(cx, cy, r, ink))
    elif style == "ring2":
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r-d*0.02:.3f}" fill="none" '
                   f'stroke="{ink}" stroke-width="{d*0.055:.3f}"/>')
        out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r-d*0.135:.3f}" fill="none" '
                   f'stroke="{ink}" stroke-width="{d*0.018:.3f}"/>')

    # icon sits in the upper half
    ir = d * (0.155 if len(lines) == 2 else 0.175)
    iy = cy - d * (0.20 if len(lines) == 2 else 0.17)
    sw = 0.16 / ir if ir else 0.16          # keep the stroke ~0.16 mm after scaling
    out.append(f'<g transform="translate({cx:.3f},{iy:.3f}) scale({ir:.4f})">'
               + ICONS[icon](fg, sw, bg) + '</g>')

    # caps under it, fitted to the disc
    # each line is fitted to the CHORD of the circle at its own height, not to one
    # fixed width - that is what kept PRODUKTION running into the ring
    import math
    rt = {"ring2": r - d*0.155, "seal": r - d*0.105, "brush": r - d*0.105,
          "ring": r - d*0.06}.get(style, r - d*0.03)
    cap0 = d * 0.132
    ty = cy + d * (0.10 if len(lines) == 2 else 0.20)
    for i, ln in enumerate(lines):
        base = ty + i * d * 0.170
        cap = cap0
        for _ in range(4):
            v = max(abs(base - cy), abs(base - cap - cy)) + d*0.02
            chord = 2*math.sqrt(max(rt*rt - v*v, 0.01)) - d*0.04
            w = V.natural_w(ln, T[600], cap) + 0.06 * cap * (len(ln) - 1)
            if w <= chord: break
            cap *= chord / w
        out.append(V.text_block(ln, T[600], cap, cx, base, fg, tracking=cap * 0.06))
    out.append("</g>")
    return "".join(out)


SET = [("vegan", ["VEGAN"]), ("koffein", ["OHNE", "KOFFEIN"]), ("hof", ["HOF", "PRODUKTION"])]


def row(style, x, y, d, gap=1.5, **kw):
    out, px = [], x
    for icon, lines in SET:
        out.append(mark(style, px, y, d, icon, lines, **kw))
        px += d + gap
    return "".join(out), px - x - gap


if __name__ == "__main__":
    import cairosvg
    V.LIVE_TEXT = False
    D = 9.0
    styles = [("brush", "A  Pinselring"), ("brushfill", "B  Pinselfläche"),
              ("seal", "C  Siegel"), ("ring2", "D  Doppelring")]
    W, H = 150.0, 24.0 * len(styles) + 8
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
         f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#F2DFA8"/>']
    y = 6.0
    for st, name in styles:
        s.append(V.text_block(name, T[500], 2.0, 14.0, y + 2.0, INK))
        g, _ = row(st, 26.0, y - 2.0, D)
        s.append(g)
        # 2.4x enlargement beside it
        g2, _ = row(st, 0, 0, D)
        s.append(f'<g transform="translate(62,{y - 3.0}) scale(2.4)">{g2}</g>')
        y += 24.0
    s.append("</svg>")
    svg = "".join(s)
    open("out/marks.svg", "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to="out/marks.png", output_width=1900)
    print("ok")
