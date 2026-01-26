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
        Article.region != "",
        Article.is_processed == 1
    ).group_by(Article.region).all()

    return [
        {
            "region": r.region if r.region else "Unknown",
            "count": r.count,
            "avg_relevance": round(r.avg_relevance or 0, 3)
        }
        for r in results
        if r.region and r.region.strip()  # Filter out empty strings
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
        Article.country != "",
        Article.is_processed == 1
    ).group_by(Article.country).order_by(
        desc(func.count(Article.id))
    ).limit(limit).all()

    return [
        {"country": r.country if r.country else "Unknown", "count": r.count}
        for r in results
        if r.country and r.country.strip()  # Filter out empty strings
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


@router.get("/country-hotspots")
async def get_country_hotspots(limit: int = 30, db: Session = Depends(get_db)):
    """
    Get country-wise hotspots with coordinates for map visualization.
    """
    # Coordinates for countries (lat, lng)
    country_coords = {
        # Asia
        "India": {"lat": 20.5937, "lng": 78.9629},
        "China": {"lat": 35.8617, "lng": 104.1954},
        "Pakistan": {"lat": 30.3753, "lng": 69.3451},
        "Bangladesh": {"lat": 23.685, "lng": 90.3563},
        "Nepal": {"lat": 28.3949, "lng": 84.124},
        "Sri Lanka": {"lat": 7.8731, "lng": 80.7718},
        "Myanmar": {"lat": 21.9162, "lng": 95.956},
        "Thailand": {"lat": 15.87, "lng": 100.9925},
        "Vietnam": {"lat": 14.0583, "lng": 108.2772},
        "Indonesia": {"lat": -0.7893, "lng": 113.9213},
        "Malaysia": {"lat": 4.2105, "lng": 101.9758},
        "Philippines": {"lat": 12.8797, "lng": 121.774},
        "Japan": {"lat": 36.2048, "lng": 138.2529},
        "South Korea": {"lat": 35.9078, "lng": 127.7669},
        "North Korea": {"lat": 40.3399, "lng": 127.5101},
        "Taiwan": {"lat": 23.6978, "lng": 120.9605},
        "Singapore": {"lat": 1.3521, "lng": 103.8198},
        "Afghanistan": {"lat": 33.9391, "lng": 67.71},
        # Middle East
        "Iran": {"lat": 32.4279, "lng": 53.688},
        "Iraq": {"lat": 33.2232, "lng": 43.6793},
        "Syria": {"lat": 34.8021, "lng": 38.9968},
        "Israel": {"lat": 31.0461, "lng": 34.8516},
        "Palestine": {"lat": 31.9522, "lng": 35.2332},
        "Saudi Arabia": {"lat": 23.8859, "lng": 45.0792},
        "UAE": {"lat": 23.4241, "lng": 53.8478},
        "Turkey": {"lat": 38.9637, "lng": 35.2433},
        "Yemen": {"lat": 15.5527, "lng": 48.5164},
        "Lebanon": {"lat": 33.8547, "lng": 35.8623},
        "Jordan": {"lat": 30.5852, "lng": 36.2384},
        "Qatar": {"lat": 25.3548, "lng": 51.1839},
        "Kuwait": {"lat": 29.3117, "lng": 47.4818},
        "Oman": {"lat": 21.4735, "lng": 55.9754},
        "Bahrain": {"lat": 26.0667, "lng": 50.5577},
        # Europe
        "Russia": {"lat": 61.524, "lng": 105.3188},
        "Ukraine": {"lat": 48.3794, "lng": 31.1656},
        "United Kingdom": {"lat": 55.3781, "lng": -3.436},
        "UK": {"lat": 55.3781, "lng": -3.436},
        "Germany": {"lat": 51.1657, "lng": 10.4515},
        "France": {"lat": 46.2276, "lng": 2.2137},
        "Italy": {"lat": 41.8719, "lng": 12.5674},
        "Poland": {"lat": 51.9194, "lng": 19.1451},
        "Spain": {"lat": 40.4637, "lng": -3.7492},
        "Netherlands": {"lat": 52.1326, "lng": 5.2913},
        "Belgium": {"lat": 50.5039, "lng": 4.4699},
        "Sweden": {"lat": 60.1282, "lng": 18.6435},
        "Norway": {"lat": 60.472, "lng": 8.4689},
        "Finland": {"lat": 61.9241, "lng": 25.7482},
        "Greece": {"lat": 39.0742, "lng": 21.8243},
        "Serbia": {"lat": 44.0165, "lng": 21.0059},
        "Hungary": {"lat": 47.1625, "lng": 19.5033},
        "Romania": {"lat": 45.9432, "lng": 24.9668},
        "Belarus": {"lat": 53.7098, "lng": 27.9534},
        # Americas
        "United States": {"lat": 37.0902, "lng": -95.7129},
        "USA": {"lat": 37.0902, "lng": -95.7129},
        "US": {"lat": 37.0902, "lng": -95.7129},
        "Canada": {"lat": 56.1304, "lng": -106.3468},
        "Mexico": {"lat": 23.6345, "lng": -102.5528},
        "Brazil": {"lat": -14.235, "lng": -51.9253},
        "Argentina": {"lat": -38.4161, "lng": -63.6167},
        "Colombia": {"lat": 4.5709, "lng": -74.2973},
        "Venezuela": {"lat": 6.4238, "lng": -66.5897},
        "Chile": {"lat": -35.6751, "lng": -71.543},
        "Peru": {"lat": -9.19, "lng": -75.0152},
        "Cuba": {"lat": 21.5218, "lng": -77.7812},
        # Africa
        "Egypt": {"lat": 26.8206, "lng": 30.8025},
        "South Africa": {"lat": -30.5595, "lng": 22.9375},
        "Nigeria": {"lat": 9.082, "lng": 8.6753},
        "Kenya": {"lat": -0.0236, "lng": 37.9062},
        "Ethiopia": {"lat": 9.145, "lng": 40.4897},
        "Sudan": {"lat": 12.8628, "lng": 30.2176},
        "Libya": {"lat": 26.3351, "lng": 17.2283},
        "Morocco": {"lat": 31.7917, "lng": -7.0926},
        "Algeria": {"lat": 28.0339, "lng": 1.6596},
        "Tunisia": {"lat": 33.8869, "lng": 9.5375},
        # Central Asia
        "Kazakhstan": {"lat": 48.0196, "lng": 66.9237},
        "Uzbekistan": {"lat": 41.3775, "lng": 64.5853},
        "Turkmenistan": {"lat": 38.9697, "lng": 59.5563},
        "Tajikistan": {"lat": 38.861, "lng": 71.2761},
        "Kyrgyzstan": {"lat": 41.2044, "lng": 74.7661},
        # Oceania
        "Australia": {"lat": -25.2744, "lng": 133.7751},
        "New Zealand": {"lat": -40.9006, "lng": 174.886},
    }

    # Get country stats with high relevance count
    results = db.query(
        Article.country,
        func.count(Article.id).label("total"),
        func.sum(
            func.cast(Article.relevance_level == RelevanceLevel.HIGH, Integer)
        ).label("high_count")
    ).filter(
        Article.country.isnot(None),
        Article.country != "",
        Article.is_processed == 1
    ).group_by(Article.country).order_by(
        desc(func.count(Article.id))
    ).limit(limit).all()

    hotspots = []
    for r in results:
        country_name = r.country.strip() if r.country else ""
        if not country_name:
            continue

        # Try to find coordinates
        coords = country_coords.get(country_name)
        if not coords:
            # Try partial match
            for key in country_coords:
                if key.lower() in country_name.lower() or country_name.lower() in key.lower():
                    coords = country_coords[key]
                    break

        if coords:
            intensity = min((r.high_count or 0) / 5, 1.0)  # Normalize intensity
            hotspots.append({
                "country": country_name,
                "lat": coords["lat"],
                "lng": coords["lng"],
                "total_articles": r.total,
                "high_relevance": r.high_count or 0,
                "intensity": round(intensity, 2)
            })

    return sorted(hotspots, key=lambda x: x["total_articles"], reverse=True)


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
