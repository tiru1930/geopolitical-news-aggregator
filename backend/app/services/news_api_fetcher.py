"""
External News API Integrations

Supports:
1. NewsAPI.org - General news (free tier: 100 requests/day)
2. GDELT - Global events database (free, unlimited)
3. Mediastack - News API (free tier: 500 requests/month)
4. TheNewsAPI - News aggregator (free tier available)

Get API keys:
- NewsAPI: https://newsapi.org/
- Mediastack: https://mediastack.com/
- TheNewsAPI: https://www.thenewsapi.com/
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.source import Source, SourceType, SourceCategory
from app.services.relevance_filter import is_relevant_article
from app.services.news_fetcher import titles_are_similar

logger = logging.getLogger(__name__)


class NewsAPIFetcher:
    """
    Fetch from NewsAPI.org
    Free tier: 100 requests/day, 1 month old articles
    """

    BASE_URL = "https://newsapi.org/v2"

    # Strategic keywords for geopolitical news
    KEYWORDS = [
        "India defence",
        "China military",
        "Indo-Pacific security",
        "Pakistan terrorism",
        "South China Sea",
        "Taiwan strait",
        "QUAD summit",
        "India China border",
        "nuclear weapons",
        "missile test",
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_everything(
        self,
        query: str,
        from_date: datetime = None,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch articles matching query"""
        if not from_date:
            from_date = datetime.utcnow() - timedelta(days=7)

        params = {
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "sortBy": "relevancy",
            "pageSize": page_size,
            "language": "en",
            "apiKey": self.api_key
        }

        try:
            with httpx.Client() as client:
                response = client.get(f"{self.BASE_URL}/everything", params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "ok":
                    return data.get("articles", [])
                return []
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []

    def fetch_strategic_news(self, db: Session) -> int:
        """Fetch news for all strategic keywords"""
        saved_count = 0

        # Get or create NewsAPI source
        source = db.query(Source).filter(Source.name == "NewsAPI").first()
        if not source:
            source = Source(
                name="NewsAPI",
                url="https://newsapi.org",
                source_type=SourceType.API,
                category=SourceCategory.NEWS_AGENCY,
                is_active=True
            )
            db.add(source)
            db.commit()

        for keyword in self.KEYWORDS:
            articles = self.fetch_everything(keyword, page_size=10)

            for article_data in articles:
                url = article_data.get("url")
                if not url:
                    continue

                # Check if exists
                existing = db.query(Article).filter(Article.url == url).first()
                if existing:
                    continue

                # Parse date
                published_at = None
                if article_data.get("publishedAt"):
                    try:
                        published_at = datetime.fromisoformat(
                            article_data["publishedAt"].replace("Z", "+00:00")
                        )
                    except:
                        pass

                article = Article(
                    title=article_data.get("title", "")[:500],
                    url=url,
                    original_content=article_data.get("content") or article_data.get("description"),
                    published_at=published_at,
                    author=article_data.get("author"),
                    image_url=article_data.get("urlToImage"),
                    source_id=source.id,
                    is_processed=0
                )
                db.add(article)
                saved_count += 1

        db.commit()
        return saved_count


class GDELTFetcher:
    """
    Fetch from GDELT Project - Global Database of Events, Language, and Tone
    FREE and unlimited! Best for comprehensive global news coverage.

    Documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    # GDELT themes for strategic news
    THEMES = [
        "MILITARY",
        "TERROR",
        "WMD",
        "ARMEDCONFLICT",
        "DIPLOMACY",
        "DEFENSE",
        "INSURGENCY",
    ]

    # Countries of interest
    COUNTRIES = [
        "India", "China", "Pakistan", "Russia", "United States",
        "Japan", "Australia", "Taiwan", "North Korea", "Iran"
    ]

    def fetch_articles(
        self,
        query: str = None,
        theme: str = None,
        country: str = None,
        timespan: str = "24h",
        max_records: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from GDELT

        Args:
            query: Search query
            theme: GDELT theme (MILITARY, TERROR, etc.)
            country: Country name
            timespan: 24h, 7d, 30d, etc.
            max_records: Max articles to return
        """
        params = {
            "format": "json",
            "timespan": timespan,
            "maxrecords": max_records,
            "sort": "DateDesc"
        }

        # Build query
        query_parts = []
        if query:
            query_parts.append(query)
        if theme:
            query_parts.append(f"theme:{theme}")
        if country:
            query_parts.append(f'sourcecountry:"{country}"')

        if query_parts:
            params["query"] = " ".join(query_parts)

        try:
            with httpx.Client() as client:
                response = client.get(self.BASE_URL, params=params, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return data.get("articles", [])
        except Exception as e:
            logger.error(f"GDELT error: {e}")
            return []

    def fetch_strategic_news(self, db: Session) -> int:
        """Fetch strategic news from GDELT"""
        saved_count = 0

        # Get or create GDELT source
        source = db.query(Source).filter(Source.name == "GDELT").first()
        if not source:
            source = Source(
                name="GDELT",
                url="https://www.gdeltproject.org",
                source_type=SourceType.API,
                category=SourceCategory.NEWS_AGENCY,
                description="Global Database of Events, Language, and Tone",
                reliability_score=7,
                is_active=True
            )
            db.add(source)
            db.commit()

        # Get recent articles for title-based deduplication (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_articles = db.query(Article).filter(
            Article.created_at >= recent_cutoff
        ).all()
        recent_titles = [a.title for a in recent_articles]

        # Collect all articles first to deduplicate
        all_articles = {}  # url -> article_data

        # Fetch for each theme
        for theme in self.THEMES:
            articles = self.fetch_articles(theme=theme, timespan="24h", max_records=20)
            for article_data in articles:
                url = article_data.get("url")
                if url and url not in all_articles:
                    all_articles[url] = article_data

        # Now save unique articles (with relevance filtering)
        filtered_count = 0
        duplicate_count = 0
        for url, article_data in all_articles.items():
            title = article_data.get("title", "")

            # FILTER: Check relevance before saving
            is_relevant, reason = is_relevant_article(title, "")
            if not is_relevant:
                filtered_count += 1
                continue

            # Check if exists in DB (by URL)
            existing = db.query(Article).filter(Article.url == url).first()
            if existing:
                duplicate_count += 1
                continue

            # Check for similar title in recent articles
            is_duplicate = False
            for recent_title in recent_titles:
                if titles_are_similar(title, recent_title):
                    is_duplicate = True
                    duplicate_count += 1
                    break

            if is_duplicate:
                continue

            # Parse date
            published_at = None
            if article_data.get("seendate"):
                try:
                    date_str = article_data["seendate"]
                    published_at = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
                except:
                    pass

            article = Article(
                title=title[:500],
                url=url,
                original_content=title,  # GDELT doesn't provide content
                published_at=published_at,
                image_url=article_data.get("socialimage"),
                source_id=source.id,
                is_processed=0
            )
            db.add(article)
            recent_titles.append(title)  # Add to recent titles for this batch
            saved_count += 1

        db.commit()
        if filtered_count > 0:
            logger.info(f"GDELT: Filtered out {filtered_count} non-relevant articles")
        if duplicate_count > 0:
            logger.info(f"GDELT: Skipped {duplicate_count} duplicate articles")
        return saved_count

    def fetch_india_related(self, db: Session) -> int:
        """Fetch India-specific strategic news"""
        queries = [
            "India China border",
            "India Pakistan",
            "Indian military",
            "Indian Navy",
            "LAC standoff",
            "India defence deal",
        ]

        saved_count = 0
        source = db.query(Source).filter(Source.name == "GDELT").first()

        for query in queries:
            articles = self.fetch_articles(query=query, timespan="24h", max_records=10)

            for article_data in articles:
                url = article_data.get("url")
                if not url:
                    continue

                existing = db.query(Article).filter(Article.url == url).first()
                if existing:
                    continue

                published_at = None
                if article_data.get("seendate"):
                    try:
                        published_at = datetime.strptime(
                            article_data["seendate"][:14], "%Y%m%d%H%M%S"
                        )
                    except:
                        pass

                article = Article(
                    title=article_data.get("title", "")[:500],
                    url=url,
                    original_content=article_data.get("title"),
                    published_at=published_at,
                    source_id=source.id if source else 1,
                    is_processed=0
                )
                db.add(article)
                saved_count += 1

        db.commit()
        return saved_count


class MediastackFetcher:
    """
    Fetch from Mediastack API
    Free tier: 500 requests/month
    """

    BASE_URL = "http://api.mediastack.com/v1/news"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_news(
        self,
        keywords: str = None,
        countries: str = "in,us,gb,cn",
        categories: str = "general,politics",
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Fetch news articles"""
        params = {
            "access_key": self.api_key,
            "countries": countries,
            "categories": categories,
            "limit": limit,
            "languages": "en",
            "sort": "published_desc"
        }

        if keywords:
            params["keywords"] = keywords

        try:
            with httpx.Client() as client:
                response = client.get(self.BASE_URL, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Mediastack error: {e}")
            return []
