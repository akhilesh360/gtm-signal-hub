from datetime import datetime, timezone

from app.models import Account, Signal, SignalType
from app.reasoning import explain_opportunity
from app.scoring import score_account


def test_reasoning_is_grounded_in_top_signal():
    account = Account(
        id="reason",
        name="Reason Co",
        domain="reason.example",
        signals=[
            Signal(
                type=SignalType.FUNDING,
                title="Raised Series A",
                observed_at=datetime.now(timezone.utc),
            )
        ],
    )
    score = score_account(account)
    result = explain_opportunity(account, score)

    assert "Raised Series A" in result["why_now"]
    assert result["reasoning_mode"] == "deterministic"
    assert result["evidence_summary"]
