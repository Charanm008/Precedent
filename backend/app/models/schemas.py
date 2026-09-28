from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Customer ──────────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None


class CustomerRead(BaseModel):
    id: int
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Deal ──────────────────────────────────────────────────────────────────────

class DealCreate(BaseModel):
    customer_name: str
    customer_industry: Optional[str] = None
    title: str
    value: float = 0.0
    stage: str = "Prospecting"
    deal_score: int = Field(default=50, ge=0, le=100)
    risk_level: str = "MEDIUM"


class DealUpdate(BaseModel):
    stage: Optional[str] = None
    deal_score: Optional[int] = Field(default=None, ge=0, le=100)
    risk_level: Optional[str] = None


class StakeholderRead(BaseModel):
    id: int
    name: str
    role: str
    concern: Optional[str] = None

    model_config = {"from_attributes": True}


class DealListItem(BaseModel):
    id: int
    title: str
    value: float
    stage: str
    deal_score: int
    risk_level: str
    created_at: datetime
    updated_at: datetime
    customer: CustomerRead

    model_config = {"from_attributes": True}


class DealDetail(BaseModel):
    id: int
    title: str
    value: float
    stage: str
    deal_score: int
    risk_level: str
    created_at: datetime
    updated_at: datetime
    customer: CustomerRead
    stakeholders: List[StakeholderRead]
    interaction_count: int

    model_config = {"from_attributes": True}


# ── Stakeholder ───────────────────────────────────────────────────────────────

class StakeholderCreate(BaseModel):
    deal_id: int
    name: str
    role: str
    concern: Optional[str] = None


# ── Interaction ───────────────────────────────────────────────────────────────

class InteractionCreate(BaseModel):
    deal_id: int
    stakeholder_id: Optional[int] = None
    type: str  # call / meeting / email / note
    summary: str
    sentiment: str = "neutral"  # positive / neutral / negative
    strategy: Optional[str] = None
    outcome: Optional[str] = None  # worked / failed / neutral
    occurred_at: Optional[datetime] = None


class InteractionRead(BaseModel):
    id: int
    deal_id: int
    stakeholder_id: Optional[int] = None
    type: str
    summary: str
    sentiment: str
    strategy: Optional[str] = None
    outcome: Optional[str] = None
    occurred_at: datetime
    stakeholder: Optional[StakeholderRead] = None

    model_config = {"from_attributes": True}
