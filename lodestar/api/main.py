"""
FastAPI application entry point for Lodestar.

Runs the REST API server. Start with:
    uvicorn lodestar.api.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lodestar.api.routes import router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lodestar API",
    description=(
        "AI platform for culturally-adapted global policy intelligence. "
        "Identifies successful governance, housing, and urban policy models "
        "and generates implementation blueprints adapted for target cultural contexts."
    ),
    version="0.1.0",
    contact={"name": "Jean-Paul Daum", "url": "https://jeanpauldaum.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="")


@app.on_event("startup")
async def on_startup() -> None:
    """Log startup message."""
    logger.info("Lodestar API starting up — version 0.1.0")
