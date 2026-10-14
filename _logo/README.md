# Logo

Jigsaw Buddy Bear logo for Puzzled Pint Berlin, generated with code.

```
uv run _logo/bear.py            # writes SVGs to images/bear/
for f in $(find images/bear -name '*.svg'); do rsvg-convert -w 1024 "$f" -o "${f%.svg}.png"; done
uv run _logo/sheet.py images/bear logo-options.pdf   # contact sheet
uv run _logo/favicon.py         # 16x16 pixel jigsaw: favicon.ico, images/favicon-16.png
```

Output: `images/bear/<layout>/` for layouts `pint`, `centre` and `bottom`,
each with `logo`, `ubahn/`, `sbahn/` and `shapes/`. Only
`images/bear/centre/logo.png` is committed and used on the site.

## Sources

| File | Source | Licence |
|---|---|---|
| `buddy-baer-logo.svg` | [buddy-baer.com](https://www.buddy-baer.com/typo3conf/ext/men_template/Resources/Public/Img/buddy_baers_logo.svg) (bear outline only) | Buddy Bär Berlin GmbH |
| `Hind-Bold.ttf` | [Google Fonts](https://github.com/google/fonts/tree/main/ofl/hind) | SIL OFL 1.1 (`Hind-OFL.txt`) |
| `ionicons-pint.svg` | [Ionicons "pint"](https://commons.wikimedia.org/wiki/File:Ionicons_pint.svg) | MIT |

Line colours are from the VBB passenger information handbook via
Wikipedia's Berlin U-Bahn and S-Bahn modules. Trams have no line colours.
