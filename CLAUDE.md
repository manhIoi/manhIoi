# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is `manhIoi/manhIoi` — a GitHub profile repository. Its sole purpose is to render the profile README shown on https://github.com/manhIoi. There is no application code, linter, or test suite here. The default branch is **`master`**; GitHub only renders the profile from the default branch.

## Structure

- `README.md` — six lines: a `<picture>` that swaps between two generated SVGs. Do not put anything else on the profile page; see "What not to add back".
- `assets/card-dark.svg`, `assets/card-light.svg` — **generated, never hand-edit.**
- `scripts/build-card.py` — the generator. Edit `P` (palette) or `ROWS` (content) and run `python3 scripts/build-card.py`. Needs Pillow only if `art.txt` is being re-rendered from a photo; the build itself is stdlib.
- `scripts/art.txt` — the ASCII portrait. Authored for a light background; the dark variant is derived from it at build time.
- `AGENTS.md` — stale inherited boilerplate describing a `skills/` layout that does not exist here. Ignore it.

## Working in this repo

Regenerate and eyeball in a real browser — the SVG uses `textLength`, which macOS QuickLook (`qlmanage`) gets wrong, so it is not a valid preview:

```sh
python3 scripts/build-card.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --screenshot=out.png --window-size=1027,690 assets/card-dark.svg
```

### Why an SVG and not a code block

A fenced code block keeps the text selectable, and that was the goal for six
iterations. It cannot do what the profile now asks for. A highlighter colours by
**syntactic role, not by word**: `TypeScript` and `Kotlin` are the same token
type, so they always get the same colour. About twenty grammars were tested; the
best any managed was three slots (`css`: grey block-comment art, one coloured
selector, grey comment value). Per-language brand colours, a timeline with
coloured nodes, and colours that do not shift with the reader's theme are all out
of reach there.

Writing each word as a `<tspan fill="…">` buys all of that. It costs the text:
an SVG in an `<img>` cannot be selected, copied, or read by a screen reader —
the `alt` text is the only thing assistive tech sees, so keep it accurate.

The git history holds the code-block version if that trade ever needs revisiting.

### Things that will bite

- **The dark portrait is the light one with its tones flipped**, done in
  `flip_tone` at build time — not a second drawing. Two details in there are
  easy to get wrong and both cost a feature: the flip works off `INK`, the
  *measured* coverage of every glyph the art uses, because the art mixes shade
  blocks with stray letters and punctuation (`Ü`, `@`, `D`, `»`) whose weight is
  not guessable — an early version lumped them all at the dense end and the eyes
  disappeared. And `FLIP_GAMMA` pushes the dark end down, because a straight
  inversion left the eyes one shade off the surrounding fur and they read as
  nothing. Ink density reads as
  *darkness* on white but as *brightness* on black, so shipping one file to both
  themes renders the cat's mouth, its darkest feature, as the brightest thing on
  the card. Flipping the `SHADE` ramp in place (spaces stay background) keeps
  both themes showing the same drawing. Redrawing the dark side from the source
  photo instead was tried and rejected — it produced a visibly different, much
  sparser cat.
- **The art needs a tighter leading than the panel** (`ART_LH`, 16px against the
  panel's 19px). Block glyphs fill their em box, so at the panel's leading they
  leave a gap between rows and the portrait breaks into horizontal bars.
- **Alignment must not depend on the reader's font.** Every `<tspan>` carries its
  own `x` and `textLength`, so columns hold even where the monospace metrics
  differ. Keep that if you touch the renderer.
- **`white-space:pre` goes on each `<text>` as an inline style.** Relying on
  `xml:space="preserve"` alone silently collapsed runs of spaces in Chrome and
  smeared the art across the full line width.
- **Colour is authored, so contrast is now your problem.** GitHub no longer
  picks it. Several brand hues are illegible on one of the two backgrounds, so
  `P` stores `(dark, light)` pairs — JavaScript yellow becomes `#9A8700` on
  white, React cyan becomes `#0B8CA8`, Next.js flips black/white.
- **Theme switching follows the OS, not GitHub.** `prefers-color-scheme` is a
  browser media query; GitHub's own theme picker cannot change what it reports.
  A reader whose GitHub theme is set explicitly to Dark while their OS is Light
  gets the light card on a dark page. Only "Sync with system" matches. Nothing in
  this repo can fix that — it is inherent to `<picture>`.

### What not to add back

- **A contribution graph.** GitHub renders the contribution calendar and "Contribution activity" list natively on the profile page, directly under the README — it cannot be removed and every visitor sees it. Third-party widgets (`ghchart.rshah.org`, `streak-stats.demolab.com`) only see *public* contributions, so for this account they render near-empty (~16) against a real count in the hundreds. Adding one makes the profile look less active, not more.
- **`github-readme-stats.vercel.app` cards.** Returned 503 for every username when last checked — a broken image on the profile. Re-verify with `curl -o /dev/null -w '%{http_code}'` before ever re-adding.
- **A `## Connect` section.** The contacts are already in the card's `Contact` block. It was removed as a duplicate.
- **HTML/CSS for colour.** GitHub's sanitizer strips `style` and `class`
  attributes and `<font>` tags, and escapes `<style>` blocks into visible text.
  Verified against the Markdown API — there is no colour control through HTML.
