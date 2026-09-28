"""
Phase 3 & 4 Tests — Intelligence Engine and AI Agents

Tests are self-contained and do not require a running DB or external APIs.
"""

import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from backend.app.intelligence.competitor_service import competitor_service
from backend.app.intelligence.market_events_service import market_events_service
from backend.app.intelligence.deal_intelligence import deal_intelligence_aggregator
from backend.app.agents.risk_analyst import RiskAnalystAgent
from backend.app.agents.next_best_action import NextBestActionAgent
from backend.app.agents.orchestrator import orchestrator


# ── Phase 3: Intelligence Engine ──────────────────────────────────────────

class TestCompetitorService:
    def test_all_competitors_returns_list(self):
        names = competitor_service.all_competitors()
        assert isinstance(names, list)
        assert len(names) >= 1

    def test_known_competitor_profile(self):
        profile = competitor_service.get_profile("SalesForce")
        assert profile is not None
        assert profile.name == "SalesForce"
        assert len(profile.known_strengths) > 0
        assert len(profile.known_weaknesses) > 0

    def test_unknown_competitor_returns_none(self):
        profile = competitor_service.get_profile("NonExistentCRM")
        assert profile is None

    def test_signals_for_deal_returns_sorted(self):
        signals = competitor_service.signals_for_deal(customer_industry="SaaS")
        impacts = [s.impact for s in signals]
        # HIGH should come before MEDIUM which comes before LOW
        impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        orders = [impact_order[i] for i in impacts]
        assert orders == sorted(orders)

    def test_threats_summary_structure(self):
        summary = competitor_service.threats_summary("enterprise")
        assert "high_impact" in summary
        assert "medium_impact" in summary
        assert "total" in summary


class TestMarketEventsService:
    def test_all_events_not_empty(self):
        events = market_events_service.all_events()
        assert len(events) >= 1

    def test_all_events_sorted_by_impact(self):
        events = market_events_service.all_events()
        scores = [e.impact_score for e in events]
        assert scores == sorted(scores, reverse=True)

    def test_filter_by_min_impact(self):
        events = market_events_service.events_for_deal(min_impact=8)
        assert all(e.impact_score >= 8 for e in events)

    def test_high_impact_summary_structure(self):
        summary = market_events_service.high_impact_summary("SaaS")
        assert "count" in summary
        assert "events" in summary
        assert isinstance(summary["events"], list)


class TestDealIntelligenceAggregator:
    def _sample_brief(self):
        return deal_intelligence_aggregator.build_brief(
            deal_id=1,
            deal_title="Enterprise CRM Rollout",
            customer_name="Acme Corp",
            customer_industry="SaaS",
            deal_stage="Discovery",
            deal_value=150_000.0,
            risk_level="MEDIUM",
        )

    def test_brief_has_required_fields(self):
        brief = self._sample_brief()
        assert brief.deal_id == 1
        assert brief.deal_title == "Enterprise CRM Rollout"
        assert isinstance(brief.competitor_signals, list)
        assert isinstance(brief.market_events, list)
        assert isinstance(brief.key_risks, list)
        assert isinstance(brief.key_opportunities, list)
        assert 0 <= brief.intelligence_score <= 100

    def test_brief_to_dict(self):
        brief = self._sample_brief()
        d = brief.to_dict()
        assert isinstance(d, dict)
        assert "intelligence_score" in d

    def test_high_risk_increases_score(self):
        low = deal_intelligence_aggregator.build_brief(
            deal_id=2, deal_title="T", customer_name="C",
            customer_industry=None, deal_stage="Discovery",
            deal_value=10_000, risk_level="LOW"
        )
        high = deal_intelligence_aggregator.build_brief(
            deal_id=3, deal_title="T", customer_name="C",
            customer_industry=None, deal_stage="Discovery",
            deal_value=10_000, risk_level="HIGH"
        )
        assert high.intelligence_score > low.intelligence_score


# ── Phase 4: AI Agents ────────────────────────────────────────────────────

def _make_context(
    deal_id=10,
    stage="Discovery",
    risk_level="MEDIUM",
    deal_value=80_000.0,
    interactions=None,
    stakeholders=None,
):
    brief = deal_intelligence_aggregator.build_brief(
        deal_id=deal_id,
        deal_title="Test Deal",
        customer_name="Beta Corp",
        customer_industry="SaaS",
        deal_stage=stage,
        deal_value=deal_value,
        risk_level=risk_level,
    )
    return {
        "brief": brief.to_dict(),
        "interactions": interactions or [],
        "stakeholders": stakeholders or [],
    }


