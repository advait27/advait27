# How this profile builds itself

Everything on the profile page is drawn by this repository. No stats cards, no
badge CDNs, no third-party image services — nothing on the page that can
rate-limit, go down, or restyle itself without warning.

```
data/snapshot.json  <-- scripts/fetch_data.py   GraphQL, nightly, stdlib only
        |
        v
scripts/render.py   -->  svg/*.svg  (light + dark)  and the README text fallback
        |
        v
scripts/verify.py   -->  CI: sanitiser, assets, budget, determinism, alt text
```

Three files matter. `fetch_data.py` talks to the API and writes a snapshot.
`render.py` reads only that snapshot and writes SVGs — it never touches the
network, so the same snapshot always produces the same bytes. `verify.py`
proves it.

---

## What GitHub actually allows

Tested by posting the README to GitHub's own rendering API (`POST /markdown`),
which applies the same sanitiser as the site, and reading back what survived.

**Kept:** `<picture>`, `<source media>`, `<img>`, `<details>`, `<summary>`,
`<samp>`, `<kbd>`, `<sub>`, `<sup>`, `<blockquote>`, `<b>`, `<br>`, tables,
`width` on `<img>`.

**Stripped:** `<style>` blocks, `style=` attributes, `class=`, inline `<svg>`,
`<script>`, `<font>`.

Two behaviours that aren't documented anywhere and are worth knowing:

- GitHub wraps `<picture>` in its own `<themed-picture>` custom element. Theme
  switching is first-class, not a trick.
- Supplying a `height` attribute on an `<img>` makes GitHub inject
  `max-height` alongside `height:auto`. Useful for a fixed-height rule,
  surprising for anything else, so these panels set `width` only.

Consequences: you cannot change the font of README *text* — only GitHub's sans
or its monospace. Anything in your own typeface has to be an image. And motion
must be SMIL inside the SVG, because scripts are stripped.

## The private-contributions trap

The most consequential finding here, and the one most guides get wrong.

A widely-repeated claim is that the built-in `GITHUB_TOKEN` returns the same
contribution numbers as a personal token. For this account it does not:

```
contributionCalendar.totalContributions   608
restrictedContributionsCount              415   <- 68%, private
totalCommitContributions                  175
```

`GITHUB_TOKEN` runs as `github-actions[bot]`, which cannot see private
contributions. On the default token this profile would render **193** instead
of 608 and silently understate the year by two thirds.

The workflow therefore prefers a `PROFILE_TOKEN` secret (a personal access
token with `read:user`) and falls back to `GITHUB_TOKEN`. When the fallback is
in use, `restrictedContributionsCount` comes back as zero, and the charts
relabel themselves "public contributions" rather than quietly showing a
smaller number under the same words.

## Why languages are ranked by repository

Ranked by bytes — what every stats card shows — this account reads as:

| by bytes | | by repository | |
|:--|--:|:--|--:|
| Jupyter Notebook | 74.2% | Python | 45.9% |
| HTML | 13.1% | Jupyter Notebook | 37.8% |
| Python | 9.8% | HTML | 13.5% |

Notebooks store rendered cell outputs — plots, images — as base64 inside their
own JSON, and Linguist counts all of it as authored code. Twenty-one megabytes
of embedded chart PNGs become "Jupyter Notebook, 74%".

Both views are in the snapshot. The panel shows the one that isn't misleading.

## Determinism

The nightly job commits. Anything non-deterministic in the pipeline therefore
becomes a commit every single night, forever. Four sources, all found the hard
way:

1. **The contribution window.** Left alone, `contributionsCollection` measures
   "the past year" from the instant of the request, so two runs minutes apart
   bucket days into different weeks and shift the chart by a fraction of a
   pixel. Pinned to whole UTC days.

2. **Repository visibility.** A personal token sees private repos; the
   workflow's token does not. Without `privacy: PUBLIC, isFork: false`, the
   language split depends on who ran the script.

3. **Float formatting.** Coordinates are emitted at fixed precision. A
   `1e-12` difference in a float repr is still a diff.

4. **Font subsetting.** This one is genuinely surprising: brotli, underneath
   fontTools' woff2 writer, produces a stream one byte longer on some runs
   than others from identical input. Two stable variants, roughly 50/50. So
   subsets are built once, content-addressed by charset, and committed under
   `assets/subset/`; rendering only base64s the committed bytes. As a bonus,
   the nightly job needs no fontTools, no brotli, and no `pip install` at all.

