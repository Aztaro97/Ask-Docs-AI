"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.middleware import setup_middleware
from app.api.routes import router
from app.api.routes.health import set_ready
from app.config import get_settings
from app.observability import configure_logging, get_logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    logger = get_logger(__name__)

    # Startup
    logger.info("application_starting", version="0.1.0")

    # Ensure data directories exist
    settings.index_path.mkdir(parents=True, exist_ok=True)
    settings.cache_path.mkdir(parents=True, exist_ok=True)
    settings.docs_path.mkdir(parents=True, exist_ok=True)

    # Initialize models (lazy loading happens on first use)
    # Models are loaded when first needed to speed up startup
    logger.info("application_initialized")
    set_ready(True)

    yield

    # Shutdown
    logger.info("application_shutting_down")
    set_ready(False)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Configure logging first
    configure_logging(
        log_level=settings.log_level,
        json_format=not settings.debug,
    )

    app = FastAPI(
        title="Ask-Docs API",
        description="RAG-based Q&A API with local LLM",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Setup middleware (CORS, rate limiting, request context)
    setup_middleware(app)

    # Include API routes
    app.include_router(router)

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
