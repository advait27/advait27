"""Font subsetting, inlined as base64.

Three constraints shape this, in order of how much trouble they cause.

1. An SVG loaded through an <img> tag cannot fetch subresources. Browsers
   refuse it for image documents, so an external font URL (Google Fonts, a
   raw.githubusercontent path, anything) silently does nothing. A @font-face
   with a base64 data: URI is the only thing that works, which means every
   SVG carries its own copy of the font.

2. Because every file carries a copy, the charset has to be small. A full
   TTF inlined into each panel would be several megabytes across the page.
   So each panel is subset to exactly the glyphs it can draw.

3. Subsetting is not reproducible. brotli, underneath fontTools' woff2
   writer, emits a stream one byte longer on some runs than others -- same
   input, same version, two stable variants. Re-subsetting on every render
   would therefore rewrite every SVG at random and the nightly job would
   commit the churn.

Hence: subsets are built once by `python3 scripts/render.py --build-fonts`,
content-addressed by charset, and committed under assets/subset/. Rendering
only reads those bytes and base64s them, so the nightly workflow needs no
fontTools, no brotli, and nothing but the standard library.

A panel's charset must not depend on the day's numbers, or the nightly run
would need a subset that isn't committed. Panels declare their charset as
static copy plus VOLATILE (and ALNUM where they print repo or language
names), which covers every value the data can produce.
"""

import base64
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
SUBSET_DIR = os.path.join(ROOT, "assets", "subset")

WEIGHTS = {
    400: "JetBrainsMono-Regular.ttf",
    700: "JetBrainsMono-Bold.ttf",
    800: "JetBrainsMono-ExtraBold.ttf",
}

# Glyphs any numeric value might produce. Folded into every panel so that a
# contribution count going from 1,247 to 1,250 cannot change the charset.
VOLATILE = "0123456789.,%+-:/()"

# For panels that print names they do not control: repos, languages. The
# ellipsis belongs here because those are exactly the strings _shorten()
# truncates, and it is only ever produced by truncating one of them.
ALNUM = ("abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
         "0123456789_-.+#/ \u2026")

# Frozen OpenType timestamp (seconds since 1904-01-01). fontTools would
# otherwise carry the source font's dates through into the output.
EPOCH = 3406000000


def _key(charset, weight):
    text = "".join(sorted(set(charset) | {" "}))
    digest = hashlib.sha256(f"{weight} {text}".encode()).hexdigest()[:16]
    return f"jbm-{weight}-{digest}.woff2"


def _path(charset, weight):
    return os.path.join(SUBSET_DIR, _key(charset, weight))


def build(charset, weight):
    """Subset and write to assets/subset/. Needs fontTools + brotli."""
    from fontTools import subset
    from fontTools.ttLib import TTFont

    font = TTFont(os.path.join(FONT_DIR, WEIGHTS[weight]))

    opts = subset.Options()
    opts.layout_features = []      # no GSUB/GPOS; monospace needs none
    opts.hinting = False
    opts.notdef_outline = False
    opts.name_IDs = []
    opts.name_legacy = False
    opts.name_languages = []
    opts.recalc_timestamp = False  # never stamp "now" into the output
    opts.drop_tables += ["FFTM", "GDEF", "DSIG"]

    sub = subset.Subsetter(options=opts)
    sub.populate(text="".join(sorted(set(charset) | {" "})))
    sub.subset(font)

    font["head"].created = EPOCH
    font["head"].modified = EPOCH

    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)

    os.makedirs(SUBSET_DIR, exist_ok=True)
    dest = _path(charset, weight)
    with open(dest, "wb") as fh:
        fh.write(buf.getvalue())
    return dest


class MissingSubset(Exception):
    """A panel asked for glyphs that have no committed subset."""


# Flipped on by `render.py --build-fonts`, which is the only path allowed to
# invoke fontTools. Rendering never rebuilds implicitly: a subset regenerated
# mid-run would land bytes that differ from the committed ones (brotli is not
# reproducible) and the nightly job would commit the churn.
AUTOBUILD = False

# Every subset path face_css() resolved this run. --build-fonts uses it to
# delete orphans, so a charset change does not leave the old file behind for
# someone to wonder about later.
USED = set()


def face_css(charset, weights=(400, 700)):
    """@font-face rules for `charset`, read from committed subsets.

    Standard library only. Raises MissingSubset if the panel's charset has
    drifted from what is committed, which is a loud failure by design: the
    quiet version is a browser falling back to its own monospace and
    silently breaking every width calculation on the page.
    """
    rules = []
    for w in weights:
        path = _path(charset, w)
        if not os.path.exists(path) and AUTOBUILD:
            build(charset, w)
        if not os.path.exists(path):
            raise MissingSubset(
                f"no subset for weight {w} at {os.path.relpath(path, ROOT)}\n"
                f"  charset ({len(set(charset))} glyphs): "
                f"{''.join(sorted(set(charset)))!r}\n"
                f"  run: python3 scripts/render.py --build-fonts"
            )
        USED.add(os.path.abspath(path))
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        rules.append(
            f"@font-face{{font-family:'JBM';font-style:normal;"
            f"font-weight:{w};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64})format('woff2')}}"
        )
    return "".join(rules)
