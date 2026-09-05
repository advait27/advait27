#!/usr/bin/env python3
"""Pre-flight checks for the profile page. Run in CI on every push.

Each check exists because the corresponding failure is invisible until
someone visits the profile and sees a broken page:

  markdown   GitHub sanitises README HTML before rendering it. A tag that
             gets stripped leaves no error anywhere -- the page just quietly
             loses a feature. This posts the README to GitHub's own
             /markdown endpoint and asserts the tags we depend on survived.
  assets     Every referenced file exists. A renamed SVG shows as a broken
             image on the one page where that costs the most.
  xml        Every SVG parses. A malformed one renders as a broken-image
             icon with no console error.
  budget     Size ceilings, per file and per page view.
  determinism  Renders twice from the same snapshot and compares bytes. This
             is what stops the nightly job committing churn forever.
  alt        Every image carries alt text.

Usage: python3 scripts/verify.py
"""

import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
README = os.path.join(ROOT, "README.md")

MAX_SVG_BYTES = 40 * 1024      # any single panel
MAX_VIEW_BYTES = 150 * 1024    # what one visitor actually downloads (one theme)

# Tags the page depends on. If GitHub's sanitiser ever drops one of these,
# the layout silently degrades, so we assert on them rather than hope.
REQUIRED_TAGS = ["picture", "source", "img", "details", "summary", "samp",
                 "blockquote", "table"]

failures = []
notes = []


def fail(check, message):
    failures.append(f"{check}: {message}")


def ok(check, message):
    notes.append(f"{check}: {message}")


# -- markdown sanitiser ------------------------------------------------------

def check_markdown():
    with open(README) as fh:
        body = fh.read()

    payload = json.dumps({"text": body, "mode": "markdown"}).encode()
    headers = {"Content-Type": "application/json",
               "Accept": "application/vnd.github+json",
               "User-Agent": "advait27-profile-verify"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"bearer {token}"

    req = urllib.request.Request("https://api.github.com/markdown",
                                 data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rendered = resp.read().decode()
    except (urllib.error.URLError, TimeoutError) as exc:
        ok("markdown", f"skipped, could not reach the API ({exc})")
        return

    for tag in REQUIRED_TAGS:
        if f"<{tag}" not in rendered:
            fail("markdown", f"<{tag}> did not survive GitHub's sanitiser")
    if "prefers-color-scheme" not in rendered:
        fail("markdown", "the dark-mode <source media> was stripped; "
                         "the page will not theme")
    ok("markdown", f"{len(REQUIRED_TAGS)} tags survived, dark-mode source intact")


# -- referenced assets exist -------------------------------------------------

def check_assets():
    with open(README) as fh:
        body = fh.read()
    refs = set(re.findall(r'(?:src|srcset)="([^"]+)"', body))
    local = [r for r in refs if not r.startswith(("http://", "https://", "data:"))]
    missing = [r for r in local if not os.path.exists(os.path.join(ROOT, r))]
    for r in missing:
        fail("assets", f"README references {r}, which does not exist")
    if not missing:
        ok("assets", f"all {len(local)} referenced files exist")

    # Every panel should be referenced in both themes, or it is dead weight.
    for path in sorted(glob.glob(os.path.join(ROOT, "svg", "*.svg"))):
        rel = os.path.relpath(path, ROOT)
        if rel not in refs:
            fail("assets", f"{rel} is generated but never referenced")


def check_alt():
    with open(README) as fh:
        body = fh.read()
    for img in re.findall(r"<img [^>]*>", body):
        if "alt=" not in img:
            fail("alt", f"image without alt text: {img[:70]}...")
    ok("alt", "every image has alt text")


# -- svg integrity -----------------------------------------------------------

def check_svgs():
    paths = sorted(glob.glob(os.path.join(ROOT, "svg", "*.svg")))
    if not paths:
        fail("xml", "no SVGs found; has render.py run?")
        return

    for path in paths:
        rel = os.path.relpath(path, ROOT)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            fail("xml", f"{rel} is not well-formed: {exc}")
            continue
        if not root.findall("{http://www.w3.org/2000/svg}title"):
            fail("a11y", f"{rel} has no <title> for assistive technology")

    ok("xml", f"{len(paths)} SVGs parse and carry <title>")


def check_budget():
    per_theme = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "svg", "*.svg"))):
        rel = os.path.relpath(path, ROOT)
        size = os.path.getsize(path)
        if size > MAX_SVG_BYTES:
            fail("budget", f"{rel} is {size / 1024:.1f} KB, over the "
                           f"{MAX_SVG_BYTES / 1024:.0f} KB per-file ceiling")
        theme = "dark" if rel.endswith("-dark.svg") else "light"
        per_theme[theme] = per_theme.get(theme, 0) + size

    for theme, total in sorted(per_theme.items()):
        if total > MAX_VIEW_BYTES:
            fail("budget", f"{theme} theme totals {total / 1024:.1f} KB, over "
                           f"the {MAX_VIEW_BYTES / 1024:.0f} KB page ceiling")
        else:
            ok("budget", f"{theme} theme {total / 1024:.1f} KB "
                         f"(ceiling {MAX_VIEW_BYTES / 1024:.0f} KB)")


# -- determinism -------------------------------------------------------------

def check_determinism():
    """Render twice and compare. See fetch_data.py for why this matters."""
    before = _digest()
    result = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "render.py")],
                            capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        fail("determinism", f"render.py failed:\n{result.stderr.strip()[:800]}")
        return
    after = _digest()

    drifted = sorted(k for k in before if before[k] != after.get(k))
    if drifted:
        fail("determinism", "re-rendering the same snapshot changed "
                            + ", ".join(drifted)
                            + " -- the nightly job would commit this every night")
    else:
        ok("determinism", f"{len(before)} files byte-identical across two renders")


def _digest():
    import hashlib
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "svg", "*.svg"))):
        with open(path, "rb") as fh:
            out[os.path.basename(path)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def main():
    check_determinism()   # first: it re-renders, and later checks read the output
    check_svgs()
    check_budget()
    check_assets()
    check_alt()
    check_markdown()

    for line in notes:
        print(f"  ok    {line}")
    for line in failures:
        print(f"  FAIL  {line}")

    if failures:
        print(f"\n{len(failures)} check(s) failed")
        sys.exit(1)
    print(f"\nall checks passed ({len(notes)})")


if __name__ == "__main__":
    main()
