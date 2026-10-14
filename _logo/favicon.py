import subprocess
import tempfile
from pathlib import Path

RED = "#E30613"
PIXELS = """
................
.....##.........
....####........
....####........
.....##.........
.##########.....
.##########.....
.##########.....
.#.########.##..
....###########.
....###########.
.#.########.##..
.####..####.....
.###....###.....
.####..####.....
................
"""


def main():
    root = Path(__file__).resolve().parent.parent
    rows = PIXELS.strip().splitlines()
    rects = "".join(
        f'<rect x="{x}" y="{y}" width="1" height="1"/>'
        for y, row in enumerate(rows) for x, c in enumerate(row) if c == "#"
    )
    tmp = Path(tempfile.mkdtemp())
    svg = tmp / "favicon.svg"
    svg.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" '
        f'shape-rendering="crispEdges"><g fill="{RED}">{rects}</g></svg>\n'
    )
    base = root / "images" / "favicon-16.png"
    subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", str(svg), "-o", str(base)], check=True)
    pngs = [str(base)]
    for size in (32, 48):
        png = tmp / f"favicon-{size}.png"
        subprocess.run(["magick", str(base), "-filter", "point", "-resize", f"{size}x{size}", str(png)], check=True)
        pngs.append(str(png))
    subprocess.run(["magick", *pngs, str(root / "favicon.ico")], check=True)


if __name__ == "__main__":
    main()
