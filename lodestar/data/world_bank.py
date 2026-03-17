"""
World Bank API client for Lodestar.

Provides access to World Bank development indicators, country data,
and governance scores via the World Bank Open Data API v2.
"""

import logging
import os

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("WORLD_BANK_BASE_URL", "https://api.worldbank.org/v2")


class CountryIndicator(BaseModel):
    """A single World Bank indicator value for a country."""

    country_code: str = Field(description="ISO 3166-1 alpha-2 or alpha-3 country code")
    indicator_id: str = Field(
        description="World Bank indicator ID, e.g. NY.GDP.MKTP.CD"
    )
    indicator_name: str = Field(description="Human-readable indicator name")
    value: float | None = Field(description="Indicator value, None if not available")
    year: int = Field(description="Year of the data point")


class CountryInfo(BaseModel):
    """Basic country information from World Bank."""

    code: str = Field(description="ISO 3166-1 alpha-2 country code")
    name: str = Field(description="Country name")
    capital_city: str = Field(description="Capital city name")
    region: str = Field(description="World Bank region classification")
    income_level: str = Field(description="World Bank income level classification")
    longitude: float | None = Field(description="Country centroid longitude")
    latitude: float | None = Field(description="Country centroid latitude")


class WorldBankClient:
    """
    Client for the World Bank Open Data API.

    Fetches development indicators, country metadata, and governance scores.
    All methods return clean Pydantic models or raise descriptive exceptions.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = 30) -> None:
        """
        Initialize the World Bank API client.

        Args:
            base_url: Base URL for the World Bank API.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        logger.debug("WorldBankClient initialized with base_url=%s", self.base_url)

    def get_indicators(
        self,
        country_code: str,
        indicators: list[str],
        year_range: tuple[int, int] = (2018, 2023),
    ) -> list[CountryIndicator]:
        """
        Fetch multiple World Bank indicators for a country.

        Args:
            country_code: ISO country code (e.g., "NG" for Nigeria).
            indicators: List of World Bank indicator IDs.
            year_range: Tuple of (start_year, end_year) for data.

        Returns:
            List of CountryIndicator models with the most recent available values.

        Raises:
            requests.HTTPError: If the API returns an error status.
            ValueError: If the country code is invalid.
        """
        results: list[CountryIndicator] = []
        date_param = f"{year_range[0]}:{year_range[1]}"

        for indicator_id in indicators:
            url = f"{self.base_url}/country/{country_code}/indicator/{indicator_id}"
            params = {"format": "json", "date": date_param, "mrv": 1, "per_page": 10}
            logger.debug("Fetching indicator %s for %s", indicator_id, country_code)
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if len(data) < 2 or not data[1]:
                    logger.warning(
                        "No data for indicator %s / country %s",
                        indicator_id,
                        country_code,
                    )
                    continue
                for entry in data[1]:
                    if entry.get("value") is not None:
                        results.append(
                            CountryIndicator(
                                country_code=country_code,
                                indicator_id=indicator_id,
                                indicator_name=entry.get("indicator", {}).get(
                                    "value", indicator_id
                                ),
                                value=float(entry["value"]),
                                year=int(entry["date"]),
                            )
                        )
                        break
            except requests.HTTPError as exc:
                logger.error("HTTP error fetching %s: %s", indicator_id, exc)
                raise
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("Parse error for indicator %s: %s", indicator_id, exc)
        return results

    def search_countries(self, query: str) -> list[CountryInfo]:
        """
        Search for countries by name.

        Args:
            query: Partial country name to search for.

        Returns:
            List of matching CountryInfo models.

        Raises:
            requests.HTTPError: If the API returns an error status.
        """
        url = f"{self.base_url}/country"
        params = {"format": "json", "per_page": 300}
        logger.debug("Searching countries with query: %s", query)
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if len(data) < 2 or not data[1]:
            return []
        query_lower = query.lower()
        results: list[CountryInfo] = []
        for country in data[1]:
            if query_lower in country.get("name", "").lower():
                try:
                    results.append(
                        CountryInfo(
                            code=country["id"],
                            name=country["name"],
                            capital_city=country.get("capitalCity", ""),
                            region=country.get("region", {}).get("value", ""),
                            income_level=country.get("incomeLevel", {}).get(
                                "value", ""
                            ),
                            longitude=float(country["longitude"])
                            if country.get("longitude")
                            else None,
                            latitude=float(country["latitude"])
                            if country.get("latitude")
                            else None,
                        )
                    )
                except (KeyError, ValueError) as exc:
                    logger.warning("Skipping malformed country entry: %s", exc)
        return results

    def get_governance_scores(self, country_code: str) -> dict[str, float | None]:
        """
        Fetch World Governance Indicators (WGI) for a country.

        Retrieves six dimensions: voice & accountability, political stability,
        government effectiveness, regulatory quality, rule of law, control of corruption.

        Args:
            country_code: ISO country code.

        Returns:
            Dict mapping governance dimension name to percentile rank score (0-100).
        """
        # Use WGI indicator IDs
        wgi_ids = {
            "voice_accountability": "VA.PER.RNK",
            "political_stability": "PV.PER.RNK",
            "government_effectiveness": "GE.PER.RNK",
            "regulatory_quality": "RQ.PER.RNK",
            "rule_of_law": "RL.PER.RNK",
            "control_of_corruption": "CC.PER.RNK",
        }
        indicators_list = list(wgi_ids.values())
        raw = self.get_indicators(country_code, indicators_list)
        raw_by_id = {ind.indicator_id: ind.value for ind in raw}
        return {dim: raw_by_id.get(ind_id) for dim, ind_id in wgi_ids.items()}
