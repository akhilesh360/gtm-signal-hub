from datetime import datetime, timezone
from hashlib import sha256

from pydantic import BaseModel, Field, HttpUrl

from app.models import Signal, SignalType


class RawSignal(BaseModel):
    company_domain: str
    type: SignalType
    title: str
    observed_at: datetime
    source: str
    source_url: HttpUrl | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


def signal_fingerprint(raw: RawSignal) -> str:
    """Stable idempotency key used to deduplicate collector output."""
    canonical = "|".join(
        [
            raw.company_domain.lower().strip(),
            raw.type.value,
            raw.title.lower().strip(),
            raw.observed_at.astimezone(timezone.utc).date().isoformat(),
            raw.source.lower().strip(),
        ]
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def normalize_signal(raw: RawSignal) -> Signal:
    """Convert collector-specific input into the canonical signal model."""
    return Signal(
        type=raw.type,
        title=" ".join(raw.title.split()),
        observed_at=raw.observed_at,
        source=raw.source.strip(),
        source_url=raw.source_url,
        confidence=raw.confidence,
    )
