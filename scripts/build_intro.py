#!/usr/bin/env python3
"""Render the typing intro to assets/intro-dark.svg and assets/intro-light.svg.

Four sentences take turns: each types in, holds, deletes itself, and the next
follows, looping forever. The animation is pure CSS inside the SVG, which is
what makes it work on a profile: GitHub serves these files into an <img>, where
stylesheets run and only scripts are blocked. Commit 6206668 proved the same
code path with a third-party service before this repo generated its own.

Typing is a clip rect whose width steps from 0 to n*CW. That only lands on
character boundaries if the text is exactly n*CW wide, which is why every <text>
carries textLength and lengthAdjust="spacing" — without them the animation
slices a glyph in half on any reader whose monospace font is not the author's.
The cursor steps over the same n*CW with the same steps(n), so it cannot drift
off the end of the text.
"""
import os
import re
from html import escape

from theme import FONTS, cw, pick

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _card_width():
    """The card's width, read from the card itself.

    The two images sit one above the other on the profile, so a width mismatch
    shows up twice: as misaligned blocks, and as different apparent text sizes,
    since GitHub scales each image to the README column independently. Reading it
    from the generated card rather than repeating the number means editing ROWS
    can never silently desynchronise them — build the card first, which is the
    order CLAUDE.md documents.
    """
    card = os.path.join(ROOT, "assets", "card-dark.svg")
    with open(card) as f:
        head = f.read(300)
    m = re.search(r'width="(\d+)"', head)
    if not m:
        raise SystemExit(f"cannot read a width from {card}; run build-card.py first")
    return int(m.group(1))

# ---- content ---------------------------------------------------------------
SENTENCES = [
    "Hi, I'm Manh Loi",
    "Software Engineer, Mobile",
    "Fintech, payments, wearables",
    "5+ years shipping to production",
]
PROMPT = "$ "          # ASCII on purpose: no ambiguous-width fallback risk

# ---- geometry --------------------------------------------------------------
# W is the card's width, not an independent choice.
W = _card_width()
FS = 18                # a headline, deliberately larger than the card's 14
CW = cw(FS)
PAD_Y = 14
DESC = 6               # descender allowance below the baseline
BASE = PAD_Y + FS
H = PAD_Y * 2 + FS + DESC
CARET_Y = BASE - FS + 4

# Each sentence is centred on its own, so a block of prompt + text + cursor sits
# in the middle of the card whatever the sentence's length. The prompt therefore
# has to move between sentences. It moves on the slot boundary, which is the
# moment the previous line has just finished deleting itself, so the only things
# on screen when it hops are the prompt and its cursor.
#
# The +1 is the cursor: it parks in the cell after the last character, so leaving
# it out of the measurement pushes the line half a character right of centre.
START = [(W - (len(PROMPT) + len(s) + 1) * CW) / 2 for s in SENTENCES]
TEXT_X = [x + len(PROMPT) * CW for x in START]

# ---- timing (seconds) ------------------------------------------------------
TYPE, DEL, PAUSE, SLOT = 0.065, 0.035, 0.3, 4.9
TOTAL = SLOT * len(SENTENCES)
BLINK = 1.0


def phases(n):
    """(type, hold, delete) for an n-character sentence.

    Typing speed is constant, so the hold absorbs the difference in sentence
    length and every sentence occupies the same SLOT. Equal slots are what keep
    the keyframe percentages clean.
    """
    t, d = n * TYPE, n * DEL
    return t, SLOT - PAUSE - t - d, d


for _s in SENTENCES:
    assert phases(len(_s))[1] > 0, f"too long for a {SLOT}s slot: {_s!r}"


def frames(i, n):
    """Keyframe offsets in seconds -> (clip width px, timing function or None).

    Both the clip width and the cursor x are driven from this one table, so they
    are stepped identically and cannot fall out of sync.
    """
    s = i * SLOT
    t, hold, d = phases(n)
    end = n * CW
    step = f"steps({n}, jump-end)"
    f = {0.0: (0.0, None), TOTAL: (0.0, None)}
    f[s] = (0.0, step)                      # start typing
    f[s + t] = (end, None)                  # typed; hold
    f[s + t + hold] = (end, step)           # start deleting
    f[s + t + hold + d] = (0.0, None)       # gone; pause to end of slot
    return sorted(f.items())


def pct(t):
    return f"{t / TOTAL * 100:.4f}"


