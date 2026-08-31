from sqlalchemy import select

from app.data import ACCOUNTS
from app.database import Base, SessionLocal, engine
from app.db_models import AccountRecord
from app.ingestion import RawSignal
from app.repository import ingest_signal, upsert_account


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for account in ACCOUNTS:
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
                        source=signal.source or "seed",
                        source_url=signal.source_url,
                        confidence=signal.confidence,
                    ),
                )


if __name__ == "__main__":
    seed_database()
