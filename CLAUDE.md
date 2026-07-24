# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is `iammanhIoi/iammanhIoi` — a GitHub profile repository. Its sole purpose is to render the profile README shown on https://github.com/iammanhIoi. There is no application code, build system, linter, or test suite here.

## Structure

- `README.md` — the profile page content, and the only file that matters functionally. It is one thing: a neofetch-style card (ASCII portrait + info panel) in a two-column `<table>`. Nothing follows it, deliberately — see "What not to add back" below.
- `AGENTS.md` — a generic Codex/skills-workspace contributor guide (references a `skills/<skill-name>/` layout, `config.toml`, validator scripts, etc.). None of that structure actually exists in this repository — treat `AGENTS.md` as stale/inherited boilerplate, not a description of this repo's real layout.
- `.gitignore` — ignores `.idea/` (JetBrains project files).

## Working in this repo

- Changes are almost always edits to `README.md` (badges via shields.io, section content, links).
- There is nothing to build, lint, or test — verify changes by checking the rendered Markdown reads correctly (e.g. via a Markdown preview) rather than running any command.
- Keep badge/shield URLs and styling consistent with the existing ones when adding new badges.

### The info panel's colors

The panel is fenced as ```` ```http ````. That is deliberate and load-bearing, not a description of the content: GitHub's HTTP-spec grammar colors `Label:` as `pl-v` (orange) and the rest of the line as `pl-s` (blue), which is what produces the neofetch look. Constraints that follow from it:

- **Every line must be `Label: value` or blank.** A line without a colon is tagged `pl-ii`, which GitHub renders on a **red background**. That rules out tree/continuation lines (`├── …`, indented wrapped text) inside the panel — one line per entry, always.
- **The label must be a valid HTTP header token: no spaces, ASCII only.** `2026.02-now:` works; `2026.02 - now:` and `● 2026.02:` are both `pl-ii`. Values are unrestricted, so `─`, `·` and other Unicode are fine to the right of the colon.
- The *first* line is parsed as the HTTP request line — anything other than a real one (`GET /iammanhIoi HTTP/1.1`) is `pl-ii` too. Keep that line intact.
- Section rules are written as `Contact: ─────` for the same reason.
- **Color is per syntactic role, not per word.** The grammar gives exactly two colors — orange label, blue value. There is no way to make "MoMo" pink or "TypeScript" its brand blue inside a fence; ~15 grammars were tested for this. `ruby` can force three colors by lexical form (`@Foo` blue, `.Foo` purple, `Foo` orange) but its parse is context-dependent and the same form lands on different classes line to line, so it looks random.
- The consequence for content: **anything you want highlighted must be the label, not the value.** That is why the `Stack` section is keyed by language (`TypeScript: … React, Next.js`) instead of by category (`Lang.Code: … TypeScript, Kotlin`) — it puts the language names in the orange slot.
- Shields.io badges give real brand colors but are images, so the text stops being selectable. That trade was tried and rejected; keep the card all-text.
- The ASCII portrait sits in a separate `<td>` in a plain ```` ```text ```` fence. It must not share a fence with the panel — the grammar would swallow the art into the `Label:` match and paint it orange.
- Blank lines around the fences inside `<td>` are required, otherwise GitHub does not parse Markdown inside the HTML block.

A colored SVG (like Andrew6rant's profile) was considered and rejected: it is an image, so the text cannot be selected, copied, or read by a screen reader.

### What not to add back

- **A contribution graph.** GitHub renders the contribution calendar and "Contribution activity" list natively on the profile page, directly under the README — it cannot be removed and every visitor sees it. Third-party widgets (`ghchart.rshah.org`, `streak-stats.demolab.com`) only see *public* contributions, so for this account they render near-empty (~16) against a real count in the hundreds. Adding one makes the profile look less active, not more.
- **`github-readme-stats.vercel.app` cards.** Returned 503 for every username when last checked — a broken image on the profile. Re-verify with `curl -o /dev/null -w '%{http_code}'` before ever re-adding.
- **A `## Connect` section.** The contacts are already in the card's `Contact:` block. It was removed as a duplicate.

### Verifying a README change

Render it through GitHub's own Markdown API instead of guessing — it returns the real token classes:

```sh
gh api --method POST /markdown -f mode=markdown -f text="$(cat README.md)" | grep pl-ii   # must be empty
```
