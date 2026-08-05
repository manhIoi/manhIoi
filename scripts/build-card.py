#!/usr/bin/env python3
"""Render the profile card to assets/card-dark.svg and assets/card-light.svg.

Every glyph is a positioned <tspan> with an explicit fill, which is the only way
to colour text per word on a GitHub profile — a fenced code block colours by
syntactic role, so all language names necessarily share one colour.

Alignment does not depend on the reader's monospace metrics: each tspan carries
its own x and textLength.
"""
import os
from html import escape

from theme import FONTS, cw, pick

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ART_SRC = os.path.join(HERE, "art.txt")

# ---- content ---------------------------------------------------------------
# Each row is a list of (text, colour-key) segments. "gap" is a blank line.
def L(label, *value):
    return [(" . ", "dim"), (label, "label"), (": ", "dim"), *value]

def dots(n):
    return ("." * n + " ", "rule")

ROWS = [
    [("manhIoi@github ", "head"), ("─" * 46, "rule")],
    L("Name",       dots(13), ("Pham Manh Loi", "value")),
    L("Role",       dots(13), ("Software Engineer, Mobile", "value")),
    L("Focus",      dots(12), ("Fintech, payments, wearables", "value")),
    L("Location",   dots(9),  ("Vietnam", "value")),
    L("Speaks",     dots(11), ("Vietnamese, English", "value")),
    L("Uptime",     dots(11), ("5+ years in production", "value")),
    "gap",
    [("─ Stack ", "head"), ("─" * 45, "rule")],
    L("Mobile",  dots(11), ("React Native", "React"), (", ", "value"),
                           ("Kotlin", "Kotlin"), (", ", "value"), ("Swift", "Swift")),
    L("Native",  dots(11), ("Compose", "Compose"), (", ", "value"),
                           ("SwiftUI", "SwiftUI"), (", ", "value"),
                           ("Android", "Android"), (", ", "value"), ("watchOS", "watchOS")),
    L("Web",     dots(14), ("TypeScript", "TypeScript"), (", ", "value"),
                           ("React", "React"), (", ", "value"),
                           ("Next.js", "Next.js"), (", ", "value"), ("Vue.js", "Vue.js")),
    L("Runtime", dots(10), ("Node.js", "Node.js"), (", ", "value"),
                           ("JavaScript", "JavaScript")),
    L("Data",    dots(13), ("PostgreSQL", "PostgreSQL"), (", ", "value"),
                           ("MongoDB", "MongoDB"), (", ", "value"), ("Realm", "Realm")),
    L("CI/CD",   dots(12), ("GitHub Actions", "Actions"), (", ", "value"),
                           ("Jenkins", "Jenkins")),
    "gap",
    [("─ Timeline ", "head"), ("─" * 42, "rule")],
    [("   ● ", "HDBank"), ("HDBank", "HDBank"),
     ("  Mobile Developer", "value"), ("        2026.02 → now", "dim")],
    [("   │ ", "rule"), ("Mobile banking and payment platform", "dim")],
    [("   ● ", "Q.Buzz"), ("Q.Buzz", "Q.Buzz"),
     ("  Mobile Developer", "value"), ("        2026.01 → now", "dim")],
    [("   │ ", "rule"), ("Daily habit tracking, health insights", "dim")],
    [("   ● ", "MoMo"), ("MoMo", "MoMo"), ("  Mobile Developer", "value"),
     ("          2021 → 2026.01", "dim")],
    [("     ", "rule"), ("Super-app, e-wallet, wearable payments", "dim")],
    "gap",
    [("─ Education ", "head"), ("─" * 41, "rule")],
    [("   ● ", "UIT"), ("UIT", "UIT"), ("  Information Technology", "value"),
     ("  2019 → 2024", "dim")],
    "gap",
    [("─ Contact ", "head"), ("─" * 43, "rule")],
    L("Email",     dots(12), ("manhloi0505@gmail.com", "value")),
    L("LinkedIn",  dots(9),  ("loi-pham-manh", "value")),
    L("GitHub",    dots(11), ("manhIoi", "value")),
    L("Facebook",  dots(9),  ("manhloi551", "value")),
    L("Instagram", dots(8),  ("p.manhloi", "value")),
    L("Phone",     dots(12), ("+84 792 465 841", "value")),
]

