# /// script
# requires-python = ">=3.11"
# dependencies = ["svgpathtools", "fonttools"]
# ///
import argparse
import math
import random
import re
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from svgpathtools import parse_path

SIZE = 1024
TEXT = ["PUZZLED", "PINT", "BERLIN"]
MAIN = "#E30613"
SHAPES = {"1-square": 0, "2-soft": 0.05, "3-rounded": 0.15, "4-round": 0.3, "5-circle": 0.5}
LINES = {
    "ubahn": {
        "U1": "#7DAD4C", "U2": "#DA421E", "U3": "#16683D", "U4": "#F0D722", "U5": "#7E5330",
        "U6": "#8C6DAB", "U7": "#009BD5", "U8": "#224F86", "U9": "#F3791D",
    },
    "sbahn": {
        "S1": "#DA6BA2", "S2": "#007734", "S25": "#007734", "S26": "#007734", "S3": "#0066AD",
        "S41": "#AD5937", "S42": "#CB6418", "S45": "#CD9C53", "S46": "#CD9C53", "S47": "#CD9C53",
        "S5": "#EB7405", "S7": "#816DA6", "S75": "#816DA6", "S8": "#66AA22", "S85": "#66AA22",
        "S9": "#992746",
    },
}


def logo_shapes(logo):
    src = Path(logo).read_text()
    d = re.sub(r"\s+", " ", re.search(r'<path[^>]*?d="([^"]*)"', src, re.S).group(1))
    subs = [p for p in re.split(r"(?=M)", d) if p.strip()]
    boxes = [parse_path(p).bbox() for p in subs]
    square = max(boxes, key=lambda b: (b[1] - b[0]) * (b[3] - b[2]))
    bear = max(subs, key=len)
    bbox = parse_path(bear).bbox()
    k = SIZE / (square[1] - square[0])
    to = lambda x, y: ((x - square[0]) * k, (y - square[2]) * k)
    return bear, f"scale({k:.5f}) translate({-square[0]:.3f} {-square[2]:.3f})", (*to(bbox[0], bbox[2]), *to(bbox[1], bbox[3])), k


def text_paths(font_path, lines, x0, y0, x1, y1, gap=0.16):
    font = TTFont(font_path)
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": 600})
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    cap = font["OS/2"].sCapHeight
    track = 0.08 * cap
    rows = []
    for line in lines:
        names = [cmap[ord(ch)] for ch in line]
        bounds = []
        for n in names:
            bp = BoundsPen(gs)
            gs[n].draw(bp)
            bounds.append(bp.bounds)
        ink = sum(gs[n].width + track for n in names[:-1]) + bounds[-1][2] - bounds[0][0]
        rows.append((names, bounds[0][0], (x1 - x0) / ink))
    heights = [s * cap for _, _, s in rows]
    g = gap * sum(heights) / len(heights)
    f = min(1, (y1 - y0) / (sum(heights) + g * (len(rows) - 1)))
    left = x1 - (x1 - x0) * f
    base = top = y1 - (sum(heights) + g * (len(rows) - 1)) * f
    out = []
    for (names, lsb, s), h in zip(rows, heights):
        s *= f
        base += h * f
        x = -lsb
        for n in names:
            pen = SVGPathPen(gs)
            gs[n].draw(pen)
            out.append(f'<path transform="translate({left + x * s:.2f} {base:.2f}) scale({s:.5f} {-s:.5f})" d="{pen.getCommands()}"/>')
            x += gs[n].width + track
        base += g * f
    return "".join(out), (left, top, x1)


def pint(src, cx, bottom, height):
    d = re.search(r'<path[^>]*?\sd="([^"]*)"', Path(src).read_text(), re.S).group(1)
    x0, x1, y0, y1 = parse_path(d).bbox()
    s = height / (y1 - y0)
    return f'<path d="{d}" transform="translate({cx - (x0 + x1) / 2 * s:.2f} {bottom - y1 * s:.2f}) scale({s:.4f})"/>'


def jigsaw(box, cols, rows, tab=0.12, jitter=0.04, seed=1):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []

    def edges(n_lines, n_segs, along0, along1, across0, across1, vertical):
        seg = (along1 - along0) / n_segs
        gap = (across1 - across0) / n_lines
        for i in range(1, n_lines):
            base = across0 + gap * i
            e = rnd.uniform(-jitter, jitter)
            flip = rnd.random() < 0.5
            pts = []
            for s in range(n_segs):
                old, flip = flip, rnd.random() < 0.5
                a = -e if flip == old else e
                b, c, d, e = (rnd.uniform(-jitter, jitter) for _ in range(4))
                sign = -1 if flip else 1

                def p(lv, wv):
                    lpos = along0 + seg * (s + lv)
                    wpos = base + gap * wv * sign
                    return (wpos, lpos) if vertical else (lpos, wpos)

                t = tab
                pts.append([
                    p(0.2, a), p(0.5 + b + d, -t + c), p(0.5 - t + b, t + c),
                    p(0.5 - 2 * t + b - d, 3 * t + c), p(0.5 + 2 * t + b - d, 3 * t + c), p(0.5 + t + b, t + c),
                    p(0.5 + b + d, -t + c), p(0.8, e), p(1.0, 0.0),
                ])
            start = (base, along0) if vertical else (along0, base)
            d_ = f"M{start[0]:.1f},{start[1]:.1f}"
            for q in pts:
                for j in range(0, 9, 3):
                    d_ += " C" + " ".join(f"{x:.1f},{y:.1f}" for x, y in q[j:j + 3])
            out.append(d_)

    edges(rows, cols, x0, x1, y0, y1, False)
    edges(cols, rows, y0, y1, x0, x1, True)
    return " ".join(out)


