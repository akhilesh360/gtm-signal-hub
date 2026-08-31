# GTM Signal Hub

AI-assisted go-to-market intelligence that turns company events into explainable account priorities and actionable **why-now** briefs.

## The problem

Static lead lists tell GTM teams *who* might fit. They do not explain *why now*. GTM Signal Hub treats account prioritization as a signal-processing problem: collect evidence, normalize it, score it, preserve provenance, and turn it into an actionable brief.

## System flow

```text
Funding / Hiring / Leadership / Product Signals
                    |
                    v
          Collector / Ingestion Layer
                    |
          normalize + deduplicate
                    |
                    v
          PostgreSQL Signal Store
                    |
          +---------+----------+
          |                    |
          v                    v
 Explainable Scoring      Reasoning Layer
  recency/confidence      why now / angle
          |                    |
          +---------+----------+
                    v
                  FastAPI
                    |
          +---------+----------+
          |                    |
       Dashboard          Integrations
```

## What is implemented

### Phase 1 — scoring foundation
- FastAPI service and Swagger docs
- Typed Pydantic account/signal contracts
- Explainable 0-100 opportunity scoring
- Signal recency decay + confidence weighting
- Evidence-level score breakdown
- Unit tests, Docker, GitHub Actions CI

### Phase 2 — production-oriented data layer
- SQLAlchemy persistence
- PostgreSQL support with SQLite local fallback
- Account + signal relational models
- Normalized collector input contract
- SHA-256 signal fingerprints for idempotent ingestion
- Duplicate signal protection
- Repeatable seed pipeline
- Docker Compose PostgreSQL environment

### Phase 3 — GTM intelligence APIs
- Evidence-grounded `why_now` reasoning
- Recommended outreach angle based on strongest signal
- Explicit `reasoning_mode` so deterministic logic is never misrepresented as an LLM call
- Account opportunity brief endpoint
- Dashboard summary endpoint
- Persistent account and signal ingestion APIs

## Signal scoring

| Signal | Base weight |
|---|---:|
| Funding event | 30 |
| Executive / GTM leadership change | 25 |
| High hiring velocity | 20 |
| Relevant technical hiring | 15 |
| Product expansion | 15 |
| Generic hiring signal | 10 |

Final contribution is based on:

```text
base_weight x recency_multiplier x confidence
```

Scores are capped at 100 and classified as `hot`, `warm`, or `watch`.

## API

```text
GET  /health
GET  /accounts
POST /accounts
POST /accounts/{account_id}/signals
GET  /accounts/ranked
GET  /accounts/{account_id}/brief
GET  /dashboard
POST /score
```

The `/accounts/{account_id}/brief` response combines the deterministic score, evidence, why-now explanation, and recommended outreach angle.

## Run locally — fastest path

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

## Run with PostgreSQL

```bash
docker compose up --build
```

Then seed the API container/database as needed and open `http://localhost:8000/docs`.

## Tests

```bash
PYTHONPATH=. python -m pytest -q
```

## Engineering decisions

**Deterministic before generative.** Ranking is auditable and testable. An LLM can enrich the recommendation layer later without controlling the source-of-truth score.

**Evidence first.** Every score retains the signals that contributed to it rather than returning an unexplained model number.

**Idempotent ingestion.** Collector output receives a stable fingerprint so retries do not silently create duplicate buying signals.

**Provider-ready AI boundary.** The reasoning response contract is separated from scoring. A production LLM provider can be introduced without rewriting the core ranking engine.

## Next phases

- [ ] Real public signal collector: company careers / job-posting changes
- [ ] Funding/news collector with source provenance
- [ ] Scheduled collectors + retries/backoff
- [ ] OpenAI or Bedrock structured reasoning provider
- [ ] Prompt/evaluation dataset for `why_now` quality
- [ ] React/Next.js visual dashboard
- [ ] Account timeline and score-history tables
- [ ] CRM webhook / Slack alert integration
- [ ] OpenTelemetry metrics and structured logging
- [ ] Cloud deployment + live demo URL

## Interview / portfolio story

GTM Signal Hub demonstrates an end-to-end system across **GTM engineering, data engineering, backend engineering, AI system design, feature engineering, explainability, idempotent pipelines, APIs, persistence, testing, and containerized deployment**.

A useful design discussion is the separation between deterministic opportunity ranking and generative reasoning: the model can help explain and operationalize evidence without becoming an opaque source of truth for the score.

---

Built by [Akhilesh](https://github.com/akhilesh360).
