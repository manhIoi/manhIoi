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
#
# Rows are not centred one by one. Centring each row independently is what the
# eye reads as *lost* symmetry: rows differ in length, so the label column lands
# somewhere new on every line and both edges come out as a zigzag. Instead the
# whole panel is one block, centred on the card, with the labels right-aligned so
# every colon falls on the same column. That single vertical axis is what makes it
# read as symmetrical, and right-aligning is also what keeps it gapless — the
# label always ends flush against its colon, so there is nothing for a dotted
# leader to span.
LABELS = ["Name", "Role", "Domain",
          "Mobile", "Web", "Backend", "Database", "CI/CD",
          "Email", "LinkedIn", "GitHub", "Phone", "Location"]
LW = max(map(len, LABELS))          # the colon column


def L(label, *value):
    assert label in LABELS, label    # LW has to cover every label used
    return [(label.rjust(LW), "label"), (": ", "dim"), *value]


# Timeline and education entries. Names are padded to a common width so the roles
# and the dates line up down the card too, on the same principle as the colons.
ORGS = ["HDBank", "Q.Buzz", "MoMo", "UIT"]
NW = max(map(len, ORGS))


def T(org, role, when):
    return [(" ● ", org), (org.ljust(NW), org), ("  ", "value"),
            (role, "value"), ("  ", "value"), (when, "dim")]


def sub(text, bar=True):
    return [(" │ " if bar else "   ", "rule"), (text, "dim")]


def H(title):
    """A section heading, expanded once the panel width is known.

    Kept as a marker rather than a literal row because the rule has to be split
    around the title to centre it, and how many dashes that takes depends on the
    panel width, which is measured from the content rows below.
    """
    return ("hdr", title)


def _is_hdr(r):
    return isinstance(r, tuple) and len(r) == 2 and r[0] == "hdr"

ROWS = [
    H("manhIoi@github"),
    L("Name",   ("Pham Manh Loi", "value")),
    L("Role",   ("Software Engineer, Mobile", "value")),
    L("Domain", ("Fintech, health tracking", "value")),
    "gap",
    H("Stack"),
    L("Mobile",   ("React Native", "React"), (", ", "value"),
                  ("Kotlin", "Kotlin"), (", ", "value"), ("Swift", "Swift")),
    L("Web",      ("TypeScript", "TypeScript"), (", ", "value"),
                  ("React", "React"), (", ", "value"),
                  ("Next.js", "Next.js"), (", ", "value"), ("Vue.js", "Vue.js")),
    L("Backend",  ("Node.js", "Node.js"), (", ", "value"), (".NET", ".NET")),
    L("Database", ("PostgreSQL", "PostgreSQL"), (", ", "value"),
                  ("MongoDB", "MongoDB")),
    L("CI/CD",    ("GitHub Actions", "Actions"), (", ", "value"),
                  ("Jenkins", "Jenkins")),
    "gap",
    H("Timeline"),
    T("HDBank", "Mobile Developer", "2026.02 → now"),
    sub("Mobile banking and payment platform"),
    T("Q.Buzz", "Mobile Developer", "2026.01 → now"),
    sub("Daily habit tracking, health insights"),
    T("MoMo", "Mobile Developer", "2021 → 2026.01"),
    sub("Super-app, e-wallet, wearable payments", bar=False),
    "gap",
    H("Education"),
    T("UIT", "Information Technology", "2019 → 2024"),
    "gap",
    H("Contact"),
    L("Email",    ("manhloi0505@gmail.com", "value")),
    L("LinkedIn", ("loi-pham-manh", "value")),
    L("GitHub",   ("manhIoi", "value")),
    L("Phone",    ("+84 792 465 841", "value")),
    L("Location", ("Vietnam", "value")),
]

# ---- geometry --------------------------------------------------------------
# The panel is 18px, not 14px, and that is a width decision rather than a taste
# one. GitHub caps the README column at ~830px, so a card wider than that is
# scaled down to fit and the reader sees FS * 830/W, never FS. Because W grows in
# proportion to FS, raising the font size alone cancels itself out exactly — the
# ceiling is 830/(0.6 * columns), so the only way to make the text bigger is to
# use fewer character columns. Hence the stacked layout below: side by side the
# card was 120 columns wide (56 of portrait + 3 + 61 of panel) and this same 14px
# type arrived as ~11px. Stacked it is 61 columns and 556px wide, comfortably
# under the cap, so 14px arrives as 14px — the size it was authored for.
FS, LH, PAD = 14, 19, 22
# The portrait keeps the smaller type it was drawn for. It does not need to match
# the panel — a bigger portrait would only add height, and stacking already costs
# plenty of that.
ART_FS = 14
ART_CW = cw(ART_FS)
# Block glyphs fill their em box, so at the panel's leading they leave a gap
# between rows and the portrait breaks up into horizontal bars. Pack the art rows
# tight enough that the blocks meet.
ART_LH = 16
CW = cw(FS)
VGAP = 18                  # breathing room between the portrait and the panel
HEAD_GAP = 8               # extra room under a section heading, see _baselines

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
AH = max(map(len, ARTS.values()))


