import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import Customer, Deal, Stakeholder, VALID_STAGES
from ..models.schemas import (
    DealCreate,
    DealDetail,
    DealListItem,
    DealUpdate,
    StakeholderRead,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["deals"])


@router.get("/deals", response_model=List[DealListItem])
def list_deals(db: Session = Depends(get_db)):
    return db.query(Deal).order_by(Deal.updated_at.desc()).all()


@router.post("/deal", response_model=DealDetail, status_code=201)
def create_deal(payload: DealCreate, db: Session = Depends(get_db)):
    if payload.stage not in VALID_STAGES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid stage '{payload.stage}'. Valid: {sorted(VALID_STAGES)}",
        )
    if payload.risk_level not in {"LOW", "MEDIUM", "HIGH"}:
        raise HTTPException(status_code=422, detail="risk_level must be LOW, MEDIUM, or HIGH")

    # Get or create customer by name
    customer = (
        db.query(Customer).filter(Customer.name == payload.customer_name).first()
    )
    if not customer:
        customer = Customer(
            name=payload.customer_name,
            industry=payload.customer_industry,
        )
        db.add(customer)
        db.flush()

    deal = Deal(
        customer_id=customer.id,
        title=payload.title,
        value=payload.value,
        stage=payload.stage,
        deal_score=payload.deal_score,
        risk_level=payload.risk_level,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    return DealDetail(
        id=deal.id,
        title=deal.title,
        value=deal.value,
        stage=deal.stage,
        deal_score=deal.deal_score,
        risk_level=deal.risk_level,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        customer=deal.customer,
        stakeholders=[StakeholderRead.model_validate(s) for s in deal.stakeholders],
        interaction_count=len(deal.interactions),
    )


@router.get("/deal/{deal_id}", response_model=DealDetail)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealDetail(
        id=deal.id,
        title=deal.title,
        value=deal.value,
        stage=deal.stage,
        deal_score=deal.deal_score,
        risk_level=deal.risk_level,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        customer=deal.customer,
        stakeholders=[StakeholderRead.model_validate(s) for s in deal.stakeholders],
        interaction_count=len(deal.interactions),
    )


@router.patch("/deal/{deal_id}", response_model=DealDetail)
def update_deal(deal_id: int, payload: DealUpdate, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if payload.stage is not None:
        if payload.stage not in VALID_STAGES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid stage '{payload.stage}'. Valid: {sorted(VALID_STAGES)}",
            )
        deal.stage = payload.stage

    if payload.deal_score is not None:
        deal.deal_score = payload.deal_score

    if payload.risk_level is not None:
        if payload.risk_level not in {"LOW", "MEDIUM", "HIGH"}:
            raise HTTPException(status_code=422, detail="risk_level must be LOW, MEDIUM, or HIGH")
        deal.risk_level = payload.risk_level

    deal.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(deal)

    return DealDetail(
        id=deal.id,
        title=deal.title,
        value=deal.value,
        stage=deal.stage,
        deal_score=deal.deal_score,
        risk_level=deal.risk_level,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        customer=deal.customer,
        stakeholders=[StakeholderRead.model_validate(s) for s in deal.stakeholders],
        interaction_count=len(deal.interactions),
    )
