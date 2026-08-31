from fastapi import FastAPI

from app.data import ACCOUNTS
from app.models import Account, AccountScore
from app.scoring import score_account


app = FastAPI(
    title="GTM Signal Hub",
    description="Turn account signals into explainable GTM priorities.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/accounts", response_model=list[Account])
def list_accounts() -> list[Account]:
    return ACCOUNTS


@app.get("/accounts/ranked", response_model=list[AccountScore])
def ranked_accounts() -> list[AccountScore]:
    scores = [score_account(account) for account in ACCOUNTS]
    return sorted(scores, key=lambda item: item.score, reverse=True)


@app.post("/score", response_model=AccountScore)
def score(account: Account) -> AccountScore:
    return score_account(account)
