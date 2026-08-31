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


def explain_opportunity(account: Account, score: AccountScore) -> ReasoningResult:
    """Create deterministic, evidence-grounded GTM reasoning.

    This fallback deliberately avoids pretending an LLM was called. A provider-backed
    implementation can replace it later while preserving the same response contract.
    """
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
    why_now = (
        f"{account.name} is a {score.tier} account with a {score.score:g}/100 score. "
        f"The strongest current trigger is: {strongest.title}."
    )

    return ReasoningResult(
        why_now=why_now,
        outreach_angle=ACTION_BY_SIGNAL[strongest.signal_type],
        evidence_summary=evidence_summary,
        reasoning_mode="deterministic",
    )
