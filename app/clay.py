import hashlib
import os
from datetime import datetime, timezone

from pydantic import BaseModel, Field, HttpUrl

from app.ingestion import RawSignal
from app.models import Account, SignalType


class ClaySignalPayload(BaseModel):
    company_name: str
    company_domain: str
    signal_type: SignalType
    signal_title: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_url: HttpUrl | None = None
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    industry: str | None = None
    employee_count: int | None = None


def account_id_from_domain(domain: str) -> str:
    normalized = domain.lower().replace("https://", "").replace("http://", "").strip("/")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]
    slug = normalized.split("/")[0].replace(".", "-")
    return f"{slug}-{digest}"


def payload_to_account(payload: ClaySignalPayload) -> Account:
    return Account(
        id=account_id_from_domain(payload.company_domain),
        name=payload.company_name,
        domain=payload.company_domain,
        industry=payload.industry,
        employee_count=payload.employee_count,
        signals=[],
    )


def payload_to_signal(payload: ClaySignalPayload) -> RawSignal:
    return RawSignal(
        company_domain=payload.company_domain,
        type=payload.signal_type,
        title=payload.signal_title,
        observed_at=payload.observed_at,
        source="clay",
        source_url=payload.source_url,
        confidence=payload.confidence,
    )


def clay_token_is_valid(token: str | None) -> bool:
    expected = os.getenv("CLAY_WEBHOOK_TOKEN")
    if not expected:
        return True
    return bool(token) and token == expected
