# GTM Signal Hub

AI-assisted go-to-market intelligence that turns company events into explainable account priorities and actionable **why-now** briefs.

## The problem

Static lead lists tell GTM teams *who* might fit. They do not explain *why now*. GTM Signal Hub treats account prioritization as a signal-processing problem: collect evidence, normalize it, score it, preserve provenance, and turn it into an actionable brief.

## Architecture

```text
Clay / Funding / Hiring / Leadership / Product Signals
                         |
                         v
              Collector + Webhook Layer
                         |
                normalize + dedupe
                         |
                         v
               PostgreSQL / SQLite
                         |
             +-----------+-----------+
             |                       |
             v                       v
    Deterministic Scoring      Reasoning Layer
    recency + confidence       OpenAI optional
             |                 safe fallback
             +-----------+-----------+
                         v
                       FastAPI
                         |
             +-----------+-----------+
             |                       |
             v                       v
     Streamlit Dashboard       Integrations
     ranking + briefs          Clay / future CRM
```

## Implemented phases

### Phase 1 — scoring foundation
- FastAPI + typed Pydantic contracts
- Explainable 0-100 scoring
- Recency decay + confidence weighting
- Evidence-level score breakdown
- Unit tests, Docker, GitHub Actions CI

### Phase 2 — production-oriented data layer
- SQLAlchemy persistence
- PostgreSQL with SQLite local fallback
- Account + signal relational models
- SHA-256 signal fingerprints
- Idempotent ingestion and duplicate protection
- Repeatable seed pipeline + Docker Compose

### Phase 3 — GTM intelligence APIs
- Evidence-grounded `why_now`
- Recommended outreach angle
- Opportunity brief + dashboard APIs
- Persistent account and signal ingestion

### Phase 4 — integrations + visual demo
- Clay-compatible webhook ingestion
- Stable account IDs derived from company domain
- Optional webhook-token protection
- Streamlit visual dashboard
- Ranked account table + KPI cards
- Interactive opportunity briefs

### Phase 5 — AI reasoning + evaluation
- Optional OpenAI reasoning provider
- Deterministic scoring remains source of truth
- Provider failures safely fall back to deterministic reasoning
- Explicit `reasoning_mode` in API output
- Tests verifying evidence-grounded fallback behavior
- `.env.example` with no committed secrets

## Signal scoring

| Signal | Base weight |
|---|---:|
| Funding event | 30 |
| Executive / GTM leadership change | 25 |
| High hiring velocity | 20 |
| Relevant technical hiring | 15 |
| Product expansion | 15 |
| Generic hiring signal | 10 |

`contribution = base_weight × recency_multiplier × confidence`

Scores are capped at 100 and classified as `hot`, `warm`, or `watch`.

## API

```text
GET  /health
GET  /accounts
POST /accounts
POST /accounts/{account_id}/signals
POST /integrations/clay/signals
GET  /accounts/ranked
GET  /accounts/{account_id}/brief
GET  /dashboard
POST /score
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

In another terminal:

```bash
streamlit run dashboard.py
```

API docs: `http://localhost:8000/docs`

Dashboard: `http://localhost:8501`

## Optional AI reasoning

The app works without an AI key. When `OPENAI_API_KEY` is configured, opportunity briefs can use the provider-backed reasoning layer. If the provider is unavailable or returns invalid output, the app falls back to deterministic evidence-grounded reasoning instead of breaking account ranking.

No API key should ever be committed to this repository.

## Clay workflow

See `docs/clay-setup.md` for the complete mapping. The intended demo flow is:

```text
Clay target accounts
 -> enrich company / job activity
 -> classify buying signal
 -> POST signal to GTM Signal Hub
 -> deduplicate + persist
 -> recompute account priority
 -> dashboard + why-now brief
```

## Tests

```bash
PYTHONPATH=. python -m pytest -q
```

## Engineering principles

**Deterministic before generative.** The LLM explains evidence; it does not secretly determine the source-of-truth score.

**Evidence first.** Scores and recommendations retain their supporting signals.

**Idempotent ingestion.** Collector retries do not create duplicate buying events.

**Graceful degradation.** External AI/provider failures do not take down ranking.

**Demo without secrets.** SQLite + deterministic reasoning make the entire core system runnable locally without paid infrastructure.

## Next

- [ ] Deploy API + PostgreSQL
- [ ] Deploy dashboard and publish live demo URL
- [ ] Connect a real Clay table to the deployed webhook
- [ ] Add public careers/job-posting collector
- [ ] Add score-history/account-timeline tables
- [ ] Add Slack/CRM hot-account alerts
- [ ] Add larger golden evaluation dataset for AI recommendations
- [ ] Structured logging + OpenTelemetry

## Interview story

GTM Signal Hub demonstrates **GTM engineering + data engineering + backend engineering + applied AI** in one system: signal ingestion, enrichment integration, idempotent pipelines, persistence, explainable feature scoring, provider-backed reasoning, evaluation, APIs, and a visual decision surface.

The key architecture choice is intentionally separating **ranking from generation**: deterministic logic decides priority while AI converts the supporting evidence into a concise, actionable GTM recommendation.

---

Built by [Akhilesh](https://github.com/akhilesh360).