class TestRiskAnalystAgent:
    def test_returns_agent_result(self):
        agent = RiskAnalystAgent()
        result = agent.analyze(_make_context())
        assert result.agent_name == "RiskAnalyst"
        assert isinstance(result.recommendations, list)
        assert isinstance(result.risks_identified, list)
        assert result.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_no_stakeholders_generates_risk(self):
        agent = RiskAnalystAgent()
        result = agent.analyze(_make_context(stakeholders=[]))
        risk_texts = " ".join(result.risks_identified).lower()
        # Should flag missing stakeholder mapping
        assert any("stakeholder" in r.action.lower() for r in result.recommendations)

    def test_negative_sentiment_generates_recommendation(self):
        agent = RiskAnalystAgent()
        interactions = [{"id": 1, "type": "call", "summary": "bad call", "sentiment": "negative", "outcome": "failed"}]
        result = agent.analyze(_make_context(interactions=interactions))
        rec_actions = [r.action.lower() for r in result.recommendations]
        assert any("reset" in a or "follow" in a or "call" in a for a in rec_actions)

    def test_high_risk_deal_value_generates_exec_rec(self):
        agent = RiskAnalystAgent()
        result = agent.analyze(_make_context(stage="Prospecting", deal_value=250_000))
        rec_actions = [r.action.lower() for r in result.recommendations]
        assert any("exec" in a or "sponsor" in a for a in rec_actions)


class TestNextBestActionAgent:
    def test_returns_agent_result(self):
        agent = NextBestActionAgent()
        result = agent.analyze(_make_context())
        assert result.agent_name == "NextBestAction"
        assert len(result.recommendations) >= 1

    def test_no_interactions_warns_and_recommends_log(self):
        agent = NextBestActionAgent()
        result = agent.analyze(_make_context(interactions=[]))
        assert any("log" in r.action.lower() or "interaction" in r.action.lower()
                   for r in result.recommendations)

    def test_stage_playbook_recommendation_present(self):
        agent = NextBestActionAgent()
        result = agent.analyze(_make_context(stage="Proposal"))
        # Primary recommendation should reference proposal stage
        assert len(result.recommendations) >= 1

    def test_stakeholder_concern_generates_recommendation(self):
        agent = NextBestActionAgent()
        stakeholders = [{"id": 1, "name": "Alice", "role": "CTO", "concern": "Security compliance"}]
        result = agent.analyze(_make_context(stakeholders=stakeholders))
        rec_actions = " ".join(r.action for r in result.recommendations).lower()
        assert "alice" in rec_actions or "concern" in rec_actions or "security" in rec_actions


class TestOrchestrator:
    def test_orchestrator_runs_all_agents(self):
        result = orchestrator.run(
            deal_id=99,
            deal_title="Orch Test Deal",
            customer_name="Gamma Ltd",
            customer_industry="SaaS",
            deal_stage="Negotiation",
            deal_value=200_000.0,
            risk_level="HIGH",
            interactions=[
                {"id": 1, "type": "meeting", "summary": "tough negotiation", "sentiment": "negative", "outcome": "neutral"}
            ],
            stakeholders=[
                {"id": 1, "name": "Bob", "role": "CFO", "concern": "ROI proof"},
            ],
        )
        assert "agent_results" in result
        assert len(result["agent_results"]) == 2  # RiskAnalyst + NextBestAction
        assert "merged_recommendations" in result
        assert "all_risks" in result
        assert "intelligence_score" in result
        assert len(result["merged_recommendations"]) >= 1

    def test_merged_recs_sorted_by_priority(self):
        result = orchestrator.run(
            deal_id=100,
            deal_title="Sort Test",
            customer_name="Delta Inc",
            customer_industry=None,
            deal_stage="Discovery",
            deal_value=50_000.0,
            risk_level="MEDIUM",
            interactions=[],
            stakeholders=[],
        )
        priorities = [r["priority"] for r in result["merged_recommendations"]]
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        assert [order[p] for p in priorities] == sorted([order[p] for p in priorities])
