"""The graphics.

Each panel is a function taking (snapshot, theme) and returning an Svg. Two
rules run through all of them.

Chart type follows the data. Daily contributions are sparse and discrete, so
they get a grid of one cell per day: a zero day is empty space. Weekly totals
are continuous enough to justify an area. A line through 0, 0, 11, 0, 0, 10
would claim values that never existed, so no panel draws one.

Charsets are declared, not discovered. A panel folds VOLATILE (and ALNUM
where it prints repo or language names) into its charset so that the glyphs
it needs never depend on the day's numbers -- otherwise the nightly run would
need a font subset that is not committed. See fontkit.
"""

import datetime as dt

from .fontkit import ALNUM, VOLATILE, face_css
from .svgkit import Svg, fmt, text_width

W = 880          # full-bleed panel width; GitHub's README column at desktop
HALF = 432       # two of these sit side by side


def _mono(n):
    """Thousands separators, so 1247 reads as 1,247."""
    return f"{n:,}"


def _shorten(s, limit):
    if len(s) <= limit:
        return s
    return s[: max(0, limit - 1)].rstrip(" ,.;:-") + "…"


def _new(width, height, title, desc, charset, weights=(400, 700)):
    """Build a panel with its font already subset to `charset`.

    `charset` is a declaration, not a description: it must cover every glyph
    the panel could ever draw, for any data. render.py checks what was
    actually drawn against it and fails on drift.
    """
    svg = Svg(width, height, title, desc)
    svg.declared = set(charset) | {" "}
    svg.font_css = face_css(charset, weights)
    return svg


# ---------------------------------------------------------------------------
# hero
# ---------------------------------------------------------------------------

def hero(snap, t):
    name = snap["name"].lower()
    role = "APPLIED AI ENGINEER"
    tag = "llm systems / rag / agentic workflows / evaluation"
    meta = "dublin, ireland     ucd smurfit     frensei"

    h = 178
    charset = set(name + role + tag + meta) | set(VOLATILE)
    svg = _new(W, h, f"{snap['name']} — applied AI engineer",
               f"{snap['name']}. {role.title()}. {tag}. {meta}.",
               charset, weights=(400, 700, 800))

    size = 38
    y = 62
    width = text_width(name, size)

    # The name types itself in: a clip rect widens left to right with a block
    # riding its edge as a cursor. fill="freeze" everywhere, so the page draws
    # once and stops rather than looping in the reader's peripheral vision.
    svg.define(
        f'<clipPath id="wipe"><rect x="0" y="{fmt(y - size)}" '
        f'height="{fmt(size * 1.4)}" width="0">'
        f'{Svg.anim("width", 0, width, 0.9, 0.1)}</rect></clipPath>'
    )
    svg.add(f'<g clip-path="url(#wipe)">'
            + svg.text(0, y, name, size, t["fg"], weight=800) + "</g>")
    svg.add(svg.rect(0, y - size * 0.78, size * 0.5, size * 0.94, t["accent"],
                     anim=Svg.anim("x", 0, width, 0.9, 0.1)
                     + '<set attributeName="opacity" to="0" begin="1s" fill="freeze"/>'))

    rule_y = y + 26
    svg.add(svg.line(0, rule_y, 0, rule_y, t["rule"], 1.5,
                     anim=Svg.anim("x2", 0, W, 0.7, 0.95)))

    svg.add(svg.text(0, rule_y + 30, role, 13.5, t["accent"], weight=700,
                     extra='letter-spacing="1.6"', anim=Svg.fade(1, 0.45, 1.15)))
    svg.add(svg.text(0, rule_y + 52, tag, 13, t["muted"],
                     anim=Svg.fade(1, 0.45, 1.3)))
    svg.add(svg.text(0, rule_y + 78, meta, 12, t["faint"],
                     anim=Svg.fade(1, 0.45, 1.45)))
    return svg


# ---------------------------------------------------------------------------
# pulse -- headline totals and a weekly area
# ---------------------------------------------------------------------------

