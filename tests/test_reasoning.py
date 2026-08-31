from datetime import datetime, timezone

from app.models import Account, Signal, SignalType
from app.reasoning import deterministic_explanation
from app.scoring import score_account


def test_reasoning_is_grounded_in_strongest_evidence():
    account = Account(
        id="acme",
        name="Acme",
        domain="acme.example",
        signals=[
            Signal(
                type=SignalType.FUNDING,
                title="Raised Series B",
                observed_at=datetime.now(timezone.utc),
                confidence=1.0,
            )
        ],
    )
    result = deterministic_explanation(account, score_account(account))
    assert "Raised Series B" in result["why_now"]
    assert result["reasoning_mode"] == "deterministic"
    assert len(result["evidence_summary"]) == 1


def test_no_signal_account_does_not_invent_reasoning():
    account = Account(id="quiet", name="Quiet Co", domain="quiet.example")
    result = deterministic_explanation(account, score_account(account))
    assert "No meaningful recent signal" in result["why_now"]
    assert result["evidence_summary"] == []
