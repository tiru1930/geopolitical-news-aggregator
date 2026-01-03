from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.database import get_db
from app.models.article import Article, RelevanceLevel
from app.models.source import Source

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall dashboard statistics"""
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Total articles
    total_articles = db.query(Article).count()

    # Articles by relevance
    high_relevance = db.query(Article).filter(
        Article.relevance_level == RelevanceLevel.HIGH,
        Article.is_processed == 1
    ).count()

    medium_relevance = db.query(Article).filter(
        Article.relevance_level == RelevanceLevel.MEDIUM,
        Article.is_processed == 1
    ).count()

    low_relevance = db.query(Article).filter(
        Article.relevance_level == RelevanceLevel.LOW,
        Article.is_processed == 1
    ).count()

    # Recent activity
    articles_24h = db.query(Article).filter(
        Article.created_at >= last_24h
    ).count()

    articles_7d = db.query(Article).filter(
        Article.created_at >= last_7d
    ).count()

    # Active sources
    active_sources = db.query(Source).filter(Source.is_active == True).count()
    total_sources = db.query(Source).count()

    # Pending processing
    pending_processing = db.query(Article).filter(
        Article.is_processed == 0
    ).count()

    return {
        "total_articles": total_articles,
        "relevance_breakdown": {
            "high": high_relevance,
            "medium": medium_relevance,
            "low": low_relevance
        },
        "recent_activity": {
            "last_24h": articles_24h,
            "last_7d": articles_7d
        },
        "sources": {
            "active": active_sources,
            "total": total_sources
        },
        "pending_processing": pending_processing
    }


@router.get("/trends")
async def get_trends(days: int = 7, db: Session = Depends(get_db)):
    """Get article trends over time"""
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)

    # Get daily counts
    daily_counts = []

    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        count = db.query(Article).filter(
            Article.created_at >= day_start,
            Article.created_at < day_end
        ).count()

        high_count = db.query(Article).filter(
            Article.created_at >= day_start,
            Article.created_at < day_end,
            Article.relevance_level == RelevanceLevel.HIGH
        ).count()

        daily_counts.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "total": count,
            "high_relevance": high_count
        })

    return daily_counts


@router.get("/regions")
async def get_region_stats(db: Session = Depends(get_db)):
    """Get article distribution by region"""
    results = db.query(
        Article.region,
        func.count(Article.id).label("count"),
        func.avg(Article.relevance_score).label("avg_relevance")
    ).filter(
        Article.region.isnot(None),
        Article.is_processed == 1
    ).group_by(Article.region).all()

    return [
        {
            "region": r.region,
            "count": r.count,
            "avg_relevance": round(r.avg_relevance or 0, 3)
        }
        for r in results
    ]


@router.get("/themes")
async def get_theme_stats(db: Session = Depends(get_db)):
    """Get article distribution by theme"""
    results = db.query(
        Article.theme,
        func.count(Article.id).label("count"),
        func.avg(Article.relevance_score).label("avg_relevance")
    ).filter(
        Article.theme.isnot(None),
        Article.is_processed == 1
    ).group_by(Article.theme).all()

    return [
        {
            "theme": r.theme,
            "count": r.count,
            "avg_relevance": round(r.avg_relevance or 0, 3)
        }
        for r in results
    ]


@router.get("/countries")
async def get_country_stats(limit: int = 20, db: Session = Depends(get_db)):
    """Get top countries by article count"""
    results = db.query(
        Article.country,
        func.count(Article.id).label("count")
    ).filter(
        Article.country.isnot(None),
        Article.is_processed == 1
    ).group_by(Article.country).order_by(
        desc(func.count(Article.id))
    ).limit(limit).all()

    return [
        {"country": r.country, "count": r.count}
        for r in results
    ]


@router.get("/hotspots")
async def get_geopolitical_hotspots(db: Session = Depends(get_db)):
    """
    Get geopolitical hotspots based on high-relevance article concentration.
    Returns data suitable for map visualization.
    """
    # Coordinates for major geopolitical regions
    region_coords = {
        "South Asia": {"lat": 20.5937, "lng": 78.9629, "zoom": 4},
        "East Asia": {"lat": 35.8617, "lng": 104.1954, "zoom": 4},
        "Indo-Pacific": {"lat": 0, "lng": 120, "zoom": 3},
        "Middle East": {"lat": 29.2985, "lng": 42.5510, "zoom": 5},
        "Europe": {"lat": 54.5260, "lng": 15.2551, "zoom": 4},
        "Central Asia": {"lat": 45.0, "lng": 68.0, "zoom": 4},
        "Africa": {"lat": -8.7832, "lng": 34.5085, "zoom": 3},
        "Americas": {"lat": 37.0902, "lng": -95.7129, "zoom": 3}
    }

    # Get articles by region with high relevance
    results = db.query(
        Article.region,
        func.count(Article.id).label("total"),
        func.sum(
            func.cast(Article.relevance_level == RelevanceLevel.HIGH, db.bind.dialect.name != 'sqlite' and Integer or Integer)
        ).label("high_count")
    ).filter(
        Article.region.isnot(None),
        Article.is_processed == 1
    ).group_by(Article.region).all()

    hotspots = []
    for r in results:
        if r.region in region_coords:
            coords = region_coords[r.region]
            intensity = min((r.high_count or 0) / 10, 1.0)  # Normalize intensity

            hotspots.append({
                "region": r.region,
                "lat": coords["lat"],
                "lng": coords["lng"],
                "total_articles": r.total,
                "high_relevance": r.high_count or 0,
                "intensity": round(intensity, 2)
            })

    return sorted(hotspots, key=lambda x: x["high_relevance"], reverse=True)


@router.get("/recent-high-impact")
async def get_recent_high_impact(limit: int = 5, db: Session = Depends(get_db)):
    """Get most recent high-impact articles for dashboard display"""
    articles = db.query(Article).filter(
        Article.relevance_level == RelevanceLevel.HIGH,
        Article.is_processed == 1
    ).order_by(desc(Article.published_at)).limit(limit).all()

    results = []
    for article in articles:
        source = db.query(Source).filter(Source.id == article.source_id).first()
        results.append({
            "id": article.id,
            "title": article.title,
            "source": source.name if source else "Unknown",
            "region": article.region,
            "theme": article.theme,
            "relevance_score": article.relevance_score,
            "published_at": article.published_at,
            "summary": article.summary_what_happened
        })

    return results


# Import Integer for type casting
from sqlalchemy import Integer
