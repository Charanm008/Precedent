"""
Next-Best-Action Agent — Phase 4

Uses deal data + intelligence brief to recommend the single most impactful
action the sales rep should take RIGHT NOW, with full reasoning.
Also generates a ranked list of additional recommended actions.
"""

from __future__ import annotations

from typing import List

from .base_agent import BaseAgent, AgentResult, Recommendation

# Stage progression map — what actions drive deals forward at each stage
_STAGE_PLAYBOOK: dict[str, dict] = {
    "Prospecting": {
        "primary_goal": "Qualify and establish interest",
        "next_step": "Book a discovery call to qualify BANT (Budget, Authority, Need, Timeline)",
        "recommended_assets": ["Cold email sequence", "Case study in their industry", "ROI calculator"],
    },
    "Discovery": {
        "primary_goal": "Understand pain, map stakeholders, confirm budget",
        "next_step": "Deliver a tailored discovery summary and proposed solution outline",
        "recommended_assets": ["Discovery recap document", "Stakeholder map", "Competitor comparison"],
    },
    "Proposal": {
        "primary_goal": "Present value, differentiate, and secure verbal commitment",
        "next_step": "Send proposal with clear ROI narrative and a mutual action plan",
        "recommended_assets": ["Custom proposal deck", "ROI model", "Reference customers"],
    },
    "Negotiation": {
        "primary_goal": "Resolve commercial objections and get legal/procurement aligned",
        "next_step": "Identify all remaining blockers and build a concession trade list",
        "recommended_assets": ["Negotiation concession guide", "Legal pre-approval checklist"],
    },
    "Closed Won": {
        "primary_goal": "Ensure smooth handoff to CS and set up for expansion",
        "next_step": "Schedule kickoff and introduce the Customer Success team",
        "recommended_assets": ["Customer success plan", "Onboarding timeline"],
    },
    "Closed Lost": {
        "primary_goal": "Learn from the loss and protect relationship for future",
        "next_step": "Conduct a deal post-mortem and log key learnings in memory",
        "recommended_assets": ["Loss analysis template"],
    },
}


