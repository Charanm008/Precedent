from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from ..database import Base


class Stage(str, enum.Enum):
    prospecting = "Prospecting"
    discovery = "Discovery"
    proposal = "Proposal"
    negotiation = "Negotiation"
    closed_won = "Closed Won"
    closed_lost = "Closed Lost"


VALID_STAGES = {s.value for s in Stage}


class RiskLevel(str, enum.Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"


class Sentiment(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class InteractionType(str, enum.Enum):
    call = "call"
    meeting = "meeting"
    email = "email"
    note = "note"


class Outcome(str, enum.Enum):
    worked = "worked"
    failed = "failed"
    neutral = "neutral"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    industry = Column(String, nullable=True)
    website = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    deals = relationship("Deal", back_populates="customer")


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    title = Column(String, nullable=False)
    value = Column(Float, nullable=False, default=0.0)
    stage = Column(String, nullable=False, default=Stage.prospecting.value)
    deal_score = Column(Integer, nullable=False, default=50)
    risk_level = Column(String, nullable=False, default=RiskLevel.medium.value)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    customer = relationship("Customer", back_populates="deals")
    stakeholders = relationship("Stakeholder", back_populates="deal")
    interactions = relationship("Interaction", back_populates="deal")


class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    concern = Column(String, nullable=True)

    deal = relationship("Deal", back_populates="stakeholders")
    interactions = relationship("Interaction", back_populates="stakeholder")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"), nullable=True)
    type = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False, default=Sentiment.neutral.value)
    strategy = Column(Text, nullable=True)
    outcome = Column(String, nullable=True)
    occurred_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    deal = relationship("Deal", back_populates="interactions")
    stakeholder = relationship("Stakeholder", back_populates="interactions")
