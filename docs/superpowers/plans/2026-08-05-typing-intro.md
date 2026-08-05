# Typing Intro Line — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a looping typewriter intro line above the profile card — four sentences that each type in, hold, delete themselves, and hand off to the next.

**Architecture:** A new generator `scripts/build-intro.py` emits `assets/intro-{dark,light}.svg`, added to `README.md` as a second `<picture>` above the existing card. The palette and font stack move out of `build-card.py` into `scripts/theme.py` so both generators share them. Animation is pure CSS `@keyframes` inside the SVG — GitHub serves these files into an `<img>`, where CSS runs and only scripts are blocked.

**Tech Stack:** Python 3 stdlib only (no Pillow — that is only needed to re-render `art.txt` from a photo). No test framework: this repo has none, and the plan does not add one. Verification is assertion scripts in the scratchpad plus a real-browser check.

**Spec:** `docs/superpowers/specs/2026-08-05-typing-intro-design.md`

## Global Constraints

- Intro SVG width **must equal 1052**, the card's `W`. Mismatch shows as two misaligned blocks on the profile.
- Every sentence `<text>` carries `textLength="{n * CW}"` and `lengthAdjust="spacing"`. Without it `steps(n)` slices glyphs in half on any reader whose monospace font differs from the author's.
- The cursor's `x` steps over the **same** `n * CW` with the **same** `steps(n)` as the clip width — never a percentage.
- `steps(n)` always means `steps(n, jump-end)`, in both the typing and deleting direction.
- Cursor is a `<rect>`, never a glyph. `▌` and `❯` are East-Asian ambiguous width and can fall back to a CJK face at double width.
- `alt` text carries all four sentences as prose. It is the only thing assistive technology sees.
- `@media (prefers-reduced-motion: reduce)` must disable the animation and leave sentence 0 legible.
- Generated files (`assets/*.svg`) are committed but never hand-edited.
- Timing, verbatim: `TYPE = 0.065`, `DEL = 0.035`, `PAUSE = 0.3`, `SLOT = 4.9`, `TOTAL = 19.6`, `BLINK = 1.0` (seconds).
- Geometry, verbatim: `FS = 18`, `CW = 10.8`, `PAD_X = 22`, `PAD_Y = 14`, `BASE = 32`, `H = 52`, `TEXT_X = 43.6`.
- Sentences, verbatim and in order:
  1. `Hi, I'm Manh Loi` (16)
  2. `Software Engineer, Mobile` (25)
  3. `Fintech, payments, wearables` (28)
  4. `5+ years shipping to production` (31)

**Shell setup — every task assumes these:**

```bash
cd /Users/manhloi/Documents/personal_source/manhIoi
SP=/private/tmp/claude-501/-Users-manhloi-Documents-personal-source-manhIoi/ebc0971c-bb96-4f31-8550-b4c955b19a20/scratchpad
```

**Deviation from the spec, already reviewed:** the spec listed `FS`, `LH`, `CW` as living in `theme.py`. They do not. The card is a 14px table and the intro an 18px headline, so type metrics stay local to each generator; `theme.py` holds only the palette, the font stack, and two helpers.

---

### Task 1: Extract `scripts/theme.py` with the card's output unchanged

The refactor must be provably invisible. `assets/card-*.svg` are committed, so `git diff` is the golden reference — no fixture needed.

**Files:**
- Create: `scripts/theme.py`
- Modify: `scripts/build-card.py` (remove lines 18–53 `P`, lines 120–124 `FONTS`, line 118 `CW`, line 170–171 in `render`)
- Test: `$SP/check_card_golden.sh`

**Interfaces:**
- Consumes: nothing.
- Produces: `theme.P` — `dict[str, tuple[str, str]]` mapping colour key to `(dark, light)` hex; `theme.FONTS` — `str`, the CSS font-family list; `theme.pick(theme: str) -> dict[str, str]` flattening `P` for one theme (`"dark"` or `"light"`); `theme.cw(fs: float) -> float` returning one monospace cell advance.

- [ ] **Step 1: Write the golden-output check**

