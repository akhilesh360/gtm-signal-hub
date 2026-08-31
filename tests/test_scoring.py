from datetime import datetime, timedelta, timezone

from app.models import Account, Signal, SignalType
from app.scoring import recency_multiplier, score_account


def test_recent_signal_gets_full_recency_weight():
    now = datetime(2026, 8, 30, tzinfo=timezone.utc)
    observed_at = now - timedelta(days=3)
    assert recency_multiplier(observed_at, now) == 1.0


def test_funding_and_leadership_create_strong_score():
    now = datetime(2026, 8, 30, tzinfo=timezone.utc)
    account = Account(
        id="test",
        name="Test Co",
        domain="test.example",
        signals=[
            Signal(
                type=SignalType.FUNDING,
                title="Raised Series B",
                observed_at=now - timedelta(days=2),
            ),
            Signal(
                type=SignalType.LEADERSHIP_CHANGE,
                title="New CRO",
                observed_at=now - timedelta(days=3),
            ),
        ],
    )

    result = score_account(account, now=now)
    assert result.score == 55
    assert result.tier == "warm"
    assert len(result.evidence) == 2


def test_score_is_capped_at_100():
    now = datetime(2026, 8, 30, tzinfo=timezone.utc)
    signals = [
        Signal(
            type=SignalType.FUNDING,
            title=f"Funding signal {i}",
            observed_at=now,
        )
        for i in range(4)
    ]
    account = Account(id="cap", name="Cap Co", domain="cap.example", signals=signals)
    assert score_account(account, now=now).score == 100
