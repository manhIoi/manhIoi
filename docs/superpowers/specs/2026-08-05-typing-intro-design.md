# Typing intro line for the profile README

**Date:** 2026-08-05
**Repo:** `manhIoi/manhIoi` (GitHub profile README, default branch `master`)

## Goal

Add a one-line self-introduction above the existing neofetch card, animated as a
typewriter: each sentence types in, holds, deletes itself, and the next one
follows. Four sentences, looping forever.

## Why not the third-party service

Commit `6206668` shipped exactly this feature through
`readme-typing-svg.demolab.com` and it worked — an external URL behind GitHub's
Camo proxy, rendered in an `<img>`. It was dropped at `e48695f` when the README
was rebuilt as the ASCII card.

It is not coming back. `CLAUDE.md` already records the cost of depending on a
third-party image host: `github-readme-stats.vercel.app` returned 503 for every
username, which on a profile page is a broken image with no fallback. The repo
already generates its own SVGs, so the same result is available with no runtime
dependency on anyone else's uptime.

`6206668` is still useful as evidence, though: it proves CSS animation inside an
SVG runs when GitHub serves that SVG into an `<img>`. Only scripts are disabled.
A repo-relative `assets/intro-*.svg` takes the identical code path.

## Content

Four sentences, matching the voice of the card below them:

| # | Sentence | `n` (chars) |
|---|---|---|
| 0 | `Hi, I'm Manh Loi` | 16 |
| 1 | `Software Engineer, Mobile` | 25 |
| 2 | `Fintech, payments, wearables` | 28 |
| 3 | `5+ years shipping to production` | 31 |

## Files

Two new SVGs and a second `<picture>` in the README — the card is left alone.

```
assets/intro-dark.svg      generated, never hand-edit
assets/intro-light.svg     generated, never hand-edit
scripts/theme.py           NEW — shared palette + type metrics
scripts/build-intro.py     NEW — renders the two intro SVGs
scripts/build-card.py      MODIFIED — imports from theme.py, output unchanged
README.md                  MODIFIED — intro <picture> added above the card
CLAUDE.md                  MODIFIED — see "Documentation" below
```

### Rejected structures

- **Embedding the intro band into the card SVG.** The card centres its ASCII
  portrait with `ay = PAD + FS + max(0, (len(ROWS) * LH - art_h) // 2)`, derived
  from `ROWS`. Adding a band re-derives that geometry, and the portrait's tone
  handling is the most fragile thing in this repo. One image would be tidier;
  it is not worth re-verifying the cat.
- **One SVG with `@media (prefers-color-scheme: dark)` inside it.** Halves the
  artifact count, but `<picture>` is the pattern this repo has already shipped
  and verified, and `render(theme)` makes the second file nearly free. The
  OS-versus-GitHub theme caveat in `CLAUDE.md` applies identically to both, so
  there is no accessibility or correctness gain to offset the unverified path.

### Why `theme.py` exists

`build-card.py` holds the palette `P`, `FONTS`, and the type metrics at module
level *and writes both SVGs at import time* (its last six lines run on import).
A second script therefore cannot `import build-card` without triggering a card
rebuild as a side effect.

Extract the shared values instead:

```
scripts/theme.py         ~40 lines   P, FONTS, FS, LH, CW, pick(theme)
scripts/build-card.py   ~170 lines   card only
scripts/build-intro.py   ~80 lines   intro only
```

Copying the palette into the new script was rejected: the two images sit
adjacent on the profile, a one-hex divergence is visible immediately, and
nothing would keep them in sync.

## Geometry

| Constant | Value | Note |
|---|---|---|
| `W` | `1052` | **Must equal the card's `W`.** Read it from the generator's printed output, do not hardcode independently. |
| `FS` | `18` | Larger than the card's 14 — this is a headline, not a table row. Not discussed during design; change it freely at review. |
| `CW` | `FS * 0.6` = `10.8` | Same derivation as the card. |
| `PAD_Y` | `14` | Vertical padding. |
| baseline `y` | `PAD_Y + FS` = `32` | |
| `H` | `52` | `baseline + descender + PAD_Y`, descender allowed as `0.25 * FS = 4.5`, rounded up. The card's `LH` is not used — this image is one line. |
| prompt `x` | `22` | Matches the card's `PAD`, so both images share a left edge. |
| text `x` | `22 + 2 * CW` = `43.6` | Clears the `$ ` prompt. |

Longest sentence renders `31 * 10.8 = 334.8px` wide, far inside `1052`.

## Colours

Taken from `theme.py`, so they track the card:

- sentence text — `head` (`#f0f6fc` dark, `#1f2328` light)
- `$ ` prompt and cursor — `label` (`#3fb950` dark, `#1a7f37` light), echoing
  the card's green keys

## Animation

### The load-bearing detail

Typing is a `<rect>` inside a `clipPath` whose `width` animates with
`steps(n)`. **`steps(n)` only lands on character boundaries if the text's
rendered width is exactly `n * CW`** — and the reader's monospace font is not
the author's. This is the failure `CLAUDE.md` warns about under "Alignment must
not depend on the reader's font", except here it does not merely shift columns:
it slices a glyph in half mid-animation.

The generator's existing discipline is the fix. Every sentence `<text>` carries
`textLength="{n * CW}"` and `lengthAdjust="spacing"`, and the clip rect animates
to that same `n * CW`. `steps(n)` is then exact under any font.

