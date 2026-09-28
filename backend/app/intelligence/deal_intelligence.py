"""
Deal Intelligence Aggregator — Phase 3

Combines competitor signals + market events into a single structured
intelligence brief for a given deal. This is the primary object consumed
by the Phase 4 AI agents.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional

from .competitor_service import CompetitorSignal, competitor_service
from .market_events_service import MarketEvent, market_events_service


@dataclass
class DealIntelligenceBrief:
    deal_id: int
    deal_title: str
    customer_name: str
    customer_industry: Optional[str]
    deal_stage: str
    deal_value: float
    risk_level: str
    competitor_signals: List[dict]          # high → low priority
    market_events: List[dict]               # high → low impact
    key_risks: List[str]                    # synthesised risk statements
    key_opportunities: List[str]            # synthesised opportunity statements
    intelligence_score: int                 # 0-100 overall external pressure index

    def to_dict(self) -> dict:
        return asdict(self)


class DealIntelligenceAggregator:
    """
    Builds a DealIntelligenceBrief by pulling data from both
    the CompetitorIntelligenceService and the MarketEventsService.
    """

    def build_brief(
        self,
        deal_id: int,
        deal_title: str,
        customer_name: str,
        customer_industry: Optional[str],
        deal_stage: str,
        deal_value: float,
        risk_level: str,
    ) -> DealIntelligenceBrief:

        # 1. Pull competitor signals
        comp_signals: List[CompetitorSignal] = competitor_service.signals_for_deal(
            customer_industry=customer_industry
        )

        # 2. Pull market events
        events: List[MarketEvent] = market_events_service.events_for_deal(
            industry=customer_industry,
            stage=deal_stage,
        )

        # 3. Synthesise risk & opportunity statements
        key_risks = self._extract_risks(comp_signals, events, risk_level, deal_stage)
        key_opportunities = self._extract_opportunities(comp_signals, events)

        # 4. Compute an external pressure / intelligence score (0-100)
        intel_score = self._compute_score(comp_signals, events, risk_level)

        return DealIntelligenceBrief(
            deal_id=deal_id,
            deal_title=deal_title,
            customer_name=customer_name,
            customer_industry=customer_industry,
            deal_stage=deal_stage,
            deal_value=deal_value,
            risk_level=risk_level,
            competitor_signals=[
                {
                    "competitor": s.name,
                    "category": s.category,
                    "headline": s.headline,
                    "detail": s.detail,
                    "impact": s.impact,
                    "source": s.source,
                    "tags": s.tags,
                }
                for s in comp_signals
            ],
            market_events=[
                {
                    "event_id": e.event_id,
                    "title": e.title,
                    "category": e.category,
                    "summary": e.summary,
                    "impact_score": e.impact_score,
                    "published_at": e.published_at,
                    "source": e.source,
                }
                for e in events
            ],
            key_risks=key_risks,
            key_opportunities=key_opportunities,
            intelligence_score=intel_score,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_risks(
        self,
        signals: List[CompetitorSignal],
        events: List[MarketEvent],
        risk_level: str,
        stage: str,
    ) -> List[str]:
        risks = []

        # From competitor signals
        for s in signals:
            if s.impact == "HIGH":
                risks.append(
                    f"[Competitor] {s.name} — {s.headline}. This is a high-impact "
                    f"competitive threat in the {s.category} dimension."
                )

        # From market events
        for e in events:
            if e.impact_score >= 8 and e.category in ("regulation", "threat", "ma"):
                risks.append(
                    f"[Market] {e.title} — {e.summary}"
                )

        # Contextual deal risk
        if risk_level == "HIGH":
            risks.insert(0, "Deal is internally flagged HIGH risk — prioritise mitigation actions.")
        if stage in ("Negotiation", "Proposal") and any(
            e.category == "trend" and "slowdown" in e.summary.lower() for e in events
        ):
            risks.append(
                "Market slowdown detected during critical negotiation phase — "
                "budget scrutiny may delay close."
            )

        return risks[:6]  # Cap to top 6

    def _extract_opportunities(
        self,
        signals: List[CompetitorSignal],
        events: List[MarketEvent],
    ) -> List[str]:
        opps = []

        # Competitor weaknesses → opportunities
        for name in competitor_service.all_competitors():
            profile = competitor_service.get_profile(name)
            if profile and profile.known_weaknesses:
                opps.append(
                    f"[Competitive Gap] {name} is weak in: "
                    + ", ".join(profile.known_weaknesses[:2])
                    + ". Use this as a differentiation angle."
                )

        # Market trend opportunities
        for e in events:
            if e.category == "trend" and e.impact_score >= 7:
                opps.append(f"[Market Trend] {e.title} — {e.summary}")

        return opps[:5]  # Cap to top 5

    def _compute_score(
        self,
        signals: List[CompetitorSignal],
        events: List[MarketEvent],
        risk_level: str,
    ) -> int:
        score = 30  # baseline

        # Competitor signal pressure
        for s in signals:
            score += {"HIGH": 12, "MEDIUM": 6, "LOW": 2}.get(s.impact, 0)

        # Market event pressure
        for e in events:
            score += max(0, e.impact_score - 4)

        # Internal risk level
        score += {"HIGH": 20, "MEDIUM": 10, "LOW": 0}.get(risk_level, 0)

        return min(score, 100)


# Module-level singleton
deal_intelligence_aggregator = DealIntelligenceAggregator()
