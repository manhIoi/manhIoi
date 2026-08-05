# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is `manhIoi/manhIoi` — a GitHub profile repository. Its sole purpose is to render the profile README shown on https://github.com/manhIoi. There is no application code, linter, or test suite here. The default branch is **`master`**; GitHub only renders the profile from the default branch.

## Structure

- `README.md` — two `<picture>` blocks: the typing intro line, then the card. Both swap between a dark and a light generated SVG, and both sit in a `<p align="center">`. Nothing else belongs on the profile page; see "What not to add back".
- `assets/card-{dark,light}.svg`, `assets/intro-{dark,light}.svg` — **generated, never hand-edit.**
- `scripts/theme.py` — the palette and font stack, shared by both generators. Type metrics are per-generator: the card is 14px, the intro 18px.
- `scripts/build-card.py` — the card generator: portrait on top, info panel below, no frame. Edit `ROWS` for content, `scripts/theme.py` for colour, then run it. Needs Pillow only if `art.txt` is being re-rendered from a photo; the build itself is stdlib. (The Pillow installed on this machine is an x86_64 build and cannot load under the arm64 interpreter.)
- `scripts/build_intro.py` — the intro generator. Edit `SENTENCES` or the timing constants, then run it. Underscored, not hyphenated, so it can be imported.
- `scripts/art.txt` — the ASCII portrait. Authored for a light background; the dark variant is derived from it at build time. It is the *only* source for the portrait — the photo it came from was never committed, and no script here reads an image.
- `docs/superpowers/{plans,specs}/2026-08-05-typing-intro*.md` — the design record for the intro. The plan is fully executed, so nothing reads these; they are kept because they hold the reasoning behind the timing and `textLength` coupling in more depth than the notes below. At ~50KB the plan is the largest tracked file in the repo, so delete them if that ever matters — the history keeps them.

That is the whole repo, plus `CLAUDE.md` and `.gitignore`. It was also carrying four orphaned logo/GIF images and an inherited `AGENTS.md` describing a `skills/` layout that never existed here; all five are deleted. Anything not referenced by `README.md` and not read by a script does not belong in `assets/`.

## Working in this repo

Regenerate and eyeball in a real browser — the SVG uses `textLength`, which macOS QuickLook (`qlmanage`) gets wrong, so it is not a valid preview:

```sh
python3 scripts/build-card.py && python3 scripts/build_intro.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --screenshot=out.png --window-size=514,1114 assets/card-dark.svg
```

The window size is the card's own `WxH`, which the build prints — pass a stale one
and the screenshot is cropped or padded, and neither is a fault in the SVG.
`out.png` lands in the repo root and is git-ignored.

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
  `P` stores `(dark, light)` pairs — React cyan becomes `#0B8CA8` on white,
  .NET's `#512BD4` is lightened for dark, Next.js flips black/white. `P` holds a
  pair only for a name the card still lists; drop the row, drop the pair.
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
  side by side: at 56 columns the card is 514px, well under the cap, so it renders
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
- **The panel is one centred block, not a stack of centred lines.** Centring each
  row independently is what reads as *lost* symmetry: rows differ in length, so
  the label column lands somewhere new on every line and both edges come out a
  zigzag. It was tried and reverted. Instead every row shares `PANEL_X`, and the
  symmetry comes from alignment inside the block — `LW` right-aligns the labels so
  every colon falls on one column, and `NW` pads the org names so the timeline's
  roles and dates line up too. Right-aligning the labels is also what keeps it
  gapless: a label always ends flush against its colon, so there is nothing for a
  dotted leader to span. Those leaders and the old runs of spaces before each date
  are gone, and `check_card_layout.py` fails if either comes back, if a row
  overflows the block, or if the colons stop sharing a column.
- **`align="center"` on the wrapping `<p>` is what centres the card on the page.**
  The card is 514px and the README column is ~830px, so without it the whole card
  sits against the left edge no matter how its contents are aligned — centring
  inside the SVG cannot fix being left-aligned as an image. Verified through the
  Markdown API that the sanitizer keeps the attribute; `check_readme.sh` fails if
  either block loses it. Do not chase this by widening the card instead: `W` over
  ~830px costs text size, per the ceiling above.
- **Headings are `H("title")` markers, expanded after the width is known.** The
  rule is split around the title so the title sits centred — `───── Stack ─────`
  rather than a title with a trailing rule. The dash count depends on `PW`, which
  is measured from the content rows, so the expansion cannot happen at the literal.
  An odd dash count goes to the right side, leaving a title at most half a cell
  off centre.
- **Row baselines are accumulated, not `n * LH`.** A heading's rule sits on the
  same baseline as its title, so at plain leading it crowds the first line of its
  section — the rule and the text under it end up tighter than two body lines are.
  `HEAD_GAP` adds room under each heading only, giving 19px between body lines,
  27px under a heading and 38px above one, so a heading belongs to the section
  below it. A full blank line instead would space it equally from both. `H` comes
  from the same accumulation, so changing `HEAD_GAP` cannot desync the height.
- **`CONTENT_W` sizes the card, and the dividers follow it.** Measured over
  content rows only, then `_stretch_rules` pads every section rule to it, so the
  headers bracket the block exactly. The portrait is wider than the panel and that
  is fine — both are centred on the same axis. Adding a row longer than the
  portrait is what widens the card.
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
  measurements inside a multi-second hold, never at a precise instant (which
  point in the hold is the next bullet), and freeze the 1s blink (`#caretN{animation-name:caretN!important}`) before
  measuring the caret's position — otherwise the caret is missing from the frame
  half the time and it looks like `x` is not animating. It is; CSS `x` on a
  `<rect>` works in Chrome.
- **The drift is one-directional, so the hold's midpoint is not a safe aim for the
  longest sentence.** Typing speed is constant and every sentence gets the same
  `SLOT`, so the longest sentence has the *shortest* hold: `'5+ years shipping to
  production'` holds 1.5s against sentence 0's 3.0s, leaving only 0.75s from the
  midpoint to the start of deletion. Capture always lands *late*, never early, so
  that margin is what the ~0.55s drift eats — the frame arrives a character or two
  into the delete phase and the assertion reads as an off-centre or short line.
  Aim `hold_start + 0.3s` instead of the midpoint. Before believing any such
  failure, check `git diff assets/`: if the SVG is unchanged, it is this.

### What not to add back

- **A contribution graph.** GitHub renders the contribution calendar and "Contribution activity" list natively on the profile page, directly under the README — it cannot be removed and every visitor sees it. Third-party widgets (`ghchart.rshah.org`, `streak-stats.demolab.com`) only see *public* contributions, so for this account they render near-empty (~16) against a real count in the hundreds. Adding one makes the profile look less active, not more.
- **`github-readme-stats.vercel.app` cards.** Returned 503 for every username when last checked — a broken image on the profile. Re-verify with `curl -o /dev/null -w '%{http_code}'` before ever re-adding.
- **A `## Connect` section.** The contacts are already in the card's `Contact` block. It was removed as a duplicate.
- **HTML/CSS for colour.** GitHub's sanitizer strips `style` and `class`
  attributes and `<font>` tags, and escapes `<style>` blocks into visible text.
  Verified against the Markdown API — there is no colour control through HTML.