def pulse(snap, t):
    win = snap["window"]
    days = win["days"]

    # Weekly aggregation. An area needs continuity to be honest, and weekly
    # sums have it where daily counts do not.
    weeks = [sum(c for _, c in days[i:i + 7]) for i in range(0, len(days), 7)]
    peak = max(weeks) or 1

    total = _mono(win["total"])
    label = "contributions in the last 365 days"
    if snap.get("private_hidden"):
        label = "public contributions in the last 365 days"

    stats = [("commits", win["commits"]), ("pull requests", win["prs"]),
             ("active days", snap["streak"]["active_days"]),
             ("repositories", snap["repos"]["total"])]

    h = 196
    charset = (set(label + "".join(k for k, _ in stats)) | set(VOLATILE)
               | set("contributions in the last days"))
    svg = _new(W, h, f"{win['total']} contributions in the last 365 days",
               f"{win['total']} contributions between {win['from']} and {win['to']}: "
               + ", ".join(f"{v} {k}" for k, v in stats) + ".",
               charset)

    svg.add(svg.text(0, 52, total, 46, t["fg"], weight=700,
                     anim=Svg.fade(1, 0.5, 0.15)))
    svg.add(svg.text(0, 74, label, 12.5, t["muted"], anim=Svg.fade(1, 0.5, 0.3)))

    # Sub-stats, right aligned as a row of columns.
    x = W
    for i, (key, value) in enumerate(reversed(stats)):
        col = max(text_width(key, 11), 60) + 26
        x -= col
        svg.add(svg.text(x, 40, _mono(value), 20, t["fg"], weight=700,
                         anim=Svg.fade(1, 0.4, 0.45 + i * 0.06)))
        svg.add(svg.text(x, 58, key, 11, t["faint"],
                         anim=Svg.fade(1, 0.4, 0.5 + i * 0.06)))

    # Area chart, drawn as a left-to-right reveal.
    top, base, left = 96, 168, 0
    span = W - left
    step = span / max(len(weeks) - 1, 1)
    pts = [(left + i * step, base - (v / peak) * (base - top))
           for i, v in enumerate(weeks)]

    line = " ".join(f"{'M' if i == 0 else 'L'}{fmt(px)} {fmt(py)}"
                    for i, (px, py) in enumerate(pts))
    svg.define(f'<linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity=".28"/>'
               f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>'
               f'</linearGradient>')
    svg.define(f'<clipPath id="reveal"><rect x="0" y="{top - 6}" '
               f'height="{fmt(base - top + 12)}" width="0">'
               f'{Svg.anim("width", 0, W, 1.1, 0.55)}</rect></clipPath>')

    svg.add(f'<g clip-path="url(#reveal)">')
    svg.add(svg.path(f"{line} L{fmt(pts[-1][0])} {fmt(base)} L{fmt(pts[0][0])} "
                     f"{fmt(base)} Z", fill="url(#fill)"))
    svg.add(svg.path(line, stroke=t["accent"], width=1.75))
    svg.add("</g>")
    svg.add(svg.line(0, base, W, base, t["rule"], 1))
    svg.add(svg.text(0, base + 17, win["from"], 10.5, t["faint"],
                     anim=Svg.fade(1, 0.4, 1.5)))
    svg.add(svg.text(W, base + 17, win["to"], 10.5, t["faint"], anchor="end",
                     anim=Svg.fade(1, 0.4, 1.5)))
    return svg


# ---------------------------------------------------------------------------
# year -- one cell per day
# ---------------------------------------------------------------------------

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec"]


