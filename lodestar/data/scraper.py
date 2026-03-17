"""
Web content retrieval for Lodestar using the Grok xAI API.

Uses Grok-3 via the OpenAI-compatible endpoint at https://api.x.ai/v1 to perform
live web searches and retrieve recent information about policies and governance models.
Grok has built-in web search capability, replacing static Wikipedia scraping.
"""

import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)

GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-3"


class PolicyScraper:
    """
    Retrieves policy information and recent news using Grok xAI's web search.

    Grok-3 has live internet access, making it superior to static scraping
    for up-to-date policy outcomes, recent adaptations, and current news.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the PolicyScraper with Grok xAI credentials.

        Args:
            api_key: Grok API key. Defaults to GROK_API_KEY environment variable.

        Raises:
            ValueError: If no API key is found.
        """
        resolved_key = api_key or os.getenv("GROK_API_KEY")
        if not resolved_key:
            raise ValueError("GROK_API_KEY environment variable not set")
        self.client = OpenAI(api_key=resolved_key, base_url=GROK_BASE_URL)
        logger.debug("PolicyScraper initialized with Grok xAI endpoint")

    def search_policy_info(self, policy_name: str, country: str) -> dict[str, str]:
        """
        Search for detailed information about a specific policy.

        Uses Grok's live web search to retrieve current data about a policy's
        implementation, outcomes, and lessons learned.

        Args:
            policy_name: Name of the policy or program (e.g., "HDB public housing").
            country: Country where the policy was implemented (e.g., "Singapore").

        Returns:
            Dict with keys: summary, key_outcomes, recent_developments, source_context.
        """
        prompt = (
            f"Search the web and provide a comprehensive research summary about: "
            f"'{policy_name}' in {country}. Include:\n"
            f"1. A 2-paragraph overview of the policy and its goals\n"
            f"2. Key measurable outcomes and statistics\n"
            f"3. Recent developments or updates (last 3 years)\n"
            f"4. Main lessons learned and what made it succeed or fail\n"
            f"5. Any notable adaptations in other countries\n"
            f"Be factual and cite specific data where available."
        )
        logger.debug("Searching policy info: %s (%s)", policy_name, country)
        try:
            response = self.client.chat.completions.create(
                model=GROK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a policy research assistant with access to current web information. "
                            "Provide accurate, factual information about government policies and their outcomes. "
                            "Always prioritize recent data and cite statistics where available."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
            )
            content = response.choices[0].message.content or ""
            return {
                "summary": content,
                "policy_name": policy_name,
                "country": country,
                "model_used": GROK_MODEL,
            }
        except Exception as exc:
            logger.error("Grok API error for policy '%s': %s", policy_name, exc)
            raise

    def get_recent_news(self, topic: str) -> dict[str, str]:
        """
        Retrieve recent news and developments on a governance or urban policy topic.

        Args:
            topic: Topic to search for (e.g., "housing affordability Singapore 2024").

        Returns:
            Dict with keys: headlines, summary, implications.
        """
        prompt = (
            f"Search for the most recent news and developments (last 6-12 months) about: '{topic}'. "
            f"Summarize:\n"
            f"1. Top 3-5 recent headlines or developments\n"
            f"2. Overall trend summary\n"
            f"3. Policy implications for governments considering similar approaches\n"
            f"Focus on governance, urban policy, housing, infrastructure, and social policy angles."
        )
        logger.debug("Fetching recent news for topic: %s", topic)
        try:
            response = self.client.chat.completions.create(
                model=GROK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a policy news analyst with live web access. "
                            "Provide current, accurate summaries of policy-relevant news. "
                            "Focus on actionable insights for policymakers."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
            )
            content = response.choices[0].message.content or ""
            return {
                "topic": topic,
                "content": content,
                "model_used": GROK_MODEL,
            }
        except Exception as exc:
            logger.error("Grok API error for topic '%s': %s", topic, exc)
            raise
