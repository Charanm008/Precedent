import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import Deal, Interaction, Stakeholder
from ..models.schemas import InteractionCreate, InteractionRead

logger = logging.getLogger(__name__)
router = APIRouter(tags=["interactions"])

VALID_TYPES = {"call", "meeting", "email", "note"}
VALID_SENTIMENTS = {"positive", "neutral", "negative"}
VALID_OUTCOMES = {"worked", "failed", "neutral"}


@router.post("/interaction", response_model=InteractionRead, status_code=201)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    # Validate deal exists
    deal = db.query(Deal).filter(Deal.id == payload.deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if payload.type not in VALID_TYPES:
        raise HTTPException(status_code=422, detail=f"type must be one of {VALID_TYPES}")
    if payload.sentiment not in VALID_SENTIMENTS:
        raise HTTPException(status_code=422, detail=f"sentiment must be one of {VALID_SENTIMENTS}")
    if payload.outcome is not None and payload.outcome not in VALID_OUTCOMES:
        raise HTTPException(status_code=422, detail=f"outcome must be one of {VALID_OUTCOMES}")

    if payload.stakeholder_id is not None:
        sh = db.query(Stakeholder).filter(
            Stakeholder.id == payload.stakeholder_id,
            Stakeholder.deal_id == payload.deal_id,
        ).first()
        if not sh:
            raise HTTPException(status_code=404, detail="Stakeholder not found for this deal")

    interaction = Interaction(
        deal_id=payload.deal_id,
        stakeholder_id=payload.stakeholder_id,
        type=payload.type,
        summary=payload.summary,
        sentiment=payload.sentiment,
        strategy=payload.strategy,
        outcome=payload.outcome,
        occurred_at=payload.occurred_at or datetime.now(timezone.utc),
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    # Memory hook — fire-and-forget; never block the response
    try:
        from memory.retain import retain_memory  # noqa: PLC0415

        stakeholder_name = None
        if interaction.stakeholder_id and interaction.stakeholder:
            stakeholder_name = interaction.stakeholder.name

        retain_memory(
            text=interaction.summary,
            metadata={
                "deal_id": interaction.deal_id,
                "customer_id": deal.customer_id,
                "stakeholder": stakeholder_name,
                "type": interaction.type,
                "sentiment": interaction.sentiment,
                "strategy": interaction.strategy,
                "outcome": interaction.outcome,
            },
            memory_id=f"interaction_{interaction.id}",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Memory hook failed (Hindsight unavailable): %s", exc)

    return interaction


@router.get("/timeline/{deal_id}", response_model=List[InteractionRead])
def get_timeline(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    interactions = (
        db.query(Interaction)
        .filter(Interaction.deal_id == deal_id)
        .order_by(Interaction.occurred_at.desc())
        .all()
    )
    return interactions