def ink(bg):
    r, g, b = (int(bg[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = sum(w * (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for w, c in zip((0.2126, 0.7152, 0.0722), (r, g, b)))
    return "#191919" if lum > 0.45 else "#ffffff"


def fit(box, radius, margin=0.045 * SIZE):
    def inside(s):
        c = SIZE / 2
        for x in (box[0], box[2]):
            for y in (box[1], box[3]):
                px, py = abs(c + (x - c) * s - c), abs(c + (y - c) * s - c)
                if max(px, py) > c - margin:
                    return False
                ox, oy = px - (c - radius), py - (c - radius)
                if ox > 0 and oy > 0 and math.hypot(ox, oy) > radius - margin:
                    return False
        return True

    lo, hi = 0.3, 1.0
    if inside(hi):
        return hi
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if inside(mid) else (lo, mid)
    return lo


def svg(art, bg, radius=None, scale=1.0):
    fg = ink(bg)
    radius = art["radius"] if radius is None else radius
    c = SIZE / 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
<defs><clipPath id="bear"><path d="{art['bear']}" transform="{art['transform']}"/></clipPath></defs>
<rect width="{SIZE}" height="{SIZE}" rx="{radius:.1f}" fill="{bg}"/>
<g transform="translate({c} {c}) scale({scale:.4f}) translate({-c} {-c})">
<path d="{art['bear']}" transform="{art['transform']}" fill="{fg}"/>
<g clip-path="url(#bear)"><path d="{art['puzzle']}" transform="rotate({art['angle']} {art['cx']:.1f} {art['cy']:.1f})" fill="none" stroke="{bg}" stroke-width="{art['stroke']:.1f}" stroke-linecap="round" stroke-linejoin="round"/></g>
<g fill="{fg}">{art['text']}{art['pint']}</g>
</g>
</svg>
"""


def main():
    ap = argparse.ArgumentParser(description="Jigsaw Buddy Bear logo in Berlin line colours")
    here = Path(__file__).parent
    ap.add_argument("out", type=Path, nargs="?", default=here.parent / "images" / "bear")
    ap.add_argument("--logo", type=Path, default=here / "buddy-baer-logo.svg")
    ap.add_argument("--font", type=Path, default=here / "Hind-Bold.ttf")
    ap.add_argument("--glass", type=Path, default=here / "ionicons-pint.svg")
    ap.add_argument("--piece", type=float, default=0.32, help="piece size relative to bear height")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--angle", type=float, default=40)
    ap.add_argument("--stroke", type=float, default=0.015, help="line width relative to bear height")
    ap.add_argument("--pint", type=float, default=0.75, help="pint height relative to space above text")
    args = ap.parse_args()
    bear, transform, (bx0, by0, bx1, by1), k = logo_shapes(args.logo)
    bh = by1 - by0
    piece = args.piece * bh
    n = math.ceil(SIZE * 1.5 / piece)
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    ty1 = (274.7 + 0.4) * k
    text, (tx0, ty0, tx1) = text_paths(args.font, TEXT, (483.7 - 343.1) * k, (188.4 + 0.4) * k, (641.1 - 343.1) * k, ty1)
    gap = 0.05 * SIZE
    centred = f'<g transform="translate(0 {cy - (ty0 + ty1) / 2:.2f})">{text}</g>'
    variants = {
        "pint": {"text": text, "pint": pint(args.glass, (tx0 + tx1) / 2, ty0 - gap, args.pint * (ty0 - gap - by0))},
        "centre": {"text": centred, "pint": ""},
        "bottom": {"text": text, "pint": ""},
    }
    art = {
        "bear": bear, "transform": transform, "radius": 15.84 * k, "angle": args.angle, "cx": cx, "cy": cy,
        "puzzle": jigsaw((cx - n * piece / 2, cy - n * piece / 2, cx + n * piece / 2, cy + n * piece / 2), n, n, seed=args.seed),
        "stroke": args.stroke * bh,
    }
    groups, seen = {"": {MAIN: ["logo"]}}, {MAIN}
    for mode, lines in LINES.items():
        groups[mode] = {}
        for line, colour in lines.items():
            if colour not in seen:
                groups[mode].setdefault(colour, []).append(line.lower())
        seen |= set(groups[mode])
    for variant, parts in variants.items():
        for mode, colours in groups.items():
            (args.out / variant / mode).mkdir(parents=True, exist_ok=True)
            for colour, names in colours.items():
                (args.out / variant / mode / f"{'-'.join(names)}.svg").write_text(svg(art | parts, colour))
        (args.out / variant / "shapes").mkdir(exist_ok=True)
        content = (min(bx0, tx0), by0, tx1, max(by1, ty1))
        for name, r in SHAPES.items():
            (args.out / variant / "shapes" / f"{name}.svg").write_text(svg(art | parts, MAIN, r * SIZE, fit(content, r * SIZE)))
        (args.out / variant / "shapes" / "6-instagram.svg").write_text(svg(art | parts, MAIN, 0, fit(content, SIZE / 2)))


if __name__ == "__main__":
    main()
