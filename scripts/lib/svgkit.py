"""A small SVG writer.

Everything is monospace, which is the whole reason the layout maths works:
JetBrains Mono has an advance width of exactly 600/1000 em, so the width of
any string is len(s) * 0.6 * font_size. No measuring, no guessing, and the
same number on every machine -- once the font is embedded (see fontkit).
"""

from xml.sax.saxutils import escape, quoteattr

ADVANCE = 0.6  # em, verified against JetBrainsMono-Regular head/hmtx


def text_width(s, size):
    """Rendered width of a monospace string at a given font-size."""
    return len(s) * ADVANCE * size


def esc(s):
    return escape(str(s))


def attr(v):
    return quoteattr(str(v))


def fmt(n):
    """Fixed-precision number formatting.

    Determinism guard: float repr differences of 1e-12 between two runs would
    otherwise produce a diff, and the nightly workflow would commit it. Two
    decimals is far below a pixel at our sizes.
    """
    return f"{float(n):.2f}".rstrip("0").rstrip(".") or "0"


class Svg:
    def __init__(self, width, height, title, desc=None, font_css=""):
        self.w = width
        self.h = height
        self.title = title
        self.desc = desc
        self.font_css = font_css
        self.css = []
        self.body = []
        self.defs = []
        # Only glyphs that get painted count toward the font subset. <title>
        # and <desc> are read by assistive tech, never rendered, so they are
        # free to say things the subset does not cover.
        self._chars = set()

    # -- content -----------------------------------------------------------

    def add(self, markup):
        self.body.append(markup)

    def define(self, markup):
        self.defs.append(markup)

    def style(self, rule):
        self.css.append(rule)

    def note_chars(self, s):
        """Record glyphs so fontkit can subset to exactly what this file uses."""
        self._chars |= set(str(s))

    @property
    def charset(self):
        return self._chars

    # -- primitives --------------------------------------------------------
    #
    # `extra` is raw attributes; `anim` is child elements (SMIL). They are
    # separate parameters because mixing them up produces `<rect <animate/>/>`,
    # which is not well-formed and renders as a broken-image icon with no
    # error message anywhere.

    @staticmethod
    def _wrap(tag, attrs, anim, content=""):
        joined = " ".join(a for a in attrs if a)
        if anim or content:
            return f"<{tag} {joined}>{content}{anim}</{tag}>"
        return f"<{tag} {joined}/>"

    def text(self, x, y, s, size=12, fill="#000", weight=None, anchor=None,
             opacity=None, extra="", anim="", track=True):
        if track:
            self.note_chars(s)
        a = [f'x="{fmt(x)}"', f'y="{fmt(y)}"', f'font-size="{fmt(size)}"',
             f'fill="{fill}"']
        if weight:
            a.append(f'font-weight="{weight}"')
        if anchor:
            a.append(f'text-anchor="{anchor}"')
        if opacity is not None:
            a.append(f'opacity="{fmt(opacity)}"')
        if extra:
            a.append(extra.strip())
        return self._wrap("text", a, anim, esc(s))

    def rect(self, x, y, w, h, fill, rx=None, opacity=None, extra="", anim=""):
        a = [f'x="{fmt(x)}"', f'y="{fmt(y)}"', f'width="{fmt(w)}"',
             f'height="{fmt(h)}"', f'fill="{fill}"']
        if rx is not None:
            a.append(f'rx="{fmt(rx)}"')
        if opacity is not None:
            a.append(f'opacity="{fmt(opacity)}"')
        if extra:
            a.append(extra.strip())
        return self._wrap("rect", a, anim)

    def line(self, x1, y1, x2, y2, stroke, width=1, opacity=None, extra="",
             anim=""):
        a = [f'x1="{fmt(x1)}"', f'y1="{fmt(y1)}"', f'x2="{fmt(x2)}"',
             f'y2="{fmt(y2)}"', f'stroke="{stroke}"',
             f'stroke-width="{fmt(width)}"']
        if opacity is not None:
            a.append(f'opacity="{fmt(opacity)}"')
        if extra:
            a.append(extra.strip())
        return self._wrap("line", a, anim)

    def path(self, d, fill="none", stroke=None, width=1, opacity=None,
             extra="", anim=""):
        a = [f'd="{d}"', f'fill="{fill}"']
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{fmt(width)}"']
        if opacity is not None:
            a.append(f'opacity="{fmt(opacity)}"')
        if extra:
            a.append(extra.strip())
        return self._wrap("path", a, anim)

    # -- animation ---------------------------------------------------------
    #
    # SMIL only. GitHub's sanitiser strips <script>, but it runs <animate>.
    # Every animation freezes: the page draws itself once and stops, rather
    # than looping in the reader's peripheral vision forever.

    @staticmethod
    def anim(attribute, frm, to, dur, begin=0, splines=".2 .7 .2 1"):
        """An eased attribute animation that freezes at its end value.

        Written as `values="a;b"` rather than `from`/`to`. keyTimes is only
        defined against a values list, and Chrome silently drops the whole
        animation when it is paired with from/to -- the attribute simply stays
        at its start value, with no console error and no visual clue beyond a
        bar that never fills.
        """
        return (f'<animate attributeName="{attribute}" '
                f'values="{fmt(frm)};{fmt(to)}" dur="{fmt(dur)}s" '
                f'begin="{fmt(begin)}s" fill="freeze" calcMode="spline" '
                f'keyTimes="0;1" keySplines="{splines}"/>')

    @staticmethod
    def fade(to=1, dur=0.5, begin=0, frm=0):
        return (f'<animate attributeName="opacity" from="{fmt(frm)}" to="{fmt(to)}" '
                f'dur="{fmt(dur)}s" begin="{fmt(begin)}s" fill="freeze"/>')

    # -- output ------------------------------------------------------------

    def render(self):
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{fmt(self.w)}" height="{fmt(self.h)}" '
            f'viewBox="0 0 {fmt(self.w)} {fmt(self.h)}" '
            f'role="img" aria-labelledby="t d">'
        ]
        parts.append(f'<title id="t">{esc(self.title)}</title>')
        parts.append(f'<desc id="d">{esc(self.desc or self.title)}</desc>')

        css = self.font_css + (
            "text{font-family:'JBM',ui-monospace,SFMono-Regular,"
            "'SF Mono',Menlo,Consolas,monospace;"
            "font-variant-ligatures:none;white-space:pre}"
        ) + "".join(self.css)
        parts.append(f"<style>{css}</style>")

        if self.defs:
            parts.append("<defs>" + "".join(self.defs) + "</defs>")
        parts.extend(self.body)
        parts.append("</svg>")
        return "".join(parts)
