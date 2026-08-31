from datetime import datetime, timezone

from app.ingestion import RawSignal, normalize_signal, signal_fingerprint
from app.models import SignalType


def test_fingerprint_is_stable_for_equivalent_signal():
    raw = RawSignal(
        company_domain="Example.com",
        type=SignalType.FUNDING,
        title=" Raised Series B ",
        observed_at=datetime(2026, 8, 30, tzinfo=timezone.utc),
        source="News",
    )
    duplicate = raw.model_copy(update={"company_domain": "example.com", "source": "news"})
    assert signal_fingerprint(raw) == signal_fingerprint(duplicate)


def test_normalizer_collapses_title_whitespace():
    raw = RawSignal(
        company_domain="example.com",
        type=SignalType.HIRING,
        title="Hiring   five   engineers",
        observed_at=datetime(2026, 8, 30, tzinfo=timezone.utc),
        source="careers",
    )
    assert normalize_signal(raw).title == "Hiring five engineers"
