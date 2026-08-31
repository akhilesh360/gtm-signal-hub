# GTM Signal Hub

AI-assisted go-to-market intelligence for prioritizing accounts based on real buying signals.

## What it does

GTM Signal Hub ingests account-level signals such as funding, hiring activity, leadership changes, technical hiring, and product expansion. It converts those raw events into explainable opportunity scores and recommended next actions for sales, growth, and GTM teams.

## Why this project

Most lead lists are static. Real GTM execution depends on **why now**: what changed at an account that makes outreach timely? This project treats GTM prioritization as a data + AI problem.

## MVP architecture

```text
Signal Sources
  |-- Funding
  |-- Hiring
  |-- Leadership
  |-- Product / Tech signals
        |
        v
Ingestion + Normalization
        |
        v
Signal Store
        |
        +--> Explainable Scoring Engine
        |
        +--> AI Reasoning Layer
        |      |-- Why now?
        |      |-- ICP fit
        |      |-- Suggested next action
        |
        v
FastAPI
        |
        v
Dashboard / Integrations
```

## Current MVP

- FastAPI service
- Typed account and signal models
- Explainable 0-100 opportunity scoring
- Recency-aware signal weighting
- Sample seed data
- REST endpoints for scoring and ranked accounts
- Unit tests
- Docker support
- GitHub Actions CI

## Scoring model

The first version intentionally uses deterministic scoring so the ranking is auditable before adding LLM-based reasoning.

| Signal | Base weight |
|---|---:|
| Funding event | 30 |
| Executive / GTM leadership change | 25 |
| High hiring velocity | 20 |
| Relevant technical hiring | 15 |
| Product expansion | 15 |
| Generic hiring signal | 10 |

Signals decay with age and are capped at a score of 100. The API also returns the evidence used to produce each score.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for Swagger.

## Example endpoints

```text
GET  /health
GET  /accounts
GET  /accounts/ranked
POST /score
```

## Run tests

```bash
pytest
```

## Docker

```bash
docker build -t gtm-signal-hub .
docker run -p 8000:8000 gtm-signal-hub
```

## Roadmap

- [ ] PostgreSQL + SQLAlchemy persistence
- [ ] Scheduled signal collectors
- [ ] Company enrichment connectors
- [ ] LLM-generated `why_now`, evidence summary, and outreach angle
- [ ] Confidence / provenance tracking
- [ ] Account timeline and score history
- [ ] React/Next.js signal dashboard
- [ ] CRM / Slack integrations
- [ ] Evaluation dataset for AI-generated recommendations
- [ ] Observability, retries, idempotency, and production deployment

## Portfolio talking points

This project demonstrates GTM engineering, data engineering, backend/API design, AI system design, feature engineering, explainability, testing, and production-oriented software practices in one end-to-end system.

---

Built by [Akhilesh](https://github.com/akhilesh360).
