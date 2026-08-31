from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db_models import AccountRecord, SignalRecord
from app.ingestion import RawSignal, normalize_signal, signal_fingerprint
from app.models import Account, Signal, SignalType


def to_account(record: AccountRecord) -> Account:
    return Account(
        id=record.id,
        name=record.name,
        domain=record.domain,
        industry=record.industry,
        employee_count=record.employee_count,
        signals=[
            Signal(
                type=SignalType(signal.type),
                title=signal.title,
                observed_at=signal.observed_at,
                source=signal.source,
                source_url=signal.source_url,
                confidence=signal.confidence,
            )
            for signal in record.signals
        ],
    )


def list_accounts(db: Session) -> list[Account]:
    statement = select(AccountRecord).options(selectinload(AccountRecord.signals))
    return [to_account(record) for record in db.scalars(statement).all()]


def upsert_account(db: Session, account: Account) -> AccountRecord:
    record = db.get(AccountRecord, account.id)
    if record is None:
        record = AccountRecord(id=account.id, name=account.name, domain=account.domain)
        db.add(record)

    record.name = account.name
    record.domain = account.domain
    record.industry = account.industry
    record.employee_count = account.employee_count
    db.commit()
    db.refresh(record)
    return record


def ingest_signal(db: Session, account_id: str, raw: RawSignal) -> bool:
    fingerprint = signal_fingerprint(raw)
    exists = db.scalar(select(SignalRecord.id).where(SignalRecord.fingerprint == fingerprint))
    if exists:
        return False

    signal = normalize_signal(raw)
    db.add(
        SignalRecord(
            account_id=account_id,
            fingerprint=fingerprint,
            type=signal.type.value,
            title=signal.title,
            observed_at=signal.observed_at,
            source=signal.source,
            source_url=str(signal.source_url) if signal.source_url else None,
            confidence=signal.confidence,
        )
    )
    db.commit()
    return True
