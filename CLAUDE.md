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

### The card is one `css` fence — and every part of that is load-bearing

The card is a **single** ```` ```css ```` block. Each line is:

```
/* <art slice> */ <Label> /* <dots> <value> */
```

which CSS tokenizes into exactly three slots:

| slot | class | dark | light |
|---|---|---|---|
| art — a block comment | `pl-c` | `#8b949e` grey | `#6e7781` grey |
| `Label` — a selector | `pl-ent` | `#7ee787` green | `#116329` green |
| value — a block comment | `pl-c` | same grey as the art | same grey as the art |

**Why CSS and not YAML.** A `#` comment runs to end of line, so with YAML the art
could only ever sit to the *right* of the panel — and art placed to the *left*
gets folded into the key and takes the key's colour. CSS has `/* … */` block
comments, which close mid-line. That is the only construct found that puts
neutral text to the left of a coloured token. ~20 grammars were tested; nothing
else does it.

Constraints, all of which have been hit for real:

- **A label must be a valid CSS selector.** It cannot start with a digit and it
  cannot contain `@`. `manhIoi@github` silently broke *every* line after it (`@`
  opens an at-rule); `2026.02-now` broke everything from `Timeline` down. This is
  why the timeline rows are keyed by employer (`HDBank`, `MoMo`, `UIT`) with the
  dates in the value — not the other way round.
- **The art may not contain `*` or `/`**, which would close its comment early.
  The ramp in use, `` .:;+xX$& ``, is safe. Check any new art before using it.
- **Every line needs both comments**, so the panel must have exactly as many rows
  as the art — no blank spacer lines. Group with the `Section /* ───── */` rules.
- **Keep total line width under ~110 characters.** The profile README column is
  narrower than a repo page's; past that the block scrolls horizontally.
- **Colour is per syntactic slot, not per word.** Three slots, that is the
  ceiling — there is no way to give "TypeScript" its brand blue or "MoMo" pink.
  The consequence: **anything you want highlighted must be a label.** That is why
  `Stack` is keyed by language rather than by category.

Verify a change by counting classes, not by eye — a broken selector fails
*silently*, downgrading later lines to plain text rather than erroring:

```sh
gh api --method POST /markdown -f mode=markdown -f text="$(cat README.md)" \
  | grep -o 'pl-ent' | wc -l    # must equal the number of panel rows
```

### Approaches that were tried and rejected

- **HTML/CSS.** GitHub's sanitizer strips `style` attributes, `class`
  attributes, and `<font>` tags outright, and escapes `<style>` blocks into
  visible text. Verified against the Markdown API — there is no colour control
  through HTML at all.
- **A generated SVG** (what `Andrew6rant/Andrew6rant` actually ships — its whole
  README is a `<picture>` of two `.svg` files). Gives arbitrary per-word colour,
  but it is an image: the text cannot be selected, copied, or read by a screen
  reader. Rejected for that reason; re-read this before "fixing" the colours.
- **Two fences in a `<table>`** (art `text`, panel `http`): renders as *two*
  grey boxes, and the table sizes its cells wider than the profile column, so
  the right side is clipped mid-word.
- **`http` grammar**: its label must be a valid header token, so any line with
  spaces before the colon is tagged `pl-ii` — a **red background** on GitHub.
- **`makefile` grammar**: only two slots (purple key, plain value), no neutral
  slot for the art.
- **`yaml` grammar**: three slots, but `#` comments run to end of line, so the
  art is stuck on the right-hand side.

### What not to add back

- **A contribution graph.** GitHub renders the contribution calendar and "Contribution activity" list natively on the profile page, directly under the README — it cannot be removed and every visitor sees it. Third-party widgets (`ghchart.rshah.org`, `streak-stats.demolab.com`) only see *public* contributions, so for this account they render near-empty (~16) against a real count in the hundreds. Adding one makes the profile look less active, not more.
- **`github-readme-stats.vercel.app` cards.** Returned 503 for every username when last checked — a broken image on the profile. Re-verify with `curl -o /dev/null -w '%{http_code}'` before ever re-adding.
- **A `## Connect` section.** The contacts are already in the card's `Contact:` block. It was removed as a duplicate.

### Verifying a README change

Render it through GitHub's own Markdown API instead of guessing — it returns the real token classes:

```sh
gh api --method POST /markdown -f mode=markdown -f text="$(cat README.md)" | grep pl-ii   # must be empty
```
