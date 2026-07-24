# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is `iammanhIoi/iammanhIoi` — a GitHub profile repository. Its sole purpose is to render the profile README shown on https://github.com/iammanhIoi. There is no application code, build system, linter, or test suite here.

## Structure

- `README.md` — the profile page content, and the only file that matters functionally. It is one thing: a neofetch-style card (ASCII portrait + info panel) in a two-column `<table>`. Nothing follows it, deliberately — see "What not to add back" below.
- `AGENTS.md` — a generic Codex/skills-workspace contributor guide (references a `skills/<skill-name>/` layout, `config.toml`, validator scripts, etc.). None of that structure actually exists in this repository — treat `AGENTS.md` as stale/inherited boilerplate, not a description of this repo's real layout.
- `.gitignore` — ignores `.idea/` (JetBrains project files).

## Working in this repo

- `README.md` is one `yaml` code block and nothing else. Editing it means editing that block — read the section below first, because several obvious-looking edits break the rendering.
- There is nothing to build, lint, or test. **Do not verify with a local Markdown preview** — IntelliJ's and VS Code's highlighters color this block completely differently from GitHub's, so a local preview will show wrong colors and send you chasing a non-bug. Use the Markdown API call below.

### The card is one `yaml` fence — and every part of that is load-bearing

The whole card is a **single** ```` ```yaml ```` block: the ASCII art and the info
panel share each line, art on the left, `Label: value` on the right. Three earlier
layouts were tried and each failed on GitHub:

- **Two fences in a `<table>`** (art `text`, panel `http`): renders as *two* grey
  boxes rather than one card, and the table forces the cells wider than the
  profile README container, so the right column gets clipped mid-word.
- **`http` grammar**: its label must be a valid header token, so a line of
  `<art>   Label:` — which has spaces before the colon — is tagged `pl-ii` and
  GitHub paints it on a **red background**. Unusable for a combined line.
- **A generated SVG**: correct colors, but it is an image, so the text cannot be
  selected, copied, or read by a screen reader.

`yaml` works because its key may contain spaces. Each line parses as
`<art><spaces>Label` → `pl-ent`, value → `pl-s`. Two colors, consistent on every
line. Constraints:

- **Every line must contain a colon**, so the panel must have exactly as many
  rows as the art — no blank spacer lines. Group with the `Section: ─────` rules
  instead. A colon-less line becomes a plain scalar and loses the key color,
  which reads as a rendering glitch.
- **The art may not contain `:` or any YAML indicator.** The source art used the
  ramp `` .:;+xX$& `` — `:` splits the key early and a leading `&` is parsed as an
  anchor, both of which scramble the line. It is remapped character-for-character
  to `` ._;+xX$W `` (`:`→`_`, `&`→`W`), which keeps the density ordering. Any new
  art must be remapped the same way before it goes in.
- **Color is per syntactic role, not per word.** Two colors total. There is no way
  to give "TypeScript" its brand blue or "MoMo" pink inside a fence; ~15 grammars
  were tested. `ruby` can force three colors by lexical form (`@Foo`, `.Foo`,
  `Foo`) but its parse is context-dependent, so the same form lands on different
  classes line to line and looks random. Shields.io badges do give brand colors,
  but they are images — that trade was tried and rejected.
- The consequence for content: **anything you want highlighted must be a label.**
  That is why `Stack` is keyed by language (`TypeScript: … React, Next.js`) rather
  than by category (`Lang.Code: … TypeScript, Kotlin`).
- **Keep the total line width under ~95 characters.** The profile README column is
  narrower than a repo page's; past that the block scrolls horizontally.
- GitHub's light theme renders these as dark green on navy — legible but muted.
  The design only really pops in dark theme, and that is GitHub's palette, not
  something the file controls.

### What not to add back

- **A contribution graph.** GitHub renders the contribution calendar and "Contribution activity" list natively on the profile page, directly under the README — it cannot be removed and every visitor sees it. Third-party widgets (`ghchart.rshah.org`, `streak-stats.demolab.com`) only see *public* contributions, so for this account they render near-empty (~16) against a real count in the hundreds. Adding one makes the profile look less active, not more.
- **`github-readme-stats.vercel.app` cards.** Returned 503 for every username when last checked — a broken image on the profile. Re-verify with `curl -o /dev/null -w '%{http_code}'` before ever re-adding.
- **A `## Connect` section.** The contacts are already in the card's `Contact:` block. It was removed as a duplicate.

### Verifying a README change

Render it through GitHub's own Markdown API instead of guessing — it returns the real token classes:

```sh
gh api --method POST /markdown -f mode=markdown -f text="$(cat README.md)" | grep pl-ii   # must be empty
```
