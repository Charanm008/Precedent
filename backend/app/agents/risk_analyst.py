"""
Risk Analyst Agent — Phase 4

Analyses deal data, interaction history, and external intelligence to
identify risks and generate specific risk-mitigation recommendations.
"""

from __future__ import annotations

from typing import List

from .base_agent import BaseAgent, AgentResult, Recommendation


class RiskAnalystAgent(BaseAgent):
    """
    Identifies deal risks across four dimensions:
      1. Competitive threats (from intelligence brief)
      2. Relationship gaps (from stakeholder / interaction data)
      3. Market / regulatory exposure (from market events)
      4. Process risks (stage-to-value mismatch, stale pipeline, etc.)
    """

    @property
    def name(self) -> str:
        return "RiskAnalyst"

    def analyze(self, context: dict) -> AgentResult:
        brief = context.get("brief", {})
        interactions: List[dict] = context.get("interactions", [])
        stakeholders: List[dict] = context.get("stakeholders", [])

        risks: List[str] = []
        recs: List[Recommendation] = []
        warnings: List[str] = []

        deal_id = brief.get("deal_id", 0)
        stage = brief.get("deal_stage", "")
        risk_level = brief.get("risk_level", "MEDIUM")
        deal_value = brief.get("deal_value", 0)
        intel_score = brief.get("intelligence_score", 0)

        # ── 1. Competitive risk ──────────────────────────────────────
        comp_signals = brief.get("competitor_signals", [])
        high_comp_signals = [s for s in comp_signals if s.get("impact") == "HIGH"]
        if high_comp_signals:
            for s in high_comp_signals:
                risks.append(f"Competitor '{s['competitor']}': {s['headline']}")
                recs.append(
                    Recommendation(
                        action=f"Prepare competitive battle card against {s['competitor']}",
                        rationale=(
                            f"{s['headline']} — this signal directly threatens your "
                            f"positioning in the {s['category']} dimension."
                        ),
                        priority="HIGH",
                        category="competitive",
                        effort="MEDIUM",
                        expected_impact=(
                            "Equips AE with concrete counter-narrative; reduces risk "
                            "of losing to this competitor's messaging."
                        ),
                    )
                )

        # ── 2. Relationship risk ────────────────────────────────────
        if len(stakeholders) == 0:
            risks.append("No stakeholders mapped — deal lacks identified champions or blockers.")
            recs.append(
                Recommendation(
                    action="Map at least 3 stakeholders (champion, economic buyer, technical evaluator)",
                    rationale=(
                        "Deals with zero stakeholder mapping close 40% less often. "
                        "Without knowing the economic buyer, pricing conversations stall."
                    ),
                    priority="HIGH",
                    category="relationship",
                    effort="LOW",
                    expected_impact="Accelerates path to proposal; identifies blockers early.",
                )
            )
        elif len(stakeholders) < 2:
            risks.append(f"Only {len(stakeholders)} stakeholder mapped — single-threaded risk.")
            recs.append(
                Recommendation(
                    action="Multi-thread: identify and engage a second stakeholder",
                    rationale=(
                        "Single-threaded deals are high-churn risk — if the champion "
                        "leaves or loses influence, the deal collapses."
                    ),
                    priority="MEDIUM",
                    category="relationship",
                    effort="MEDIUM",
                    expected_impact="Reduces deal-collapse risk from champion churn.",
                )
            )

        # ── 3. Interaction sentiment risk ───────────────────────────
        negative_interactions = [
            i for i in interactions if i.get("sentiment") == "negative"
        ]
        if negative_interactions:
            risks.append(
                f"{len(negative_interactions)} negative interaction(s) recorded — "
                "deal sentiment trending unfavourably."
            )
            recs.append(
                Recommendation(
                    action="Schedule a relationship reset call with the primary stakeholder",
                    rationale=(
                        f"{len(negative_interactions)} negative interaction(s) detected. "
                        "Unaddressed negative sentiment compounds over time."
                    ),
                    priority="HIGH",
                    category="relationship",
                    effort="LOW",
                    expected_impact="Recovers deal momentum; surfaces hidden objections.",
                )
            )

        # ── 4. Market / regulatory risk ─────────────────────────────
        market_events = brief.get("market_events", [])
        reg_events = [e for e in market_events if e.get("category") == "regulation"]
        if reg_events:
            for e in reg_events:
                risks.append(f"Regulatory exposure: {e['title']}")
                recs.append(
                    Recommendation(
                        action=f"Add compliance/legal to deal review: '{e['title']}'",
                        rationale=e["summary"],
                        priority="HIGH" if e["impact_score"] >= 8 else "MEDIUM",
                        category="risk",
                        effort="MEDIUM",
                        expected_impact=(
                            "Proactively addressing regulatory concerns builds trust "
                            "and prevents last-minute legal blockers."
                        ),
                    )
                )

        # ── 5. Process / pipeline risk ──────────────────────────────
        if deal_value > 100_000 and stage in ("Prospecting", "Discovery"):
            risks.append(
                f"High-value deal (${deal_value:,.0f}) still in early stage '{stage}' — "
                "may require executive alignment before progressing."
            )
            recs.append(
                Recommendation(
                    action="Arrange executive sponsor meeting before next stage gate",
                    rationale=(
                        "Deals above $100K typically require C-suite or VP sign-off. "
                        "Early executive engagement shortens close cycles by 25%."
                    ),
                    priority="MEDIUM",
                    category="process",
                    effort="HIGH",
                    expected_impact="Accelerates deal velocity and reduces late-stage surprises.",
                )
            )

        if intel_score > 70:
            warnings.append(
                f"External intelligence pressure score is {intel_score}/100 — "
                "significant competitive and market pressure detected."
            )

        # ── Build confidence ────────────────────────────────────────
        high_recs = [r for r in recs if r.priority == "HIGH"]
        confidence = "HIGH" if len(high_recs) <= 1 else "MEDIUM" if len(high_recs) <= 3 else "LOW"

        return AgentResult(
            agent_name=self.name,
            deal_id=deal_id,
            summary=(
                f"Identified {len(risks)} risk(s) across competitive, relationship, "
                f"market, and process dimensions for deal '{brief.get('deal_title', '')}'. "
                f"Intelligence pressure score: {intel_score}/100."
            ),
            situation_assessment=self._build_assessment(brief, risks, interactions, stakeholders),
            recommendations=sorted(recs, key=lambda r: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r.priority]),
            risks_identified=risks,
            opportunities_identified=brief.get("key_opportunities", []),
            confidence=confidence,
            warnings=warnings,
        )

    def _build_assessment(
        self, brief: dict, risks: List[str], interactions: List[dict], stakeholders: List[dict]
    ) -> str:
        stage = brief.get("deal_stage", "Unknown")
        value = brief.get("deal_value", 0)
        risk_level = brief.get("risk_level", "MEDIUM")
        n_interactions = len(interactions)
        n_stakeholders = len(stakeholders)
        n_risks = len(risks)

        return (
            f"This deal is currently in the '{stage}' stage with a value of ${value:,.0f} "
            f"and is internally rated as {risk_level} risk. "
            f"{n_stakeholders} stakeholder(s) have been identified and {n_interactions} "
            f"interaction(s) recorded. "
            f"External intelligence analysis has surfaced {n_risks} risk factor(s). "
            + (
                "Immediate attention to high-priority risks is recommended before "
                "progressing to the next stage."
                if n_risks > 2
                else "Risk profile is manageable — focus on relationship momentum."
            )
        )
