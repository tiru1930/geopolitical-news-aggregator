import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from sqlalchemy.orm import Session

from app.models.source import Source, SourceType
from app.models.article import Article
from app.services.relevance_filter import is_relevant_article

logger = logging.getLogger(__name__)


def normalize_title(title: str) -> str:
    """Normalize title for comparison - lowercase, remove punctuation, extra spaces"""
    if not title:
        return ""
    # Lowercase
    title = title.lower()
    # Remove common prefixes like "Breaking:", "UPDATE:", etc.
    title = re.sub(r'^(breaking|update|exclusive|just in|watch|video)[:|\-]?\s*', '', title)
    # Remove punctuation
    title = re.sub(r'[^\w\s]', '', title)
    # Remove extra spaces
    title = ' '.join(title.split())
    return title


def titles_are_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
    """Check if two titles are similar using simple word overlap"""
    norm1 = normalize_title(title1)
    norm2 = normalize_title(title2)

    if norm1 == norm2:
        return True

    # Simple word overlap ratio
    words1 = set(norm1.split())
    words2 = set(norm2.split())

    if not words1 or not words2:
        return False

    intersection = words1 & words2
    union = words1 | words2

    similarity = len(intersection) / len(union) if union else 0
    return similarity >= threshold


class NewsFetcher:
    """
    Fetches news from various sources (RSS feeds, APIs, web scraping).
    """

    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch_rss_feed(self, source: Source) -> List[Dict[str, Any]]:
        """Fetch articles from an RSS feed"""
        articles = []

        try:
            feed = feedparser.parse(source.feed_url)

            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS parse warning for {source.name}: {feed.bozo_exception}")

            for entry in feed.entries[:50]:  # Limit per fetch
                # Parse publication date
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_at = datetime(*entry.updated_parsed[:6])
                elif hasattr(entry, 'published'):
                    try:
                        published_at = date_parser.parse(entry.published)
                    except:
                        pass

                # Extract image URL if available
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0].get('url')
                elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get('url')

                # Get content
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].get('value', '')
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description

                # Clean HTML from content
                if content:
                    soup = BeautifulSoup(content, 'lxml')
                    content = soup.get_text(separator=' ', strip=True)

                articles.append({
                    "title": entry.get('title', '').strip(),
                    "url": entry.get('link', ''),
                    "original_content": content[:10000],  # Limit content size
                    "published_at": published_at,
                    "author": entry.get('author', ''),
                    "image_url": image_url,
                    "source_id": source.id
                })

            logger.info(f"Fetched {len(articles)} articles from {source.name}")

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source.name}: {e}")

        return articles

    def fetch_webpage_content(self, url: str) -> Optional[str]:
        """Fetch and extract main content from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()

            # Try to find main content
            main_content = None

            # Common article containers
            for selector in ['article', '.article-body', '.story-body', '.post-content',
                             '.entry-content', 'main', '.content']:
                content = soup.select_one(selector)
                if content:
                    main_content = content.get_text(separator=' ', strip=True)
                    break

            if not main_content:
                # Fallback to body
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator=' ', strip=True)

            return main_content[:10000] if main_content else None

        except Exception as e:
            logger.error(f"Error fetching webpage {url}: {e}")
            return None

    def fetch_from_source(self, source: Source) -> List[Dict[str, Any]]:
        """Fetch articles from a source based on its type"""
        if source.source_type == SourceType.RSS:
            return self.fetch_rss_feed(source)
        elif source.source_type == SourceType.SCRAPE:
            # For scraping, we'd need source-specific logic
            logger.warning(f"Scraping not implemented for {source.name}")
            return []
        elif source.source_type == SourceType.API:
            # API sources need specific implementations
            logger.warning(f"API fetching not implemented for {source.name}")
            return []

        return []

    def save_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Save fetched articles to database, filtering for relevance and skipping duplicates"""
        saved_count = 0
        filtered_count = 0
        duplicate_count = 0

        # Get recent articles for title-based deduplication (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_articles = self.db.query(Article).filter(
            Article.created_at >= recent_cutoff
        ).all()
        recent_titles = [a.title for a in recent_articles]

        for article_data in articles:
            # FILTER: Check if article is relevant to defence/security topics
            title = article_data.get("title", "")
            content = article_data.get("original_content", "")
            is_relevant, reason = is_relevant_article(title, content)

            if not is_relevant:
                filtered_count += 1
                continue

            # Check if article already exists (by URL)
            existing = self.db.query(Article).filter(
                Article.url == article_data["url"]
            ).first()

            if existing:
                duplicate_count += 1
                continue

            # Check for similar title in recent articles
            is_duplicate = False
            for recent_title in recent_titles:
                if titles_are_similar(title, recent_title):
                    is_duplicate = True
                    duplicate_count += 1
                    logger.debug(f"Title duplicate detected: '{title}' similar to '{recent_title}'")
                    break

            if is_duplicate:
                continue

            # Create new article
            article = Article(
                title=article_data["title"],
                url=article_data["url"],
                original_content=article_data.get("original_content"),
                published_at=article_data.get("published_at"),
                author=article_data.get("author"),
                image_url=article_data.get("image_url"),
                source_id=article_data["source_id"],
                is_processed=0
            )

            self.db.add(article)
            recent_titles.append(title)  # Add to recent titles for this batch
            saved_count += 1

        if saved_count > 0:
            self.db.commit()

        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} non-relevant articles")
        if duplicate_count > 0:
            logger.info(f"Skipped {duplicate_count} duplicate articles")

        return saved_count

    def fetch_all_sources(self) -> Dict[str, int]:
        """Fetch from all active sources"""
        results = {}

        sources = self.db.query(Source).filter(Source.is_active == True).all()

        for source in sources:
            try:
                articles = self.fetch_from_source(source)
                saved = self.save_articles(articles)

                # Update source fetch status
                source.last_fetched_at = datetime.utcnow()
                source.last_fetch_status = "success"
                self.db.commit()

                results[source.name] = saved
                logger.info(f"Saved {saved} new articles from {source.name}")

            except Exception as e:
                source.last_fetch_status = f"failed: {str(e)[:100]}"
                self.db.commit()
                results[source.name] = 0
                logger.error(f"Failed to fetch from {source.name}: {e}")

        return results


