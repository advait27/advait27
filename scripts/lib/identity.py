"""Static identity graphics, separate from measured GitHub activity.

All copy is based on the existing profile. Former-role outcomes retain their
employer labels; technology names describe tools used, never skill scores.
"""

from .fontkit import ALNUM, VOLATILE
from .svgkit import new_panel

W = 880


def _panel(height, title, desc, theme, width=W):
    # One shared alphabet keeps the extra panels small and their font subsets
    # stable when individual phrases change.
    svg = new_panel(width, height, title, desc, set(ALNUM + VOLATILE + '~'), (400, 700))
    svg.add(svg.rect(.5, .5, width - 1, height - 1, theme['surface'], rx=18,
                     extra=f'stroke="{theme["rule"]}"'))
    return svg


def _circle(svg, x, y, r, fill, stroke=None):
    edge = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ''
    svg.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{edge}/>')


def hero(snap, t):
    svg = _panel(330, f'{snap["name"]} - Applied AI and forward deployed engineering',
                 'Advait Dharmadhikari. Building AI that holds up in the real world. '
                 'Agentic systems, RAG, evaluation and enterprise deployment. '
                 'Dublin, Ireland. Open to AI engineering and consulting opportunities.', t)
    # Blueprint field is decorative, with no implied performance measurement.
    for x in range(578, 865, 22):
        for y in range(28, 290, 22):
            _circle(svg, x, y, .8, t['rule'])
    svg.add(svg.rect(30, 30, 30, 24, t['accent'], rx=6))
    svg.add(svg.text(45, 46, 'AD', 12, t['surface'], weight=700, anchor='middle'))
    svg.add(svg.text(72, 46, 'APPLIED AI / FORWARD DEPLOYED ENGINEERING', 11, t['accent'], weight=700))
    svg.add(svg.text(30, 112, 'Advait', 50, t['fg'], weight=700))
    svg.add(svg.text(30, 167, 'Dharmadhikari', 45, t['fg'], weight=700))
    svg.add(svg.text(32, 205, 'Building AI that holds up', 18, t['muted']))
    svg.add(svg.text(32, 231, 'in the real world.', 18, t['muted']))
    svg.add(svg.line(30, 259, 535, 259, t['rule']))
    svg.add(svg.text(32, 286, 'DUBLIN, IE  /  AGENTS + RAG + EVALUATION', 11, t['faint']))
    svg.add(svg.text(32, 308, 'OPEN TO AI ENGINEERING + CONSULTING', 10.5, t['accent'], weight=700))

    # A feedback circuit: context and tools feed an agent; verified evidence
    # flows back. The labels deliberately describe the engineering approach.
    for x, y, xx, yy in [(625, 82, 725, 154), (818, 82, 725, 154),
                          (725, 154, 625, 231), (725, 154, 818, 231)]:
        svg.add(svg.line(x, y, xx, yy, t['accent'], 1.2, opacity=.5))
    svg.add(svg.path('M625 231 L586 231 L586 82 L625 82', stroke=t['rule'], width=1.5,
                     extra='stroke-dasharray="4 5"'))
    svg.add(svg.path('M818 231 L850 231 L850 82 L818 82', stroke=t['rule'], width=1.5,
                     extra='stroke-dasharray="4 5"'))
    for x, y, label in [(625, 82, 'CONTEXT'), (818, 82, 'TOOLS'),
                         (625, 231, 'EVALS'), (818, 231, 'EVIDENCE')]:
        svg.add(svg.rect(x - 44, y - 16, 88, 32, t['raised'], rx=8,
                         extra=f'stroke="{t["rule"]}"'))
        svg.add(svg.text(x, y + 4, label, 10, t['muted'], anchor='middle'))
    _circle(svg, 725, 154, 47, t['surface'], t['accent'])
    _circle(svg, 725, 154, 38, t['raised'], t['rule'])
    svg.add(svg.text(725, 159, 'AGENT', 13, t['accent'], weight=700, anchor='middle'))
    svg.add(svg.text(725, 290, 'DESIGN. VERIFY. DEPLOY.', 11, t['signal'], anchor='middle'))
    return svg


