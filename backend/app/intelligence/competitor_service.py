"""
Competitor Intelligence Service — Phase 3

Gathers and structures competitor information relevant to an active deal.
This module is intentionally decoupled from the DB layer so it can be
called by both API routes and agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CompetitorSignal:
    """A single intelligence signal about one competitor."""
    name: str
    category: str          # "pricing" | "product" | "news" | "partnership"
    headline: str
    detail: str
    impact: str            # "HIGH" | "MEDIUM" | "LOW"
    source: str            # free-text — URL or label
    tags: List[str] = field(default_factory=list)


@dataclass
class CompetitorProfile:
    name: str
    industry: str
    known_strengths: List[str] = field(default_factory=list)
    known_weaknesses: List[str] = field(default_factory=list)
    signals: List[CompetitorSignal] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Static intelligence library — replace with a live scraper / API in prod
# ---------------------------------------------------------------------------
_COMPETITOR_DB: dict[str, CompetitorProfile] = {
    "SalesForce": CompetitorProfile(
        name="SalesForce",
        industry="CRM / SaaS",
        known_strengths=[
            "Enterprise brand recognition",
            "Deep ecosystem (AppExchange)",
            "Advanced AI (Einstein GPT)",
        ],
        known_weaknesses=[
            "High licensing costs",
            "Steep onboarding curve",
            "Bloated UI for SMB teams",
        ],
        signals=[
            CompetitorSignal(
                name="SalesForce",
                category="pricing",
                headline="Salesforce raises Enterprise Cloud prices by 9 %",
                detail=(
                    "Effective Q4, Salesforce will increase Enterprise Cloud "
                    "SKU pricing across all tiers. Existing contracts are locked "
                    "until renewal — new logos face the higher rate immediately."
                ),
                impact="HIGH",
                source="techcrunch.com/2026/salesforce-price-hike",
                tags=["pricing", "enterprise", "q4"],
            ),
            CompetitorSignal(
                name="SalesForce",
                category="product",
                headline="Einstein Copilot GA released — 50 native integrations",
                detail=(
                    "Salesforce GA'd Einstein Copilot across all Sales Cloud tiers. "
                    "50 out-of-the-box CRM integrations announced. Threat to deals "
                    "where AI-first pitch is the differentiator."
                ),
                impact="MEDIUM",
                source="salesforce.com/news/einstein-copilot-ga",
                tags=["ai", "product", "ga"],
            ),
        ],
    ),
    "HubSpot": CompetitorProfile(
        name="HubSpot",
        industry="CRM / Marketing",
        known_strengths=[
            "Generous free tier",
            "Best-in-class inbound marketing stack",
            "Low time-to-value",
        ],
        known_weaknesses=[
            "Weak enterprise deal management",
            "Limited offline / on-prem option",
            "Reporting depth behind enterprise CRMs",
        ],
        signals=[
            CompetitorSignal(
                name="HubSpot",
                category="partnership",
                headline="HubSpot–LinkedIn Sales Navigator deep integration launched",
                detail=(
                    "HubSpot now syncs LinkedIn Sales Navigator activity directly "
                    "into deal timelines. Strong play for social-led sales motions."
                ),
                impact="MEDIUM",
                source="hubspot.com/product/linkedin-sn-integration",
                tags=["integration", "linkedin", "social"],
            ),
        ],
    ),
    "Pipedrive": CompetitorProfile(
        name="Pipedrive",
        industry="CRM / SMB",
        known_strengths=[
            "Pipeline-first UI",
            "Affordable entry price",
            "Quick setup",
        ],
        known_weaknesses=[
            "Limited AI capabilities",
            "Weak enterprise support SLAs",
            "No built-in marketing automation",
        ],
        signals=[
            CompetitorSignal(
                name="Pipedrive",
                category="news",
                headline="Pipedrive acquires Dealbot AI — launches AI assistant beta",
                detail=(
                    "Pipedrive acquired Dealbot AI and shipped a beta AI sales "
                    "assistant inside its pipeline view. Directly competes with "
                    "AI-recommendation features."
                ),
                impact="HIGH",
                source="pipedrive.com/blog/dealbot-acquisition",
                tags=["ai", "acquisition", "beta"],
            ),
        ],
    ),
    "Zoho CRM": CompetitorProfile(
        name="Zoho CRM",
        industry="CRM / SMB-Mid Market",
        known_strengths=[
            "Extremely cost-competitive",
            "Full Zoho suite integration",
            "Strong India / APAC presence",
        ],
        known_weaknesses=[
            "UI polish lags competitors",
            "Enterprise sales cycle support limited",
            "Support quality inconsistent",
        ],
        signals=[],
    ),
}


class CompetitorIntelligenceService:
    """
    Resolves competitor profiles and signals relative to a deal's industry.
    Falls back to all known competitors when industry is unrecognised.
    """

    def get_profile(self, name: str) -> Optional[CompetitorProfile]:
        return _COMPETITOR_DB.get(name)

    def all_competitors(self) -> List[str]:
        return list(_COMPETITOR_DB.keys())

    def signals_for_deal(
        self,
        customer_industry: Optional[str],
        competitors: Optional[List[str]] = None,
    ) -> List[CompetitorSignal]:
        """
        Return all high-relevance competitor signals.

        If `competitors` is supplied, limit to that list.
        Otherwise return all signals across every tracked competitor.
        """
        target_names = competitors if competitors else list(_COMPETITOR_DB.keys())
        signals: List[CompetitorSignal] = []
        for name in target_names:
            profile = _COMPETITOR_DB.get(name)
            if profile:
                signals.extend(profile.signals)
        return sorted(signals, key=lambda s: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[s.impact])

    def threats_summary(self, customer_industry: Optional[str]) -> dict:
        """Structured threat summary — consumed by agents."""
        all_signals = self.signals_for_deal(customer_industry)
        return {
            "high_impact": [s.__dict__ for s in all_signals if s.impact == "HIGH"],
            "medium_impact": [s.__dict__ for s in all_signals if s.impact == "MEDIUM"],
            "low_impact": [s.__dict__ for s in all_signals if s.impact == "LOW"],
            "total": len(all_signals),
        }


# Module-level singleton
competitor_service = CompetitorIntelligenceService()
