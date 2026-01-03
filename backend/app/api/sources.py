from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.source import Source, SourceType, SourceCategory
from app.models.article import Article
from app.models.user import User, UserRole
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.services.news_fetcher import seed_default_sources
from app.api.auth import decode_token

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Require admin role for this endpoint"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user


@router.get("/", response_model=List[SourceResponse])
async def get_sources(db: Session = Depends(get_db)):
    """Get all news sources"""
    sources = db.query(Source).order_by(Source.name).all()

    responses = []
    for source in sources:
        article_count = db.query(Article).filter(
            Article.source_id == source.id
        ).count()

        responses.append(SourceResponse(
            id=source.id,
            name=source.name,
            url=source.url,
            feed_url=source.feed_url,
            source_type=source.source_type,
            category=source.category,
            country=source.country,
            language=source.language,
            description=source.description,
            reliability_score=source.reliability_score,
            bias_rating=source.bias_rating,
            is_active=source.is_active,
            fetch_interval_minutes=source.fetch_interval_minutes,
            last_fetched_at=source.last_fetched_at,
            last_fetch_status=source.last_fetch_status,
            article_count=article_count,
            created_at=source.created_at,
            updated_at=source.updated_at
        ))

    return responses


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get a single source by ID"""
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    article_count = db.query(Article).filter(
        Article.source_id == source.id
    ).count()

    return SourceResponse(
        id=source.id,
        name=source.name,
        url=source.url,
        feed_url=source.feed_url,
        source_type=source.source_type,
        category=source.category,
        country=source.country,
        language=source.language,
        description=source.description,
        reliability_score=source.reliability_score,
        bias_rating=source.bias_rating,
        is_active=source.is_active,
        fetch_interval_minutes=source.fetch_interval_minutes,
        last_fetched_at=source.last_fetched_at,
        last_fetch_status=source.last_fetch_status,
        article_count=article_count,
        created_at=source.created_at,
        updated_at=source.updated_at
    )


@router.post("/", response_model=SourceResponse)
async def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new news source (Admin only)"""
    # Check if source already exists
    existing = db.query(Source).filter(Source.name == source_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source with this name already exists")

    source = Source(
        name=source_data.name,
        url=source_data.url,
        feed_url=source_data.feed_url,
        source_type=SourceType(source_data.source_type),
        category=SourceCategory(source_data.category),
        country=source_data.country,
        language=source_data.language,
        description=source_data.description,
        reliability_score=source_data.reliability_score,
        bias_rating=source_data.bias_rating,
        is_active=source_data.is_active,
        fetch_interval_minutes=source_data.fetch_interval_minutes
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return SourceResponse(
        id=source.id,
        name=source.name,
        url=source.url,
        feed_url=source.feed_url,
        source_type=source.source_type,
        category=source.category,
        country=source.country,
        language=source.language,
        description=source.description,
        reliability_score=source.reliability_score,
        bias_rating=source.bias_rating,
        is_active=source.is_active,
        fetch_interval_minutes=source.fetch_interval_minutes,
        last_fetched_at=source.last_fetched_at,
        last_fetch_status=source.last_fetch_status,
        article_count=0,
        created_at=source.created_at,
        updated_at=source.updated_at
    )


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a news source (Admin only)"""
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Update fields that are provided
    update_data = source_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "source_type":
                value = SourceType(value)
            elif field == "category":
                value = SourceCategory(value)
            setattr(source, field, value)

    db.commit()
    db.refresh(source)

    article_count = db.query(Article).filter(
        Article.source_id == source.id
    ).count()

    return SourceResponse(
        id=source.id,
        name=source.name,
        url=source.url,
        feed_url=source.feed_url,
        source_type=source.source_type,
        category=source.category,
        country=source.country,
        language=source.language,
        description=source.description,
        reliability_score=source.reliability_score,
        bias_rating=source.bias_rating,
        is_active=source.is_active,
        fetch_interval_minutes=source.fetch_interval_minutes,
        last_fetched_at=source.last_fetched_at,
        last_fetch_status=source.last_fetch_status,
        article_count=article_count,
        created_at=source.created_at,
        updated_at=source.updated_at
    )


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a news source (Admin only)"""
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(source)
    db.commit()

    return {"message": "Source deleted successfully"}


@router.post("/seed-defaults")
async def seed_defaults(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Seed database with default news sources (Admin only)"""
    seed_default_sources(db)
    return {"message": "Default sources seeded successfully"}


@router.post("/{source_id}/toggle")
async def toggle_source(
    source_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Toggle source active status (Admin only)"""
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.is_active = not source.is_active
    db.commit()

    return {"is_active": source.is_active}


@router.post("/seed-additional")
async def seed_additional_sources(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Add additional curated news sources (Admin only)"""
    from app.services.additional_sources import seed_additional_sources as seed_func
    count = seed_func(db)
    return {"message": f"Added {count} additional sources"}


@router.post("/fetch-all")
async def fetch_all_news(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Trigger immediate fetch from all RSS sources (Admin only)"""
    from app.tasks.fetch_news import fetch_all_news as fetch_task
    # Trigger the Celery task
    task = fetch_task.delay()
    return {"message": "Fetch task started", "task_id": str(task.id)}


@router.post("/fetch-rss-sync")
async def fetch_rss_sync(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Fetch from all RSS sources synchronously (Admin only)"""
    from app.services.news_fetcher import NewsFetcher, seed_default_sources
    from app.models.source import Source

    # Ensure default sources exist
    source_count = db.query(Source).count()
    if source_count == 0:
        seed_default_sources(db)

    fetcher = NewsFetcher(db)
    results = fetcher.fetch_all_sources()
    total = sum(results.values())
    return {"message": f"Fetched {total} articles", "by_source": results}


@router.post("/fetch-gdelt")
async def fetch_gdelt_news(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Fetch news from GDELT (Admin only)"""
    from app.services.news_api_fetcher import GDELTFetcher
    fetcher = GDELTFetcher()
    count = fetcher.fetch_strategic_news(db)
    return {"message": f"Fetched {count} articles from GDELT"}


@router.post("/fetch-newsapi")
async def fetch_newsapi_news(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Fetch news from NewsAPI.org (Admin only)"""
    from app.services.news_api_fetcher import NewsAPIFetcher
    from app.config import settings

    if not settings.newsapi_key:
        raise HTTPException(status_code=400, detail="NewsAPI key not configured")

    fetcher = NewsAPIFetcher(settings.newsapi_key)
    count = fetcher.fetch_strategic_news(db)
    return {"message": f"Fetched {count} articles from NewsAPI"}


@router.post("/fetch-twitter")
async def fetch_twitter_news(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Fetch news from Twitter/X (Admin only)"""
    from app.services.twitter_fetcher import TwitterFetcher
    from app.config import settings

    if not settings.twitter_bearer_token:
        raise HTTPException(status_code=400, detail="Twitter bearer token not configured")

    fetcher = TwitterFetcher(settings.twitter_bearer_token)
    results = fetcher.fetch_strategic_tweets(db)
    total = sum(results.values())
    return {"message": f"Fetched {total} tweets", "by_account": results}


@router.post("/cleanup-irrelevant")
async def cleanup_irrelevant_articles(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Remove irrelevant articles (Admin only)"""
    from app.services.relevance_filter import is_relevant_article

    articles = db.query(Article).all()
    deleted_count = 0
    kept_count = 0

    for article in articles:
        is_relevant, reason = is_relevant_article(article.title, article.original_content)
        if not is_relevant:
            db.delete(article)
            deleted_count += 1
        else:
            kept_count += 1

    db.commit()
    return {
        "message": f"Cleanup complete",
        "deleted": deleted_count,
        "kept": kept_count
    }


@router.post("/cleanup-duplicates")
async def cleanup_duplicate_articles(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Remove duplicate articles (Admin only)"""
    from app.services.news_fetcher import titles_are_similar

    articles = db.query(Article).order_by(Article.created_at.asc()).all()
    seen_titles = []
    deleted_count = 0
    kept_count = 0

    for article in articles:
        is_duplicate = False
        for seen_title in seen_titles:
            if titles_are_similar(article.title, seen_title):
                is_duplicate = True
                break

        if is_duplicate:
            db.delete(article)
            deleted_count += 1
        else:
            seen_titles.append(article.title)
            kept_count += 1

    db.commit()
    return {
        "message": f"Duplicate cleanup complete",
        "deleted": deleted_count,
        "kept": kept_count
    }


@router.post("/reprocess-scores")
async def reprocess_article_scores(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Recalculate relevance scores (Admin only)"""
    from app.services.relevance_scorer import get_relevance_scorer
    from app.models.article import RelevanceLevel

    scorer = get_relevance_scorer()
    articles = db.query(Article).all()
    updated_count = 0

    for article in articles:
        # Recalculate scores
        scores = scorer.calculate_scores(
            article.title,
            article.original_content or ""
        )

        article.geo_score = scores["geo_score"]
        article.military_score = scores["military_score"]
        article.diplomatic_score = scores["diplomatic_score"]
        article.economic_score = scores["economic_score"]
        article.relevance_score = scores["relevance_score"]
        article.relevance_level = RelevanceLevel(scores["relevance_level"])

        # Update region/theme if empty
        if not article.region or not article.theme:
            classification = scorer.extract_region_theme(
                article.title,
                article.original_content or ""
            )
            if not article.region:
                article.region = classification.get("region")
            if not article.country:
                article.country = classification.get("country")
            if not article.theme:
                article.theme = classification.get("theme")
            if not article.domain:
                article.domain = classification.get("domain")

        updated_count += 1

    db.commit()
    return {
        "message": f"Reprocessed {updated_count} articles with keyword scoring"
    }


@router.post("/reprocess-llm")
async def reprocess_with_llm(
    db: Session = Depends(get_db),
    limit: int = 50,
    admin: User = Depends(require_admin)
):
    """Reprocess articles using LLM scoring (Admin only)"""
    from app.services.llm_scorer import get_llm_scorer
    from app.services.relevance_scorer import get_relevance_scorer
    from app.models.article import RelevanceLevel
    from app.config import settings

    if not settings.groq_api_key:
        raise HTTPException(status_code=400, detail="Groq API key not configured")

    llm_scorer = get_llm_scorer()
    keyword_scorer = get_relevance_scorer()

    # Get articles to reprocess (prioritize unprocessed or low-scored)
    articles = db.query(Article).order_by(
        Article.relevance_score.asc()
    ).limit(limit).all()

    updated_count = 0
    high_count = 0
    errors = []

    for article in articles:
        try:
            content = article.original_content or ""

            # Use LLM for scoring
            result = llm_scorer.score_article(article.title, content)

            article.relevance_score = result["relevance_score"]
            article.relevance_level = RelevanceLevel(result["relevance_level"])

            # Update classification
            classification = result.get("classification", {})
            article.region = classification.get("region", article.region)
            article.country = classification.get("country", article.country)
            article.theme = classification.get("theme", article.theme)
            article.domain = classification.get("domain", article.domain)

            # Update keyword scores for display
            keyword_scores = keyword_scorer.calculate_scores(article.title, content)
            article.geo_score = keyword_scores["geo_score"]
            article.military_score = keyword_scores["military_score"]
            article.diplomatic_score = keyword_scores["diplomatic_score"]
            article.economic_score = keyword_scores["economic_score"]

            if result["relevance_level"] == "high":
                high_count += 1

            updated_count += 1

        except Exception as e:
            errors.append(f"Article {article.id}: {str(e)[:100]}")
            continue

    db.commit()

    return {
        "message": f"LLM reprocessed {updated_count} articles",
        "high_relevance": high_count,
        "errors": len(errors),
        "error_details": errors[:5] if errors else []
    }
