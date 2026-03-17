"""
Semantic policy matcher for Lodestar.

Takes a target context (city, domain, constraints) and returns the
top-N most analogous successful policies from the ChromaDB knowledge base.
"""

import logging
from typing import Any

from lodestar.engine.embeddings import EmbeddingsDB

logger = logging.getLogger(__name__)


class PolicyMatcher:
    """
    Matches a policy query to the most relevant historical success cases.

    Uses semantic similarity via ChromaDB to find policies from analogous
    contexts, ranked by relevance to the target city and domain.
    """

    def __init__(self, db: EmbeddingsDB | None = None) -> None:
        """
        Initialize the PolicyMatcher.

        Args:
            db: EmbeddingsDB instance. If None, creates a new one and initializes it.
        """
        if db is None:
            self.db = EmbeddingsDB()
            self.db.initialize_db()
        else:
            self.db = db
        logger.debug("PolicyMatcher initialized")

    def match(
        self,
        city: str,
        domain: str,
        country: str = "",
        context: str = "",
        n_results: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Find the top matching policies for a target city and domain.

        Constructs a rich query string from the target context and performs
        semantic search against the policy knowledge base.

        Args:
            city: Target city name (e.g., "Lagos").
            domain: Problem domain (e.g., "housing", "governance", "urban_mobility").
            country: Target country (e.g., "Nigeria"). Optional but improves results.
            context: Additional context about the problem. Optional.
            n_results: Number of top matches to return.

        Returns:
            List of match dicts, each with keys:
            - id: Policy ID
            - name: Policy name
            - country: Source country
            - domain: Policy domain
            - similarity_score: Float 0-1 (higher = more similar)
            - document: Full policy text used for embedding
            - metadata: Raw ChromaDB metadata
        """
        query_parts = [
            f"City seeking policy solutions: {city}",
            f"Problem domain: {domain}",
        ]
        if country:
            query_parts.append(f"Country context: {country}")
        if context:
            query_parts.append(f"Specific context: {context}")
        query_parts.append(
            f"Looking for successful {domain} policies that can be adapted "
            f"for urban environments in developing or middle-income contexts."
        )
        query = "\n".join(query_parts)
        logger.info("Matching policies for: city=%s, domain=%s", city, domain)
        raw_results = self.db.search_similar(query, n_results=n_results)
        enriched = []
        for result in raw_results:
            enriched.append(
                {
                    "id": result["id"],
                    "name": result["metadata"].get("name", result["id"]),
                    "country": result["metadata"].get("country", ""),
                    "city": result["metadata"].get("city", ""),
                    "domain": result["metadata"].get("domain", ""),
                    "year_start": result["metadata"].get("year_start", ""),
                    "similarity_score": result["similarity_score"],
                    "document": result["document"],
                    "metadata": result["metadata"],
                }
            )
        logger.info("Matched %d policies", len(enriched))
        return enriched
