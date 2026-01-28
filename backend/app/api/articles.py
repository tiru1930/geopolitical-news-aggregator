from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.article import Article, RelevanceLevel
from app.models.source import Source
from app.schemas.article import ArticleResponse, ArticleListResponse

router = APIRouter()


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    region: Optional[str] = None,
    country: Optional[str] = None,
    theme: Optional[str] = None,
    domain: Optional[str] = None,
    relevance_level: Optional[str] = None,
    source_id: Optional[int] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    processed_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of articles with optional filters.
    """
    query = db.query(Article)

    # Apply filters
    if processed_only:
        query = query.filter(Article.is_processed == 1)

    if region:
        query = query.filter(Article.region == region)

    if country:
        query = query.filter(Article.country == country)

    if theme:
        query = query.filter(Article.theme == theme)

    if domain:
        query = query.filter(Article.domain == domain)

    if relevance_level:
        query = query.filter(Article.relevance_level == relevance_level)

    if source_id:
        query = query.filter(Article.source_id == source_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.original_content.ilike(search_term)
            )
        )

    if start_date:
        query = query.filter(Article.published_at >= start_date)

    if end_date:
        query = query.filter(Article.published_at <= end_date)

    # Get total count
    total = query.count()

    # Apply pagination and ordering - Priority articles (India & neighbors) first
    articles = query.order_by(
        desc(Article.is_priority),  # Priority articles first
        desc(Article.relevance_score),
        desc(Article.published_at)
    ).offset((page - 1) * page_size).limit(page_size).all()

    # Build response with source names
    article_responses = []
    for article in articles:
        source = db.query(Source).filter(Source.id == article.source_id).first()
        response = ArticleResponse(
            id=article.id,
            title=article.title,
            url=article.url,
            original_content=article.original_content[:500] if article.original_content else None,
            published_at=article.published_at,
            author=article.author,
            image_url=article.image_url,
            source_id=article.source_id,
            source_name=source.name if source else None,
            summary_bullets=article.summary_bullets,
            summary_what_happened=article.summary_what_happened,
            summary_why_matters=article.summary_why_matters,
            summary_india_implications=article.summary_india_implications,
            summary_future_developments=article.summary_future_developments,
            relevance_level=article.relevance_level or RelevanceLevel.LOW,
            relevance_score=article.relevance_score or 0.0,
            geo_score=article.geo_score or 0.0,
            military_score=article.military_score or 0.0,
            diplomatic_score=article.diplomatic_score or 0.0,
            economic_score=article.economic_score or 0.0,
            is_priority=article.is_priority or False,
            region=article.region,
            country=article.country,
            theme=article.theme,
            domain=article.domain,
            entities=article.entities or [],
            is_processed=article.is_processed,
            created_at=article.created_at,
            updated_at=article.updated_at
        )
        article_responses.append(response)

    total_pages = (total + page_size - 1) // page_size

    return ArticleListResponse(
        articles=article_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/high-relevance", response_model=List[ArticleResponse])
async def get_high_relevance_articles(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get top high-relevance articles - India & neighbors prioritized"""
    articles = db.query(Article).filter(
        Article.is_processed == 1,
        Article.relevance_level == RelevanceLevel.HIGH
    ).order_by(
        desc(Article.is_priority),  # Priority articles first
        desc(Article.relevance_score),
        desc(Article.published_at)
    ).limit(limit).all()

    responses = []
    for article in articles:
        source = db.query(Source).filter(Source.id == article.source_id).first()
        responses.append(ArticleResponse(
            id=article.id,
            title=article.title,
            url=article.url,
            original_content=article.original_content[:500] if article.original_content else None,
            published_at=article.published_at,
            author=article.author,
            image_url=article.image_url,
            source_id=article.source_id,
            source_name=source.name if source else None,
            summary_bullets=article.summary_bullets,
            summary_what_happened=article.summary_what_happened,
            summary_why_matters=article.summary_why_matters,
            summary_india_implications=article.summary_india_implications,
            summary_future_developments=article.summary_future_developments,
            relevance_level=article.relevance_level or RelevanceLevel.LOW,
            relevance_score=article.relevance_score or 0.0,
            geo_score=article.geo_score or 0.0,
            military_score=article.military_score or 0.0,
            diplomatic_score=article.diplomatic_score or 0.0,
            economic_score=article.economic_score or 0.0,
            is_priority=article.is_priority or False,
            region=article.region,
            country=article.country,
            theme=article.theme,
            domain=article.domain,
            entities=article.entities or [],
            is_processed=article.is_processed,
            created_at=article.created_at,
            updated_at=article.updated_at
        ))

    return responses


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a single article by ID"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    source = db.query(Source).filter(Source.id == article.source_id).first()

    return ArticleResponse(
        id=article.id,
        title=article.title,
        url=article.url,
        original_content=article.original_content,
        published_at=article.published_at,
        author=article.author,
        image_url=article.image_url,
        source_id=article.source_id,
        source_name=source.name if source else None,
        summary_bullets=article.summary_bullets,
        summary_what_happened=article.summary_what_happened,
        summary_why_matters=article.summary_why_matters,
        summary_india_implications=article.summary_india_implications,
        summary_future_developments=article.summary_future_developments,
        relevance_level=article.relevance_level or RelevanceLevel.LOW,
        relevance_score=article.relevance_score or 0.0,
        geo_score=article.geo_score or 0.0,
        military_score=article.military_score or 0.0,
        diplomatic_score=article.diplomatic_score or 0.0,
        economic_score=article.economic_score or 0.0,
        is_priority=article.is_priority or False,
        region=article.region,
        country=article.country,
        theme=article.theme,
        domain=article.domain,
        entities=article.entities or [],
        is_processed=article.is_processed,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


@router.get("/regions/list")
async def get_regions(db: Session = Depends(get_db)):
    """Get list of all regions with article counts"""
    results = db.query(
        Article.region,
        db.query(Article).filter(Article.region == Article.region).count()
    ).filter(
        Article.region.isnot(None),
        Article.is_processed == 1
    ).group_by(Article.region).all()

    return [{"region": r[0], "count": r[1]} for r in results if r[0]]


@router.get("/themes/list")
async def get_themes(db: Session = Depends(get_db)):
    """Get list of all themes with article counts"""
    results = db.query(
        Article.theme,
        db.query(Article).filter(Article.theme == Article.theme).count()
    ).filter(
        Article.theme.isnot(None),
        Article.is_processed == 1
    ).group_by(Article.theme).all()

    return [{"theme": t[0], "count": t[1]} for t in results if t[0]]


@router.post("/reprocess-all")
async def reprocess_all_articles(db: Session = Depends(get_db)):
    """
    Mark all articles for reprocessing.
    They will be reprocessed by the background worker.
    """
    try:
        # Reset is_processed to 0 for all articles
        count = db.query(Article).filter(Article.is_processed == 1).update({
            Article.is_processed: 0
        })
        db.commit()
        return {
            "status": "success",
            "message": f"Marked {count} articles for reprocessing",
            "articles_queued": count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/reprocess-without-summary")
async def reprocess_articles_without_summary(db: Session = Depends(get_db)):
    """
    Reprocess only articles that don't have bullet summaries yet.
    """
    try:
        # Find articles without bullet summary
        count = db.query(Article).filter(
            Article.is_processed == 1,
            (Article.summary_bullets.is_(None)) | (Article.summary_bullets == "")
        ).update({
            Article.is_processed: 0
        })
        db.commit()
        return {
            "status": "success",
            "message": f"Marked {count} articles for reprocessing",
            "articles_queued": count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
