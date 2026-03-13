"""Health check endpoints for Kubernetes probes."""

from fastapi import APIRouter, Response, status

from app.config import get_settings
from app.observability import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Simple state tracking for readiness
_ready = False


def set_ready(ready: bool = True) -> None:
    """Set application readiness state."""
    global _ready
    _ready = ready
    logger.info("readiness_changed", ready=ready)


def is_ready() -> bool:
    """Check if application is ready."""
    return _ready


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    """Liveness probe - returns 200 if process is alive.

    Kubernetes uses this to know if the container should be restarted.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(response: Response) -> dict[str, str | bool]:
    """Readiness probe - returns 200 if ready to serve traffic.

    Kubernetes uses this to know if traffic should be sent to this pod.
    Checks:
    - Models are loaded
    - Index is available (if exists)
    """
    settings = get_settings()

    checks = {
        "models_loaded": _ready,
        "config_valid": settings.docs_path is not None,
    }

    all_ready = all(checks.values())

    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if all_ready else "not_ready",
        **checks,
    }


@router.get("/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