def year(snap, t):
    days = snap["window"]["days"]
    counts = sorted(c for _, c in days if c > 0)

    def bucket(c):
        if c <= 0 or not counts:
            return 0
        for i, q in enumerate((0.25, 0.5, 0.75)):
            if c <= counts[min(int(len(counts) * q), len(counts) - 1)]:
                return i + 1
        return 4

    left, top = 34, 30
    cell, gap = 12.4, 2.6
    pitch = cell + gap

    # Columns are calendar weeks starting Sunday, so the grid lines up with
    # the way GitHub itself draws the year.
    first = dt.date.fromisoformat(days[0][0])
    lead = (first.weekday() + 1) % 7          # Python Monday=0; calendar wants Sunday=0
    grid = {}
    for i, (date, count) in enumerate(days):
        col, row = divmod(lead + i, 7)
        grid[(col, row)] = (date, count)
    cols = max(c for c, _ in grid) + 1

    h = int(top + 7 * pitch + 34)
    charset = set("".join(MONTHS) + "monwedfri" + "less more") | set(VOLATILE)
    svg = _new(W, h, "Contribution activity, one cell per day",
               f"Daily contributions from {snap['window']['from']} to "
               f"{snap['window']['to']}; darker cells are busier days.", charset)

    # Month labels sit above the first column of each month.
    seen = set()
    for (col, row), (date, _) in sorted(grid.items()):
        d = dt.date.fromisoformat(date)
        if d.month not in seen and d.day <= 7:
            seen.add(d.month)
            svg.add(svg.text(left + col * pitch, top - 9, MONTHS[d.month - 1],
                             10, t["faint"], anim=Svg.fade(1, 0.4, 0.2)))

    for i, name in ((1, "mon"), (3, "wed"), (5, "fri")):
        svg.add(svg.text(0, top + i * pitch + cell * 0.78, name, 9.5, t["faint"],
                         anim=Svg.fade(1, 0.4, 0.2)))

    # 365 cells is a lot of markup. One <use> per day against a single
    # template rect, and one <animate> per column rather than per cell, takes
    # the file from ~68 KB to ~25 KB -- worth it on a page that loads six of
    # these. Cells fade in column by column: a wipe across the year.
    svg.define(f'<rect id="c" width="{fmt(cell)}" height="{fmt(cell)}" rx="2.4"/>')
    for col in range(cols):
        column = [f'<g opacity="0">{Svg.fade(1, 0.32, 0.25 + col * 0.011)}']
        for row in range(7):
            if (col, row) not in grid:
                continue
            _, count = grid[(col, row)]
            column.append(
                f'<use href="#c" x="{fmt(left + col * pitch)}" '
                f'y="{fmt(top + row * pitch)}" '
                f'fill="{t["ramp"][bucket(count)]}"/>'
            )
        column.append("</g>")
        svg.add("".join(column))

    legend_y = top + 7 * pitch + 18
    svg.add(svg.text(left, legend_y + 9, "less", 10, t["faint"],
                     anim=Svg.fade(1, 0.4, 1.1)))
    x = left + 34
    for shade in t["ramp"]:
        svg.add(svg.rect(x, legend_y, 11, 11, shade, rx=2.2,
                         anim=Svg.fade(1, 0.4, 1.1)))
        x += 14
    svg.add(svg.text(x + 4, legend_y + 9, "more", 10, t["faint"],
                     anim=Svg.fade(1, 0.4, 1.1)))

    active = snap["streak"]["active_days"]
    right = f"{active} active days since {snap['created'][:4]}"
    svg.note_chars(right)
    svg.add(svg.text(W, legend_y + 9, right, 10.5, t["faint"], anchor="end",
                     anim=Svg.fade(1, 0.4, 1.15)))
    return svg


# ---------------------------------------------------------------------------
# streak
# ---------------------------------------------------------------------------

def _pretty(date):
    if not date:
        return "—"
    d = dt.date.fromisoformat(date)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def streak(snap, t):
    s = snap["streak"]
    rows = [
        ("current streak", s["current"], "days",
         f"{_pretty(s['current_from'])} → {_pretty(s['current_to'])}"),
        ("longest streak", s["longest"], "days",
         f"{_pretty(s['longest_from'])} → {_pretty(s['longest_to'])}"),
        ("all time", s["all_time"], "contributions",
         f"since {_pretty(s['since'])}"),
    ]

    h = 184
    charset = (set("current streak longest all time days contributions since")
               | set("".join(MONTHS)) | set(VOLATILE) | {"→"})
    svg = _new(HALF, h, "Contribution streaks",
               "; ".join(f"{k}: {v} {u} ({r})" for k, v, u, r in rows) + ".",
               charset)

    svg.add(svg.line(0, 0.5, HALF, 0.5, t["rule"], 1))
    for i, (key, value, unit, range_text) in enumerate(rows):
        y = 46 + i * 48
        svg.add(svg.text(0, y, key, 11, t["faint"], anim=Svg.fade(1, 0.4, 0.2 + i * 0.1)))
        num = _mono(value)
        svg.add(svg.text(0, y + 22, num, 24, t["fg"], weight=700,
                         anim=Svg.fade(1, 0.45, 0.28 + i * 0.1)))
        svg.add(svg.text(text_width(num, 24) + 7, y + 22, unit, 11, t["muted"],
                         anim=Svg.fade(1, 0.45, 0.32 + i * 0.1)))
        svg.add(svg.text(HALF, y + 22, range_text, 10.5, t["faint"], anchor="end",
                         anim=Svg.fade(1, 0.45, 0.36 + i * 0.1)))
        if i < len(rows) - 1:
            svg.add(svg.line(0, y + 36, HALF, y + 36, t["grid"], 1,
                             anim=Svg.fade(1, 0.4, 0.4 + i * 0.1)))
    return svg