```bash
cat > "$SP/check_card_golden.sh" <<'EOF'
#!/bin/bash
# The theme.py extraction must not change a single byte of the card.
set -euo pipefail
cd /Users/manhloi/Documents/personal_source/manhIoi

out=$(python3 scripts/build-card.py)
echo "generator said: $out"

[[ "$out" == 1052x690* ]] || { echo "FAIL: expected 1052x690, got: $out"; exit 1; }

if ! git diff --quiet -- assets/card-dark.svg assets/card-light.svg; then
  echo "FAIL: card SVGs changed:"
  git diff --stat -- assets/card-dark.svg assets/card-light.svg
  exit 1
fi

python3 -c "
import sys; sys.path.insert(0, 'scripts')
import theme
assert theme.pick('dark')['label'] == '#3fb950', theme.pick('dark')['label']
assert theme.pick('light')['label'] == '#1a7f37', theme.pick('light')['label']
assert abs(theme.cw(18) - 10.8) < 1e-9, theme.cw(18)   # 18*0.6 is not exactly 10.8
assert 'Menlo' in theme.FONTS
print('theme.py OK')
"
echo "PASS"
EOF
chmod +x "$SP/check_card_golden.sh"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `"$SP/check_card_golden.sh"`
Expected: FAIL — `ModuleNotFoundError: No module named 'theme'`. The `1052x690` and `git diff` parts pass already; that is the point, they are the invariant.

- [ ] **Step 3: Create `scripts/theme.py`**

Move `P` and `FONTS` **verbatim** from `build-card.py` — do not retype the hex values.

```python
#!/usr/bin/env python3
"""Palette and font stack shared by every generated SVG in assets/.

This exists as its own module because build-card.py writes both card files at
import time, so a second generator cannot import it without triggering a card
rebuild as a side effect.

Type metrics deliberately do NOT live here. The card is a 14px table and the
intro is an 18px headline, so each generator owns its own sizes; only colour
and the font stack have to agree between the two images, because they sit
adjacent on the profile and a one-hex divergence is visible immediately.
"""

# (dark, light). Brand hues are nudged where the true brand colour would be
# illegible against one of the two backgrounds.
P = {
    "bg":     ("#0d1117", "#ffffff"),
    "border": ("#30363d", "#d0d7de"),
    "art":    ("#c9d1d9", "#24292f"),   # neutral, matches the value colour
    "value":  ("#c9d1d9", "#24292f"),
    "label":  ("#3fb950", "#1a7f37"),   # green in both themes
    "head":   ("#f0f6fc", "#1f2328"),
    "rule":   ("#30363d", "#d8dee4"),
    "dim":    ("#6e7681", "#8c959f"),

    "TypeScript": ("#3178C6", "#2F74C0"),
    "Kotlin":     ("#A277FF", "#7F52FF"),
    "Swift":      ("#F05138", "#D63A22"),
    "JavaScript": ("#F7DF1E", "#9A8700"),
    "React":      ("#61DAFB", "#0B8CA8"),
    "Next.js":    ("#ffffff", "#000000"),
    "Node.js":    ("#6BBF59", "#417E38"),
    "Vue.js":     ("#4FC08D", "#2F8F63"),
    "PostgreSQL": ("#6E8FF0", "#31648C"),
    "MongoDB":    ("#4DB33D", "#2E7D32"),
    "Realm":      ("#8E9AD6", "#39477F"),
    "Compose":    ("#7CB0F7", "#2C5FB3"),
    "SwiftUI":    ("#FF9F6B", "#B34700"),
    "Android":    ("#3DDC84", "#1F8B4C"),
    "watchOS":    ("#d0d7de", "#57606a"),
    "Jenkins":    ("#E8756B", "#B4352A"),
    "Actions":    ("#79C0FF", "#0969DA"),

    "Q.Buzz": ("#38BDF8", "#0369A1"),
    "HDBank": ("#FF6B5E", "#E2231A"),
    "MoMo":   ("#F072B6", "#A50064"),
    "UIT":    ("#79C0FF", "#005BAA"),
}

