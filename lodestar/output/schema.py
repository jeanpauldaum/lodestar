"""
Pydantic data models for Lodestar output structures.

Defines the canonical data shapes for all Lodestar analysis outputs,
from individual policy records through complete implementation briefs.
"""

from typing import Any

from pydantic import BaseModel, Field


class Policy(BaseModel):
    """A globally successful policy case in the Lodestar knowledge base."""

    id: str = Field(description="Unique identifier, e.g. 'singapore_hdb'")
    name: str = Field(description="Full policy name")
    country: str = Field(description="Country where implemented")
    city: str = Field(description="Primary city of implementation")
    domain: str = Field(
        description="Policy domain: housing, governance, urban_mobility, etc."
    )
    year_start: int = Field(
        description="Year the policy was launched or significantly reformed"
    )
    description: str = Field(description="2-3 sentence overview of the policy")
    key_outcomes: list[str] = Field(description="Measurable outcomes achieved")
    prerequisites: list[str] = Field(
        description="Conditions required for successful implementation"
    )
    cultural_context: dict[str, Any] = Field(
        description="Cultural dimension data for source country"
    )
    success_factors: list[str] = Field(description="Key factors that drove success")
    failure_risks: list[str] = Field(description="Known failure modes and risks")
    data_sources: list[str] = Field(description="Data sources and references")


class CulturalProfile(BaseModel):
    """Cultural dimension profile for a country."""

    country_code: str = Field(description="ISO 3166-1 alpha-2 country code")
    country_name: str = Field(description="Country name")
    power_distance: int = Field(description="Hofstede PDI score 0-100")
    individualism: int = Field(description="Hofstede IDV score 0-100")
    uncertainty_avoidance: int = Field(description="Hofstede UAI score 0-100")
    long_term_orientation: int = Field(description="Hofstede LTO score 0-100")
    indulgence: int = Field(description="Hofstede IND score 0-100")
    institutional_trust: int = Field(
        description="Composite institutional trust score 0-100"
    )
    tech_adoption_index: int = Field(description="Technology adoption readiness 0-100")


class MatchResult(BaseModel):
    """A single matched policy from semantic search."""

    id: str = Field(description="Policy ID")
    name: str = Field(description="Policy name")
    country: str = Field(description="Source country")
    city: str = Field(description="Source city")
    domain: str = Field(description="Policy domain")
    year_start: str = Field(description="Launch year")
    similarity_score: float = Field(description="Semantic similarity score 0-1")


class PredictedOutcome(BaseModel):
    """A single predicted outcome from impact simulation."""

    outcome: str = Field(description="Description of the measurable outcome")
    value_range: str = Field(description="Predicted range, e.g. '25-40% improvement'")
    confidence: float = Field(description="Confidence level 0-1")
    timeline: str = Field(description="Expected timeline, e.g. '3-5 years'")


class ResourceRequirements(BaseModel):
    """Resource estimates for policy implementation."""

    estimated_budget_usd: str = Field(
        description="Budget range, e.g. '$500M-$1.2B over 10 years'"
    )
    key_staffing: str = Field(description="Staffing requirements")
    critical_partners: list[str] = Field(description="Key partner organizations needed")


class SimulationResult(BaseModel):
    """Output of the ImpactSimulator."""

    predicted_outcomes: list[PredictedOutcome] = Field(
        description="Predicted measurable outcomes"
    )
    confidence_score: float = Field(description="Overall simulation confidence 0-1")
    timeline: str = Field(description="Overall implementation timeline")
    resource_requirements: ResourceRequirements = Field(
        description="Resource estimates"
    )
    key_risks: list[str] = Field(description="Top implementation risks")
    bear_case: str = Field(description="Pessimistic scenario description")
    bull_case: str = Field(description="Optimistic scenario description")
    recommended_pilot: str = Field(description="Recommended pilot project")


class RiskAssessment(BaseModel):
    """Output of the RiskAnalyzer."""

    risk_factors: list[str] = Field(description="Specific implementation risk factors")
    mitigation_strategies: list[str] = Field(
        description="Risk mitigation recommendations"
    )
    overall_risk_score: float = Field(
        description="Overall risk score 0-100 (higher = riskier)"
    )
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, HIGH, or CRITICAL")
    key_warnings: list[str] = Field(
        description="Critical warnings requiring immediate attention"
    )


class CulturalFitScore(BaseModel):
    """Output of the CulturalScorer."""

    score: float = Field(description="Cultural Fit Score 0-100 (higher = better fit)")
    grade: str = Field(description="Letter grade A/B/C/D/F")
    source_country: str = Field(description="Source country name")
    target_country: str = Field(description="Target country name")
    dimension_scores: dict[str, float] = Field(
        description="Per-dimension similarity scores"
    )
    adaptation_notes: list[str] = Field(
        description="Specific adaptation recommendations"
    )
    summary: str = Field(description="Human-readable summary")


class AdaptedRecommendation(BaseModel):
    """Output of the CulturalAdaptor."""

    original_policy: str = Field(description="Original policy name and country")
    target_country: str = Field(description="Target country for adaptation")
    cultural_fit_score: float = Field(description="Cultural Fit Score")
    adaptation_level: str = Field(
        description="MINIMAL, MODERATE, SIGNIFICANT, or FUNDAMENTAL"
    )
    adapted_elements: list[str] = Field(description="Specific adaptation modifications")
    implementation_approach: str = Field(
        description="Recommended implementation approach"
    )
    communication_strategy: str = Field(
        description="Communication strategy for target culture"
    )
    governance_structure: str = Field(description="Recommended governance model")
    quick_wins: list[str] = Field(description="Early wins to build political momentum")
    avoid_list: list[str] = Field(
        description="Things to avoid that worked in source country"
    )


class LodestarBrief(BaseModel):
    """
    The complete Lodestar analysis output for a city+domain query.

    This is the canonical output model — everything else builds toward this.
    """

    query_city: str = Field(description="Target city for analysis")
    query_country: str = Field(description="Target country")
    query_domain: str = Field(description="Policy domain analyzed")
    matched_policies: list[MatchResult] = Field(
        description="Top 3 semantically matched policies"
    )
    cultural_fit_scores: list[CulturalFitScore] = Field(
        description="Cultural fit for each matched policy"
    )
    simulation: SimulationResult = Field(description="Impact simulation results")
    risk_assessment: RiskAssessment = Field(
        description="Implementation risk assessment"
    )
    adapted_recommendations: list[AdaptedRecommendation] = Field(
        description="Culturally-adapted recommendations"
    )
    executive_summary: str = Field(description="3-paragraph executive summary")
    generated_at: str = Field(description="ISO 8601 timestamp of generation")