# Default news sources to seed the database
DEFAULT_SOURCES = [
    {
        "name": "Reuters World News",
        "url": "https://www.reuters.com",
        "feed_url": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best",
        "source_type": "rss",
        "category": "news_agency",
        "country": "International",
        "reliability_score": 9
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com",
        "feed_url": "https://www.aljazeera.com/xml/rss/all.xml",
        "source_type": "rss",
        "category": "news_agency",
        "country": "Qatar",
        "reliability_score": 7
    },
    {
        "name": "The Diplomat",
        "url": "https://thediplomat.com",
        "feed_url": "https://thediplomat.com/feed/",
        "source_type": "rss",
        "category": "think_tank",
        "country": "USA",
        "reliability_score": 8
    },
    {
        "name": "Defense News",
        "url": "https://www.defensenews.com",
        "feed_url": "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml",
        "source_type": "rss",
        "category": "military",
        "country": "USA",
        "reliability_score": 8
    },
    {
        "name": "CSIS",
        "url": "https://www.csis.org",
        "feed_url": "https://www.csis.org/analysis/feed",
        "source_type": "rss",
        "category": "think_tank",
        "country": "USA",
        "reliability_score": 9
    },
    {
        "name": "The Hindu - International",
        "url": "https://www.thehindu.com",
        "feed_url": "https://www.thehindu.com/news/international/feeder/default.rss",
        "source_type": "rss",
        "category": "news_agency",
        "country": "India",
        "reliability_score": 8
    },
    {
        "name": "Times of India - Defence",
        "url": "https://timesofindia.indiatimes.com",
        "feed_url": "https://timesofindia.indiatimes.com/rssfeeds/4719161.cms",
        "source_type": "rss",
        "category": "news_agency",
        "country": "India",
        "reliability_score": 7
    },
    {
        "name": "South China Morning Post",
        "url": "https://www.scmp.com",
        "feed_url": "https://www.scmp.com/rss/91/feed",
        "source_type": "rss",
        "category": "news_agency",
        "country": "Hong Kong",
        "reliability_score": 7
    }
]


def seed_default_sources(db: Session):
    """Seed database with default news sources"""
    from app.models.source import Source, SourceType, SourceCategory

    for source_data in DEFAULT_SOURCES:
        existing = db.query(Source).filter(Source.name == source_data["name"]).first()
        if not existing:
            source = Source(
                name=source_data["name"],
                url=source_data["url"],
                feed_url=source_data["feed_url"],
                source_type=SourceType(source_data["source_type"]),
                category=SourceCategory(source_data["category"]),
                country=source_data["country"],
                reliability_score=source_data["reliability_score"],
                is_active=True
            )
            db.add(source)

    db.commit()
    logger.info("Default sources seeded")