def render(theme):
    c = pick(theme)

    css = [
        # Reduced-motion fallback lives in the static attributes, so it needs no
        # override here: killing the animations leaves sentence 0 fully revealed,
        # its cursor parked at the end of the text, and the prompt at sentence 0's
        # centred position.
        "@media (prefers-reduced-motion: reduce){"
        ".clip,.caret,.cg,.pg{animation:none!important}}"
    ]
    # The prompt steps between the four centred positions. It is a <text>, and x
    # is not a CSS geometry property there (unlike on the caret's <rect>), so this
    # has to be a transform.
    css.append(
        f"#pg{{animation:pg {TOTAL}s steps(1,jump-end) infinite}}"
        f"@keyframes pg{{"
        + "".join(f"{pct(i * SLOT)}%{{transform:translateX({x - START[0]:.2f}px)}}"
                  for i, x in enumerate(START))
        + f"100%{{transform:translateX({START[-1] - START[0]:.2f}px)}}}}")
    for i, s in enumerate(SENTENCES):
        n = len(s)
        fr = frames(i, n)
        css.append(
            f"#clip{i}{{animation:clip{i} {TOTAL}s linear infinite}}"
            f"@keyframes clip{i}{{"
            + "".join(
                f"{pct(o)}%{{width:{w:.2f}px;"
                + (f"animation-timing-function:{tf};" if tf else "")
                + "}"
                for o, (w, tf) in fr)
            + "}")
        css.append(
            f"#caret{i}{{animation:caret{i} {TOTAL}s linear infinite,"
            f"blink {BLINK}s steps(1,jump-end) infinite}}"
            f"@keyframes caret{i}{{"
            + "".join(
                f"{pct(o)}%{{x:{TEXT_X[i] + w:.2f}px;"
                + (f"animation-timing-function:{tf};" if tf else "")
                + "}"
                for o, (w, tf) in fr)
            + "}")
        # Slot gating sits on an outer <g> so it never competes with the blink
        # for the opacity property on the same element.
        gate_off, gate_on = fr[0][0], i * SLOT
        gone = i * SLOT + sum(phases(n)[:3])
        css.append(
            f"#cg{i}{{animation:cg{i} {TOTAL}s steps(1,jump-end) infinite}}"
            f"@keyframes cg{i}{{"
            f"{pct(gate_off)}%{{opacity:0}}"
            f"{pct(gate_on)}%{{opacity:1}}"
            f"{pct(gone)}%{{opacity:0}}"
            f"100%{{opacity:0}}}}")
    css.append("@keyframes blink{0%{opacity:1}50%{opacity:0}}")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONTS}" font-size="{FS}">',
        f'  <style>{"".join(css)}</style>',
        "  <defs>",
    ]
    for i, s in enumerate(SENTENCES):
        # Static width is the reduced-motion state: sentence 0 fully revealed,
        # the rest collapsed so they cannot overlap it.
        w0 = f"{len(s) * CW:.2f}" if i == 0 else "0"
        out.append(f'    <clipPath id="cp{i}"><rect id="clip{i}" class="clip" '
                   f'x="{TEXT_X[i]:.2f}" y="0" width="{w0}" height="{H}"/></clipPath>')
    out.append("  </defs>")
    out.append(f'  <g id="pg" class="pg">'
               f'<text style="white-space:pre" fill="{c["label"]}" '
               f'x="{START[0]:.2f}" y="{BASE}" textLength="{len(PROMPT) * CW:.2f}" '
               f'lengthAdjust="spacing">{escape(PROMPT)}</text></g>')
    for i, s in enumerate(SENTENCES):
        n = len(s)
        out.append(f'  <g clip-path="url(#cp{i})">'
                   f'<text style="white-space:pre" fill="{c["head"]}" '
                   f'x="{TEXT_X[i]:.2f}" y="{BASE}" textLength="{n * CW:.2f}" '
                   f'lengthAdjust="spacing">{escape(s)}</text></g>')
        cx = f"{TEXT_X[i] + n * CW:.2f}" if i == 0 else f"{TEXT_X[i]:.2f}"
        op = "1" if i == 0 else "0"
        out.append(f'  <g id="cg{i}" class="cg" opacity="{op}">'
                   f'<rect id="caret{i}" class="caret" x="{cx}" y="{CARET_Y}" '
                   f'width="{CW:.2f}" height="{FS}" fill="{c["label"]}" '
                   f'shape-rendering="crispEdges"/></g>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    for t in ("dark", "light"):
        with open(os.path.join(ROOT, "assets", f"intro-{t}.svg"), "w") as f:
            f.write(render(t))
    print(f"{W}x{H}  {len(SENTENCES)} sentences  "
          f"longest {max(map(len, SENTENCES))} cols  loop {TOTAL:g}s")
