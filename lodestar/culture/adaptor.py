"""
Cultural adaptation logic for Lodestar recommendations.

Takes a base policy recommendation and transforms it with specific,
actionable modifications tailored to the target country's cultural context.
"""

import logging
from typing import Any

from lodestar.culture.profiles import get_profile

logger = logging.getLogger(__name__)


class CulturalAdaptor:
    """
    Generates culturally-adapted policy recommendations.

    Uses the Cultural Fit Score and dimensional profiles to produce specific
    implementation modifications that increase success probability in the
    target cultural context.
    """

    def adapt(
        self,
        policy: dict[str, Any],
        cultural_fit_result: dict[str, Any],
        target_country_code: str,
    ) -> dict[str, Any]:
        """
        Generate a culturally-adapted recommendation for a policy.

        Args:
            policy: Policy dict from the knowledge base.
            cultural_fit_result: Output from CulturalScorer.score().
            target_country_code: ISO code for the target country.

        Returns:
            Dict with keys:
            - original_policy: Policy name and country
            - target_country: Target country name
            - cultural_fit_score: Float score
            - adaptation_level: "MINIMAL" | "MODERATE" | "SIGNIFICANT" | "FUNDAMENTAL"
            - adapted_elements: List of specific adaptations to make
            - implementation_approach: Recommended rollout approach string
            - communication_strategy: How to communicate the policy
            - governance_structure: Recommended governance model
            - quick_wins: List of early wins to build momentum
            - avoid_list: List of things that worked in source but will fail in target
        """
        target_profile = get_profile(target_country_code)
        target_name = (
            target_profile.get("name", target_country_code)
            if target_profile
            else target_country_code
        )
        fit_score = cultural_fit_result.get("score", 50.0)
        adaptation_notes = cultural_fit_result.get("adaptation_notes", [])

        # Determine adaptation level
        if fit_score >= 75:
            adaptation_level = "MINIMAL"
        elif fit_score >= 55:
            adaptation_level = "MODERATE"
        elif fit_score >= 35:
            adaptation_level = "SIGNIFICANT"
        else:
            adaptation_level = "FUNDAMENTAL"

        adapted_elements = list(adaptation_notes)
        avoid_list: list[str] = []
        quick_wins: list[str] = []

        if target_profile:
            trust_level = target_profile.get("institutional_trust", 50)
            power_dist = target_profile.get("power_distance", 50)
            tech_adoption = target_profile.get("tech_adoption_index", 50)

            if trust_level < 40:
                adapted_elements.append(
                    "Establish independent accountability board with civil society representation "
                    "before launch — low trust environments require pre-built credibility infrastructure."
                )
                avoid_list.append(
                    "Avoid single-agency control structures that worked in high-trust source countries — "
                    "they will read as corrupt monopoly in this context."
                )
                quick_wins.append(
                    "Publish all budget data, contracts, and progress reports in real-time from Day 1 "
                    "to establish credibility baseline."
                )

            if power_dist > 70:
                adapted_elements.append(
                    "Secure visible head-of-state or prime minister endorsement for launch — "
                    "top-down legitimacy signals are decisive in high power-distance cultures."
                )
                quick_wins.append(
                    "Host high-visibility launch event with senior leadership to signal priority status."
                )

            if tech_adoption < 55:
                adapted_elements.append(
                    "Build USSD/SMS fallback for all digital touchpoints — "
                    "assume smartphone penetration is 40-60% of target audience at launch."
                )
                avoid_list.append(
                    "Do not replicate the app-first user experience from the source country — "
                    "digital exclusion will undermine adoption metrics."
                )

        # Implementation approach based on fit score
        if fit_score >= 70:
            implementation_approach = (
                "Direct adaptation: deploy source model with localization adjustments. "
                "3-month scoping → 6-month pilot district → 18-month city rollout."
            )
        elif fit_score >= 50:
            implementation_approach = (
                "Modified transfer: restructure governance and communication layers while "
                "preserving core operational model. 6-month co-design → 12-month pilot → 3-year rollout."
            )
        else:
            implementation_approach = (
                "Hybrid model: extract only the structural principles from source model and "
                "co-design implementation locally. 12-month design phase with community consultation "
                "→ 18-month limited pilot → phased expansion based on evidence."
            )

        communication_strategy = self._get_communication_strategy(target_profile)
        governance_structure = self._get_governance_structure(target_profile)

        logger.info(
            "Adaptation generated for %s → %s: %s (score: %.1f)",
            policy.get("name", "policy"),
            target_name,
            adaptation_level,
            fit_score,
        )

        return {
            "original_policy": f"{policy.get('name', 'Policy')} ({policy.get('country', 'Unknown')})",
            "target_country": target_name,
            "cultural_fit_score": fit_score,
            "adaptation_level": adaptation_level,
            "adapted_elements": adapted_elements,
            "implementation_approach": implementation_approach,
            "communication_strategy": communication_strategy,
            "governance_structure": governance_structure,
            "quick_wins": quick_wins,
            "avoid_list": avoid_list,
        }

    def _get_communication_strategy(self, profile: dict[str, Any] | None) -> str:
        """Generate communication strategy based on cultural profile."""
        if profile is None:
            return "Use multi-channel communication with local language adaptation."
        trust = profile.get("institutional_trust", 50)
        individualism = profile.get("individualism", 50)
        if trust > 70 and individualism > 60:
            return (
                "Data-forward, individual-benefit messaging through digital channels. "
                "Trust is high — lead with evidence and personal ROI."
            )
        if trust < 40:
            return (
                "Community leader and civil society-mediated messaging. "
                "Government as facilitator, not protagonist. Lead with community voice, not official statements."
            )
        return (
            "Multi-stakeholder communication: official channels supplemented by community networks. "
            "Emphasize collective benefit and social proof from early adopter communities."
        )

    def _get_governance_structure(self, profile: dict[str, Any] | None) -> str:
        """Recommend governance structure based on cultural profile."""
        if profile is None:
            return "Establish dedicated implementation unit with clear accountability."
        trust = profile.get("institutional_trust", 50)
        power_dist = profile.get("power_distance", 50)
        if trust > 70:
            return (
                "Lean implementation team within existing ministry structure. "
                "High trust reduces need for independent oversight layers."
            )
        if power_dist > 70 and trust < 45:
            return (
                "Dual-track governance: strong executive sponsorship (for legitimacy) + "
                "independent implementation unit (for accountability). "
                "International technical assistance recommended for first 3 years."
            )
        return (
            "Semi-autonomous implementation agency with parliamentary oversight. "
            "Civil society observers on governance board. Regular public progress hearings."
        )