# ---------------------------------------------------------------------------
# langs -- by repository, not by byte
# ---------------------------------------------------------------------------

def langs(snap, t):
    data = snap["langs"]["by_repo"][:5]
    total = sum(v for _, v in snap["langs"]["by_repo"]) or 1

    h = 184
    charset = set(ALNUM) | set(VOLATILE) | set("of repositories")
    svg = _new(HALF, h, "Languages by repository",
               "Primary language across public non-fork repositories: "
               + ", ".join(f"{k} {100 * v / total:.0f}%" for k, v in data) + ".",
               charset)

    svg.add(svg.line(0, 0.5, HALF, 0.5, t["rule"], 1))
    svg.add(svg.text(0, 26, "by primary language of repository", 11, t["faint"],
                     anim=Svg.fade(1, 0.4, 0.2)))

    bar_x, bar_w = 132, HALF - 132 - 46
    for i, (name, count) in enumerate(data):
        y = 52 + i * 23
        pct = 100 * count / total
        svg.add(svg.text(0, y + 8, _shorten(name.lower(), 20), 11.5, t["fg"],
                         anim=Svg.fade(1, 0.4, 0.3 + i * 0.07)))
        svg.add(svg.rect(bar_x, y, bar_w, 9, t["grid"], rx=4.5,
                         anim=Svg.fade(1, 0.4, 0.3 + i * 0.07)))
        svg.add(svg.rect(bar_x, y, 0, 9, t["accent"], rx=4.5,
                         anim=Svg.anim("width", 0, bar_w * pct / 100, 0.75,
                                        0.35 + i * 0.07)))
        svg.add(svg.text(HALF, y + 8, f"{pct:.0f}%", 11, t["muted"], anchor="end",
                         anim=Svg.fade(1, 0.4, 0.45 + i * 0.07)))

    note = f"{snap['langs']['repo_count']} public repositories"
    svg.note_chars(note)
    svg.add(svg.text(0, h - 10, note, 10, t["faint"], anim=Svg.fade(1, 0.4, 1.0)))
    return svg


# ---------------------------------------------------------------------------
# now -- what was actually touched, most recently
# ---------------------------------------------------------------------------

def now(snap, t):
    repos = snap["repos"]["recent"]
    h = 46 + len(repos) * 26 + 14
    charset = set(ALNUM) | set(VOLATILE) | set("".join(MONTHS)) | set("pushed")
    svg = _new(W, h, "Recently pushed repositories",
               "; ".join(f"{r['name']} ({r['language'] or 'n/a'}), pushed "
                         f"{r['pushed']}" for r in repos) + ".", charset)

    svg.add(svg.line(0, 0.5, W, 0.5, t["rule"], 1))
    svg.add(svg.text(0, 26, "most recently pushed", 11, t["faint"],
                     anim=Svg.fade(1, 0.4, 0.2)))

    for i, repo in enumerate(repos):
        y = 52 + i * 26
        begin = 0.28 + i * 0.08
        name = _shorten(repo["name"], 26)
        svg.add(svg.text(0, y, name, 13, t["accent"], weight=700,
                         anim=Svg.fade(1, 0.4, begin)))
        lang = repo["language"] or ""
        if lang:
            svg.add(svg.text(250, y, _shorten(lang, 18), 11, t["muted"],
                             anim=Svg.fade(1, 0.4, begin + 0.02)))
        desc = _shorten(repo["description"], 52) if repo["description"] else ""
        if desc:
            svg.add(svg.text(392, y, desc, 11, t["faint"],
                             anim=Svg.fade(1, 0.4, begin + 0.04)))
        svg.add(svg.text(W, y, _pretty(repo["pushed"]), 10.5, t["faint"],
                         anchor="end", anim=Svg.fade(1, 0.4, begin + 0.06)))
    return svg


PANELS = {
    "hero":   (hero, W),
    "pulse":  (pulse, W),
    "year":   (year, W),
    "streak": (streak, HALF),
    "langs":  (langs, HALF),
    "now":    (now, W),
}