The cursor gets its own `x` animated with **the same `steps(n)` over the same
`n * CW`** — not a percentage, which would drift off the end of the text.

### Timing

Fixed **4.9s slot per sentence**, so keyframe percentages stay clean. Typing
speed is constant at 65ms/char and deletion at 35ms/char; the hold absorbs the
difference in sentence length. A 0.3s pause closes each slot.

| # | `n` | type | hold | delete | pause |
|---|---|---|---|---|---|
| 0 | 16 | 1.04s | 3.00s | 0.56s | 0.3s |
| 1 | 25 | 1.63s | 2.10s | 0.88s | 0.3s |
| 2 | 28 | 1.82s | 1.80s | 0.98s | 0.3s |
| 3 | 31 | 2.02s | 1.50s | 1.09s | 0.3s |

Total loop **19.6s**, `animation-iteration-count: infinite`.

### Keyframe shape

All four sentences share one 19.6s timeline; each is clipped to width 0 outside
its own slot. Per-keyframe `animation-timing-function` switches between stepped
typing and the flat hold. For sentence `i` with slot start `s = i * 4.9`:

```
  s + 0                      width 0          steps(n)
  s + type                   width n * CW     (hold, no stepping)
  s + type + hold            width n * CW     steps(n)
  s + type + hold + delete   width 0
```

converted to percentages of 19.6s. Keyframes at `0%` and `100%` pin width to 0
so sentences stay hidden outside their slot.

`steps(n)` means `steps(n, jump-end)` — the CSS default — in both directions:
typing leaves width at 0 for the first 65ms and then reveals character 1;
deleting holds the full width for the first 35ms and then removes the last
character. Do not substitute `jump-start`; it drops a character instantly at
the start of each phase.

The animated property is the `width` **geometry property** of the clip rect,
which CSS can animate on an SVG `<rect>` in Chrome 79+, Firefox 70+, and
Safari 14+. If verification step 3 shows it not animating, the fallback is SMIL
`<animate attributeName="width" calcMode="discrete">` with a generated `values`
list — verbose, but the generator emits it and SMIL is unaffected by the `<img>`
script restriction. Do not reach for the fallback before step 3 has actually
failed.

### Cursor

A `<rect>`, not a glyph — `▌` and `❯` are East-Asian ambiguous width and can
fall back to a CJK face at double width, the same trap `CLAUDE.md` documents for
the card's box-drawing characters. A rect has no font dependency. Add
`shape-rendering="crispEdges"` to avoid subpixel blur.

Two nested elements, so the two opacity animations do not collide:

- outer `<g>` — slot gating, opacity steps to 1 only during this sentence's slot
- inner `<rect>` — a continuous 1s blink

## Accessibility

Both are requirements, not polish.

- **`alt` carries all four sentences as prose.** `CLAUDE.md` states that `alt`
  is the only thing assistive technology sees for these cards. `6206668` used
  `alt="Typing SVG"`; repeating that would be a regression.

  ```
  Hi, I'm Manh Loi. Software Engineer, Mobile. Fintech, payments, wearables.
  5+ years shipping to production.
  ```

- **`@media (prefers-reduced-motion: reduce)`** disables the animation and
  renders sentence 0 complete, with a static (non-blinking) cursor. A reader who
  has asked for less motion should not get a 20s loop.

## README markup

The intro goes above the card, unlinked (the card keeps its `<a>`):

```html
<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/intro-dark.svg">
    <img alt="Hi, I'm Manh Loi. Software Engineer, Mobile. Fintech, payments, wearables. 5+ years shipping to production." src="assets/intro-light.svg">
  </picture>
</p>
```

## Verification

`CLAUDE.md`'s Chrome `--screenshot` recipe **does not apply here.** A still
frame cannot show an animation, and opening a `.svg` directly is a *document*
context, which permits more than `<img>` does. Verify in this order:

1. **Refactor regression — the important one.** After moving constants into
   `theme.py`, run `python3 scripts/build-card.py`; it must still print
   `1052x690` and leave `assets/card-*.svg` byte-identical:

   ```sh
   python3 scripts/build-card.py && git diff --stat -- assets/card-dark.svg assets/card-light.svg
   # must be empty
   ```

2. **Intro width matches the card.** `python3 scripts/build-intro.py` prints its
   `W`; it must read `1052`.

3. **Animation actually runs under `<img>` restrictions.** Write a throwaway
   HTML in the scratchpad containing only
   `<img src=".../assets/intro-dark.svg">`, open it in a real browser, and watch
   it. This reproduces the exact restriction GitHub imposes; if it animates
   there, it animates on the profile.

4. **Sanitizer keeps the markup.** Confirm the `<picture>`/`<source>` survives:

   ```sh
   gh api --method POST /markdown -f mode=markdown -f text="$(cat README.md)" | grep -c 'intro-'
   ```

## Documentation

`CLAUDE.md`'s Structure section currently reads *"`README.md` — six lines: a
`<picture>` that swaps between two generated SVGs. Do not put anything else on
the profile page"*. Shipping this makes that false, and the next session will
trust it. Updating it is part of this change, not a follow-up:

- the README line count and the second `<picture>`
- `scripts/theme.py` and `scripts/build-intro.py` in the file list, and the fact
  that two build scripts now need running
- a note under "Things that will bite" covering the
  `textLength` / `steps(n)` coupling