# Box-drawing glyphs are East-Asian "ambiguous width": a font without them can
# fall back to a CJK face and render them double-width, which would shear the
# portrait. Lead with faces that carry the full set at single-cell width.
FONTS = ("Menlo,'DejaVu Sans Mono','Noto Sans Mono',Consolas,'Cascadia Mono',"
         "ui-monospace,SFMono-Regular,'Liberation Mono','Courier New',monospace")


def pick(theme):
    """Flatten P to a {key: colour} map for one theme ("dark" or "light")."""
    i = 0 if theme == "dark" else 1
    return {k: v[i] for k, v in P.items()}


def cw(fs):
    """Advance width of one monospace cell at font-size fs."""
    return fs * 0.6
```

- [ ] **Step 4: Rewire `scripts/build-card.py`**

Four edits. Delete the moved blocks; do not leave copies behind.

1. After `from html import escape` (line 12), add:

```python
from theme import FONTS, cw, pick
```

2. Delete the whole `# ---- palette ---` block — the comment on lines 18–20 and the `P = {...}` literal, lines 21–53.

3. Replace `CW = FS * 0.6` (line 118) with:

```python
CW = cw(FS)
```

and delete the `FONTS = (...)` assignment with its two-line comment (lines 120–124).

4. In `render`, replace the first two lines:

```python
def render(theme):
    i = 0 if theme == "dark" else 1
    c = {k: v[i] for k, v in P.items()}
```

with:

```python
def render(theme):
    c = pick(theme)
```

`python3 scripts/build-card.py` puts `scripts/` on `sys.path`, so the bare `from theme import` resolves with no package layout.

- [ ] **Step 5: Run the check to verify it passes**

Run: `"$SP/check_card_golden.sh"`
Expected: prints `generator said: 1052x690  art 56 cols ...`, then `theme.py OK`, then `PASS`. An empty `git diff` here is the whole proof: the extraction changed no output.

- [ ] **Step 6: Commit**

```bash
git add scripts/theme.py scripts/build-card.py
git commit -m "Extract the shared palette and font stack into scripts/theme.py"
```

---

### Task 2: Generate the intro SVG, geometry only

Get the file, the dimensions, and the text metrics right with no animation. A static first frame is easier to diagnose than a broken loop.

**Files:**
- Create: `scripts/build-intro.py`, `assets/intro-dark.svg`, `assets/intro-light.svg`
- Test: `$SP/check_intro_geom.py`

**Interfaces:**
- Consumes: `theme.FONTS`, `theme.pick`, `theme.cw` from Task 1.
- Produces: `build_intro.SENTENCES` — `list[str]`, four items; `build_intro.phases(n: int) -> tuple[float, float, float]` returning `(type, hold, delete)` seconds; `build_intro.frames(i: int, n: int) -> list[tuple[float, tuple[float, str | None]]]` returning keyframe offsets in seconds sorted ascending, each mapped to `(clip_width_px, timing_function_or_None)`; module constants `W`, `H`, `FS`, `CW`, `BASE`, `TEXT_X`, `TOTAL`. Task 3 extends this file; Task 4 consumes the two SVGs.

- [ ] **Step 1: Write the failing geometry check**

