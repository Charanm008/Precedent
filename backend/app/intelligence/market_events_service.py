"""
Market Events Service — Phase 3

Tracks and serves external market signals (funding rounds, M&A, regulation
changes, industry news) that are relevant to an active deal's context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class MarketEvent:
    event_id: str
    title: str
    category: str       # "funding" | "regulation" | "ma" | "trend" | "threat"
    summary: str
    detail: str
    relevance_tags: List[str]   # industries / stages / keywords
    impact_score: int           # 1-10
    published_at: str           # ISO date string
    source: str


# ---------------------------------------------------------------------------
# Static event catalogue — wire up a news API (e.g. NewsAPI, GDELT) in prod
# ---------------------------------------------------------------------------
_MARKET_EVENTS: List[MarketEvent] = [
    MarketEvent(
        event_id="EVT-001",
        title="$2.3B Series D raised by AI-native CRM startup 'Vela'",
        category="funding",
        summary=(
            "Vela, an AI-native CRM for enterprise sales, closed a $2.3B Series D "
            "at a $14B valuation. Signals continued VC confidence in AI sales tooling."
        ),
        detail=(
            "Vela raised from a16z, Tiger Global, and Google Ventures. "
            "Their GTM targets Fortune 500 procurement and sales ops. "
            "Expected to GA their full product in Q1 2027."
        ),
        relevance_tags=["SaaS", "CRM", "enterprise", "AI", "sales"],
        impact_score=8,
        published_at="2026-09-20",
        source="techcrunch.com/2026/09/vela-series-d",
    ),
    MarketEvent(
        event_id="EVT-002",
        title="EU AI Act enforcement begins — sales AI tools under scrutiny",
        category="regulation",
        summary=(
            "EU AI Act Category B enforcement started Sept 2026. "
            "AI systems making decisions about deal scoring or customer risk must "
            "provide explainability trails or face €15M fines."
        ),
        detail=(
            "Any AI-generated recommendation presented to an end-user that "
            "influences a commercial decision is now considered a 'high-risk AI system' "
            "under Art. 6(2). Vendors must maintain audit logs and explanation records."
        ),
        relevance_tags=["regulation", "EU", "AI", "compliance", "enterprise"],
        impact_score=9,
        published_at="2026-09-01",
        source="europa.eu/ai-act/enforcement-2026",
    ),
    MarketEvent(
        event_id="EVT-003",
        title="Gartner: 65 % of B2B sales orgs to adopt AI deal coaching by 2027",
        category="trend",
        summary=(
            "Gartner's latest report forecasts that 65% of B2B sales orgs will deploy "
            "AI deal-coaching tools within 18 months, up from 22% today."
        ),
        detail=(
            "Adoption is fastest in technology, financial services, and manufacturing. "
            "The report identifies 'persistent deal memory' as the #1 differentiator "
            "driving NRR improvements of 18% YoY in early adopters."
        ),
        relevance_tags=["trend", "B2B", "sales", "AI", "enterprise", "SaaS"],
        impact_score=7,
        published_at="2026-09-15",
        source="gartner.com/reports/ai-deal-coaching-2027",
    ),
    MarketEvent(
        event_id="EVT-004",
        title="Microsoft acquires ConversationAI — deep Outlook + Teams CRM hooks",
        category="ma",
        summary=(
            "Microsoft completed acquisition of ConversationAI, integrating "
            "meeting transcript analysis directly into Dynamics 365 and Teams."
        ),
        detail=(
            "The acquisition adds automatic deal summaries from Teams calls "
            "into Dynamics CRM records. This makes Microsoft's stack substantially "
            "stickier for existing M365 enterprise customers."
        ),
        relevance_tags=["M&A", "Microsoft", "enterprise", "CRM", "integration"],
        impact_score=8,
        published_at="2026-09-10",
        source="bloomberg.com/news/microsoft-conversationai",
    ),
    MarketEvent(
        event_id="EVT-005",
        title="Data privacy regulation tightens in India — DPDP Act penalties active",
        category="regulation",
        summary=(
            "India's Digital Personal Data Protection Act penalties are now active. "
            "SaaS vendors storing Indian customer data must comply or face ₹250Cr fines."
        ),
        detail=(
            "Affects any deal involving Indian enterprise customers where PII is stored "
            "outside India or processed by AI models without explicit consent."
        ),
        relevance_tags=["regulation", "India", "privacy", "compliance", "SaaS"],
        impact_score=8,
        published_at="2026-09-05",
        source="meity.gov.in/dpdp-penalties",
    ),
    MarketEvent(
        event_id="EVT-006",
        title="Slowdown in enterprise SaaS spending in Q3 2026",
        category="trend",
        summary=(
            "Multiple analyst firms report a 12% YoY slowdown in enterprise SaaS "
            "budget approvals in Q3 2026, with procurement cycles extending by 3-6 weeks."
        ),
        detail=(
            "CFOs are scrutinising AI tool ROI more aggressively. Deals under $100K ARR "
            "closing faster; deals above $500K ARR seeing extra security/procurement reviews."
        ),
        relevance_tags=["budget", "enterprise", "SaaS", "sales", "slowdown"],
        impact_score=6,
        published_at="2026-09-18",
        source="forrester.com/q3-saas-spending-2026",
    ),
]


class MarketEventsService:
    """Serves and filters market events by relevance to a deal context."""

    def all_events(self) -> List[MarketEvent]:
        return sorted(_MARKET_EVENTS, key=lambda e: e.impact_score, reverse=True)

    def events_for_deal(
        self,
        industry: Optional[str] = None,
        stage: Optional[str] = None,
        min_impact: int = 5,
    ) -> List[MarketEvent]:
        """
        Filter events relevant to a deal by industry tag and minimum impact score.
        If no industry supplied, returns all events above impact threshold.
        """
        results = []
        for event in _MARKET_EVENTS:
            if event.impact_score < min_impact:
                continue
            if industry:
                industry_lower = industry.lower()
                tag_match = any(
                    industry_lower in tag.lower() or tag.lower() in industry_lower
                    for tag in event.relevance_tags
                )
                if not tag_match:
                    # Still include high-impact cross-industry signals
                    if event.impact_score < 8:
                        continue
            results.append(event)
        return sorted(results, key=lambda e: e.impact_score, reverse=True)

    def high_impact_summary(self, industry: Optional[str] = None) -> dict:
        events = self.events_for_deal(industry=industry, min_impact=7)
        return {
            "count": len(events),
            "events": [
                {
                    "event_id": e.event_id,
                    "title": e.title,
                    "category": e.category,
                    "impact_score": e.impact_score,
                    "summary": e.summary,
                    "published_at": e.published_at,
                    "source": e.source,
                }
                for e in events
            ],
        }


# Module-level singleton
market_events_service = MarketEventsService()
