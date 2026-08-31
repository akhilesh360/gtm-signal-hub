import json
import os
from typing import Protocol

from app.models import Account, AccountScore


class LLMProvider(Protocol):
    def explain(self, account: Account, score: AccountScore) -> dict[str, object]: ...


class OpenAIReasoningProvider:
    """Optional provider-backed GTM reasoning.

    Activated only when OPENAI_API_KEY is present. Deterministic scoring remains
    the source of truth; this provider only turns evidence into an actionable brief.
    """

    def __init__(self, model: str | None = None) -> None:
        from openai import OpenAI

        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

    def explain(self, account: Account, score: AccountScore) -> dict[str, object]:
        evidence = [
            {
                "signal_type": item.signal_type.value,
                "title": item.title,
                "contribution": item.contribution,
            }
            for item in score.evidence[:5]
        ]

        prompt = {
            "task": "Create a concise evidence-grounded GTM opportunity brief.",
            "rules": [
                "Use only the supplied evidence.",
                "Do not invent company facts.",
                "Return JSON only.",
                "Keep why_now and outreach_angle concise and specific.",
            ],
            "required_schema": {
                "why_now": "string",
                "outreach_angle": "string",
                "evidence_summary": ["string"],
            },
            "account": {
                "name": account.name,
                "domain": account.domain,
                "industry": account.industry,
                "employee_count": account.employee_count,
            },
            "score": {"value": score.score, "tier": score.tier},
            "evidence": evidence,
        }

        response = self.client.responses.create(
            model=self.model,
            input=json.dumps(prompt),
        )
        parsed = json.loads(response.output_text)
        return {
            "why_now": parsed["why_now"],
            "outreach_angle": parsed["outreach_angle"],
            "evidence_summary": parsed.get("evidence_summary", []),
            "reasoning_mode": f"openai:{self.model}",
        }


def get_llm_provider() -> LLMProvider | None:
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIReasoningProvider()
    return None
