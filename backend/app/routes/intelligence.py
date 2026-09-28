"""
Intelligence API Routes — Phase 3

Exposes competitor intelligence and market events via REST endpoints.
All routes are NEW — this file does not modify any Phase 1/2 routes.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..intelligence.competitor_service import competitor_service, CompetitorProfile
from ..intelligence.market_events_service import market_events_service, MarketEvent
from ..intelligence.deal_intelligence import deal_intelligence_aggregator

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


# ── Pydantic response schemas ──────────────────────────────────────────────

class SignalOut(BaseModel):
    competitor: str
    category: str
    headline: str
    detail: str
    impact: str
    source: str
    tags: List[str]


class CompetitorOut(BaseModel):
    name: str
    industry: str
    known_strengths: List[str]
    known_weaknesses: List[str]
    signals: List[SignalOut]


class MarketEventOut(BaseModel):
    event_id: str
    title: str
    category: str
    summary: str
    detail: str
    impact_score: int
    published_at: str
    source: str


class DealBriefOut(BaseModel):
    deal_id: int
    deal_title: str
    customer_name: str
    customer_industry: Optional[str]
    deal_stage: str
    deal_value: float
    risk_level: str
    competitor_signals: List[dict]
    market_events: List[dict]
    key_risks: List[str]
    key_opportunities: List[str]
    intelligence_score: int


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.get(
    "/competitors",
    response_model=List[CompetitorOut],
    summary="List all tracked competitors",
)
def list_competitors():
    """
    Returns a list of all competitors tracked in the intelligence knowledge base,
    including their known strengths, weaknesses, and latest signals.
    """
    results = []
    for name in competitor_service.all_competitors():
        profile = competitor_service.get_profile(name)
        if profile:
            results.append(
                CompetitorOut(
                    name=profile.name,
                    industry=profile.industry,
                    known_strengths=profile.known_strengths,
                    known_weaknesses=profile.known_weaknesses,
                    signals=[
                        SignalOut(
                            competitor=s.name,
                            category=s.category,
                            headline=s.headline,
                            detail=s.detail,
                            impact=s.impact,
                            source=s.source,
                            tags=s.tags,
                        )
                        for s in profile.signals
                    ],
                )
            )
    return results


@router.get(
    "/competitors/{name}",
    response_model=CompetitorOut,
    summary="Get a single competitor profile",
)
def get_competitor(name: str):
    profile = competitor_service.get_profile(name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Competitor '{name}' not found.")
    return CompetitorOut(
        name=profile.name,
        industry=profile.industry,
        known_strengths=profile.known_strengths,
        known_weaknesses=profile.known_weaknesses,
        signals=[
            SignalOut(
                competitor=s.name,
                category=s.category,
                headline=s.headline,
                detail=s.detail,
                impact=s.impact,
                source=s.source,
                tags=s.tags,
            )
            for s in profile.signals
        ],
    )


@router.get(
    "/signals",
    response_model=List[SignalOut],
    summary="Get competitor signals filtered by industry",
)
def get_signals(industry: Optional[str] = Query(None, description="Customer industry for relevance filtering")):
    """
    Returns competitor signals relevant to a given industry context.
    Returns all signals if no industry provided.
    """
    signals = competitor_service.signals_for_deal(customer_industry=industry)
    return [
        SignalOut(
            competitor=s.name,
            category=s.category,
            headline=s.headline,
            detail=s.detail,
            impact=s.impact,
            source=s.source,
            tags=s.tags,
        )
        for s in signals
    ]


@router.get(
    "/market-events",
    response_model=List[MarketEventOut],
    summary="Get market events relevant to a deal",
)
def get_market_events(
    industry: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    min_impact: int = Query(default=5, ge=1, le=10),
):
    """
    Returns market events (funding, regulation, trends, M&A) filtered
    by industry relevance and minimum impact score.
    """
    events = market_events_service.events_for_deal(
        industry=industry, stage=stage, min_impact=min_impact
    )
    return [
        MarketEventOut(
            event_id=e.event_id,
            title=e.title,
            category=e.category,
            summary=e.summary,
            detail=e.detail,
            impact_score=e.impact_score,
            published_at=e.published_at,
            source=e.source,
        )
        for e in events
    ]


@router.get(
    "/brief/{deal_id}",
    response_model=DealBriefOut,
    summary="Build intelligence brief for a deal",
)
def get_deal_intelligence_brief(
    deal_id: int,
    deal_title: str = Query(...),
    customer_name: str = Query(...),
    deal_stage: str = Query(...),
    deal_value: float = Query(...),
    risk_level: str = Query(...),
    customer_industry: Optional[str] = Query(None),
):
    """
    Generates a full intelligence brief for a deal by aggregating:
    - Competitor signals ranked by impact
    - Market events filtered by industry
    - Synthesised key risks and opportunities
    - Overall intelligence pressure score (0-100)
    """
    brief = deal_intelligence_aggregator.build_brief(
        deal_id=deal_id,
        deal_title=deal_title,
        customer_name=customer_name,
        customer_industry=customer_industry,
        deal_stage=deal_stage,
        deal_value=deal_value,
        risk_level=risk_level,
    )
    return DealBriefOut(**brief.to_dict())