class NextBestActionAgent(BaseAgent):
    """
    Determines the next-best-action for the current deal state.
    Uses stage playbook + interaction patterns + intelligence signals.
    """

    @property
    def name(self) -> str:
        return "NextBestAction"

    def analyze(self, context: dict) -> AgentResult:
        brief = context.get("brief", {})
        interactions: List[dict] = context.get("interactions", [])
        stakeholders: List[dict] = context.get("stakeholders", [])

        deal_id = brief.get("deal_id", 0)
        deal_title = brief.get("deal_title", "")
        stage = brief.get("deal_stage", "Prospecting")
        risk_level = brief.get("risk_level", "MEDIUM")
        deal_value = brief.get("deal_value", 0)
        intel_score = brief.get("intelligence_score", 0)

        playbook = _STAGE_PLAYBOOK.get(stage, _STAGE_PLAYBOOK["Prospecting"])
        recs: List[Recommendation] = []
        opportunities: List[str] = brief.get("key_opportunities", [])
        risks: List[str] = brief.get("key_risks", [])
        warnings: List[str] = []

        # ── Primary next-best-action from stage playbook ─────────────
        recs.append(
            Recommendation(
                action=playbook["next_step"],
                rationale=(
                    f"Deal is in '{stage}' stage. The primary goal at this stage is: "
                    f"{playbook['primary_goal']}."
                ),
                priority="HIGH",
                category="process",
                effort="MEDIUM",
                expected_impact=f"Progresses deal toward '{self._next_stage(stage)}' stage.",
            )
        )

        # ── Interaction-based actions ────────────────────────────────
        last_interaction = interactions[-1] if interactions else None
        days_since_last = None

        if last_interaction:
            failed_outcomes = [i for i in interactions if i.get("outcome") == "failed"]
            if failed_outcomes:
                last_failed = failed_outcomes[-1]
                recs.append(
                    Recommendation(
                        action=f"Follow up on failed strategy: '{last_failed.get('strategy', 'previous approach')}'",
                        rationale=(
                            "Last interaction outcome was marked 'failed'. "
                            "Revisiting with a different angle prevents deal stagnation."
                        ),
                        priority="HIGH",
                        category="relationship",
                        effort="LOW",
                        expected_impact="Re-engages prospect with fresh framing.",
                    )
                )

            # Check for positive momentum
            positive = [i for i in interactions if i.get("sentiment") == "positive"]
            if positive and stage in ("Discovery", "Proposal"):
                recs.append(
                    Recommendation(
                        action="Leverage positive sentiment: ask for referral or case study participation",
                        rationale=(
                            f"{len(positive)} positive interaction(s) recorded. "
                            "High-sentiment prospects are 3x more likely to provide references."
                        ),
                        priority="MEDIUM",
                        category="opportunity",
                        effort="LOW",
                        expected_impact="Builds social proof; accelerates peer-to-peer validation.",
                    )
                )
        else:
            warnings.append("No interactions recorded — deal health cannot be determined from history.")
            recs.append(
                Recommendation(
                    action="Log the first interaction to establish deal baseline",
                    rationale=(
                        "No interactions recorded. Without interaction history, "
                        "memory-powered recommendations are limited."
                    ),
                    priority="HIGH",
                    category="process",
                    effort="LOW",
                    expected_impact="Enables memory-based pattern matching in future analyses.",
                )
            )

        # ── Stakeholder-based actions ────────────────────────────────
        if stakeholders:
            unconvinced = [s for s in stakeholders if "concern" in s and s["concern"]]
            if unconvinced:
                for s in unconvinced[:2]:
                    recs.append(
                        Recommendation(
                            action=f"Address {s['name']}'s concern: \"{s.get('concern', 'unknown concern')}\"",
                            rationale=(
                                f"{s['name']} ({s.get('role', 'stakeholder')}) has a documented concern. "
                                "Unresolved stakeholder concerns are the #1 cause of late-stage deal loss."
                            ),
                            priority="HIGH",
                            category="relationship",
                            effort="MEDIUM",
                            expected_impact="Removes blockers and accelerates stakeholder buy-in.",
                        )
                    )

        # ── Competitive counter-action ───────────────────────────────
        high_signals = [
            s for s in brief.get("competitor_signals", []) if s.get("impact") == "HIGH"
        ]
        if high_signals:
            s = high_signals[0]
            recs.append(
                Recommendation(
                    action=f"Send competitive differentiation brief to champion vs. {s['competitor']}",
                    rationale=(
                        f"{s['headline']} — proactively addressing competitor moves "
                        "positions your rep as a trusted advisor, not just a vendor."
                    ),
                    priority="MEDIUM",
                    category="competitive",
                    effort="MEDIUM",
                    expected_impact="Inoculates champion against competitor FUD before it reaches budget decision.",
                )
            )

        # ── High pressure warning ────────────────────────────────────
        if intel_score > 65:
            warnings.append(
                f"Intelligence pressure score is {intel_score}/100 — "
                "multiple external threats active. Prioritise high-priority actions immediately."
            )

        confidence = "HIGH" if len(interactions) >= 3 and len(stakeholders) >= 2 else "MEDIUM"

        return AgentResult(
            agent_name=self.name,
            deal_id=deal_id,
            summary=(
                f"Deal '{deal_title}' is in '{stage}' stage. "
                f"Recommended next action: {playbook['next_step']}. "
                f"{len(recs)} total recommended actions generated."
            ),
            situation_assessment=self._build_assessment(
                deal_title, stage, deal_value, risk_level, len(interactions), len(stakeholders), intel_score
            ),
            recommendations=sorted(recs, key=lambda r: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r.priority]),
            risks_identified=risks,
            opportunities_identified=opportunities,
            confidence=confidence,
            warnings=warnings,
        )

    def _next_stage(self, stage: str) -> str:
        stages = list(_STAGE_PLAYBOOK.keys())
        try:
            idx = stages.index(stage)
            return stages[min(idx + 1, len(stages) - 1)]
        except ValueError:
            return "next stage"

    def _build_assessment(
        self,
        title: str,
        stage: str,
        value: float,
        risk: str,
        n_interactions: int,
        n_stakeholders: int,
        intel_score: int,
    ) -> str:
        return (
            f"Deal '{title}' is currently in the '{stage}' stage, valued at ${value:,.0f}, "
            f"with {risk} risk level. "
            f"The deal has {n_interactions} logged interaction(s) and {n_stakeholders} "
            f"mapped stakeholder(s). "
            f"External intelligence score is {intel_score}/100. "
            + (
                "Deal appears well-engaged — focus on accelerating to close."
                if n_interactions >= 5
                else "Early-stage deal — focus on qualification and stakeholder mapping."
            )
        )
