"""Generates every themed asset for the 3liAf profile from one palette.

The ASCII banner is drawn as SVG <rect> elements on an exact grid, not as text.
Text-based block art depends on the viewer's font resolving U+2588 with the same
advance width as a space -- it usually does not, and the grid collapses.
Rects have no font dependency at all.

Run:  python tools/build_assets.py
"""

import os

# ---------------------------------------------------------------- palette ---
SUNSET = ["#ff4d8d", "#ff6a5e", "#ff7b4a", "#ff9a3c", "#ffb85c", "#ffd166"]
BG_DEEP = "#1b1026"
BG_DARK = "#120a1a"
BAR = "#2a1836"
BORDER = "#3d2547"
TEXT = "#c9a7c7"
TEXT_BRIGHT = "#f3e9f7"
MUTED = "#8f7aa0"

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ASSETS = os.path.join(ROOT, "assets")

# ------------------------------------------------------------- pixel font ---
# 5x5 cells per glyph. '#' = filled.
FONT = {
    "A": [".###.", "#...#", "#####", "#...#", "#...#"],
    "F": ["#####", "#....", "#####", "#....", "#...."],
    "I": ["#####", "..#..", "..#..", "..#..", "#####"],
    "L": ["#....", "#....", "#....", "#....", "#####"],
    "O": ["#####", "#...#", "#...#", "#...#", "#####"],
    "S": ["#####", "#....", "#####", "....#", "#####"],
    "U": ["#...#", "#...#", "#...#", "#...#", "#####"],
    "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#.."],
}
GLYPH_W, GLYPH_H = 5, 5
LETTER_GAP = 1   # columns between letters
WORD_GAP = 3     # extra columns between words


def layout(text):
    """Return (list of (col, row) filled cells, total column count)."""
    cells, col = [], 0
    for i, ch in enumerate(text):
        if ch == " ":
            col += WORD_GAP
            continue
        if i > 0 and text[i - 1] != " ":
            col += LETTER_GAP
        rows = FONT[ch]
        for r in range(GLYPH_H):
            for c in range(GLYPH_W):
                if rows[r][c] == "#":
                    cells.append((col + c, r))
        col += GLYPH_W
    return cells, col


