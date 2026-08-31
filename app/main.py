from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session

from app.clay import ClaySignalPayload, clay_token_is_valid, payload_to_account, payload_to_signal
from app.data import ACCOUNTS
from app.database import Base, engine, get_db
from app.ingestion import RawSignal
from app.models import Account, AccountScore, DashboardSummary, OpportunityBrief
from app.reasoning import explain_opportunity
from app.repository import ingest_signal, list_accounts as list_persisted_accounts, upsert_account
from app.scoring import score_account


app = FastAPI(
    title="GTM Signal Hub",
    description="Turn account signals into explainable GTM priorities.",
    version="0.3.0",
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.3.0"}


@app.get("/accounts", response_model=list[Account])
def list_accounts(db: Session = Depends(get_db)) -> list[Account]:
    persisted = list_persisted_accounts(db)
    return persisted or ACCOUNTS


@app.post("/accounts", response_model=Account)
def save_account(account: Account, db: Session = Depends(get_db)) -> Account:
    upsert_account(db, account.model_copy(update={"signals": []}))
    for signal in account.signals:
        ingest_signal(
            db,
            account.id,
            RawSignal(
                company_domain=account.domain,
                type=signal.type,
                title=signal.title,
                observed_at=signal.observed_at,
                source=signal.source or "api",
                source_url=signal.source_url,
                confidence=signal.confidence,
            ),
        )
    return account


@app.post("/integrations/clay/signals")
def ingest_clay_signal(
    payload: ClaySignalPayload,
    db: Session = Depends(get_db),
    x_clay_token: str | None = Header(default=None),
) -> dict[str, object]:
    if not clay_token_is_valid(x_clay_token):
        raise HTTPException(status_code=401, detail="Invalid Clay webhook token")

    account = payload_to_account(payload)
    upsert_account(db, account)
    created = ingest_signal(db, account.id, payload_to_signal(payload))
    return {
        "account_id": account.id,
        "created": created,
        "deduplicated": not created,
        "source": "clay",
    }


@app.post("/accounts/{account_id}/signals")
def add_signal(account_id: str, raw: RawSignal, db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        created = ingest_signal(db, account_id, raw)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to ingest signal. Ensure the account exists.") from exc
    return {"created": created, "deduplicated": not created}


@app.get("/accounts/ranked", response_model=list[AccountScore])
def ranked_accounts(db: Session = Depends(get_db)) -> list[AccountScore]:
    accounts = list_persisted_accounts(db) or ACCOUNTS
    scores = [score_account(account) for account in accounts]
    return sorted(scores, key=lambda item: item.score, reverse=True)


@app.get("/accounts/{account_id}/brief", response_model=OpportunityBrief)
def account_brief(account_id: str, db: Session = Depends(get_db)) -> OpportunityBrief:
    accounts = list_persisted_accounts(db) or ACCOUNTS
    account = next((item for item in accounts if item.id == account_id), None)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    score = score_account(account)
    reasoning = explain_opportunity(account, score)
    return OpportunityBrief(account=account, score=score, **reasoning)


@app.get("/dashboard", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)) -> DashboardSummary:
    accounts = list_persisted_accounts(db) or ACCOUNTS
    ranked = sorted((score_account(account) for account in accounts), key=lambda item: item.score, reverse=True)
    return DashboardSummary(
        total_accounts=len(accounts),
        hot_accounts=sum(item.tier == "hot" for item in ranked),
        warm_accounts=sum(item.tier == "warm" for item in ranked),
        watch_accounts=sum(item.tier == "watch" for item in ranked),
        total_signals=sum(len(account.signals) for account in accounts),
        top_accounts=ranked[:10],
    )


@app.post("/score", response_model=AccountScore)
def score(account: Account) -> AccountScore:
    return score_account(account)
