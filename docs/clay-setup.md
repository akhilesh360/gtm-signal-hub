# Clay -> GTM Signal Hub

Clay can act as the enrichment/orchestration layer while GTM Signal Hub remains the system that stores evidence, scores accounts, and generates opportunity briefs.

## Recommended Clay table columns

| Column | Example |
|---|---|
| Company Name | Acme AI |
| Company Domain | acme.ai |
| Signal Type | technical_hiring |
| Signal Title | Hiring 5 data platform engineers |
| Observed At | 2026-08-30T18:00:00Z |
| Source URL | source page URL |
| Confidence | 0.90 |
| Industry | AI Infrastructure |
| Employee Count | 180 |

Supported `signal_type` values:

- `funding`
- `leadership_change`
- `high_hiring_velocity`
- `technical_hiring`
- `product_expansion`
- `hiring`

## Clay HTTP request

Configure a Clay HTTP API enrichment to send a `POST` request to:

```text
https://YOUR_DEPLOYED_API/integrations/clay/signals
```

JSON body:

```json
{
  "company_name": "{{Company Name}}",
  "company_domain": "{{Company Domain}}",
  "signal_type": "{{Signal Type}}",
  "signal_title": "{{Signal Title}}",
  "observed_at": "{{Observed At}}",
  "source_url": "{{Source URL}}",
  "confidence": 0.9,
  "industry": "{{Industry}}",
  "employee_count": 180
}
```

## Optional webhook protection

Set `CLAY_WEBHOOK_TOKEN` in the deployed backend environment. Then configure this request header in Clay:

```text
X-Clay-Token: <your token>
```

Do not commit the token to GitHub.

## What happens after Clay sends a row

1. The company domain is normalized into a stable account ID.
2. The account is created or updated.
3. The signal receives a deterministic fingerprint.
4. Duplicate retries are ignored.
5. The evidence becomes available to the scoring engine.
6. `/accounts/ranked` and `/dashboard` reflect the account.
7. `/accounts/{account_id}/brief` turns the evidence into a GTM recommendation.

## Suggested first Clay workflow

Start with company + careers/job-posting enrichment because it is easy to explain in a demo:

```text
Target account list
  -> enrich company
  -> find/open job postings
  -> classify relevant hiring signal
  -> HTTP POST to GTM Signal Hub
  -> score changes
  -> account moves up/down ranked list
```

That gives the project a visible end-to-end story without requiring proprietary data.