def impact(snap, t):
    items = [('80-90%', 'lower LLM token spend', 'Frensei / previous role'),
             ('~60%', 'fewer unreliable outputs', 'Frensei / internal eval set'),
             ('~20%', 'operational cost savings', 'IndiGo / 300+ aircraft fleet')]
    svg = _panel(156, 'Selected outcomes from previous roles',
                 '; '.join(' / '.join(row) for row in items), t)
    svg.add(svg.text(24, 29, 'SELECTED IMPACT / PREVIOUS ROLES', 10, t['faint'], weight=700))
    for i, (value, label, source) in enumerate(items):
        x = 24 + i * 290
        if i:
            svg.add(svg.line(x - 16, 49, x - 16, 131, t['rule']))
        svg.add(svg.text(x, 83, value, 32, t['accent'], weight=700))
        svg.add(svg.text(x, 108, label, 12, t['fg']))
        svg.add(svg.text(x, 131, source, 10, t['faint']))
    return svg


PROJECTS = {
    'eadip': ('01', 'EADIP', 'Enterprise decision intelligence',
              ['A governed multi-agent platform for business questions.',
               'Plan, retrieve, query and independently verify each claim.'],
              'Python / FastAPI / Postgres / Qdrant / Neo4j',
              ['PLAN', 'RETRIEVE', 'VERIFY']),
    'veritas': ('02', 'VERITAS', 'Hypothesis-driven data investigation',
                ['A self-hosted MCP server for evidence-backed analysis.',
                 'Test hypotheses. Trace numeric claims to executed artifacts.'],
                'Python / MCP / DuckDB / Docker',
                ['HYPOTHESIS', 'QUERY', 'EVIDENCE']),
}


def _project(key, t):
    index, name, subtitle, lines, stack, nodes = PROJECTS[key]
    svg = _panel(192, f'{name} - {subtitle}', ' '.join(lines) + ' ' + stack, t)
    svg.add(svg.text(24, 29, 'SELECTED BUILD / ' + index, 10, t['faint'], weight=700))
    svg.add(svg.text(24, 67, name, 28, t['fg'], weight=700))
    svg.add(svg.text(24, 92, subtitle, 13, t['accent']))
    for i, line in enumerate(lines):
        svg.add(svg.text(24, 122 + i * 20, line, 11.5, t['muted']))
    svg.add(svg.text(24, 173, stack, 10, t['faint']))
    for i, node in enumerate(nodes):
        y = 41 + i * 48
        if i:
            svg.add(svg.line(756, y - 22, 756, y - 5, t['accent'], 1.3))
        svg.add(svg.rect(683, y - 5, 146, 30, t['raised'], rx=7,
                         extra=f'stroke="{t["rule"]}"'))
        svg.add(svg.text(756, y + 14, node, 10, t['accent'] if i == 2 else t['muted'],
                         anchor='middle', weight=700))
    svg.add(svg.path('M846 28 L854 28 L854 36 M845 37 L854 28',
                     stroke=t['accent'], width=1.5))
    return svg


def eadip(snap, t):
    return _project('eadip', t)


def veritas(snap, t):
    return _project('veritas', t)


def skills(snap, t):
    rows = [('BUILD', 'Python / TypeScript / SQL'),
            ('ORCHESTRATE', 'LangGraph / MCP / FastAPI'),
            ('GROUND', 'Postgres / Qdrant / Neo4j'),
            ('SHIP', 'Docker / GCP / Azure')]
    svg = _panel(184, 'Core engineering toolkit',
                 '; '.join(label + ': ' + tools for label, tools in rows), t, width=432)
    svg.add(svg.text(18, 28, 'CORE TOOLKIT', 11, t['accent'], weight=700))
    for i, (label, tools) in enumerate(rows):
        y = 57 + i * 34
        svg.add(svg.text(18, y, label, 9, t['faint'], weight=700))
        svg.add(svg.text(126, y, tools, 10.8, t['fg']))
        if i < len(rows) - 1:
            svg.add(svg.line(18, y + 14, 414, y + 14, t['rule']))
    return svg