`verify.py` renders twice and compares hashes, so a regression here fails CI
instead of being discovered a month of commits later.

## Fonts

An SVG loaded through an `<img>` tag cannot fetch subresources — browsers
refuse it for image documents — so an external font URL silently does nothing.
A `@font-face` with a base64 `data:` URI does work, which means every SVG
carries its own copy of the font.

That makes charset size the whole game. Each panel is subset to exactly the
glyphs it can draw, which keeps the worst panel around 9 KB of font and the
whole page at 88 KB per theme.

The catch: a panel's charset must not depend on the day's numbers, or a
contribution count going from 608 to 610 would need a subset that isn't
committed. So panels *declare* a charset — static copy, plus every digit and
punctuation mark a value could produce, plus the alphabet where they print
repo or language names. `render.py` compares what was declared against what was
actually drawn and fails on drift, because the quiet failure mode is a browser
falling back to its own monospace and breaking every width calculation on the
page.

JetBrains Mono is used throughout (SIL OFL 1.1, licence shipped in
`assets/fonts/`). Its advance width is exactly 600/1000 em, so the width of any
string is `len(s) * 0.6 * font_size` — which is why the layout maths needs no
measuring and gives the same answer on every machine.

## Chart choices

Daily contributions are sparse and discrete, so they get one cell per day: a
zero day is empty space. A line through `0, 0, 11, 0, 0, 10` would claim values
that never existed. Weekly totals are continuous enough to justify an area, so
that is the only place a filled curve appears.

The headline row shows commits, pull requests, active days, and repositories.
Code reviews sat at zero, and a zero does not earn a quarter of the widest row
on the page.

## Accessibility

The README uses real `##` markdown headings, so GitHub's file outline and
heading anchors both work. Rendering headings as SVG — which some guides
recommend, to get a custom typeface on them — empties the outline and removes
every anchor link. Not worth it.

Beyond that: every SVG carries `role="img"` with `<title>` and `<desc>`; every
`<img>` has real alt text; and the numbers are repeated as a plain markdown
table inside a `<details>` block, so the page still says something when images
don't load at all. `verify.py` enforces the alt text and the `<title>`.

## Gotchas worth writing down

- **A screenshot of an animated SVG lies.** SMIL inside an `<img>` runs on the
  image's own timeline, and a headless screenshot captures it a few frames in —
  half-filled bars, invisible text. Chrome's `--virtual-time-budget` does not
  drive that clock either. Inline the SVG and call `setCurrentTime()` to check
  a final state.
- **`animVal` does not show SMIL on SVG geometry.** Blink applies animated
  `width`/`height`/`x`/`y` through the CSS cascade, so `rect.width.animVal`
  keeps reporting the base value while the shape animates correctly on screen.
  Measuring it will convince you of a bug that isn't there.
- **`<animate>` is a child element, not an attribute.** Emitting
  `<rect ... <animate/>/>` produces a broken-image icon and no error anywhere.
- **`<use>` plus one animation per column** takes the year grid from 68 KB to
  32 KB versus 365 individually animated rects.
- **A new profile README is cached.** If it doesn't show up on the profile,
  edit it once through the web UI to force a refresh.
- **Pinned repositories and the bio cannot be set through the API.** No
  GraphQL mutation exists. Both are manual, in the UI.

## Running it locally

```bash
GITHUB_TOKEN=$(gh auth token) GH_LOGIN=advait27 python3 scripts/fetch_data.py
python3 scripts/render.py
python3 scripts/verify.py
```

Only one command needs anything installed. After changing static copy in
`scripts/lib/panels.py`, rebuild the font subsets and commit what lands in
`assets/subset/`:

```bash
pip install fonttools brotli
python3 scripts/render.py --build-fonts
```

## Credit

The idea of a profile that draws its own graphics, and the survey of what
GitHub's sanitiser keeps, come from
[A GitHub profile that generates itself](https://agreeable-credit-859.notion.site/A-GitHub-profile-that-generates-itself-3abedfe9a65a81e4afc9daed90cb4e7e).
The private-contributions finding, the by-repository language ranking, the
committed-subset approach to determinism, the dual-theme rendering, and the
verification harness are this repository's own.
