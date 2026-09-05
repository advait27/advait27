#!/usr/bin/env python3
"""Turn data/snapshot.json into svg/*.svg, plus the README's text fallback.

Standard library only, and deliberately offline: rendering never touches the
network, so the same snapshot always produces the same bytes and a diff in
svg/ always means the data moved. `verify.py` enforces that by rendering
twice and comparing.

  python3 scripts/render.py                 render every panel, both themes
  python3 scripts/render.py --build-fonts   also (re)build font subsets

--build-fonts is the only path that imports fontTools. Run it after changing
any static copy in panels.py, and commit what lands in assets/subset/.
"""

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib import fontkit, panels                                # noqa: E402
from lib.theme import THEMES                                   # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SNAPSHOT = os.path.join(ROOT, "data", "snapshot.json")
SVG_DIR = os.path.join(ROOT, "svg")
README = os.path.join(ROOT, "README.md")

START = "<!-- data:start -->"
END = "<!-- data:end -->"


class GlyphDrift(Exception):
    """A panel drew a glyph its declared charset does not cover."""


def render_panel(name, snap, theme):
    build, _ = panels.PANELS[name]
    svg = build(snap, theme)

    # The panel declares which glyphs it can ever need; svgkit records which
    # it actually drew. Anything drawn but not declared would fall back to the
    # browser's own monospace, quietly breaking every width calculation on the
    # page, so it fails here instead.
    missing = svg.charset - svg.declared
    if missing:
        raise GlyphDrift(
            f"{name}: drew {sorted(missing)!r} without declaring it. "
            f"Add it to the panel's charset, then rerun with --build-fonts."
        )
    return svg.render()


def fallback_markdown(snap):
    """The numbers as text, for when the images do not load.

    A profile made of images says nothing in a feed reader, a plain-text
    mirror, or to anyone whose connection dropped the SVGs. This block goes
    inside a <details> so it costs no visual space and stays readable.
    """
    win, streak, langs, repos = (snap["window"], snap["streak"],
                                 snap["langs"], snap["repos"])
    total = sum(v for _, v in langs["by_repo"]) or 1
    kind = "Public contributions" if snap.get("private_hidden") else "Contributions"

    rows = [
        (f"{kind} (365 days)", f"{win['total']:,}"),
        ("Commits / pull requests / reviews",
         f"{win['commits']:,} / {win['prs']:,} / {win['reviews']:,}"),
        ("Current streak", f"{streak['current']:,} days"),
        ("Longest streak", f"{streak['longest']:,} days"),
        ("All-time contributions", f"{streak['all_time']:,}"),
        ("Active days since " + snap["created"][:4], f"{streak['active_days']:,}"),
        ("Public repositories", f"{repos['total']:,}"),
    ]

    lines = [START, "", "| | |", "|:--|--:|"]
    lines += [f"| {k} | {v} |" for k, v in rows]
    lines += ["", "**Languages, by primary language of repository**", "",
              "| | |", "|:--|--:|"]
    lines += [f"| {k} | {100 * v / total:.0f}% ({v}) |"
              for k, v in langs["by_repo"][:5]]
    lines += ["", "**Most recently pushed**", "", "| | | |", "|:--|:--|--:|"]
    lines += [f"| [{r['name']}](https://github.com/{snap['login']}/{r['name']}) "
              f"| {r['language'] or '—'} | {r['pushed']} |"
              for r in repos["recent"]]
    stale = " · snapshot is stale; the last refresh could not reach the API" \
        if snap.get("stale") else ""
    lines += ["", f"<sub>Generated {snap['generated']} from "
                  f"`data/snapshot.json`{stale}.</sub>", "", END]
    return "\n".join(lines)


def splice_readme(snap):
    if not os.path.exists(README):
        return False
    with open(README) as fh:
        text = fh.read()
    if START not in text or END not in text:
        print(f"::warning::{START} / {END} markers not found in README.md; "
              f"text fallback not updated")
        return False
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    updated = head + fallback_markdown(snap) + tail
    if updated == text:
        return False
    with open(README, "w") as fh:
        fh.write(updated)
    return True


def main():
    if "--build-fonts" in sys.argv:
        fontkit.AUTOBUILD = True

    with open(SNAPSHOT) as fh:
        snap = json.load(fh)

    os.makedirs(SVG_DIR, exist_ok=True)
    written, total_bytes = [], 0
    for name in sorted(panels.PANELS):
        for theme in THEMES:
            markup = render_panel(name, snap, theme)
            path = os.path.join(SVG_DIR, f"{name}-{theme['name']}.svg")
            with open(path, "w") as fh:
                fh.write(markup)
            total_bytes += len(markup)
            written.append((os.path.basename(path), len(markup)))

    for filename, size in written:
        print(f"  {filename:24} {size / 1024:7.1f} KB")
    print(f"  {'total':24} {total_bytes / 1024:7.1f} KB")

    if fontkit.AUTOBUILD:
        pruned = 0
        for path in glob.glob(os.path.join(fontkit.SUBSET_DIR, "*.woff2")):
            if os.path.abspath(path) not in fontkit.USED:
                os.remove(path)
                pruned += 1
        if pruned:
            print(f"  pruned {pruned} orphaned font subset(s)")

    if splice_readme(snap):
        print("  README.md text fallback updated")


if __name__ == "__main__":
    main()