```bash
cat > "$SP/check_intro_geom.py" <<'PY'
import re, sys, xml.dom.minidom
sys.path.insert(0, "/Users/manhloi/Documents/personal_source/manhIoi/scripts")
import build_intro as B

ROOT = "/Users/manhloi/Documents/personal_source/manhIoi"

# The card's width is the contract; a mismatch shows as two misaligned blocks.
card = open(f"{ROOT}/assets/card-dark.svg").read(200)
card_w = int(re.search(r'width="(\d+)"', card).group(1))
assert B.W == card_w == 1052, (B.W, card_w)
assert (B.H, B.FS, B.BASE) == (52, 18, 32), (B.H, B.FS, B.BASE)
# 18*0.6 == 10.799999999999999, so compare with tolerance, never ==
assert abs(B.CW - 10.8) < 1e-9 and abs(B.TEXT_X - 43.6) < 1e-9, (B.CW, B.TEXT_X)

assert [len(s) for s in B.SENTENCES] == [16, 25, 28, 31], [len(s) for s in B.SENTENCES]
assert B.SENTENCES[0] == "Hi, I'm Manh Loi"
assert B.SENTENCES[3] == "5+ years shipping to production"

# Constant typing speed, fixed slot: the hold absorbs the length difference.
for s in B.SENTENCES:
    t, hold, d = B.phases(len(s))
    assert hold > 0, f"no hold left for {s!r}"
    assert abs(t - len(s) * 0.065) < 1e-9
    assert abs(t + hold + d + 0.3 - 4.9) < 1e-9, (s, t, hold, d)
assert abs(B.TOTAL - 19.6) < 1e-9, B.TOTAL

for theme in ("dark", "light"):
    svg = open(f"{ROOT}/assets/intro-{theme}.svg").read()
    xml.dom.minidom.parseString(svg)          # must be well-formed
    assert f'width="{B.W}"' in svg and f'height="{B.H}"' in svg
    assert svg.count("<text") == 5, svg.count("<text")   # 4 sentences + $ prompt
    assert svg.count("<clipPath") == 4, svg.count("<clipPath")
    # every sentence pinned to n*CW so steps(n) lands on character boundaries
    for s in B.SENTENCES:
        assert f'textLength="{len(s) * B.CW:.2f}"' in svg, s
    assert 'lengthAdjust="spacing"' in svg
    # html.escape turns the apostrophe into &#x27;, not &apos;
    assert "Hi, I&#x27;m Manh Loi" in svg
    # cursor is geometry, never a glyph
    assert "▌" not in svg and "❯" not in svg

d = open(f"{ROOT}/assets/intro-dark.svg").read()
l = open(f"{ROOT}/assets/intro-light.svg").read()
assert "#f0f6fc" in d and "#3fb950" in d, "dark palette missing"
assert "#1f2328" in l and "#1a7f37" in l, "light palette missing"
assert d != l

print("PASS geometry")
PY
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 "$SP/check_intro_geom.py"`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_intro'`.

- [ ] **Step 3: Write `scripts/build-intro.py`**

The check imports it as `build_intro`, so the file also needs an underscore alias. Create the file as `scripts/build_intro.py` and note that `README`/docs refer to it by that name — a hyphen would make it unimportable.

```python
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
from html import escape

from theme import FONTS, cw, pick

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---- content ---------------------------------------------------------------
SENTENCES = [
    "Hi, I'm Manh Loi",
    "Software Engineer, Mobile",
    "Fintech, payments, wearables",
    "5+ years shipping to production",
]
PROMPT = "$ "          # ASCII on purpose: no ambiguous-width fallback risk

# ---- geometry --------------------------------------------------------------
# W is the card's width, not an independent choice. build-card.py prints it.
W = 1052
FS = 18                # a headline, deliberately larger than the card's 14
CW = cw(FS)
PAD_X, PAD_Y = 22, 14  # PAD_X matches the card's PAD so both share a left edge
DESC = 6               # descender allowance below the baseline
BASE = PAD_Y + FS
H = PAD_Y * 2 + FS + DESC
TEXT_X = PAD_X + len(PROMPT) * CW
CARET_Y = BASE - FS + 4

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
    n0 = len(SENTENCES[0])

    css = [
        # Reduced-motion fallback lives in the static attributes, so it needs no
        # override here: killing the animations leaves sentence 0 fully revealed
        # and its cursor parked at the end of the text.
        "@media (prefers-reduced-motion: reduce){"
        ".clip,.caret,.cg{animation:none!important}}"
    ]
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
                f"{pct(o)}%{{x:{TEXT_X + w:.2f}px;"
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
                   f'x="{TEXT_X:.2f}" y="0" width="{w0}" height="{H}"/></clipPath>')
    out.append("  </defs>")
    out.append(f'  <text style="white-space:pre" fill="{c["label"]}" '
               f'x="{PAD_X}" y="{BASE}" textLength="{len(PROMPT) * CW:.2f}" '
               f'lengthAdjust="spacing">{escape(PROMPT)}</text>')
    for i, s in enumerate(SENTENCES):
        n = len(s)
        out.append(f'  <g clip-path="url(#cp{i})">'
                   f'<text style="white-space:pre" fill="{c["head"]}" '
                   f'x="{TEXT_X:.2f}" y="{BASE}" textLength="{n * CW:.2f}" '
                   f'lengthAdjust="spacing">{escape(s)}</text></g>')
        cx = f"{TEXT_X + n * CW:.2f}" if i == 0 else f"{TEXT_X:.2f}"
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
```

