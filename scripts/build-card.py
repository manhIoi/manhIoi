#!/usr/bin/env python3
"""Render the profile card to assets/card-dark.svg and assets/card-light.svg.

Every glyph is a positioned <tspan> with an explicit fill, which is the only way
to colour text per word on a GitHub profile — a fenced code block colours by
syntactic role, so all language names necessarily share one colour.

Alignment does not depend on the reader's monospace metrics: each tspan carries
its own x and textLength.
"""
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ART_SRC = os.path.join(HERE, "art.txt")

# ---- palette ---------------------------------------------------------------
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

    "HDBank": ("#FF6B5E", "#E2231A"),
    "MoMo":   ("#F072B6", "#A50064"),
    "UIT":    ("#79C0FF", "#005BAA"),
}

# ---- content ---------------------------------------------------------------
# Each row is a list of (text, colour-key) segments. "gap" is a blank line.
def L(label, *value):
    return [(" . ", "dim"), (label, "label"), (": ", "dim"), *value]

def dots(n):
    return ("." * n + " ", "rule")

ROWS = [
    [("manhIoi@github ", "head"), ("─" * 46, "rule")],
    L("Name",       dots(13), ("Pham Manh Loi", "value")),
    L("Role",       dots(13), ("Software Engineer, Mobile", "value")),
    L("Focus",      dots(12), ("Fintech, payments, wearables", "value")),
    L("Location",   dots(9),  ("Vietnam", "value")),
    L("Speaks",     dots(11), ("Vietnamese, English", "value")),
    L("Uptime",     dots(11), ("5+ years in production", "value")),
    "gap",
    [("─ Stack ", "head"), ("─" * 45, "rule")],
    L("Mobile",  dots(11), ("React Native", "React"), (", ", "value"),
                           ("Kotlin", "Kotlin"), (", ", "value"), ("Swift", "Swift")),
    L("Native",  dots(11), ("Compose", "Compose"), (", ", "value"),
                           ("SwiftUI", "SwiftUI"), (", ", "value"),
                           ("Android", "Android"), (", ", "value"), ("watchOS", "watchOS")),
    L("Web",     dots(14), ("TypeScript", "TypeScript"), (", ", "value"),
                           ("React", "React"), (", ", "value"),
                           ("Next.js", "Next.js"), (", ", "value"), ("Vue.js", "Vue.js")),
    L("Runtime", dots(10), ("Node.js", "Node.js"), (", ", "value"),
                           ("JavaScript", "JavaScript")),
    L("Data",    dots(13), ("PostgreSQL", "PostgreSQL"), (", ", "value"),
                           ("MongoDB", "MongoDB"), (", ", "value"), ("Realm", "Realm")),
    L("CI/CD",   dots(12), ("GitHub Actions", "Actions"), (", ", "value"),
                           ("Jenkins", "Jenkins")),
    "gap",
    [("─ Timeline ", "head"), ("─" * 42, "rule")],
    [("   ● ", "HDBank"), ("HDBank", "HDBank"),
     ("  Mobile Developer", "value"), ("        2026.02 → now", "dim")],
    [("   │ ", "rule"), ("Mobile banking and payment platform", "dim")],
    [("   ● ", "MoMo"), ("MoMo", "MoMo"), ("  Mobile Developer", "value"),
     ("          2021 → 2026.01", "dim")],
    [("   │ ", "rule"), ("Super-app, e-wallet, wearable payments", "dim")],
    [("   ● ", "UIT"), ("UIT", "UIT"), ("  Information Technology", "value"),
     ("     2019 → 2024", "dim")],
    "gap",
    [("─ Contact ", "head"), ("─" * 43, "rule")],
    L("Email",     dots(12), ("manhloi0505@gmail.com", "value")),
    L("LinkedIn",  dots(9),  ("loi-pham-manh", "value")),
    L("GitHub",    dots(11), ("manhIoi", "value")),
    L("Facebook",  dots(9),  ("manhloi551", "value")),
    L("Instagram", dots(8),  ("p.manhloi", "value")),
    L("Phone",     dots(12), ("+84 792 465 841", "value")),
]

# ---- geometry --------------------------------------------------------------
FS, LH, PAD = 14, 19, 22
CW = FS * 0.6
GAP = 3 * CW
FONTS = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
         "'DejaVu Sans Mono','Liberation Mono','Courier New',monospace")

ART = open(ART_SRC).read().rstrip("\n").split("\n")
AW = max(len(a) for a in ART)
PW = max(sum(len(t) for t, _ in r) for r in ROWS if r != "gap")
W = round(PAD * 2 + AW * CW + GAP + PW * CW)
H = round(PAD * 2 + max(len(ART), len(ROWS)) * LH)


def render(theme):
    i = 0 if theme == "dark" else 1
    c = {k: v[i] for k, v in P.items()}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="{FONTS}" font-size="{FS}">',
           f'  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
           f'fill="{c["bg"]}" stroke="{c["border"]}"/>']
    y0 = PAD + FS
    for n, line in enumerate(ART):
        if line.strip():
            out.append(
                f'  <text style="white-space:pre" fill="{c["art"]}" x="{PAD}" '
                f'y="{y0 + n*LH}" textLength="{len(line)*CW:.2f}" '
                f'lengthAdjust="spacing">{escape(line)}</text>')
    x0 = AW + 3
    for n, row in enumerate(ROWS):
        if row == "gap":
            continue
        col, spans = x0, []
        for text, key in row:
            spans.append(
                f'<tspan fill="{c[key]}" x="{PAD + col*CW:.2f}" '
                f'textLength="{len(text)*CW:.2f}" lengthAdjust="spacing">'
                f'{escape(text)}</tspan>')
            col += len(text)
        out.append(f'  <text style="white-space:pre" y="{y0 + n*LH}">'
                   f'{"".join(spans)}</text>')
    out.append("</svg>")
    return "\n".join(out)


for t in ("dark", "light"):
    with open(os.path.join(ROOT, "assets", f"card-{t}.svg"), "w") as f:
        f.write(render(t))
print(f"{W}x{H}  art {AW}x{len(ART)}  panel {PW} cols  {len(ROWS)} rows")
