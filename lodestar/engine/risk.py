"""
Risk analysis module for Lodestar.

Evaluates implementation risks for policy adaptations based on
cultural fit, institutional capacity, and historical failure patterns.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Analyzes implementation risks for policy transfer scenarios.

    Combines cultural fit scores, governance indicators, and domain-specific
    risk patterns to produce structured risk assessments.
    """

    DOMAIN_RISK_FACTORS: dict[str, list[str]] = {
        "housing": [
            "Land tenure complexity and existing property rights disputes",
            "Construction capacity and supply chain constraints",
            "Financing and mortgage market maturity",
            "Political economy of displacement and resettlement",
        ],
        "governance": [
            "Civil service capacity and resistance to digital transformation",
            "Infrastructure gaps in connectivity and hardware access",
            "Data privacy legislation misalignment",
            "Trust deficit between citizens and government institutions",
        ],
        "urban_mobility": [
            "Existing informal transport operator resistance",
            "Right-of-way acquisition and urban density constraints",
            "Maintenance capacity and spare parts supply chain",
            "Fare affordability for low-income populations",
        ],
        "education": [
            "Teacher training pipeline and union dynamics",
            "Curriculum localization complexity",
            "Family economic pressure on school attendance",
            "Assessment system overhaul resistance",
        ],
        "infrastructure": [
            "Engineering talent scarcity for complex systems",
            "Multi-decade funding commitment uncertainty",
            "Climate and geological context mismatches",
            "Regulatory and safety standard gaps",
        ],
        "urban_planning": [
            "Long-term political continuity requirements",
            "Real estate market distortion risks",
            "Community displacement and gentrification",
            "Siloed municipal department coordination failures",
        ],
    }

    MITIGATION_STRATEGIES: dict[str, list[str]] = {
        "capacity": [
            "Establish a dedicated implementation unit with protected budget",
            "Commission capacity gap assessment before launch",
            "Partner with international technical assistance programs",
        ],
        "political": [
            "Build multi-party legislative consensus before launch",
            "Create independent oversight body to reduce political interference",
            "Pilot in low-risk district before city-wide rollout",
        ],
        "financial": [
            "Establish dedicated infrastructure fund with 10-year horizon",
            "Structure public-private partnerships with performance guarantees",
            "Pursue multilateral development bank co-financing",
        ],
        "cultural": [
            "Conduct deep community consultation with local leaders",
            "Adapt communication strategy for local media channels",
            "Hire local implementation managers, not expat-only teams",
        ],
    }

    def analyze(
        self,
        matched_policies: list[dict[str, Any]],
        target_city: str,
        target_country: str,
        domain: str,
        cultural_fit_score: float = 50.0,
        governance_score: float | None = None,
    ) -> dict[str, Any]:
        """
        Analyze implementation risks for a policy adaptation scenario.

        Args:
            matched_policies: List of matched policy dicts from PolicyMatcher.
            target_city: Name of the target city.
            target_country: Name of the target country.
            domain: Policy domain being analyzed.
            cultural_fit_score: Cultural Fit Score (0-100, higher = better fit).
            governance_score: Target country governance percentile (0-100). Optional.

        Returns:
            Dict with keys:
            - risk_factors: List of specific risk strings
            - mitigation_strategies: List of mitigation strings
            - overall_risk_score: Float 0-100 (higher = riskier)
            - risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
            - key_warnings: List of critical warning strings
        """
        logger.info(
            "Analyzing risks for %s, %s (domain: %s)",
            target_city,
            target_country,
            domain,
        )

        domain_risks = self.DOMAIN_RISK_FACTORS.get(
            domain, self.DOMAIN_RISK_FACTORS["infrastructure"]
        )
        risk_factors = list(domain_risks)

        # Cultural gap risks
        cultural_gap = 100 - cultural_fit_score
        if cultural_gap > 60:
            risk_factors.append(
                f"High cultural distance (fit score: {cultural_fit_score:.0f}/100) — "
                "significant institutional trust and adoption pattern mismatches likely"
            )
        elif cultural_gap > 35:
            risk_factors.append(
                f"Moderate cultural distance (fit score: {cultural_fit_score:.0f}/100) — "
                "targeted adaptation of communication and rollout sequencing required"
            )

        # Governance risks
        key_warnings = []
        if governance_score is not None and governance_score < 40:
            risk_factors.append(
                f"Low governance effectiveness score ({governance_score:.0f}/100) — "
                "institutional capacity gaps may undermine implementation fidelity"
            )
            key_warnings.append(
                "CRITICAL: Target country governance capacity is below threshold for "
                "unassisted implementation. External technical assistance strongly recommended."
            )

        # Policy transfer distance from matched cases
        avg_similarity = (
            sum(p.get("similarity_score", 0.5) for p in matched_policies)
            / len(matched_policies)
            if matched_policies
            else 0.5
        )
        if avg_similarity < 0.4:
            risk_factors.append(
                "Low semantic similarity to known success cases — "
                "this context may be novel and untested territory"
            )

        # Collect mitigation strategies
        mitigations = []
        for category in ["capacity", "political", "financial", "cultural"]:
            mitigations.extend(self.MITIGATION_STRATEGIES[category][:1])

        # Calculate overall risk score (0-100)
        base_score = 30.0
        cultural_penalty = cultural_gap * 0.25
        governance_penalty = (100 - (governance_score or 50)) * 0.15
        similarity_penalty = (1.0 - avg_similarity) * 20
        overall_score = min(
            100.0,
            base_score + cultural_penalty + governance_penalty + similarity_penalty,
        )

        risk_level = (
            "LOW"
            if overall_score < 35
            else "MEDIUM"
            if overall_score < 55
            else "HIGH"
            if overall_score < 75
            else "CRITICAL"
        )

        logger.info(
            "Risk assessment complete: score=%.1f (%s)", overall_score, risk_level
        )
        return {
            "risk_factors": risk_factors,
            "mitigation_strategies": mitigations,
            "overall_risk_score": round(overall_score, 1),
            "risk_level": risk_level,
            "key_warnings": key_warnings,
        }
