"""
FRED (Federal Reserve Economic Data) API client for Lodestar.

Uses the fredapi library to fetch macroeconomic series relevant to
policy analysis: GDP, inflation, unemployment, housing indices, etc.
"""

import logging
import os
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

try:
    from fredapi import Fred

    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    logger.warning("fredapi not installed — FRED client will be unavailable")


class FREDClient:
    """
    Client for the FRED (Federal Reserve Economic Data) API.

    Wraps fredapi to provide clean interfaces for policy-relevant
    economic time series. Requires a FRED_API_KEY environment variable.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the FRED client.

        Args:
            api_key: FRED API key. Defaults to FRED_API_KEY environment variable.

        Raises:
            ImportError: If fredapi is not installed.
            ValueError: If no API key is provided or found in environment.
        """
        if not FRED_AVAILABLE:
            raise ImportError("fredapi is required: pip install fredapi")
        resolved_key = api_key or os.getenv("FRED_API_KEY")
        if not resolved_key:
            raise ValueError("FRED_API_KEY environment variable not set")
        self.fred = Fred(api_key=resolved_key)
        logger.debug("FREDClient initialized")

    def get_series(self, series_id: str, limit: int = 20) -> dict[str, Any]:
        """
        Fetch a FRED time series by ID.

        Args:
            series_id: FRED series identifier (e.g., "GDP", "CPIAUCSL").
            limit: Maximum number of observations to return (most recent).

        Returns:
            Dict with keys: series_id, title, units, frequency, observations (list of {date, value}).

        Raises:
            ValueError: If the series_id is not found.
        """
        logger.debug("Fetching FRED series: %s", series_id)
        try:
            info = self.fred.get_series_info(series_id)
            data: pd.Series = self.fred.get_series(series_id)
            data = data.dropna().tail(limit)
            observations = [
                {"date": str(date.date()), "value": float(val)}
                for date, val in data.items()
            ]
            return {
                "series_id": series_id,
                "title": info.get("title", series_id),
                "units": info.get("units", ""),
                "frequency": info.get("frequency", ""),
                "observations": observations,
            }
        except Exception as exc:
            logger.error("Error fetching FRED series %s: %s", series_id, exc)
            raise ValueError(
                f"Could not fetch FRED series '{series_id}': {exc}"
            ) from exc

    def search_series(self, query: str, limit: int = 10) -> list[dict[str, str]]:
        """
        Search FRED for series matching a query.

        Args:
            query: Search terms.
            limit: Maximum number of results to return.

        Returns:
            List of dicts with keys: id, title, units, frequency, last_updated.
        """
        logger.debug("Searching FRED for: %s", query)
        try:
            results = self.fred.search(query, limit=limit)
            if results is None or results.empty:
                return []
            output = []
            for _, row in results.iterrows():
                output.append(
                    {
                        "id": row.get("id", ""),
                        "title": row.get("title", ""),
                        "units": row.get("units", ""),
                        "frequency": row.get("frequency", ""),
                        "last_updated": str(row.get("last_updated", "")),
                    }
                )
            return output
        except Exception as exc:
            logger.warning("FRED search failed for '%s': %s", query, exc)
            return []

    def get_gdp_data(self, country: str = "US") -> dict[str, Any]:
        """
        Fetch GDP data. Currently supports US data via FRED.

        Args:
            country: Country code. Only "US" is supported via FRED directly.

        Returns:
            Dict with GDP series data.
        """
        series_map = {"US": "GDP", "UK": "UKNGDP"}
        series_id = series_map.get(country.upper(), "GDP")
        logger.debug(
            "Fetching GDP data for country: %s (series: %s)", country, series_id
        )
        return self.get_series(series_id)

    def get_inflation_data(self) -> dict[str, Any]:
        """
        Fetch US CPI (inflation) data.

        Returns:
            Dict with CPI series data (CPIAUCSL — Consumer Price Index for All Urban Consumers).
        """
        logger.debug("Fetching US inflation (CPI) data")
        return self.get_series("CPIAUCSL")

    def get_housing_index(self) -> dict[str, Any]:
        """
        Fetch US housing price index (Case-Shiller National Home Price Index).

        Returns:
            Dict with CSUSHPISA series data.
        """
        logger.debug("Fetching housing price index")
        return self.get_series("CSUSHPISA")
