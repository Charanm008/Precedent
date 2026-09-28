"""
Agent Orchestrator — Phase 4

Runs all registered agents against a deal context and merges results
into a single unified recommendation set. This is the single entry-point
called by the agents API route.
"""

from __future__ import annotations

from typing import List

from .base_agent import AgentResult, Recommendation
from .risk_analyst import RiskAnalystAgent
from .next_best_action import NextBestActionAgent
from ..intelligence.deal_intelligence import deal_intelligence_aggregator


class AgentOrchestrator:
    """
    Orchestrates execution of all registered agents and merges their outputs
    into a unified final result.
    """

    def __init__(self):
        self._agents = [
            RiskAnalystAgent(),
            NextBestActionAgent(),
        ]

    def run(
        self,
        deal_id: int,
        deal_title: str,
        customer_name: str,
        customer_industry: str | None,
        deal_stage: str,
        deal_value: float,
        risk_level: str,
        interactions: List[dict],
        stakeholders: List[dict],
    ) -> dict:
        """
        Builds the intelligence brief and runs all agents.
        Returns a merged orchestration result.
        """
        # Build intelligence brief
        brief = deal_intelligence_aggregator.build_brief(
            deal_id=deal_id,
            deal_title=deal_title,
            customer_name=customer_name,
            customer_industry=customer_industry,
            deal_stage=deal_stage,
            deal_value=deal_value,
            risk_level=risk_level,
        )

        context = {
            "brief": brief.to_dict(),
            "interactions": interactions,
            "stakeholders": stakeholders,
        }

        # Run all agents
        agent_results: List[AgentResult] = []
        for agent in self._agents:
            result = agent.analyze(context)
            agent_results.append(result)

        # Merge and deduplicate recommendations
        merged_recs = self._merge_recommendations(agent_results)

        # Merge risks and opportunities across all agents
        all_risks = []
        all_opportunities = []
        all_warnings = []
        for result in agent_results:
            all_risks.extend(result.risks_identified)
            all_opportunities.extend(result.opportunities_identified)
            all_warnings.extend(result.warnings)

        unique_risks = list(dict.fromkeys(all_risks))
        unique_opportunities = list(dict.fromkeys(all_opportunities))
        unique_warnings = list(dict.fromkeys(all_warnings))

        return {
            "deal_id": deal_id,
            "deal_title": deal_title,
            "intelligence_score": brief.intelligence_score,
            "agent_results": [r.to_dict() for r in agent_results],
            "merged_recommendations": [
                {
                    "action": r.action,
                    "rationale": r.rationale,
                    "priority": r.priority,
                    "category": r.category,
                    "effort": r.effort,
                    "expected_impact": r.expected_impact,
                }
                for r in merged_recs
            ],
            "all_risks": unique_risks,
            "all_opportunities": unique_opportunities,
            "warnings": unique_warnings,
            "intelligence_brief": brief.to_dict(),
        }

    def _merge_recommendations(self, results: List[AgentResult]) -> List[Recommendation]:
        """
        Merges recommendations from all agents, deduplicating by action text
        and sorting HIGH → MEDIUM → LOW.
        """
        seen_actions: set[str] = set()
        merged: List[Recommendation] = []

        for result in results:
            for rec in result.recommendations:
                # Simple dedup: skip if action text already seen
                key = rec.action[:60].lower().strip()
                if key not in seen_actions:
                    seen_actions.add(key)
                    merged.append(rec)

        return sorted(
            merged,
            key=lambda r: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r.priority], r.effort),
        )


# Module-level singleton
orchestrator = AgentOrchestrator()
