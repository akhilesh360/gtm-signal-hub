from app.llm import get_llm_provider
from app.models import Account, AccountScore, SignalType


ACTION_BY_SIGNAL = {
    SignalType.FUNDING: "Lead with how your product can help deploy new capital into growth efficiently.",
    SignalType.LEADERSHIP_CHANGE: "Reach out while the new leader is evaluating priorities, vendors, and operating systems.",
    SignalType.HIGH_HIRING_VELOCITY: "Connect the hiring surge to the operational bottleneck your product solves.",
    SignalType.TECHNICAL_HIRING: "Reference the technical investment and position your product as leverage for the growing team.",
    SignalType.PRODUCT_EXPANSION: "Tie outreach to the new product motion and the infrastructure needed to support expansion.",
    SignalType.HIRING: "Use the open role as evidence of an active business priority and validate the underlying need.",
}


class ReasoningResult(dict):
    """JSON-friendly GTM reasoning payload."""


def deterministic_explanation(account: Account, score: AccountScore) -> ReasoningResult:
    if not score.evidence:
        return ReasoningResult(
            why_now="No meaningful recent signal is available yet.",
            outreach_angle="Keep the account on a watch list and wait for stronger evidence.",
            evidence_summary=[],
            reasoning_mode="deterministic",
        )

    strongest = score.evidence[0]
    evidence_summary = [
        f"{item.title} (+{item.contribution:g} points)" for item in score.evidence[:3]
    ]
    return ReasoningResult(
        why_now=(
            f"{account.name} is a {score.tier} account with a {score.score:g}/100 score. "
            f"The strongest current trigger is: {strongest.title}."
        ),
        outreach_angle=ACTION_BY_SIGNAL[strongest.signal_type],
        evidence_summary=evidence_summary,
        reasoning_mode="deterministic",
    )


def explain_opportunity(account: Account, score: AccountScore) -> ReasoningResult:
    """Use optional provider reasoning, with a safe deterministic fallback."""
    provider = get_llm_provider()
    if provider is not None:
        try:
            return ReasoningResult(**provider.explain(account, score))
        except Exception:
            # A provider outage must never make account ranking unavailable.
            fallback = deterministic_explanation(account, score)
            fallback["reasoning_mode"] = "deterministic_fallback"
            return fallback
    return deterministic_explanation(account, score)
