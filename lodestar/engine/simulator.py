"""
Impact simulation engine for Lodestar.

Uses Anthropic Claude to generate structured predictions of policy
implementation outcomes, timelines, and resource requirements.
"""

import json
import logging
import os
from typing import Any

import anthropic

logger = logging.getLogger(__name__)


SIMULATION_SYSTEM_PROMPT = """You are a senior policy analyst at a leading urban development institute.
You have deep expertise in policy transfer, implementation science, and comparative governance.
Your role is to provide rigorous, evidence-based impact simulations for policy adaptation proposals.

When generating simulations:
- Ground predictions in analogous historical implementations
- Quantify outcomes with ranges, not point estimates
- Acknowledge uncertainty honestly
- Flag context-specific risks
- Always produce valid JSON matching the requested schema"""


class ImpactSimulator:
    """
    Generates structured impact simulations for policy adaptations using Claude.

    Produces probabilistic outcome ranges, timelines, resource requirements,
    and confidence-scored predictions grounded in comparative policy evidence.
    """

    def __init__(
        self, api_key: str | None = None, model: str = "claude-sonnet-4-6"
    ) -> None:
        """
        Initialize the impact simulator.

        Args:
            api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
            model: Claude model ID to use for simulations.

        Raises:
            ValueError: If no API key is found.
        """
        resolved_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=resolved_key)
        self.model = model
        logger.debug("ImpactSimulator initialized with model=%s", model)

    def simulate(
        self,
        matched_policies: list[dict[str, Any]],
        target_city: str,
        target_country: str,
        domain: str,
        cultural_fit_score: float = 50.0,
        additional_context: str = "",
    ) -> dict[str, Any]:
        """
        Generate an impact simulation for a policy adaptation scenario.

        Args:
            matched_policies: Top 3 matched policies from PolicyMatcher.
            target_city: Name of target city (e.g., "Lagos").
            target_country: Name of target country (e.g., "Nigeria").
            domain: Policy domain (e.g., "housing").
            cultural_fit_score: Cultural Fit Score (0-100).
            additional_context: Any extra context about the target situation.

        Returns:
            Dict with keys:
            - predicted_outcomes: List of {outcome, value_range, confidence, timeline}
            - confidence_score: Overall confidence float 0-1
            - timeline: Implementation timeline string
            - resource_requirements: Dict with budget, staffing, timeline estimates
            - key_risks: List of risk strings
            - bear_case: Pessimistic scenario description
            - bull_case: Optimistic scenario description
            - recommended_pilot: Pilot project recommendation string
        """
        policies_summary = "\n".join(
            f"- {p['name']} ({p['country']}, {p.get('year_start', 'n/a')}): "
            f"similarity={p.get('similarity_score', 0):.2f}"
            for p in matched_policies
        )

        prompt = f"""Simulate the impact of adapting the following successful policies to {target_city}, {target_country}.

TARGET CONTEXT:
- City: {target_city}
- Country: {target_country}
- Domain: {domain}
- Cultural Fit Score: {cultural_fit_score:.0f}/100
{f"- Additional context: {additional_context}" if additional_context else ""}

REFERENCE POLICIES (most analogous global success cases):
{policies_summary}

Generate a rigorous impact simulation. Return ONLY a valid JSON object with this exact structure:
{{
  "predicted_outcomes": [
    {{
      "outcome": "description of measurable outcome",
      "value_range": "e.g. 25-40% improvement",
      "confidence": 0.75,
      "timeline": "e.g. 3-5 years"
    }}
  ],
  "confidence_score": 0.65,
  "timeline": "Overall implementation timeline e.g. '18 months pilot + 5 year rollout'",
  "resource_requirements": {{
    "estimated_budget_usd": "e.g. $500M-$1.2B over 10 years",
    "key_staffing": "e.g. 200-400 FTE implementation team",
    "critical_partners": ["World Bank", "Local municipality", "NGO partners"]
  }},
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "bear_case": "Pessimistic scenario: what happens if implementation fails",
  "bull_case": "Optimistic scenario: what happens if implementation succeeds",
  "recommended_pilot": "Specific pilot project recommendation"
}}

Generate 4-6 predicted_outcomes. Make confidence_score reflect actual uncertainty given cultural fit."""

        logger.info("Running impact simulation for %s, %s", target_city, target_country)
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=SIMULATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_content = message.content[0].text
            # Extract JSON from response
            json_start = raw_content.find("{")
            json_end = raw_content.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in simulation response")
            json_str = raw_content[json_start:json_end]
            result = json.loads(json_str)
            logger.info(
                "Simulation complete. Confidence: %.2f",
                result.get("confidence_score", 0),
            )
            return result
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse simulation JSON: %s", exc)
            raise ValueError(f"Simulation returned invalid JSON: {exc}") from exc
        except anthropic.APIError as exc:
            logger.error("Anthropic API error during simulation: %s", exc)
            raise