# ---- geometry --------------------------------------------------------------
FS, LH, PAD = 14, 19, 22
# Block glyphs fill their em box, so at the panel's 19px leading they leave a gap
# between rows and the portrait breaks up into horizontal bars. Pack the art rows
# tight enough that the blocks meet.
ART_LH = 16
CW = cw(FS)
GAP = 3 * CW

# Ink density reads as *darkness* on a light background but as *brightness* on a
# dark one, so the one portrait has to be tone-flipped for the dark theme or the
# cat's mouth — its darkest feature — comes out as the brightest thing on it.
#
# The flip is by measured ink coverage, not by a hand-written ramp: the art also
# contains stray letters and punctuation (`Ü`, `@`, `D`, `»`) whose weight is not
# obvious by eye, and lumping them all at one end wipes out small dark features.
# The eyes are two such glyphs, and they vanished when this was a guess.
INK = {" ": 0.000, "`": 0.022, "'": 0.042, ".": 0.043, ",": 0.063, "-": 0.065,
       "\u00b2": 0.071, "_": 0.075, ":": 0.077, "!": 0.082, "\u2310": 0.083,
       '"': 0.083, "\u250c": 0.095, "\u00bb": 0.096, ";": 0.097, "\u2514": 0.108,
       "|": 0.113, "[": 0.130, "]": 0.130, "=": 0.130, "j": 0.149, "\u2591": 0.152,
       "\u00fb": 0.194, "H": 0.226, "\u00dc": 0.231, "D": 0.236, "R": 0.242,
       "@": 0.258, "\u2592": 0.410, "\u2593": 0.661, "\u2588": 0.825}
OUT = " .:\u2591\u2592\u2593\u2588"          # what the flipped art is drawn with
MAX = max(INK.values())
# A straight inversion leaves small dark features barely below the surrounding
# fur — the eyes came out a shade off the coat and read as nothing. Pushing the
# dark end down separates them without hollowing out the body.
FLIP_GAMMA = 1.4


def flip_tone(line):
    out = []
    for ch in line:
        if ch == " ":
            out.append(" ")                     # background stays background
            continue
        want = MAX * ((MAX - INK.get(ch, MAX / 2)) / MAX) ** FLIP_GAMMA
        out.append(min(OUT, key=lambda o: abs(INK[o] - want)))
    return "".join(out)


_art = open(ART_SRC).read().rstrip("\n").split("\n")
_w = max(len(a) for a in _art)
ARTS = {"light": [a.ljust(_w) for a in _art],
        "dark":  [flip_tone(a.ljust(_w)) for a in _art]}
AW = _w
PW = max(sum(len(t) for t, _ in r) for r in ROWS if r != "gap")
W = round(PAD * 2 + AW * CW + GAP + PW * CW)
H = round(PAD * 2 + max(max(map(len, ARTS.values())), len(ROWS)) * LH)


def render(theme):
    c = pick(theme)
    ART = ARTS[theme]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="{FONTS}" font-size="{FS}">',
           f'  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
           f'fill="{c["bg"]}" stroke="{c["border"]}"/>']
    y0 = PAD + FS
    art_h = len(ART) * ART_LH
    ay = PAD + FS + max(0, (len(ROWS) * LH - art_h) // 2)
    for n, line in enumerate(ART):
        if line.strip():
            out.append(
                f'  <text style="white-space:pre" fill="{c["art"]}" x="{PAD}" '
                f'y="{ay + n*ART_LH}" textLength="{len(line)*CW:.2f}" '
                f'lengthAdjust="spacing">{escape(line)}</text>')
    x0 = AW + 3
    for n, row in enumerate(ROWS):
        if row == "gap":
            continue
        col, spans = x0, []
        for text, key in row:
            spans.append(
                f'<tspan fill="{c[key]}" x="{PAD + col*CW:.2f}" '
                f'textLength="{len(text)*CW:.2f}" lengthAdjust="spacing">'
                f'{escape(text)}</tspan>')
            col += len(text)
        out.append(f'  <text style="white-space:pre" y="{y0 + n*LH}">'
                   f'{"".join(spans)}</text>')
    out.append("</svg>")
    return "\n".join(out)


for t in ("dark", "light"):
    with open(os.path.join(ROOT, "assets", f"card-{t}.svg"), "w") as f:
        f.write(render(t))
print(f"{W}x{H}  art {AW} cols  "
      f"{{{', '.join(f'{t}:{len(a)}' for t, a in ARTS.items())}}} rows  "
      f"panel {PW} cols  {len(ROWS)} rows")
