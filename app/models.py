from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class SignalType(str, Enum):
    FUNDING = "funding"
    LEADERSHIP_CHANGE = "leadership_change"
    HIGH_HIRING_VELOCITY = "high_hiring_velocity"
    TECHNICAL_HIRING = "technical_hiring"
    PRODUCT_EXPANSION = "product_expansion"
    HIRING = "hiring"


class Signal(BaseModel):
    type: SignalType
    title: str
    observed_at: datetime
    source: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Account(BaseModel):
    id: str
    name: str
    domain: str
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    signals: List[Signal] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    signal_type: SignalType
    title: str
    base_weight: float
    recency_multiplier: float
    confidence: float
    contribution: float


class AccountScore(BaseModel):
    account_id: str
    account_name: str
    score: float
    tier: str
    why_now: str
    evidence: List[ScoreBreakdown]
