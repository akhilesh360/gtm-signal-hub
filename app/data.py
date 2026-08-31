from datetime import datetime, timedelta, timezone

from app.models import Account, Signal, SignalType


NOW = datetime.now(timezone.utc)

ACCOUNTS = [
    Account(
        id="acme-ai",
        name="Acme AI",
        domain="acme.example",
        industry="AI Infrastructure",
        employee_count=180,
        signals=[
            Signal(
                type=SignalType.FUNDING,
                title="Raised a new growth round",
                observed_at=NOW - timedelta(days=4),
                source="demo",
                confidence=0.95,
            ),
            Signal(
                type=SignalType.TECHNICAL_HIRING,
                title="Hiring multiple data platform engineers",
                observed_at=NOW - timedelta(days=2),
                source="demo",
                confidence=0.9,
            ),
            Signal(
                type=SignalType.LEADERSHIP_CHANGE,
                title="Appointed a new VP of Revenue",
                observed_at=NOW - timedelta(days=12),
                source="demo",
                confidence=0.9,
            ),
        ],
    ),
    Account(
        id="northstar-cloud",
        name="Northstar Cloud",
        domain="northstar.example",
        industry="Developer Tools",
        employee_count=90,
        signals=[
            Signal(
                type=SignalType.HIGH_HIRING_VELOCITY,
                title="Open roles increased sharply this month",
                observed_at=NOW - timedelta(days=9),
                source="demo",
                confidence=0.85,
            ),
            Signal(
                type=SignalType.PRODUCT_EXPANSION,
                title="Launched enterprise product tier",
                observed_at=NOW - timedelta(days=18),
                source="demo",
                confidence=0.9,
            ),
        ],
    ),
    Account(
        id="orbit-data",
        name="Orbit Data",
        domain="orbit.example",
        industry="Analytics",
        employee_count=55,
        signals=[
            Signal(
                type=SignalType.HIRING,
                title="Hiring an account executive",
                observed_at=NOW - timedelta(days=45),
                source="demo",
                confidence=0.8,
            )
        ],
    ),
]