- [ ] **Step 4: Run the generator, then the check**

```bash
python3 scripts/build_intro.py
python3 "$SP/check_intro_geom.py"
```

Expected: generator prints `1052x52  4 sentences  longest 31 cols  loop 19.6s`, then `PASS geometry`.

If the `<clipPath>` count assertion trips, print the actual count and reconcile it against the emitted file rather than loosening the assertion — a wrong number of clip paths means sentences share one, which would break the animation in a way Task 4 cannot catch.

**Float note that applies to this whole plan:** `18 * 0.6` is `10.799999999999999`, not `10.8`, so never compare `CW` or anything derived from it with `==`. Formatting through `:.2f` on both sides is safe and is what the generator and the checks both do. The card is unaffected — `14 * 0.6` happens to be exactly `8.4`.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_intro.py assets/intro-dark.svg assets/intro-light.svg
git commit -m "Generate the typing intro SVG pair"
```

---

### Task 3: Verify the CSS timeline is internally consistent

Task 2 emitted the keyframes; nothing has checked that they describe a sane timeline. This task adds no features — it proves the generated CSS before a browser is involved, because a browser will show *something* either way and a subtly wrong timeline looks like a rendering quirk.

**Files:**
- Test: `$SP/check_intro_css.py`
- Modify: `scripts/build_intro.py` only if the check finds a real defect

**Interfaces:**
- Consumes: `build_intro.frames`, `build_intro.SENTENCES`, `build_intro.TOTAL`, `build_intro.CW`, `build_intro.TEXT_X` from Task 2.
- Produces: nothing consumed downstream.

- [ ] **Step 1: Write the timeline check**

```bash
cat > "$SP/check_intro_css.py" <<'PY'
import re, sys
sys.path.insert(0, "/Users/manhloi/Documents/personal_source/manhIoi/scripts")
import build_intro as B

svg = open("/Users/manhloi/Documents/personal_source/manhIoi/assets/intro-dark.svg").read()
css = re.search(r"<style>(.*?)</style>", svg, re.S).group(1)

for i, s in enumerate(B.SENTENCES):
    n, fr = len(s), B.frames(i, n)
    offs = [o for o, _ in fr]
    assert offs == sorted(offs), (i, offs)
    assert offs[0] == 0.0 and abs(offs[-1] - B.TOTAL) < 1e-9, (i, offs)
    # exactly one full-width plateau, and it is the hold
    widths = [w for _, (w, _) in fr]
    assert widths[0] == 0.0 and widths[-1] == 0.0, (i, widths)
    assert max(widths) == n * B.CW, (i, max(widths), n * B.CW)
    # stepping is declared in both directions, with the character count
    assert css.count(f"steps({n}, jump-end)") >= 2, (n, css.count(f"steps({n}, jump-end)"))
    for name in (f"@keyframes clip{i}", f"@keyframes caret{i}", f"@keyframes cg{i}"):
        assert name + "{" in css, name
    # cursor ends where the text ends
    assert f"x:{B.TEXT_X + n * B.CW:.2f}px" in css, (i, B.TEXT_X + n * B.CW)

# slots do not overlap: sentence i is gone before i+1 starts typing
for i, s in enumerate(B.SENTENCES):
    t, hold, d = B.phases(len(s))
    assert i * B.SLOT + t + hold + d <= (i + 1) * B.SLOT + 1e-9, i

