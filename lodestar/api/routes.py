"""
FastAPI route handlers for Lodestar.

Provides REST endpoints for policy analysis, policy listing, and health checks.
"""

import json
import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lodestar.culture.adaptor import CulturalAdaptor
from lodestar.culture.scorer import CulturalScorer
from lodestar.engine.embeddings import EmbeddingsDB
from lodestar.engine.matcher import PolicyMatcher
from lodestar.engine.risk import RiskAnalyzer
from lodestar.engine.simulator import ImpactSimulator

logger = logging.getLogger(__name__)

router = APIRouter()

# Shared instances (initialized at startup)
_db: EmbeddingsDB | None = None
_matcher: PolicyMatcher | None = None
_scorer = CulturalScorer()
_adaptor = CulturalAdaptor()
_risk_analyzer = RiskAnalyzer()


def get_db() -> EmbeddingsDB:
    """Get or initialize the shared EmbeddingsDB instance."""
    global _db
    if _db is None:
        _db = EmbeddingsDB()
        _db.initialize_db()
    return _db


def get_matcher() -> PolicyMatcher:
    """Get or initialize the shared PolicyMatcher instance."""
    global _matcher
    if _matcher is None:
        _matcher = PolicyMatcher(db=get_db())
    return _matcher


class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint."""

    city: str
    domain: str
    country: str = ""
    context: str = ""


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    policy_count: int
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check service health and policy count."""
    try:
        db = get_db()
        count = db.collection.count() if db.collection else 0
    except Exception:
        count = 0
    return HealthResponse(
        status="ok",
        version="0.1.0",
        policy_count=count,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/analyze")
async def analyze(request: AnalyzeRequest) -> dict:
    """
    Run full Lodestar analysis for a city and domain.

    Returns matched policies, cultural fit scores, impact simulation,
    risk assessment, and culturally-adapted recommendations.
    """
    logger.info("Analysis request: city=%s, domain=%s", request.city, request.domain)
    matcher = get_matcher()
    matched = matcher.match(
        city=request.city,
        domain=request.domain,
        country=request.country,
        context=request.context,
    )
    if not matched:
        raise HTTPException(
            status_code=404,
            detail=f"No policies found for domain '{request.domain}'. Run 'lodestar ingest' first.",
        )

    # Load seed policies for full data
    seed_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "seed_policies.json"
    )
    seed_policies: dict[str, dict] = {}
    if os.path.exists(seed_path):
        with open(seed_path) as f:
            for p in json.load(f):
                seed_policies[p["id"]] = p

    # Cultural Fit Scores
    # Try to find country code from common mappings
    country_code_map = {
        "nigeria": "NG",
        "lagos": "NG",
        "brazil": "BR",
        "detroit": "US",
        "united states": "US",
        "us": "US",
        "singapore": "SG",
        "estonia": "EE",
        "colombia": "CO",
        "rwanda": "RW",
        "india": "IN",
        "china": "CN",
        "germany": "DE",
        "france": "FR",
        "uk": "UK",
    }
    target_code = country_code_map.get(request.country.lower(), "US")

    cultural_fit_scores = []
    for policy in matched:
        source_map = {
            "singapore": "SG",
            "estonia": "EE",
            "colombia": "CO",
            "austria": "AT",
            "rwanda": "RW",
            "brazil": "BR",
            "finland": "FI",
            "netherlands": "NL",
            "japan": "JP",
            "denmark": "DK",
            "south korea": "KR",
        }
        source_code = source_map.get(policy.get("country", "").lower(), "US")
        try:
            cs = _scorer.score(source_code, target_code)
            cultural_fit_scores.append(cs)
        except ValueError as exc:
            logger.warning("Cultural scoring failed: %s", exc)
            cultural_fit_scores.append(
                {
                    "score": 50.0,
                    "grade": "C",
                    "source_country": policy.get("country", ""),
                    "target_country": request.country,
                    "dimension_scores": {},
                    "adaptation_notes": [],
                    "summary": "",
                }
            )

    avg_fit = (
        sum(cs["score"] for cs in cultural_fit_scores) / len(cultural_fit_scores)
        if cultural_fit_scores
        else 50.0
    )

    # Risk assessment
    risk = _risk_analyzer.analyze(
        matched_policies=matched,
        target_city=request.city,
        target_country=request.country,
        domain=request.domain,
        cultural_fit_score=avg_fit,
    )

    # Impact simulation
    try:
        simulator = ImpactSimulator()
        simulation = simulator.simulate(
            matched_policies=matched,
            target_city=request.city,
            target_country=request.country,
            domain=request.domain,
            cultural_fit_score=avg_fit,
        )
    except Exception as exc:
        logger.error("Simulation failed: %s", exc)
        simulation = {
            "predicted_outcomes": [],
            "confidence_score": 0.0,
            "timeline": "Simulation unavailable",
            "resource_requirements": {
                "estimated_budget_usd": "TBD",
                "key_staffing": "TBD",
                "critical_partners": [],
            },
            "key_risks": ["Simulation service unavailable"],
            "bear_case": "N/A",
            "bull_case": "N/A",
            "recommended_pilot": "N/A",
        }

    # Cultural adaptations
    adapted_recs = []
    for i, policy in enumerate(matched):
        full_policy = seed_policies.get(policy["id"], policy)
        cs = (
            cultural_fit_scores[i]
            if i < len(cultural_fit_scores)
            else {"score": 50.0, "adaptation_notes": []}
        )
        try:
            rec = _adaptor.adapt(full_policy, cs, target_code)
            adapted_recs.append(rec)
        except Exception as exc:
            logger.warning("Adaptation failed for %s: %s", policy["id"], exc)

    return {
        "query_city": request.city,
        "query_country": request.country,
        "query_domain": request.domain,
        "matched_policies": matched,
        "cultural_fit_scores": cultural_fit_scores,
        "simulation": simulation,
        "risk_assessment": risk,
        "adapted_recommendations": adapted_recs,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/policies")
async def list_policies() -> list[dict]:
    """List all seeded policies in the knowledge base."""
    db = get_db()
    return db.get_all_policies()


@router.get("/policies/{policy_id}")
async def get_policy(policy_id: str) -> dict:
    """
    Retrieve a specific policy by ID.

    Args:
        policy_id: Policy identifier (e.g., 'singapore_hdb').
    """
    db = get_db()
    all_policies = db.get_all_policies()
    for policy in all_policies:
        if policy["id"] == policy_id:
            return policy
    raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found")
