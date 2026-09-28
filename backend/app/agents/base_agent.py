"""
Base Agent — Phase 4

Defines the abstract interface all Precedent agents must implement.
All agents receive a DealIntelligenceBrief and return a structured
AgentResult with typed recommendations and explanations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Recommendation:
    action: str                   # Short imperative statement e.g. "Schedule exec sponsor call"
    rationale: str                # Why this action is recommended
    priority: str                 # "HIGH" | "MEDIUM" | "LOW"
    category: str                 # "relationship" | "competitive" | "risk" | "process" | "opportunity"
    effort: str                   # "LOW" | "MEDIUM" | "HIGH"
    expected_impact: str          # Free-text expected outcome


@dataclass
class AgentResult:
    agent_name: str
    deal_id: int
    summary: str                          # 1-2 sentence executive summary
    situation_assessment: str             # Detailed deal situation analysis
    recommendations: List[Recommendation]
    risks_identified: List[str]
    opportunities_identified: List[str]
    confidence: str                       # "HIGH" | "MEDIUM" | "LOW"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "deal_id": self.deal_id,
            "summary": self.summary,
            "situation_assessment": self.situation_assessment,
            "recommendations": [
                {
                    "action": r.action,
                    "rationale": r.rationale,
                    "priority": r.priority,
                    "category": r.category,
                    "effort": r.effort,
                    "expected_impact": r.expected_impact,
                }
                for r in self.recommendations
            ],
            "risks_identified": self.risks_identified,
            "opportunities_identified": self.opportunities_identified,
            "confidence": self.confidence,
            "warnings": self.warnings,
        }


class BaseAgent(ABC):
    """Abstract base for all Precedent reasoning agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier / display name of this agent."""

    @abstractmethod
    def analyze(self, context: dict) -> AgentResult:
        """
        Perform agentic analysis on the provided context dict.

        The context dict must contain at minimum:
          - "brief": DealIntelligenceBrief.to_dict()
          - "interactions": list of interaction dicts from Phase 1
          - "stakeholders": list of stakeholder dicts from Phase 1
        """
