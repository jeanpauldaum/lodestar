"""
Tests for the PolicyMatcher and EmbeddingsDB modules.

Uses mock ChromaDB collection to avoid requiring a real database in CI.
"""

from unittest.mock import MagicMock

import pytest

from lodestar.engine.embeddings import EmbeddingsDB
from lodestar.engine.matcher import PolicyMatcher

MOCK_POLICIES = [
    {
        "id": "singapore_hdb",
        "name": "Singapore Public Housing (HDB)",
        "country": "Singapore",
        "city": "Singapore",
        "domain": "housing",
        "year_start": "1960",
        "description": "National public housing authority built 80% of Singapore's housing stock.",
        "similarity_score": 0.91,
    },
    {
        "id": "vienna_gemeindebau",
        "name": "Vienna Social Housing (Gemeindebau)",
        "country": "Austria",
        "city": "Vienna",
        "domain": "housing",
        "year_start": "1919",
        "description": "Municipal social housing providing affordable rentals for 60% of Vienna residents.",
        "similarity_score": 0.85,
    },
]


class TestPolicyMatcher:
    """Tests for PolicyMatcher using mock EmbeddingsDB."""

    def _make_mock_db(self) -> EmbeddingsDB:
        """Create a mock EmbeddingsDB that returns test data."""
        mock_db = MagicMock(spec=EmbeddingsDB)
        mock_db.search_similar.return_value = [
            {
                "id": "singapore_hdb",
                "document": "Policy: Singapore Public Housing...",
                "metadata": {
                    "name": "Singapore Public Housing (HDB)",
                    "country": "Singapore",
                    "city": "Singapore",
                    "domain": "housing",
                    "year_start": "1960",
                },
                "distance": 0.09,
                "similarity_score": 0.91,
            },
            {
                "id": "vienna_gemeindebau",
                "document": "Policy: Vienna Social Housing...",
                "metadata": {
                    "name": "Vienna Social Housing (Gemeindebau)",
                    "country": "Austria",
                    "city": "Vienna",
                    "domain": "housing",
                    "year_start": "1919",
                },
                "distance": 0.15,
                "similarity_score": 0.85,
            },
        ]
        return mock_db

    def test_match_returns_list(self) -> None:
        """match() should return a list."""
        db = self._make_mock_db()
        matcher = PolicyMatcher(db=db)
        results = matcher.match(city="Lagos", domain="housing", country="Nigeria")
        assert isinstance(results, list)

    def test_match_returns_correct_count(self) -> None:
        """match() should return the number of results from the DB."""
        db = self._make_mock_db()
        matcher = PolicyMatcher(db=db)
        results = matcher.match(city="Lagos", domain="housing")
        assert len(results) == 2

    def test_match_result_has_required_fields(self) -> None:
        """Each match result must have required fields."""
        db = self._make_mock_db()
        matcher = PolicyMatcher(db=db)
        results = matcher.match(city="Lagos", domain="housing")
        required = {"id", "name", "country", "domain", "similarity_score"}
        for result in results:
            assert required.issubset(result.keys())

    def test_match_calls_db_with_query_containing_city(self) -> None:
        """match() should include the city name in the query sent to EmbeddingsDB."""
        db = self._make_mock_db()
        matcher = PolicyMatcher(db=db)
        matcher.match(city="Lagos", domain="housing", country="Nigeria")
        call_args = db.search_similar.call_args
        query_text = call_args[0][0]
        assert "Lagos" in query_text

    def test_match_includes_similarity_score(self) -> None:
        """Similarity scores should be in 0-1 range."""
        db = self._make_mock_db()
        matcher = PolicyMatcher(db=db)
        results = matcher.match(city="Lagos", domain="housing")
        for result in results:
            assert 0.0 <= result["similarity_score"] <= 1.0

    def test_empty_db_returns_empty_list(self) -> None:
        """When DB has no results, match() should return empty list."""
        mock_db = MagicMock(spec=EmbeddingsDB)
        mock_db.search_similar.return_value = []
        matcher = PolicyMatcher(db=mock_db)
        results = matcher.match(city="TestCity", domain="housing")
        assert results == []


class TestEmbeddingsDB:
    """Tests for EmbeddingsDB initialization and schema."""

    def test_ensure_initialized_raises_before_init(self) -> None:
        """Calling search_similar before initialize_db should raise RuntimeError."""
        db = EmbeddingsDB(persist_dir="/tmp/test_lodestar_embeddings")
        with pytest.raises(RuntimeError, match="not initialized"):
            db.search_similar("test query")

    def test_add_policy_requires_initialization(self) -> None:
        """add_policy before initialize_db should raise RuntimeError."""
        db = EmbeddingsDB(persist_dir="/tmp/test_lodestar_embeddings")
        with pytest.raises(RuntimeError, match="not initialized"):
            db.add_policy(
                {
                    "id": "test",
                    "name": "Test",
                    "description": "X",
                    "domain": "housing",
                    "country": "US",
                }
            )
