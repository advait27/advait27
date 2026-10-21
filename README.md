<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/hero-dark.svg">
  <img alt="Advait Dharmadhikari. Applied AI and forward deployed engineering. Building AI that holds up in the real world. Dublin, Ireland. Open to AI engineering and consulting." src="svg/hero-light.svg" width="880">
</picture>
</p>

<p align="center">
  <samp>
    <a href="https://www.linkedin.com/in/advaitdharmadhikari">LinkedIn</a> ·
    <a href="https://advaitdharmadhikari.netlify.app">Portfolio</a> ·
    <a href="https://medium.com/@advaitdharmadhikari7">Writing</a> ·
    <a href="mailto:advaitdharmadhikari27@gmail.com">Email</a>
  </samp>
</p>

# From business questions to production AI

I'm **Advait**, an AI engineer based in **Dublin, Ireland**. I build agentic
systems, retrieval pipelines and evaluation infrastructure that turn ambiguous
business problems into software people can use and trust.

My path into engineering started in business analytics and operations. That
perspective still shapes how I build: start with the decision, ground the
system in evidence, and measure whether it helps.

> **Open to opportunities:** Founding AI Engineer, Applied AI Engineer,
> Forward Deployed Engineer and AI consulting — in Ireland, across Europe
> and globally.

<p>
<samp>
<a href="#selected-work">Selected work</a> /
<a href="#research">Research</a> /
<a href="#engineering-toolkit">Toolkit</a> /
<a href="#experience">Experience</a> /
<a href="#github-activity">Activity</a>
</samp>
</p>

## What I focus on

| Build useful intelligence | Make it dependable | Take it into production |
|:--|:--|:--|
| Agents, RAG, tool use and decision intelligence | Evaluation, grounded claims, observability and human oversight | APIs, tenant isolation, secure integrations and enterprise deployment |

My independent work includes **EADIP**, **Veritas**, open-source Python
packages and research into the reliability and oversight of agentic AI.

## Selected work

<p>
<a href="https://github.com/advait27/EADIP">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/eadip-dark.svg">
  <img alt="Explore EADIP: a governed multi-agent platform for business questions, with independent verification of numeric claims." src="svg/eadip-light.svg" width="880">
</picture>
</a>
</p>

