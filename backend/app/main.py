from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api import articles, sources, dashboard, alerts, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Geopolitical News Aggregator...")
    init_db()
    logger.info("Database initialized")

    # Trigger initial news fetch on startup
    try:
        from app.tasks.fetch_news import fetch_all_news, fetch_gdelt_news
        logger.info("Triggering initial news fetch...")
        # Queue the fetch tasks (non-blocking)
        fetch_all_news.delay()
        fetch_gdelt_news.delay()
        logger.info("Initial fetch tasks queued")
    except Exception as e:
        logger.warning(f"Could not queue initial fetch: {e}")

    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Geopolitical News Aggregator API",
    description="AI-powered strategic news aggregation and analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])


@app.get("/")
async def root():
    return {
        "message": "Geopolitical News Aggregator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