# ------------------------------------------------------------ banner .svg ---
def build_banner():
    text = "ALI YOUSUF"
    cells, cols = layout(text)

    CELL_W, CELL_H = 11, 17          # grid pitch
    DOT_W, DOT_H = 9.0, 15.0         # drawn size, leaving a 2px pixel gutter
    OX, OY = 50, 64                  # banner origin
    W, H = 880, 330

    art_w = cols * CELL_W

    # Prompt lines. textLength pins the rendered width so the typing mask math
    # is exact no matter which monospace font the viewer actually has.
    CHAR_W = 8.4
    l1_plain, l1_cmd = "3liAf@github:~$ ", "whoami"
    l2_plain, l2_cmd = "3liAf@github:~$ ", "ls skills/"
    l1_w = round((len(l1_plain) + len(l1_cmd)) * CHAR_W, 1)
    l2_w = round((len(l2_plain) + len(l2_cmd)) * CHAR_W, 1)

    rects = []
    for c, r in cells:
        x = OX + c * CELL_W
        y = OY + r * CELL_H
        delay = round(c * 0.022, 3)   # left-to-right draw-in
        rects.append(
            f'<rect class="px" x="{x}" y="{y}" width="{DOT_W}" height="{DOT_H}" '
            f'rx="1.5" style="animation-delay:{delay}s"/>'
        )
    rects = "\n        ".join(rects)

    chips = [("Python", 63), ("PyTorch", 70), ("LangChain", 85),
             ("FastAPI", 70), ("AWS", 46), ("Docker", 63)]
    chip_svg, cx = [], 50
    for i, (label, w) in enumerate(chips):
        col = SUNSET[i]
        chip_svg.append(
            f'<g class="chip" style="animation-delay:{6.6 + i * 0.18:.2f}s">'
            f'<rect x="{cx}" y="272" width="{w}" height="24" rx="6" fill="{col}" '
            f'fill-opacity="0.14" stroke="{col}" stroke-opacity="0.5"/>'
            f'<text class="mono" x="{cx + w / 2}" y="288" font-size="12" fill="{col}" '
            f'text-anchor="middle">{label}</text></g>'
        )
        cx += w + 10
    chip_svg = "\n        ".join(chip_svg)

    stops = "".join(
        f'<stop offset="{i * 100 // (len(SUNSET) - 1)}%" stop-color="{c}"/>'
        for i, c in enumerate(SUNSET)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal banner reading ALI YOUSUF">
  <title>Ali Afzal Yousuf - AI Engineer</title>
  <defs>
    <linearGradient id="sunset" gradientUnits="userSpaceOnUse" x1="{OX}" y1="0" x2="{OX + art_w}" y2="0">{stops}</linearGradient>
    <linearGradient id="bg" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0%" stop-color="{BG_DEEP}"/><stop offset="100%" stop-color="{BG_DARK}"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff7b4a" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#ff7b4a" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="12"/></clipPath>
    <mask id="m1"><rect class="wipe w1" x="50" y="178" width="{l1_w}" height="20" fill="#fff"/></mask>
    <mask id="m2"><rect class="wipe w2" x="50" y="240" width="{l2_w}" height="20" fill="#fff"/></mask>
    <style>
      .mono {{ font-family: ui-monospace,'SFMono-Regular','JetBrains Mono','Cascadia Mono',Consolas,'Liberation Mono',Menlo,monospace; }}
      .px,.scene,.wipe,.out,.chip,.cur {{ animation-duration:14s; animation-iteration-count:infinite; animation-timing-function:linear; }}
      .scene {{ animation-name:sceneFade; }}
      @keyframes sceneFade {{ 0%,94% {{opacity:1}} 99%,100% {{opacity:0}} }}
      .px {{ fill:url(#sunset); opacity:0; animation-name:pxIn; transform-box:fill-box; transform-origin:center; }}
      @keyframes pxIn {{ 0%,1% {{opacity:0;transform:scale(.35)}} 6%,100% {{opacity:1;transform:scale(1)}} }}
      .wipe {{ transform-box:fill-box; transform-origin:left center; }}
      .w1 {{ animation-name:type1; }} .w2 {{ animation-name:type2; }}
      @keyframes type1 {{ 0%,18% {{transform:scaleX(0)}} 27%,100% {{transform:scaleX(1)}} }}
      @keyframes type2 {{ 0%,36% {{transform:scaleX(0)}} 46%,100% {{transform:scaleX(1)}} }}
      .cur {{ opacity:0; }}
      .cur1 {{ animation-name:cur1; }} .cur2 {{ animation-name:cur2; }}
      @keyframes cur1 {{ 0%,17% {{opacity:0;transform:translateX(0)}} 18% {{opacity:1;transform:translateX(0)}}
        27%,33% {{opacity:1;transform:translateX({l1_w}px)}} 34%,100% {{opacity:0;transform:translateX({l1_w}px)}} }}
      @keyframes cur2 {{ 0%,35% {{opacity:0;transform:translateX(0)}} 36% {{opacity:1;transform:translateX(0)}}
        46%,100% {{opacity:1;transform:translateX({l2_w}px)}} }}
      .blink {{ animation:blink 1.06s steps(1,end) infinite; }}
      @keyframes blink {{ 0%,50% {{opacity:1}} 50.01%,100% {{opacity:0}} }}
      .out {{ opacity:0; animation-name:fadeUp; animation-delay:3.9s; }}
      @keyframes fadeUp {{ 0%,2% {{opacity:0;transform:translateY(4px)}} 6%,100% {{opacity:1;transform:translateY(0)}} }}
      .chip {{ opacity:0; animation-name:chipIn; transform-box:fill-box; transform-origin:center; }}
      @keyframes chipIn {{ 0%,2% {{opacity:0;transform:translateY(5px) scale(.94)}} 6%,100% {{opacity:1;transform:translateY(0) scale(1)}} }}
      @media (prefers-reduced-motion:reduce) {{
        .px,.scene,.wipe,.out,.chip,.cur,.blink {{ animation:none !important; opacity:1 !important; transform:none !important; }}
      }}
    </style>
  </defs>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect y="34" width="{W}" height="150" fill="url(#glow)"/>
    <rect width="{W}" height="34" fill="{BAR}"/>
    <circle cx="24" cy="17" r="6" fill="#ff5f57"/><circle cx="46" cy="17" r="6" fill="#febc2e"/><circle cx="68" cy="17" r="6" fill="#28c840"/>
    <text class="mono" x="{W // 2}" y="22" font-size="12.5" fill="#a98bb8" text-anchor="middle">3liAf@github - zsh</text>

    <g class="scene">
        {rects}

      <g mask="url(#m1)">
        <text class="mono" x="50" y="193" font-size="14" textLength="{l1_w}" lengthAdjust="spacing" xml:space="preserve"><tspan fill="{SUNSET[4]}">3liAf@github</tspan><tspan fill="{MUTED}">:</tspan><tspan fill="{SUNSET[2]}">~</tspan><tspan fill="{MUTED}">$ </tspan><tspan fill="{TEXT_BRIGHT}">{l1_cmd}</tspan></text>
      </g>
      <g class="cur cur1"><rect class="blink" x="50" y="181" width="8" height="15" fill="{SUNSET[2]}"/></g>

      <text class="out mono" x="50" y="219" font-size="14" fill="{TEXT}">Ali Afzal Yousuf <tspan fill="{SUNSET[0]}">.</tspan> AI Engineer <tspan fill="{SUNSET[0]}">.</tspan> Founder @ Astrameld</text>

      <g mask="url(#m2)">
        <text class="mono" x="50" y="255" font-size="14" textLength="{l2_w}" lengthAdjust="spacing" xml:space="preserve"><tspan fill="{SUNSET[4]}">3liAf@github</tspan><tspan fill="{MUTED}">:</tspan><tspan fill="{SUNSET[2]}">~</tspan><tspan fill="{MUTED}">$ </tspan><tspan fill="{TEXT_BRIGHT}">{l2_cmd}</tspan></text>
      </g>
      <g class="cur cur2"><rect class="blink" x="50" y="243" width="8" height="15" fill="{SUNSET[2]}"/></g>

        {chip_svg}
    </g>
    <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{BORDER}"/>
  </g>
</svg>
'''


# ----------------------------------------------------------- divider .svg ---
def build_divider():
    stops = "".join(
        f'<stop offset="{i * 100 // (len(SUNSET) - 1)}%" stop-color="{c}"/>'
        for i, c in enumerate(SUNSET)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 6" width="880" height="6" role="presentation">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="18%" stop-color="#fff" stop-opacity="1"/>
      <stop offset="82%" stop-color="#fff" stop-opacity="1"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="m"><rect width="880" height="6" fill="url(#fade)"/></mask>
  </defs>
  <rect width="880" height="6" rx="3" fill="url(#g)" mask="url(#m)"/>
</svg>
'''


# ----------------------------------------------------------- avatar .png ----
def build_avatar(path, size=800):
    """Dark 'AY' knocked out of a full-bleed sunset gradient.

    GitHub crops avatars to a circle, so there is no border treatment and the
    lettering sits well inside the inscribed circle -- nothing to clip.
    """
    from PIL import Image, ImageDraw

    def hex2rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    grad = [hex2rgb(c) for c in SUNSET]

    def sample(t):
        t = max(0.0, min(1.0, t)) * (len(grad) - 1)
        i = int(t)
        j = min(i + 1, len(grad) - 1)
        f = t - i
        return tuple(int(grad[i][k] + (grad[j][k] - grad[i][k]) * f) for k in range(3))

    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)

    # diagonal gradient: each anti-diagonal line gets one sampled colour
    for k in range(2 * size):
        d.line([(k, 0), (0, k)], fill=sample(k / (2.0 * size - 1)), width=1)

    # "AY" sized to sit comfortably inside the circular crop
    cells, cols = layout("AY")
    cell = int(size * 0.055)
    dot = int(cell * 0.86)
    ox = int((size - cols * cell) / 2)
    oy = int((size - GLYPH_H * cell) / 2)

    dark = hex2rgb(BG_DEEP)
    for c, r in cells:
        x, y = ox + c * cell, oy + r * cell
        d.rounded_rectangle([x, y, x + dot, y + dot],
                            radius=max(2, dot // 6), fill=dark)

    img.save(path, "PNG", optimize=True)
    return img


# --------------------------------------------------------- banner preview ---
def build_banner_preview(path):
    """Rasterize just the pixel grid so the alignment can actually be eyeballed."""
    from PIL import Image, ImageDraw

    def hex2rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    cells, cols = layout("ALI YOUSUF")
    CELL_W, CELL_H, DOT_W, DOT_H, OX, OY = 11, 17, 9, 15, 50, 64
    img = Image.new("RGB", (880, 200), hex2rgb(BG_DEEP))
    d = ImageDraw.Draw(img)
    grad = [hex2rgb(c) for c in SUNSET]

    def sample(t):
        t = max(0.0, min(1.0, t)) * (len(grad) - 1)
        i = int(t); j = min(i + 1, len(grad) - 1); f = t - i
        return tuple(int(grad[i][k] + (grad[j][k] - grad[i][k]) * f) for k in range(3))

    for c, r in cells:
        x, y = OX + c * CELL_W, OY + r * CELL_H
        d.rounded_rectangle([x, y, x + DOT_W, y + DOT_H], radius=2,
                            fill=sample(c / (cols - 1)))
    img.save(path, "PNG")


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)

    with open(os.path.join(ASSETS, "banner.svg"), "w", encoding="utf-8") as f:
        f.write(build_banner())
    with open(os.path.join(ASSETS, "divider.svg"), "w", encoding="utf-8") as f:
        f.write(build_divider())

    build_avatar(os.path.join(ASSETS, "avatar.png"))

    # Local-only alignment check; never written in CI so it stays out of the repo.
    if os.environ.get("BANNER_PREVIEW"):
        build_banner_preview(os.path.join(ASSETS, "_banner_check.png"))

    print("wrote banner.svg, divider.svg, avatar.png")
