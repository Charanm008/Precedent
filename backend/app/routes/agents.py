"""
Agents API Routes — Phase 4

Exposes the agentic reasoning layer via REST endpoints.
All routes are NEW — this file does not modify any Phase 1/2 routes.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..agents.orchestrator import orchestrator

router = APIRouter(prefix="/agents", tags=["agents"])


# ── Request / Response schemas ─────────────────────────────────────────────

class StakeholderInput(BaseModel):
    id: int
    name: str
    role: str
    concern: Optional[str] = None


class InteractionInput(BaseModel):
    id: int
    type: str
    summary: str
    sentiment: str = "neutral"
    strategy: Optional[str] = None
    outcome: Optional[str] = None
    stakeholder_id: Optional[int] = None


class AnalysisRequest(BaseModel):
    deal_id: int
    deal_title: str
    customer_name: str
    customer_industry: Optional[str] = None
    deal_stage: str = "Prospecting"
    deal_value: float = Field(default=0.0, ge=0)
    risk_level: str = "MEDIUM"
    interactions: List[InteractionInput] = Field(default_factory=list)
    stakeholders: List[StakeholderInput] = Field(default_factory=list)


class RecommendationOut(BaseModel):
    action: str
    rationale: str
    priority: str
    category: str
    effort: str
    expected_impact: str


class AgentResultOut(BaseModel):
    agent_name: str
    deal_id: int
    summary: str
    situation_assessment: str
    recommendations: List[RecommendationOut]
    risks_identified: List[str]
    opportunities_identified: List[str]
    confidence: str
    warnings: List[str]


class OrchestratorResultOut(BaseModel):
    deal_id: int
    deal_title: str
    intelligence_score: int
    agent_results: List[AgentResultOut]
    merged_recommendations: List[RecommendationOut]
    all_risks: List[str]
    all_opportunities: List[str]
    warnings: List[str]
    intelligence_brief: dict


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=OrchestratorResultOut,
    summary="Run all agents against a deal",
)
def analyze_deal(payload: AnalysisRequest):
    """
    Runs the full agent stack (RiskAnalyst + NextBestAction) against the
    provided deal context. Returns merged recommendations, risks,
    opportunities, and individual agent reasoning.
    """
    if payload.risk_level not in {"LOW", "MEDIUM", "HIGH"}:
        raise HTTPException(status_code=422, detail="risk_level must be LOW, MEDIUM, or HIGH")

    result = orchestrator.run(
        deal_id=payload.deal_id,
        deal_title=payload.deal_title,
        customer_name=payload.customer_name,
        customer_industry=payload.customer_industry,
        deal_stage=payload.deal_stage,
        deal_value=payload.deal_value,
        risk_level=payload.risk_level,
        interactions=[i.model_dump() for i in payload.interactions],
        stakeholders=[s.model_dump() for s in payload.stakeholders],
    )
    return result


@router.get(
    "/agents",
    summary="List available reasoning agents",
)
def list_agents():
    """Returns metadata about all registered reasoning agents."""
    return {
        "agents": [
            {
                "name": "RiskAnalyst",
                "description": (
                    "Identifies risks across 5 dimensions: competitive threats, "
                    "relationship gaps, sentiment, market/regulatory exposure, and "
                    "process risks. Generates prioritised mitigation recommendations."
                ),
                "version": "1.0",
                "phase": "Phase 4",
            },
            {
                "name": "NextBestAction",
                "description": (
                    "Determines the single most impactful next action using stage "
                    "playbooks, interaction patterns, stakeholder concerns, and "
                    "competitive intelligence signals."
                ),
                "version": "1.0",
                "phase": "Phase 4",
            },
        ]
    }
