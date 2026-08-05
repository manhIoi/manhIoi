# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is `manhIoi/manhIoi` — a GitHub profile repository. Its sole purpose is to render the profile README shown on https://github.com/manhIoi. There is no application code, linter, or test suite here. The default branch is **`master`**; GitHub only renders the profile from the default branch.

## Structure

- `README.md` — two `<picture>` blocks: the typing intro line, then the card. Both swap between a dark and a light generated SVG. Nothing else belongs on the profile page; see "What not to add back".
- `assets/card-{dark,light}.svg`, `assets/intro-{dark,light}.svg` — **generated, never hand-edit.**
- `scripts/theme.py` — the palette and font stack, shared by both generators. Type metrics are per-generator: the card is 14px, the intro 18px.
- `scripts/build-card.py` — the card generator: portrait on top, info panel below, no frame. Edit `ROWS` for content, `scripts/theme.py` for colour, then run it. Needs Pillow only if `art.txt` is being re-rendered from a photo; the build itself is stdlib. (The Pillow installed on this machine is an x86_64 build and cannot load under the arm64 interpreter.)
- `scripts/build_intro.py` — the intro generator. Edit `SENTENCES` or the timing constants, then run it. Underscored, not hyphenated, so it can be imported.
- `scripts/art.txt` — the ASCII portrait. Authored for a light background; the dark variant is derived from it at build time.
- `AGENTS.md` — stale inherited boilerplate describing a `skills/` layout that does not exist here. Ignore it.

## Working in this repo

Regenerate and eyeball in a real browser — the SVG uses `textLength`, which macOS QuickLook (`qlmanage`) gets wrong, so it is not a valid preview:

```sh
python3 scripts/build-card.py && python3 scripts/build_intro.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --screenshot=out.png --window-size=556,1188 assets/card-dark.svg
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
- **Raising `FS` does not make the text bigger — fewer columns does.** GitHub caps
  the README column at about 830px and scales a wider image down to fit, so the
  reader sees `FS * 830/W`. `W` grows in proportion to `FS`, so the two cancel
  almost exactly: the ceiling is `830 / (0.6 * columns)`, whatever the font size.
  Measured on the live profile, the old 120-column card (portrait 56 + gap 3 +
  panel 61) rendered at 0.79 scale, so its 14px text arrived as ~11px, and 18px
  would have arrived as ~11.1px. That is why the layout is stacked rather than
  side by side: at 61 columns the card is 556px, well under the cap, so it renders
  1:1 and 14px is really 14px. Keep `W <= 830`. Widening the panel content costs
  text size, and the portrait's `ART_FS` is separate precisely so the picture
  cannot drag the width back up.
- **The intro's width is read from the card, not repeated.** `build_intro.py`
  parses `assets/card-dark.svg` for it, so build the card first — the order in the
  command above. They must match: the two images sit one above the other and
  GitHub scales each to the column independently, so a mismatch shows up as both
  misaligned blocks and two different apparent text sizes.
- **The card has no border, and the background fill must stay.** The frame was
  removed because it read as a box with the intro line stranded outside it. Do not
  also drop the `fill` to make it transparent: a reader whose GitHub theme is set
  to Dark while their OS is Light gets the *light* card on a dark page, and the
  opaque background is the only thing keeping that dark text legible.
- **The intro centres each sentence separately, so the prompt moves.** `START[i]`
  centres a block of prompt + sentence + cursor, and the `+ 1` for the cursor cell
  matters: leave it out and every line sits half a character right of centre. The
  `$` therefore hops between the four positions, which it does on the slot
  boundary — the instant the previous line has finished deleting itself, so only
  the prompt and cursor are on screen when it moves. It is a `<text>`, and `x` is
  *not* a CSS geometry property there (it is on the cursor's `<rect>`), so the hop
  is `transform: translateX`, animated on the wrapping `#pg` group.
- **Any probe that shifts the timeline must shift `.pg` too.** Injecting
  `animation-delay` into `.clip,.caret,.cg` but not `.pg` leaves the prompt at
  sentence 0's position while the sentences move to theirs. That looks exactly
  like a centring bug in the generator, and it is not one.
- **The intro's `steps(n)` is coupled to `textLength`.** Typing is a clip rect
  whose width steps from 0 to `n * CW`, which only lands on character boundaries
  because each `<text>` is pinned to exactly that width with `textLength` and
  `lengthAdjust="spacing"`. Drop either and the animation slices glyphs in half
  for any reader whose monospace font is not yours — the failure is invisible
  locally. The cursor steps over the same `n * CW`; give it a percentage instead
  and it drifts off the end of the text.
- **A still screenshot cannot verify the intro, and `--virtual-time-budget` does
  not help.** It does not advance CSS animation time for an SVG inside an `<img>`
  — two budgets produce byte-identical frames even though the animation is
  running. To capture a chosen moment, copy the SVG and inject
  `.clip,.caret,.cg{animation-delay:-2200ms!important}` before `</style>`.
  `!important` is required: the shipped rules select by `#id` and their
  `animation` shorthand resets the delay to `0s`, so a class rule loses on
  specificity. Load the copy through an `<img>` — opening a `.svg` directly is a
  document context and permits more than GitHub's `<img>` does.
- **Headless capture lands ~0.55s into the animation, and not stably.** So aim
  measurements at the middle of a multi-second hold, never a precise instant, and
  freeze the 1s blink (`#caretN{animation-name:caretN!important}`) before
  measuring the caret's position — otherwise the caret is missing from the frame
  half the time and it looks like `x` is not animating. It is; CSS `x` on a
  `<rect>` works in Chrome.

### What not to add back

- **A contribution graph.** GitHub renders the contribution calendar and "Contribution activity" list natively on the profile page, directly under the README — it cannot be removed and every visitor sees it. Third-party widgets (`ghchart.rshah.org`, `streak-stats.demolab.com`) only see *public* contributions, so for this account they render near-empty (~16) against a real count in the hundreds. Adding one makes the profile look less active, not more.
- **`github-readme-stats.vercel.app` cards.** Returned 503 for every username when last checked — a broken image on the profile. Re-verify with `curl -o /dev/null -w '%{http_code}'` before ever re-adding.
- **A `## Connect` section.** The contacts are already in the card's `Contact` block. It was removed as a duplicate.
- **HTML/CSS for colour.** GitHub's sanitizer strips `style` and `class`
  attributes and `<font>` tags, and escapes `<style>` blocks into visible text.
  Verified against the Markdown API — there is no colour control through HTML.
