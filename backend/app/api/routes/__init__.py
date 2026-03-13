"""API routes."""

from fastapi import APIRouter

from app.api.routes import health, index, query

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(index.router, prefix="/index", tags=["index"])
router.include_router(query.router, prefix="/query", tags=["query"])
