import logging
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.news_fetcher import NewsFetcher, seed_default_sources
from app.models.source import Source

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.fetch_news.fetch_all_news")
def fetch_all_news(self):
    """
    Fetch news from all active sources.
    Scheduled to run every 30 minutes.
    """
    db = SessionLocal()
    try:
        # Ensure default sources exist
        source_count = db.query(Source).count()
        if source_count == 0:
            logger.info("No sources found, seeding defaults...")
            seed_default_sources(db)

        # Fetch from all sources
        fetcher = NewsFetcher(db)
        results = fetcher.fetch_all_sources()

        total_fetched = sum(results.values())
        logger.info(f"Fetch complete. Total new articles: {total_fetched}")

        return {
            "status": "success",
            "total_new_articles": total_fetched,
            "by_source": results
        }

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.fetch_news.fetch_from_source")
def fetch_from_source(self, source_id: int):
    """
    Fetch news from a specific source.
    """
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()

        if not source:
            return {"status": "error", "error": "Source not found"}

        fetcher = NewsFetcher(db)
        articles = fetcher.fetch_from_source(source)
        saved = fetcher.save_articles(articles)

        logger.info(f"Fetched {saved} articles from {source.name}")

        return {
            "status": "success",
            "source": source.name,
            "articles_saved": saved
        }

    except Exception as e:
        logger.error(f"Error fetching from source {source_id}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.fetch_news.test_source_feed")
def test_source_feed(feed_url: str):
    """
    Test if an RSS feed URL is valid and working.
    """
    import feedparser

    try:
        feed = feedparser.parse(feed_url)

        if feed.bozo and feed.bozo_exception:
            return {
                "status": "warning",
                "message": f"Feed parsed with warning: {feed.bozo_exception}",
                "entries_count": len(feed.entries)
            }

        return {
            "status": "success",
            "title": feed.feed.get("title", "Unknown"),
            "entries_count": len(feed.entries),
            "sample_entry": feed.entries[0].get("title") if feed.entries else None
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(bind=True, name="app.tasks.fetch_news.fetch_gdelt_news")
def fetch_gdelt_news(self):
    """
    Fetch news from GDELT (free, unlimited).
    Scheduled to run every 2 hours.
    """
    db = SessionLocal()
    try:
        from app.services.news_api_fetcher import GDELTFetcher
        fetcher = GDELTFetcher()
        count = fetcher.fetch_strategic_news(db)
        logger.info(f"GDELT fetch complete. New articles: {count}")
        return {"status": "success", "articles_fetched": count}
    except Exception as e:
        logger.error(f"Error fetching from GDELT: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.fetch_news.fetch_twitter_news")
def fetch_twitter_news(self):
    """
    Fetch tweets from strategic Twitter accounts.
    Scheduled to run every hour (if configured).
    """
    from app.config import settings

    if not settings.twitter_bearer_token:
        logger.debug("Twitter not configured, skipping")
        return {"status": "skipped", "reason": "Twitter bearer token not configured"}

    db = SessionLocal()
    try:
        from app.services.twitter_fetcher import TwitterFetcher
        fetcher = TwitterFetcher(settings.twitter_bearer_token)
        results = fetcher.fetch_strategic_tweets(db)
        total = sum(results.values())
        logger.info(f"Twitter fetch complete. New tweets: {total}")
        return {"status": "success", "tweets_fetched": total, "by_account": results}
    except Exception as e:
        logger.error(f"Error fetching from Twitter: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.fetch_news.fetch_newsapi_news")
def fetch_newsapi_news(self):
    """
    Fetch news from NewsAPI.org.
    Scheduled to run every 6 hours (if configured).
    """
    from app.config import settings

    if not settings.newsapi_key:
        logger.debug("NewsAPI not configured, skipping")
        return {"status": "skipped", "reason": "NewsAPI key not configured"}

    db = SessionLocal()
    try:
        from app.services.news_api_fetcher import NewsAPIFetcher
        fetcher = NewsAPIFetcher(settings.newsapi_key)
        count = fetcher.fetch_strategic_news(db)
        logger.info(f"NewsAPI fetch complete. New articles: {count}")
        return {"status": "success", "articles_fetched": count}
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
