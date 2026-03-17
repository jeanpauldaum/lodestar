"""
Cultural Fit Score engine for Lodestar.

Computes a composite score (0-100) representing how well a source policy's
cultural context maps to a target country's cultural dimensions. A higher
score means the policy can be transferred with less adaptation.
"""

import logging
from typing import Any

from lodestar.culture.profiles import get_profile

logger = logging.getLogger(__name__)

# Weights for each dimension's contribution to the Cultural Fit Score
DIMENSION_WEIGHTS: dict[str, float] = {
    "power_distance": 0.20,
    "individualism": 0.15,
    "uncertainty_avoidance": 0.15,
    "long_term_orientation": 0.15,
    "institutional_trust": 0.20,
    "tech_adoption_index": 0.15,
}


class CulturalScorer:
    """
    Computes Cultural Fit Scores between policy source and target countries.

    The score reflects dimensional similarity across Hofstede measures plus
    institutional trust and technology adoption readiness.
    """

    def score(
        self,
        source_country_code: str,
        target_country_code: str,
    ) -> dict[str, Any]:
        """
        Calculate the Cultural Fit Score between two countries.

        Args:
            source_country_code: ISO code of the country where policy originated.
            target_country_code: ISO code of the country receiving the policy.

        Returns:
            Dict with keys:
            - score: Float 0-100 (higher = better cultural fit)
            - grade: Letter grade A/B/C/D/F
            - dimension_scores: Dict of per-dimension similarity scores
            - adaptation_notes: List of specific adaptation recommendations
            - summary: Human-readable summary string

        Raises:
            ValueError: If either country code is not found in profiles.
        """
        source = get_profile(source_country_code)
        target = get_profile(target_country_code)
        if source is None:
            raise ValueError(
                f"No cultural profile for source country: {source_country_code}"
            )
        if target is None:
            raise ValueError(
                f"No cultural profile for target country: {target_country_code}"
            )

        logger.debug(
            "Scoring cultural fit: %s → %s",
            source.get("name", source_country_code),
            target.get("name", target_country_code),
        )

        dimension_scores: dict[str, float] = {}
        adaptation_notes: list[str] = []
        weighted_sum = 0.0

        for dimension, weight in DIMENSION_WEIGHTS.items():
            source_val = source.get(dimension)
            target_val = target.get(dimension)
            if source_val is None or target_val is None:
                continue
            # Similarity: 1 - normalized absolute difference
            diff = abs(float(source_val) - float(target_val))
            similarity = 1.0 - (diff / 100.0)
            dim_score = similarity * 100
            dimension_scores[dimension] = round(dim_score, 1)
            weighted_sum += dim_score * weight
            self._generate_adaptation_note(
                dimension, source_val, target_val, source, target, adaptation_notes
            )

        fit_score = round(weighted_sum, 1)
        grade = self._score_to_grade(fit_score)

        source_name = source.get("name", source_country_code)
        target_name = target.get("name", target_country_code)
        summary = (
            f"Cultural Fit Score: {fit_score}/100 ({grade}) — "
            f"{source_name} → {target_name}. "
            f"{'Strong cultural alignment; direct transfer feasible with minor localization.' if fit_score >= 70 else 'Moderate alignment; targeted cultural adaptation required before rollout.' if fit_score >= 50 else 'Significant cultural distance; deep institutional redesign needed.'}"
        )

        logger.info(
            "Cultural Fit Score %s→%s: %.1f (%s)",
            source_country_code,
            target_country_code,
            fit_score,
            grade,
        )
        return {
            "score": fit_score,
            "grade": grade,
            "source_country": source_name,
            "target_country": target_name,
            "dimension_scores": dimension_scores,
            "adaptation_notes": adaptation_notes,
            "summary": summary,
        }

    def _generate_adaptation_note(
        self,
        dimension: str,
        source_val: float,
        target_val: float,
        source: dict[str, Any],
        target: dict[str, Any],
        notes: list[str],
    ) -> None:
        """Generate targeted adaptation notes based on dimensional gaps."""
        diff = float(target_val) - float(source_val)
        abs_diff = abs(diff)
        target_name = target.get("name", "target")

        if abs_diff < 20:
            return  # Small gap — no note needed

        if dimension == "power_distance":
            if diff > 0:
                notes.append(
                    f"Higher power distance in {target_name}: structure rollout as top-down mandate "
                    "from senior leadership rather than bottom-up participation model."
                )
            else:
                notes.append(
                    f"Lower power distance in {target_name}: flatten decision-making hierarchy, "
                    "enable frontline input, and avoid authoritarian communication framing."
                )
        elif dimension == "individualism":
            if diff < 0:
                notes.append(
                    f"More collectivist culture in {target_name}: emphasize community benefits, "
                    "family outcomes, and group participation over individual rights narratives."
                )
            else:
                notes.append(
                    f"More individualist culture in {target_name}: stress personal choice, "
                    "opt-in mechanisms, and individual economic benefits in messaging."
                )
        elif dimension == "uncertainty_avoidance":
            if diff > 0:
                notes.append(
                    f"Higher uncertainty avoidance in {target_name}: invest heavily in pilot programs, "
                    "detailed legal frameworks, and transparent communication before scaling."
                )
            else:
                notes.append(
                    f"Lower uncertainty avoidance in {target_name}: can move faster and tolerate "
                    "ambiguity — use agile rollout with iterative feedback loops."
                )
        elif dimension == "long_term_orientation":
            if diff < 0:
                notes.append(
                    f"Shorter-term orientation in {target_name}: structure benefits to show "
                    "quick wins within 12-24 months while building toward long-term goals."
                )
            else:
                notes.append(
                    f"Longer-term orientation in {target_name}: can invest in multi-decade "
                    "infrastructure plans; frame success in generational terms."
                )
        elif dimension == "institutional_trust":
            if diff < 0:
                notes.append(
                    f"Lower institutional trust in {target_name}: build credibility through "
                    "independent oversight, radical transparency, and community-controlled governance."
                )
        elif dimension == "tech_adoption_index":
            if diff < 0:
                notes.append(
                    f"Lower tech adoption in {target_name}: design for feature phones and "
                    "offline access; invest in digital literacy programs alongside technology deployment."
                )

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert a numeric fit score to a letter grade."""
        if score >= 80:
            return "A"
        if score >= 65:
            return "B"
        if score >= 50:
            return "C"
        if score >= 35:
            return "D"
        return "F"
