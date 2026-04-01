from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class JobProfile:
    title: str
    raw_text: str
    required_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    certificates: list[str] = field(default_factory=list)
    education_requirement: str | None = None
    experience_requirement: str | None = None
    city: str | None = None
    salary_range: str | None = None
    growth_path: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_pretty_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class StudentProfile:
    name: str
    raw_text: str
    school_name: str | None = None
    major: str | None = None
    skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    certificates: list[str] = field(default_factory=list)
    education_level: str | None = None
    target_roles: list[str] = field(default_factory=list)
    target_industries: list[str] = field(default_factory=list)
    city_preference: str | None = None
    projects: list[str] = field(default_factory=list)
    internships: list[str] = field(default_factory=list)
    awards: list[str] = field(default_factory=list)
    profile_completeness: int = 0
    competitiveness_score: int = 0
    missing_sections: list[str] = field(default_factory=list)
    agent_answers: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_pretty_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class MatchBreakdown:
    basic_requirements: int
    professional_skills: int
    professional_literacy: int
    growth_potential: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MatchResult:
    score: int
    breakdown: MatchBreakdown
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    shared_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    explanation: str = ""
    confidence_label: str = "中"

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "breakdown": self.breakdown.to_dict(),
            "strengths": self.strengths,
            "gaps": self.gaps,
            "suggestions": self.suggestions,
            "shared_skills": self.shared_skills,
            "missing_skills": self.missing_skills,
            "explanation": self.explanation,
            "confidence_label": self.confidence_label,
        }

    def to_pretty_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class CareerPlan:
    primary_role: str
    backup_roles: list[str] = field(default_factory=list)
    primary_score: int = 0
    overview: str = ""
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    primary_growth_path: list[str] = field(default_factory=list)
    transition_paths: list[str] = field(default_factory=list)
    action_plan_30_days: list[str] = field(default_factory=list)
    action_plan_90_days: list[str] = field(default_factory=list)
    action_plan_180_days: list[str] = field(default_factory=list)
    recommended_projects: list[str] = field(default_factory=list)
    learning_sprints: list[dict[str, str]] = field(default_factory=list)
    next_review_targets: list[str] = field(default_factory=list)
    growth_comparison: dict[str, Any] = field(default_factory=dict)
    stakeholder_views: list[dict[str, Any]] = field(default_factory=list)
    evaluation_metrics: list[dict[str, Any]] = field(default_factory=list)
    competency_dimensions: list[dict[str, Any]] = field(default_factory=list)
    service_loop: list[dict[str, str]] = field(default_factory=list)
    assessment_tasks: list[str] = field(default_factory=list)
    self_assessment: dict[str, Any] = field(default_factory=dict)
    resource_map: list[dict[str, Any]] = field(default_factory=list)
    agent_questions: list[dict[str, str]] = field(default_factory=list)
    innovation_highlights: list[dict[str, str]] = field(default_factory=list)
    technical_keywords: list[str] = field(default_factory=list)
    technical_modules: list[dict[str, str]] = field(default_factory=list)
    evidence_bundle: dict[str, Any] = field(default_factory=dict)
    service_scenarios: list[str] = field(default_factory=list)
    product_signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_pretty_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
