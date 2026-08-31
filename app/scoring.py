from datetime import datetime, timezone

from app.models import Account, AccountScore, ScoreBreakdown, SignalType


SIGNAL_WEIGHTS = {
    SignalType.FUNDING: 30,
    SignalType.LEADERSHIP_CHANGE: 25,
    SignalType.HIGH_HIRING_VELOCITY: 20,
    SignalType.TECHNICAL_HIRING: 15,
    SignalType.PRODUCT_EXPANSION: 15,
    SignalType.HIRING: 10,
}


def recency_multiplier(observed_at: datetime, now: datetime) -> float:
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    age_days = max((now - observed_at).days, 0)

    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 90:
        return 0.5
    return 0.25


def score_account(account: Account, now: datetime | None = None) -> AccountScore:
    now = now or datetime.now(timezone.utc)
    evidence: list[ScoreBreakdown] = []

    for signal in account.signals:
        base = SIGNAL_WEIGHTS[signal.type]
        recency = recency_multiplier(signal.observed_at, now)
        contribution = round(base * recency * signal.confidence, 2)
        evidence.append(
            ScoreBreakdown(
                signal_type=signal.type,
                title=signal.title,
                base_weight=base,
                recency_multiplier=recency,
                confidence=signal.confidence,
                contribution=contribution,
            )
        )

    evidence.sort(key=lambda item: item.contribution, reverse=True)
    score = round(min(sum(item.contribution for item in evidence), 100), 2)

    if score >= 70:
        tier = "hot"
    elif score >= 40:
        tier = "warm"
    else:
        tier = "watch"

    top_reasons = [item.title for item in evidence[:2]]
    why_now = "; ".join(top_reasons) if top_reasons else "No recent buying signals detected."

    return AccountScore(
        account_id=account.id,
        account_name=account.name,
        score=score,
        tier=tier,
        why_now=why_now,
        evidence=evidence,
    )