**[EADIP — Enterprise Autonomous Decision Intelligence Platform](https://github.com/advait27/EADIP)**
<br>A governed system that investigates business questions end to end:
plan, retrieve, query, verify and report. An independent Verification Agent
re-derives numeric claims before they enter a report. Human approval gates
side-effecting actions, Postgres row-level security isolates tenants, and
GraphRAG grounds metric-lineage questions. Built across 12 delivery phases
with 274 unit and integration tests.

<p>
<a href="https://github.com/advait27/Veritas">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/veritas-dark.svg">
  <img alt="Explore Veritas: a self-hosted MCP server for hypothesis-driven, evidence-backed data investigation." src="svg/veritas-light.svg" width="880">
</picture>
</a>
</p>

**[Veritas — hypothesis-driven investigation over MCP](https://github.com/advait27/Veritas)**
<br>A self-hosted MCP server that builds and tests hypothesis trees over CSV,
Parquet and Excel data using DuckDB. Numeric claims trace to executed
artifacts; opportunity and risk discovery uses false-discovery-rate control
and a public evaluation suite of planted-cause datasets.

<details>
<summary><b>Six published Python packages + more projects</b></summary>

| Package | Purpose |
|:--|:--|
| [hallucimap](https://pypi.org/project/hallucimap/) | Hallucination-risk scoring and segment-level triage for LLM outputs |
| [fraudguard](https://pypi.org/project/fraudguard/) | Fraud and anomaly classification for financial transactions |
| [finfeatures](https://pypi.org/project/finfeatures/) | Financial and time-series feature engineering |
| [finance-automl](https://pypi.org/project/finance-automl/) | Financial time-series AutoML with leakage prevention |
| [esgprofiler](https://pypi.org/project/esgprofiler/) | ESG scoring and profiling with NLP |
| [mlopter](https://pypi.org/project/mlopter/) | ML-enhanced optimization with pluggable solvers |

More builds: [ChartSense](https://github.com/advait27/chartsense) ·
[Jarvis](https://github.com/advait27/jarvis) ·
[AI Cost & Growth Optimizer](https://github.com/advait27/ai-cost-growth-optimizer) ·
[Market Pulse AI](https://github.com/advait27/market-pulse-AI).

</details>

## Impact from previous roles

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/impact-dark.svg">
  <img alt="Previous-role outcomes: 80–90% lower LLM token spend and approximately 60% fewer unreliable outputs at Frensei; approximately 20% operational cost savings at IndiGo." src="svg/impact-light.svg" width="880">
</picture>
</p>

These outcomes come from earlier work, including my **former role at Frensei
Innovation Labs**. The output-reliability reduction was measured on an internal
evaluation set of labelled broker threads.

| Outcome | Previous work |
|:--|:--|
| **80–90% lower LLM token spend per broker** | Targeted-surveillance architecture at Frensei: header scan → PII-masked body fetch → LLM classification |
| **~60% fewer hallucinated or inconsistent outputs** | Production evaluation, structured-output checks and calibrated confidence thresholds at Frensei |
| **~20% operational cost savings** | ML optimization across a 300+ aircraft fleet at IndiGo |
| **~40% decision-quality improvement** | Production ML and BI frameworks on GCP / Azure at IndiGo |
| **25% new-business growth** | A 15-member analyst team at CHRIST Consulting |

## Research

**Forward Deployed Engineering: A Systems Engineering Perspective**
<br><samp>First-author preprint / 2026</samp>
<br>Studies forward deployed engineering as a systems-engineering discipline
through a multivocal literature review, mapping it to ISO/IEC/IEEE 15288
lifecycle processes and proposing a cross-organizational enterprise-AI
deployment lifecycle.

**What Agent Traces Cannot Tell You: Evidentiary Adequacy of Runtime Records for Agentic AI Oversight**
<br><samp>First-author preprint + open benchmark / 2026</samp>
<br>Tests whether runtime records support the findings of fact required for AI
oversight. Across 1,200 enterprise agent trajectories, six determination
families and four record conditions, coverage rises from **16.3%** for action
logs and OpenTelemetry GenAI spans to **100%** for a labelled substrate.

Ongoing research: **context engineering, enterprise agents, AI evaluation
and observability**.

## Engineering toolkit

| Layer | Tools and practices |
|:--|:--|
| Languages & APIs | Python · TypeScript · SQL · FastAPI · MCP |
| Agents & retrieval | LangGraph · multi-agent orchestration · RAG · semantic search · tool calling · context and graph engineering |
| Data & storage | PostgreSQL · DuckDB · Supabase · Redis · Qdrant · Neo4j |
| Reliability | Evaluation harnesses · structured outputs · confidence scoring · OpenTelemetry · pytest · mypy · ruff |
| Deployment | Docker · GCP · Azure · CI · multi-tenant SaaS · hybrid and VPC deployment |
| Security | PII masking · prompt-injection defense · OAuth 2.0 · row-level security · AES-256-GCM |

## Experience

**Founding AI Engineer & Product Lead — Frensei Innovation Labs / ClawbackVault AI**
<br><samp>Previous role · Dublin, Ireland</samp>
<br>Built AI architecture, enterprise deployment and product strategy for a
compliance-intelligence platform serving financial-services broker-dealers.
Developed a four-tier signal engine across 15+ behavioural categories,
privacy-first surveillance and agentic compliance-research workflows.
Built and led a 15-person cross-functional team across AI engineering,
cybersecurity and analytics.

**Business Analyst & ML Engineer — IndiGo / InterGlobe Aviation**
<br><samp>Jan 2024 – Aug 2025 · Gurugram, India</samp>
<br>Delivered ML-driven optimization and decision intelligence across a 300+
aircraft fleet. Promoted into ML engineering within six months, connecting
data science with executive decision-making.

**Business Intelligence Engineer, Business Technology & Product — IndiGo**
<br><samp>Jun 2023 – Dec 2023 · Gurugram, India</samp>

**Teaching Assistant, Digital Technologies in Business — University College Dublin**
<br><samp>Jan – May 2026</samp>
<br>Taught postgraduate tutorials on AI in business, digital transformation
and data-driven decision-making for 150+ students.

<details>
<summary><b>Earlier experience & mentoring</b></summary>

**Business Development Analyst, Team Lead — CHRIST Consulting**
<br><samp>Jun 2021 – Jun 2022 · India</samp>
<br>Led a 15-member analyst team on market-entry and growth strategy;
approximately 15% improvement in renewals and upsells.

**Business Analytics & ML Mentor — topmate.io**
<br><samp>2025 – 2026</samp>
<br>Coached professionals on LLM application development and moving into
AI engineering roles.

Earlier internships in data science and analytics: IndiGo, LetsGrowMore,
The Sparks Foundation and EntryLevel (2020–2023).

</details>

## Education

- **MSc, Business Analytics** — UCD Michael Smurfit Graduate Business School *(Sep 2025 – Aug 2026)*
- **PG Professional Certification, AI & Machine Learning** — IIT Kanpur *(2023 – 2024)*
- **BBA, Business Analytics & Data Science** — Christ University, Bangalore *(2020 – 2023)*

Honours: **Global Leadership Programme**, awarded by the Dean of the UCD
College of Business, and the **UCD Advantage Award** (2026).

## GitHub activity

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/pulse-dark.svg">
  <img alt="Measured GitHub contributions over the last 365 days, with weekly totals and activity statistics." src="svg/pulse-light.svg" width="880">
</picture>
</p>

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/streak-dark.svg">
  <img alt="Measured current streak, longest streak and all-time GitHub contributions." src="svg/streak-light.svg" width="432">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/skills-dark.svg">
  <img alt="Core toolkit: Python, TypeScript, SQL, LangGraph, MCP, FastAPI, Postgres, Qdrant, Neo4j, Docker, GCP and Azure." src="svg/skills-light.svg" width="432">
</picture>
</p>

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/year-dark.svg">
  <img alt="Daily GitHub contributions over the last year; one cell per day." src="svg/year-light.svg" width="880">
</picture>
</p>

<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="svg/now-dark.svg">
  <img alt="Most recently pushed public repositories; generated from the GitHub API." src="svg/now-light.svg" width="880">
</picture>
</p>

<details>
<summary>Activity data, language breakdown and repository links as text</summary>

<!-- data:start -->

| | |
|:--|--:|
| Contributions (365 days) | 1,442 |
| Commits / pull requests / reviews | 193 / 10 / 0 |
| Current streak | 1 days |
| Longest streak | 10 days |
| All-time contributions | 1,575 |
| Active days since 2020 | 165 |
| Public repositories | 38 |

**Languages, measured — by primary language of repository**

| | |
|:--|--:|
| Python | 47% (18) |
| Jupyter Notebook | 37% (14) |
| HTML | 13% (5) |
| JavaScript | 3% (1) |

<sub>Ranked by bytes instead, this reads as 74% Jupyter Notebook — notebooks store rendered cell outputs as base64 in their own JSON, and Linguist counts those plots as authored code.</sub>

**Most recently pushed**

| | | |
|:--|:--|--:|
| [EADIP](https://github.com/advait27/EADIP) | HTML | 2026-09-27 |
| [Advait-portfolio](https://github.com/advait27/Advait-portfolio) | HTML | 2026-09-17 |
| [AI-Research](https://github.com/advait27/AI-Research) | Python | 2026-09-17 |
| [Krypton](https://github.com/advait27/Krypton) | Python | 2026-09-14 |
| [AtlasAI](https://github.com/advait27/AtlasAI) | Python | 2026-08-30 |

<sub>Generated 2026-10-21 from `data/snapshot.json`.</sub>

<!-- data:end -->

</details>

<sub>Activity figures are measured from the GitHub API. The toolkit describes
technologies I use; it is not a proficiency score. Career outcomes above are
from previous roles and are separate from GitHub activity.</sub>

## Writing & speaking

I write about applied AI, RAG, agentic architecture, evaluation and turning
AI into adopted products on [Medium](https://medium.com/@advaitdharmadhikari7).

Podcasts: [The Business Technologist](https://open.spotify.com/show/2nMlpUNSqh9ZiI1vsg5B1g) ·
[5 Minute Boosters](https://open.spotify.com/show/32D27hJiy5sEZ7RnULzcBS).

## Let's build something useful

Working on agents, evaluation, decision intelligence or enterprise AI?
[Get in touch](mailto:advaitdharmadhikari27@gmail.com) or
[connect on LinkedIn](https://www.linkedin.com/in/advaitdharmadhikari).

<details>
<summary>How this profile builds itself</summary>

Custom SVGs, generated in light and dark themes with embedded JetBrains Mono.
The graphics are served from this repository.

A nightly [workflow](.github/workflows/refresh.yml) fetches GitHub data into
[`data/snapshot.json`](data/snapshot.json).
[`scripts/render.py`](scripts/render.py) renders every panel offline and updates
the text fallback. Committed font subsets keep repeated renders deterministic;
[`scripts/verify.py`](scripts/verify.py) checks assets, accessibility metadata,
size limits, output stability and GitHub's Markdown sanitiser.

Implementation notes: [`docs/how-it-works.md`](docs/how-it-works.md).

</details>

---

<sub>Dublin, Ireland · English, Hindi, Marathi ·
<a href="mailto:advaitdharmadhikari27@gmail.com">advaitdharmadhikari27@gmail.com</a></sub>
