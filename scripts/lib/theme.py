"""Colour tokens. Every graphic is emitted once per theme; the README picks
between them with <picture media="(prefers-color-scheme: dark)">.

Charts keep transparent backgrounds; identity and project panels use explicit
surfaces so their borders and technical illustrations remain legible.
"""

LIGHT = {
    "name":   "light",
    "fg":     "#16191d",
    "muted":  "#626b75",
    "faint":  "#687782",
    "rule":   "#e2e5e9",
    "grid":   "#eef0f2",
    "accent": "#087f72",
    "signal": "#526c16",
    "surface": "#f4f8f7",
    "raised": "#ffffff",
    # 5-step ramp, empty -> busiest
    "ramp":   ["#edf2f1", "#cdebe2", "#8cd2bc", "#3daa90", "#087f72"],
}

DARK = {
    "name":   "dark",
    "fg":     "#e6edf3",
    "muted":  "#8b949e",
    "faint":  "#89999f",
    "rule":   "#262c34",
    "grid":   "#1a1f26",
    "accent": "#62dfc3",
    "signal": "#c8ed87",
    "surface": "#111c20",
    "raised": "#16262a",
    "ramp":   ["#18272b", "#174b43", "#237e6c", "#36b397", "#62dfc3"],
}

THEMES = (LIGHT, DARK)
