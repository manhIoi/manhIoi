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