assert "prefers-reduced-motion" in css
assert "@keyframes blink{" in css
# percentages stay inside 0..100
for p in re.findall(r"(\d+\.\d+)%\{", css):
    assert 0.0 <= float(p) <= 100.0, p
print("PASS css timeline")
PY
```

- [ ] **Step 2: Run it**

Run: `python3 "$SP/check_intro_css.py"`
Expected: `PASS css timeline`.

If an assertion fails, fix `scripts/build_intro.py` and re-run both this and `check_intro_geom.py` — then regenerate and re-commit the SVGs, since the committed files must match the generator.

- [ ] **Step 3: Commit only if the generator changed**

```bash
git status --short
# if scripts/build_intro.py or assets/intro-*.svg changed:
git add scripts/build_intro.py assets/intro-dark.svg assets/intro-light.svg
git commit -m "Fix the intro keyframe timeline"
```

---

### Task 4: Prove it animates under `<img>` restrictions

`CLAUDE.md`'s Chrome `--screenshot` recipe cannot settle this: one still frame cannot show motion, and opening a `.svg` directly is a *document* context that permits more than `<img>` does. Two screenshots at different delays, through an `<img>`, is the proof.

**Files:**
- Test: `$SP/intro-probe.html`

**Interfaces:**
- Consumes: `assets/intro-dark.svg`, `assets/intro-light.svg` from Task 2.
- Produces: nothing consumed downstream.

- [ ] **Step 1: Build the probe page**

Loading through `<img>` is the whole point — an inline `<svg>` would not reproduce GitHub's restriction.

```bash
cat > "$SP/intro-probe.html" <<'EOF'
<body style="margin:0;background:#0d1117">
<img src="/Users/manhloi/Documents/personal_source/manhIoi/assets/intro-dark.svg">
</body>
EOF
```

- [ ] **Step 2: Capture two frames mid-loop**

Sentence 0 types for 1.04s, so ~0.6s in it is partly typed and ~2.5s in it is fully typed and holding. Those two frames must differ.

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for d in 600 2500; do
  "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --virtual-time-budget=$d --screenshot="$SP/frame-$d.png" \
    --window-size=1052,52 "$SP/intro-probe.html"
done
python3 -c "
import hashlib
a = hashlib.sha256(open('$SP/frame-600.png','rb').read()).hexdigest()
b = hashlib.sha256(open('$SP/frame-2500.png','rb').read()).hexdigest()
print('600ms ', a[:16]); print('2500ms', b[:16])
assert a != b, 'FAIL: identical frames — the animation is not running under <img>'
print('PASS frames differ')
"
```

`--virtual-time-budget` advances the page clock deterministically, so this does not race real time.

- [ ] **Step 3: Look at both frames**

Read `$SP/frame-600.png` and `$SP/frame-2500.png`. Confirm by eye:
- the 600ms frame shows a partial `Hi, I'm Manh Loi`, the 2500ms frame the full sentence
- **no glyph is sliced vertically down its middle** — that is the `textLength`/`steps(n)` failure, and it is the single most likely defect
- the green `$` prompt is present and the cursor sits flush against the last character, not floating past it

If frames are identical, CSS geometry animation is not running in this context. Switch the clip width to the SMIL fallback the spec names — `<animate attributeName="width" calcMode="discrete">` with a generated `values` list — and re-run steps 2 and 3. Do not reach for it before this step has actually failed.

- [ ] **Step 4: Check the light variant too**

```bash
sed -i '' 's/intro-dark/intro-light/; s/#0d1117/#ffffff/' "$SP/intro-probe.html"
"$CHROME" --headless --disable-gpu --hide-scrollbars --virtual-time-budget=2500 \
  --screenshot="$SP/frame-light.png" --window-size=1052,52 "$SP/intro-probe.html"
```

Read `$SP/frame-light.png`. The text must be dark on white and legible — the light palette uses `#1f2328` text with a `#1a7f37` prompt.

- [ ] **Step 5: No commit**

Nothing in the repo changed unless the fallback was needed. If it was, commit as in Task 3 step 3.

---

### Task 5: Wire it into the README and correct `CLAUDE.md`

