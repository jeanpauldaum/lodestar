"""
Tests for Lodestar output modules: schema validation and brief generation.
"""

from datetime import datetime, timezone

from lodestar.output.brief import generate_markdown_brief
from lodestar.output.schema import (
    MatchResult,
    Policy,
    RiskAssessment,
)

SAMPLE_POLICY = {
    "id": "singapore_hdb",
    "name": "Singapore Public Housing (HDB)",
    "country": "Singapore",
    "city": "Singapore",
    "domain": "housing",
    "year_start": 1960,
    "description": "The Housing Development Board built 80% of Singapore housing stock.",
    "key_outcomes": ["80% home ownership", "Mixed-income integration"],
    "prerequisites": ["Strong state capacity", "Land availability"],
    "cultural_context": {"power_distance": 74, "institutional_trust": 88},
    "success_factors": ["Political will", "Long-term planning"],
    "failure_risks": ["Land scarcity", "Affordability drift"],
    "data_sources": ["World Bank", "HDB Annual Report"],
}


class TestPolicySchema:
    """Tests for the Policy Pydantic model."""

    def test_valid_policy_parses(self) -> None:
        """A valid policy dict should parse without errors."""
        policy = Policy(**SAMPLE_POLICY)
        assert policy.id == "singapore_hdb"
        assert policy.domain == "housing"

    def test_policy_year_is_int(self) -> None:
        """year_start should be stored as an integer."""
        policy = Policy(**SAMPLE_POLICY)
        assert isinstance(policy.year_start, int)

    def test_policy_key_outcomes_is_list(self) -> None:
        """key_outcomes should be a list."""
        policy = Policy(**SAMPLE_POLICY)
        assert isinstance(policy.key_outcomes, list)


class TestMatchResult:
    """Tests for MatchResult schema."""

    def test_match_result_parses(self) -> None:
        """MatchResult should parse a valid dict."""
        data = {
            "id": "singapore_hdb",
            "name": "Singapore HDB",
            "country": "Singapore",
            "city": "Singapore",
            "domain": "housing",
            "year_start": "1960",
            "similarity_score": 0.91,
        }
        result = MatchResult(**data)
        assert result.similarity_score == 0.91

    def test_similarity_score_float(self) -> None:
        """similarity_score should be a float."""
        data = {
            "id": "x",
            "name": "X",
            "country": "X",
            "city": "X",
            "domain": "housing",
            "year_start": "2000",
            "similarity_score": 0.75,
        }
        result = MatchResult(**data)
        assert isinstance(result.similarity_score, float)


class TestRiskAssessment:
    """Tests for RiskAssessment schema."""

    def test_risk_assessment_parses(self) -> None:
        """RiskAssessment should parse valid data."""
        data = {
            "risk_factors": ["Land costs", "Political resistance"],
            "mitigation_strategies": ["Pilot first", "Engage community"],
            "overall_risk_score": 62.5,
            "risk_level": "HIGH",
            "key_warnings": [],
        }
        ra = RiskAssessment(**data)
        assert ra.risk_level == "HIGH"
        assert ra.overall_risk_score == 62.5


class TestBriefGeneration:
    """Tests for the Markdown brief generator."""

    def _make_brief_data(self) -> dict:
        """Create a minimal but valid brief data dict."""
        return {
            "query_city": "Lagos",
            "query_country": "Nigeria",
            "query_domain": "housing",
            "matched_policies": [
                {
                    "id": "singapore_hdb",
                    "name": "Singapore HDB",
                    "country": "Singapore",
                    "city": "Singapore",
                    "domain": "housing",
                    "year_start": "1960",
                    "similarity_score": 0.91,
                },
            ],
            "cultural_fit_scores": [
                {
                    "score": 42.0,
                    "grade": "D",
                    "source_country": "Singapore",
                    "target_country": "Nigeria",
                    "dimension_scores": {"institutional_trust": 40.0},
                    "adaptation_notes": [
                        "High institutional trust gap requires accountability structures"
                    ],
                    "summary": "Significant cultural distance.",
                },
            ],
            "simulation": {
                "predicted_outcomes": [
                    {
                        "outcome": "Housing affordability",
                        "value_range": "20-35%",
                        "confidence": 0.65,
                        "timeline": "5-8 years",
                    }
                ],
                "confidence_score": 0.65,
                "timeline": "2 years pilot + 10 year rollout",
                "resource_requirements": {
                    "estimated_budget_usd": "$2B-$5B",
                    "key_staffing": "500 FTE",
                    "critical_partners": ["World Bank", "AfDB"],
                },
                "key_risks": ["Land acquisition"],
                "bear_case": "Political instability derails program",
                "bull_case": "500,000 units built by 2035",
                "recommended_pilot": "Pilot in Yaba district",
            },
            "risk_assessment": {
                "risk_factors": ["Institutional capacity gaps"],
                "mitigation_strategies": ["External technical assistance"],
                "overall_risk_score": 68.0,
                "risk_level": "HIGH",
                "key_warnings": [],
            },
            "adapted_recommendations": [],
            "executive_summary": "This is the executive summary.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def test_generates_non_empty_markdown(self) -> None:
        """Brief should generate non-empty Markdown."""
        brief_data = self._make_brief_data()
        result = generate_markdown_brief(brief_data)
        assert len(result) > 500

    def test_markdown_contains_city_name(self) -> None:
        """Generated brief should include the target city name."""
        brief_data = self._make_brief_data()
        result = generate_markdown_brief(brief_data)
        assert "Lagos" in result

    def test_markdown_contains_policy_name(self) -> None:
        """Generated brief should include matched policy names."""
        brief_data = self._make_brief_data()
        result = generate_markdown_brief(brief_data)
        assert "Singapore HDB" in result

    def test_markdown_contains_risk_level(self) -> None:
        """Generated brief should include risk level."""
        brief_data = self._make_brief_data()
        result = generate_markdown_brief(brief_data)
        assert "HIGH" in result

    def test_markdown_starts_with_header(self) -> None:
        """Generated brief should start with a Markdown h1 header."""
        brief_data = self._make_brief_data()
        result = generate_markdown_brief(brief_data)
        assert result.startswith("# Lodestar Analysis:")
