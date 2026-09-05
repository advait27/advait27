"""Colour tokens. Every graphic is emitted once per theme; the README picks
between them with <picture media="(prefers-color-scheme: dark)">.

Backgrounds stay transparent on purpose. GitHub ships four themes (light,
light high-contrast, dark, dark dimmed) and a painted background would show
as a slab in the two we don't generate for.
"""

LIGHT = {
    "name":   "light",
    "fg":     "#16191d",
    "muted":  "#626b75",
    "faint":  "#99a1aa",
    "rule":   "#e2e5e9",
    "grid":   "#eef0f2",
    "accent": "#c2410c",
    # 5-step ramp, empty -> busiest
    "ramp":   ["#eceef0", "#fadfcd", "#f4b088", "#e2733a", "#c2410c"],
}

DARK = {
    "name":   "dark",
    "fg":     "#e6edf3",
    "muted":  "#8b949e",
    "faint":  "#6e7681",
    "rule":   "#262c34",
    "grid":   "#1a1f26",
    "accent": "#f0883e",
    "ramp":   ["#171b21", "#4a2a12", "#8a4a1c", "#c9702c", "#f0883e"],
}

THEMES = (LIGHT, DARK)