**Files:**
- Modify: `README.md`, `CLAUDE.md`
- Test: `$SP/check_readme.sh`

**Interfaces:**
- Consumes: `assets/intro-{dark,light}.svg` from Task 2.
- Produces: the shipped profile.

- [ ] **Step 1: Write the render check**

```bash
cat > "$SP/check_readme.sh" <<'EOF'
#!/bin/bash
set -euo pipefail
cd /Users/manhloi/Documents/personal_source/manhIoi

html=$(gh api --method POST /markdown -f mode=markdown -f text="$(cat README.md)")

# GitHub's sanitizer must keep both <picture> blocks
for f in intro-dark intro-light card-dark card-light; do
  grep -q "$f" <<<"$html" || { echo "FAIL: sanitizer dropped $f"; exit 1; }
done
grep -q 'Software Engineer, Mobile' <<<"$html" || { echo "FAIL: alt text missing"; exit 1; }
grep -q 'pl-ii' <<<"$html" && { echo "FAIL: red-background token present"; exit 1; }

# every sentence must be in the alt text, not just some
for s in "Hi, I'm Manh Loi" "Fintech, payments, wearables" "5+ years shipping to production"; do
  grep -qF "$s" <<<"$html" || { echo "FAIL: alt missing: $s"; exit 1; }
done
echo "PASS readme"
EOF
chmod +x "$SP/check_readme.sh"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `"$SP/check_readme.sh"`
Expected: FAIL — `sanitizer dropped intro-dark`, because the README does not reference it yet.

- [ ] **Step 3: Add the intro to `README.md`**

Insert above the existing card block. The intro is unlinked; the card keeps its `<a>`.

```html
<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/intro-dark.svg">
    <img alt="Hi, I'm Manh Loi. Software Engineer, Mobile. Fintech, payments, wearables. 5+ years shipping to production." src="assets/intro-light.svg">
  </picture>
</p>

<a href="https://github.com/manhIoi">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/card-dark.svg">
    <img alt="Pham Manh Loi — Software Engineer, Mobile. HDBank, previously MoMo. React Native, Kotlin, Swift, TypeScript." src="assets/card-light.svg">
  </picture>
</a>
```

- [ ] **Step 4: Run the check to verify it passes**

Run: `"$SP/check_readme.sh"`
Expected: `PASS readme`.

- [ ] **Step 5: Correct `CLAUDE.md`**

Three edits. The Structure section currently claims the README is six lines and that nothing else belongs on the page; shipping this makes that false, and the next session will trust it.

1. Replace the `README.md` and generated-asset bullets:

```markdown
- `README.md` — two `<picture>` blocks: the typing intro line, then the card. Both swap between a dark and a light generated SVG. Nothing else belongs on the profile page; see "What not to add back".
- `assets/card-{dark,light}.svg`, `assets/intro-{dark,light}.svg` — **generated, never hand-edit.**
- `scripts/theme.py` — the palette and font stack, shared by both generators. Type metrics are per-generator: the card is 14px, the intro 18px.
- `scripts/build-card.py` — the card generator. Edit `ROWS` for content, `scripts/theme.py` for colour, then run it.
- `scripts/build_intro.py` — the intro generator. Edit `SENTENCES` or the timing constants, then run it. Underscored, not hyphenated, so it can be imported.
```

2. Replace the build command in "Working in this repo" — there are two generators now:

```sh
python3 scripts/build-card.py && python3 scripts/build_intro.py
```

3. Add to "Things that will bite":

```markdown
- **The intro's `steps(n)` is coupled to `textLength`.** Typing is a clip rect
  whose width steps from 0 to `n * CW`, which only lands on character boundaries
  because each `<text>` is pinned to exactly that width with `textLength` and
  `lengthAdjust="spacing"`. Drop either and the animation slices glyphs in half
  for any reader whose monospace font is not yours — the failure is invisible
  locally. The cursor steps over the same `n * CW`; give it a percentage instead
  and it drifts off the end of the text.
