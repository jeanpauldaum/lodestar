"""
Cultural dimension profiles for Lodestar.

Contains Hofstede cultural dimension scores and supplementary data for 20+
countries, used to compute Cultural Fit Scores for policy transfer analysis.

Hofstede dimensions:
- power_distance (PDI): Acceptance of unequal power distribution (0-100)
- individualism (IDV): Individual vs. collective orientation (0-100)
- uncertainty_avoidance (UAI): Tolerance for ambiguity (0-100)
- long_term_orientation (LTO): Future vs. present/past focus (0-100)
- indulgence (IND): Gratification of desires (0-100)
- masculinity (MAS): Achievement vs. caring orientation (0-100)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Hofstede dimension scores by country (ISO codes as keys)
# Sources: Hofstede Insights (hofstede-insights.com), GLOBE Study
CULTURAL_PROFILES: dict[str, dict[str, Any]] = {
    "US": {
        "name": "United States",
        "power_distance": 40,
        "individualism": 91,
        "uncertainty_avoidance": 46,
        "long_term_orientation": 26,
        "indulgence": 68,
        "masculinity": 62,
        "institutional_trust": 55,
        "tech_adoption_index": 82,
        "regulatory_quality": 90,
        "notes": "High individualism and low power distance; pragmatic, short-term oriented; high tech adoption",
    },
    "UK": {
        "name": "United Kingdom",
        "power_distance": 35,
        "individualism": 89,
        "uncertainty_avoidance": 35,
        "long_term_orientation": 51,
        "indulgence": 69,
        "masculinity": 66,
        "institutional_trust": 60,
        "tech_adoption_index": 80,
        "regulatory_quality": 92,
        "notes": "Very low power distance; highly individualistic; pragmatic and open to change",
    },
    "DE": {
        "name": "Germany",
        "power_distance": 35,
        "individualism": 67,
        "uncertainty_avoidance": 65,
        "long_term_orientation": 83,
        "indulgence": 40,
        "masculinity": 66,
        "institutional_trust": 72,
        "tech_adoption_index": 75,
        "regulatory_quality": 93,
        "notes": "High uncertainty avoidance; very long-term oriented; strong institutions; methodical implementation culture",
    },
    "FR": {
        "name": "France",
        "power_distance": 68,
        "individualism": 71,
        "uncertainty_avoidance": 86,
        "long_term_orientation": 63,
        "indulgence": 48,
        "masculinity": 43,
        "institutional_trust": 52,
        "tech_adoption_index": 72,
        "regulatory_quality": 86,
        "notes": "High power distance and uncertainty avoidance; centralized state tradition; strong administrative culture",
    },
    "IT": {
        "name": "Italy",
        "power_distance": 50,
        "individualism": 76,
        "uncertainty_avoidance": 75,
        "long_term_orientation": 61,
        "indulgence": 30,
        "masculinity": 70,
        "institutional_trust": 40,
        "tech_adoption_index": 65,
        "regulatory_quality": 74,
        "notes": "Moderate power distance; high uncertainty avoidance; regional variation strong; lower institutional trust",
    },
    "SE": {
        "name": "Sweden",
        "power_distance": 31,
        "individualism": 71,
        "uncertainty_avoidance": 29,
        "long_term_orientation": 53,
        "indulgence": 78,
        "masculinity": 5,
        "institutional_trust": 85,
        "tech_adoption_index": 88,
        "regulatory_quality": 96,
        "notes": "Extremely low power distance and masculinity; very high trust; consensus-driven; global leader in digital governance",
    },
    "DK": {
        "name": "Denmark",
        "power_distance": 18,
        "individualism": 74,
        "uncertainty_avoidance": 23,
        "long_term_orientation": 35,
        "indulgence": 70,
        "masculinity": 16,
        "institutional_trust": 87,
        "tech_adoption_index": 88,
        "regulatory_quality": 97,
        "notes": "Lowest power distance globally; extremely high institutional trust; pioneering in urban sustainability",
    },
    "FI": {
        "name": "Finland",
        "power_distance": 33,
        "individualism": 63,
        "uncertainty_avoidance": 59,
        "long_term_orientation": 38,
        "indulgence": 57,
        "masculinity": 26,
        "institutional_trust": 83,
        "tech_adoption_index": 85,
        "regulatory_quality": 96,
        "notes": "Very low power distance; high institutional trust; long history of collaborative governance and education reform",
    },
    "NL": {
        "name": "Netherlands",
        "power_distance": 38,
        "individualism": 80,
        "uncertainty_avoidance": 53,
        "long_term_orientation": 67,
        "indulgence": 68,
        "masculinity": 14,
        "institutional_trust": 80,
        "tech_adoption_index": 87,
        "regulatory_quality": 96,
        "notes": "Very low power distance; highly individualistic but consensus-driven (polder model); global infrastructure leader",
    },
    "JP": {
        "name": "Japan",
        "power_distance": 54,
        "individualism": 46,
        "uncertainty_avoidance": 92,
        "long_term_orientation": 88,
        "indulgence": 42,
        "masculinity": 95,
        "institutional_trust": 75,
        "tech_adoption_index": 80,
        "regulatory_quality": 88,
        "notes": "Extremely high uncertainty avoidance and long-term orientation; group harmony valued; precision in infrastructure",
    },
    "KR": {
        "name": "South Korea",
        "power_distance": 60,
        "individualism": 18,
        "uncertainty_avoidance": 85,
        "long_term_orientation": 100,
        "indulgence": 29,
        "masculinity": 39,
        "institutional_trust": 60,
        "tech_adoption_index": 92,
        "regulatory_quality": 83,
        "notes": "Extremely long-term oriented; highly collective; very high tech adoption; strong state-led development tradition",
    },
    "CN": {
        "name": "China",
        "power_distance": 80,
        "individualism": 20,
        "uncertainty_avoidance": 30,
        "long_term_orientation": 87,
        "indulgence": 24,
        "masculinity": 66,
        "institutional_trust": 65,
        "tech_adoption_index": 85,
        "regulatory_quality": 60,
        "notes": "Very high power distance; highly collective; long-term oriented; state capacity very high; rapid implementation ability",
    },
    "SG": {
        "name": "Singapore",
        "power_distance": 74,
        "individualism": 20,
        "uncertainty_avoidance": 8,
        "long_term_orientation": 72,
        "indulgence": 46,
        "masculinity": 48,
        "institutional_trust": 88,
        "tech_adoption_index": 91,
        "regulatory_quality": 97,
        "notes": "Very high institutional trust and governance quality; pragmatic; long-term planning; meritocratic; multiethnic management expertise",
    },
    "EE": {
        "name": "Estonia",
        "power_distance": 40,
        "individualism": 60,
        "uncertainty_avoidance": 60,
        "long_term_orientation": 82,
        "indulgence": 16,
        "masculinity": 30,
        "institutional_trust": 78,
        "tech_adoption_index": 90,
        "regulatory_quality": 90,
        "notes": "High tech adoption; strong e-governance culture; Nordic-influenced trust levels; small population aids rapid rollout",
    },
    "BR": {
        "name": "Brazil",
        "power_distance": 69,
        "individualism": 38,
        "uncertainty_avoidance": 76,
        "long_term_orientation": 44,
        "indulgence": 59,
        "masculinity": 49,
        "institutional_trust": 35,
        "tech_adoption_index": 70,
        "regulatory_quality": 52,
        "notes": "High power distance and uncertainty avoidance; lower institutional trust; strong informal economy; mobile-first digital habits",
    },
    "CO": {
        "name": "Colombia",
        "power_distance": 67,
        "individualism": 13,
        "uncertainty_avoidance": 80,
        "long_term_orientation": 13,
        "indulgence": 83,
        "masculinity": 64,
        "institutional_trust": 30,
        "tech_adoption_index": 55,
        "regulatory_quality": 58,
        "notes": "Highly collectivist; short-term oriented; high uncertainty avoidance; Medellín transformation shows rapid context change is possible",
    },
    "NG": {
        "name": "Nigeria",
        "power_distance": 80,
        "individualism": 30,
        "uncertainty_avoidance": 55,
        "long_term_orientation": 13,
        "indulgence": 84,
        "masculinity": 60,
        "institutional_trust": 22,
        "tech_adoption_index": 52,
        "regulatory_quality": 30,
        "notes": "High power distance; very low institutional trust; strong informal networks; mobile money penetration high; federal structure adds complexity",
    },
    "RW": {
        "name": "Rwanda",
        "power_distance": 75,
        "individualism": 27,
        "uncertainty_avoidance": 45,
        "long_term_orientation": 70,
        "indulgence": 25,
        "masculinity": 40,
        "institutional_trust": 72,
        "tech_adoption_index": 48,
        "regulatory_quality": 68,
        "notes": "High state capacity for Africa; long-term vision (Vision 2050); collectivist Umuganda culture; exceptional governance reform track record",
    },
    "IN": {
        "name": "India",
        "power_distance": 77,
        "individualism": 48,
        "uncertainty_avoidance": 40,
        "long_term_orientation": 51,
        "indulgence": 26,
        "masculinity": 56,
        "institutional_trust": 45,
        "tech_adoption_index": 68,
        "regulatory_quality": 55,
        "notes": "High power distance; moderate uncertainty avoidance; massive scale challenges; strong tech talent base; federal complexity",
    },
    "AE": {
        "name": "UAE",
        "power_distance": 90,
        "individualism": 25,
        "uncertainty_avoidance": 80,
        "long_term_orientation": 36,
        "indulgence": 52,
        "masculinity": 50,
        "institutional_trust": 70,
        "tech_adoption_index": 85,
        "regulatory_quality": 82,
        "notes": "Very high power distance; top-down change possible rapidly; high financial resources; strong tech adoption ambition",
    },
}


def get_profile(country_code: str) -> dict[str, Any] | None:
    """
    Retrieve the cultural profile for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., "SG", "NG").

    Returns:
        Cultural profile dict, or None if country is not in the database.
    """
    profile = CULTURAL_PROFILES.get(country_code.upper())
    if profile is None:
        logger.warning("No cultural profile found for country code: %s", country_code)
    return profile


def list_available_countries() -> list[str]:
    """
    Return sorted list of country codes with cultural profiles.

    Returns:
        Sorted list of ISO 3166-1 alpha-2 country codes.
    """
    return sorted(CULTURAL_PROFILES.keys())


def get_profile_by_name(country_name: str) -> dict[str, Any] | None:
    """
    Look up a cultural profile by country name (case-insensitive partial match).

    Args:
        country_name: Full or partial country name.

    Returns:
        First matching cultural profile dict, or None if not found.
    """
    query = country_name.lower()
    for code, profile in CULTURAL_PROFILES.items():
        if query in profile.get("name", "").lower():
            return {**profile, "code": code}
    logger.warning("No cultural profile found for country name: %s", country_name)
    return None