def _row_cols(r):
    return sum(len(t) for t, _ in r)


def _is_rule(r):
    """An expanded section header: a row that ends in a run of box-drawing."""
    return (r != "gap" and bool(r) and not _is_hdr(r)
            and r[-1][1] == "rule" and set(r[-1][0]) == {"─"})


# Measured over content rows only, so the dividers take their length from the
# content instead of the content being sized to fit a divider chosen by hand.
CONTENT_W = max(_row_cols(r) for r in ROWS
                if r != "gap" and not _is_hdr(r) and not _is_rule(r))


def _expand_headers(rows, target):
    """Split each heading's rule around its title, so the title sits centred.

    The odd dash goes to the right side, so a title that cannot be centred
    exactly is off by half a cell rather than a whole one.
    """
    out = []
    for r in rows:
        if _is_hdr(r):
            title = r[1]
            dashes = target - len(title) - 2      # two spaces flanking the title
            left = dashes // 2
            r = [("─" * left, "rule"), (" ", "rule"), (title, "head"),
                 (" ", "rule"), ("─" * (dashes - left), "rule")]
        out.append(r)
    return out


# Stacked, so width is whichever block is wider rather than the sum of both.
INNER = max(AW * ART_CW, CONTENT_W * CW)
W = round(PAD * 2 + INNER)
# Dividers span exactly the content block, so the panel reads as one rectangle
# with the section headers bracketing it. The portrait above is wider, and that is
# fine — both are centred on the same axis.
PW = CONTENT_W
ROWS = _expand_headers(ROWS, PW)
# Left edge shared by every panel row, which centres the block as a whole.
PANEL_X = (W - PW * CW) / 2


def _baselines(rows):
    """Baseline offset per row, and the panel's total advance.

    Not a flat n * LH. A heading's rule sits on the same baseline as its title, so
    at plain leading it crowds the first line of its section — the rule and the
    text below it end up closer than two lines of body text are. HEAD_GAP buys that
    line some room without opening a full blank line, which would space the heading
    as far from its own section as from the one above.
    """
    ys, y = [], 0
    for r in rows:
        if r == "gap":
            ys.append(None)
            y += LH
            continue
        ys.append(y)
        y += LH + (HEAD_GAP if _is_rule(r) else 0)
    return ys, y


ROW_Y, PANEL_H = _baselines(ROWS)
H = round(PAD * 2 + AH * ART_LH + VGAP + PANEL_H)


def render(theme):
    c = pick(theme)
    ART = ARTS[theme]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="{FONTS}" font-size="{FS}">',
           # No stroke: the border read as a box drawn around the card with the
           # intro line stranded outside it. The fill stays, and it has to — a
           # reader whose GitHub theme is Dark while their OS is Light gets the
           # light card on a dark page, and only an opaque background keeps the
           # dark text on it legible.
           f'  <rect width="{W}" height="{H}" rx="10" fill="{c["bg"]}"/>']
    # Portrait on top, centred: it keeps its smaller type so it is narrower than
    # the panel that sets the card's width.
    ax = (W - AW * ART_CW) / 2
    ay = PAD + ART_FS
    for n, line in enumerate(ART):
        if line.strip():
            out.append(
                f'  <text style="white-space:pre" font-size="{ART_FS}" '
                f'fill="{c["art"]}" x="{ax:.2f}" '
                f'y="{ay + n*ART_LH}" textLength="{len(line)*ART_CW:.2f}" '
                f'lengthAdjust="spacing">{escape(line)}</text>')
    y0 = PAD + AH * ART_LH + VGAP + FS
    for n, row in enumerate(ROWS):
        if row == "gap":
            continue
        # One shared left edge for every row: the panel is a single centred block,
        # not a stack of independently centred lines. The alignment inside it — the
        # colon column, the padded org names — is what carries the symmetry.
        x = PANEL_X
        spans = []
        for text, key in row:
            spans.append(
                f'<tspan fill="{c[key]}" x="{x:.2f}" '
                f'textLength="{len(text)*CW:.2f}" lengthAdjust="spacing">'
                f'{escape(text)}</tspan>')
            x += len(text) * CW
        out.append(f'  <text style="white-space:pre" y="{y0 + ROW_Y[n]}">'
                   f'{"".join(spans)}</text>')
    out.append("</svg>")
    return "\n".join(out)


for t in ("dark", "light"):
    with open(os.path.join(ROOT, "assets", f"card-{t}.svg"), "w") as f:
        f.write(render(t))
print(f"{W}x{H}  art {AW} cols  "
      f"{{{', '.join(f'{t}:{len(a)}' for t, a in ARTS.items())}}} rows  "
      f"panel {PW} cols  {len(ROWS)} rows")
