import re
import subprocess
import sys
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
W, H = 842, 595
VARIANTS = [("A", "pint", "Pint + text at bottom"), ("B", "centre", "No pint, text centred"), ("C", "bottom", "No pint, text at bottom")]
MODES = [("", "Logo red"), ("ubahn", "U-Bahn"), ("sbahn", "S-Bahn")]
FONT = "font-family='Adwaita Sans, FreeSans, sans-serif'"


def embed(path, x, y, size):
    src = path.read_text()
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", src, flags=re.S)
    return f'<svg x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" viewBox="0 0 1024 1024">{inner}</svg>'


def label(path, mode):
    names = path.stem.split("-")
    return "Logo red" if path.stem == "logo" else " / ".join(n.upper() for n in names)


def hexcode(path):
    return re.search(r'<rect[^>]*fill="(#[0-9A-Fa-f]{6})"', path.read_text()).group(1).upper()


def page(body, title):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#fff"/>
<text x="36" y="44" {FONT} font-size="20" font-weight="bold" fill="#111">{title}</text>
{body}</svg>"""


pages = []
body, size = "", 230
for i, (code, folder, desc) in enumerate(VARIANTS):
    x = 36 + i * (size + 40)
    body += embed(root / folder / "logo.svg", x, 110, size)
    body += f'<text x="{x}" y="{110 + size + 30}" {FONT} font-size="18" font-weight="bold" fill="#111">{code} — {desc}</text>'
    body += f'<text x="{x}" y="{110 + size + 50}" {FONT} font-size="11" fill="#555">images/bear/{folder}/</text>'
body += f'<text x="36" y="70" {FONT} font-size="12" fill="#555">Reply with a layout letter plus a colour, e.g. “B · U8”. Page 2 shows shapes; pages 3–5 show every colour per layout.</text>'
pages.append(page(body, "Puzzled Pint Berlin — logo options"))

for code, folder, desc in VARIANTS:
    files = [(m, p) for m, _ in MODES for p in sorted((root / folder / m).glob("*.svg"), key=lambda p: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.stem)])]
    cols, tile, gx, gy = 10, 66, 77, 120
    body, row, col, last = "", 0, 0, None
    for m, p in files:
        if col == cols:
            row, col = row + 1, 0
        last = m
        x, y = 36 + col * gx, 70 + row * gy
        body += embed(p, x, y, tile)
        tag = f"{code}·{label(p, m)}" if p.stem != "logo" else f"{code}·RED"
        body += f'<text x="{x}" y="{y + tile + 11}" {FONT} font-size="7.5" font-weight="bold" fill="#111">{tag}</text>'
        body += f'<text x="{x}" y="{y + tile + 20}" {FONT} font-size="6.5" fill="#666">{dict(MODES)[m]} · {hexcode(p)}</text>'
        col += 1
    pages.append(page(body, f"{code} — {desc}"))

SHAPES = [("1-square", "Square"), ("2-soft", "Soft (as Buddy Bär)"), ("3-rounded", "Rounded"), ("4-round", "Round"), ("5-circle", "Circle"), ("6-instagram", "Instagram: square, circle-safe")]
body = f'<text x="36" y="66" {FONT} font-size="11" fill="#555">Main red logo, five corner radii per layout. Codes like “B·circle”.</text>'
for r, (code, folder, desc) in enumerate(VARIANTS):
    y = 84 + r * 160
    body += f'<text x="36" y="{y + 70}" {FONT} font-size="22" font-weight="bold" fill="#111">{code}</text>'
    for c, (name, nice) in enumerate(SHAPES):
        x = 70 + c * 127
        body += embed(root / folder / "shapes" / f"{name}.svg", x, y, 112)
        body += f'<text x="{x}" y="{y + 125}" {FONT} font-size="9" font-weight="bold" fill="#111">{code}·{name.split("-")[1]}</text>'
        body += f'<text x="{x}" y="{y + 136}" {FONT} font-size="7.5" fill="#666">{nice}</text>'
pages.insert(1, page(body, "Shapes — main red logo"))

tmp = out.parent / "sheet-pages"
tmp.mkdir(exist_ok=True)
paths = []
for i, svg in enumerate(pages):
    f = tmp / f"p{i}.svg"
    f.write_text(svg)
    paths.append(str(f))
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(out), *paths], check=True)