- **A still screenshot cannot verify the intro.** Capture two frames with
  different `--virtual-time-budget` values through an `<img>` tag and check they
  differ. Opening the `.svg` directly is a document context and permits more
  than GitHub's `<img>` does.
```

- [ ] **Step 6: Full regression, then commit**

```bash
"$SP/check_card_golden.sh" && python3 "$SP/check_intro_geom.py" \
  && python3 "$SP/check_intro_css.py" && "$SP/check_readme.sh"
git add README.md CLAUDE.md
git commit -m "Add the typing intro line to the profile README"
```

Expected: all four print `PASS`. Do not commit on a partial pass.

- [ ] **Step 7: Push and confirm on the live profile**

`master` is the default branch and the only one GitHub renders the profile from.

```bash
git push origin master
```

Then open <https://github.com/manhIoi> and watch one full 19.6s loop. Camo caches aggressively, so a stale intro may need a hard reload. Confirm all four sentences appear in order and no glyph is clipped mid-character.

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
|---|---|
| Content — four sentences | 2 (`SENTENCES`), asserted in 2 step 1 |
| Files / rejected structures | 1, 2 |
| Why `theme.py` exists | 1 |
| Geometry — `W` matches card, `FS`, `H`, paddings | 2, asserted against `card-dark.svg` |
| Colours from `theme.py` | 1, 2, asserted per theme in 2 step 1 |
| `textLength` / `steps(n)` coupling | 2 (emit), 3 (assert), 4 step 3 (visual), 5 (document) |
| Timing table, 19.6s loop | 2 (`phases`), 3 (non-overlap assert) |
| Keyframe shape, `jump-end`, CSS-geometry + SMIL fallback | 2, 3, 4 step 3 |
| Cursor as `<rect>`, nested blink/gate | 2, asserted in 2 step 1 and 3 step 1 |
| `alt` with all four sentences | 5, asserted per sentence in 5 step 1 |
| `prefers-reduced-motion` | 2 (static attributes carry the fallback), 3 assert |
| README markup | 5 |
| Verification 1–4 | 1 step 5, 2 step 4, 4, 5 step 4 |
| Documentation | 5 step 5 |

No gaps.

**Placeholder scan:** no `TBD`/`TODO`, no "add error handling", no "similar to Task N". Every code step carries the actual code; the palette in Task 1 is the full literal rather than an instruction to copy it.

**Type consistency:** `pick`/`cw`/`FONTS`/`P` are defined in Task 1 and used under those names in Tasks 1–2. `phases` returns `(type, hold, delete)` and `frames` returns `[(seconds, (width_px, timing|None))]` in Task 2; Task 3 unpacks both in exactly that shape. Module is `build_intro` (underscore) everywhere — in the import, the run command, and `CLAUDE.md`.

**Five defects found and fixed during review**, all by executing the plan's own
assertions against a prototype rather than reading them:

1. The module was `build-intro.py` in the spec, which Python cannot import.
   Task 2 creates `scripts/build_intro.py`; Task 5 documents why.
2. `theme.cw(18) == 10.8` and `B.CW == 10.8` both fail — `18 * 0.6` is
   `10.799999999999999`. Replaced with a `1e-9` tolerance.
3. `svg.count("<text") == 4` was wrong: there are **five** `<text>` elements,
   because the `$` prompt is its own unclipped one.
4. `svg.count("clipPath") == 5` was wrong twice over — the string occurs 8 times
   (open and close tags), and `clip-path="url(...)"` does not match it at all,
   being hyphenated and lowercase. Now `count("<clipPath") == 4`.
5. `html.escape` produces `&#x27;`, not `&apos;`, so the apostrophe assertion
   could never have passed.

Keyframe offsets were checked for all four sentences: monotonic, first at `0.0`,
last at `TOTAL`, every percentage inside `0..100`, and sentence `i` fully gone
before `i+1` begins. Sentence 0 emits 5 keyframes, the rest 6.

**Unused variable:** Task 2's `gate_off` is always `0.0`; it is kept as a named read of `frames()[0][0]` rather than a bare literal so the gate and the clip cannot drift apart. Harmless.
