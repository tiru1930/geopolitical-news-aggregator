from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "geopolitical_news",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.fetch_news",
        "app.tasks.process_articles"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
)

# Scheduled tasks (beat schedule)
celery_app.conf.beat_schedule = {
    # Fetch news from all RSS sources every 30 minutes
    "fetch-rss-periodic": {
        "task": "app.tasks.fetch_news.fetch_all_news",
        "schedule": crontab(minute=f"*/{settings.fetch_interval_minutes}"),
    },
    # Process unprocessed articles every 5 minutes
    "process-articles-periodic": {
        "task": "app.tasks.process_articles.process_pending_articles",
        "schedule": crontab(minute="*/5"),
    },
    # Fetch from GDELT every 2 hours (free, unlimited)
    "fetch-gdelt-periodic": {
        "task": "app.tasks.fetch_news.fetch_gdelt_news",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    # Fetch from Twitter every hour (if configured)
    "fetch-twitter-periodic": {
        "task": "app.tasks.fetch_news.fetch_twitter_news",
        "schedule": crontab(minute=15),  # At :15 every hour
    },
    # Fetch from NewsAPI every 6 hours (if configured)
    "fetch-newsapi-periodic": {
        "task": "app.tasks.fetch_news.fetch_newsapi_news",
        "schedule": crontab(minute=30, hour="*/6"),
    },
    # Cleanup old articles weekly
    "cleanup-old-articles": {
        "task": "app.tasks.process_articles.cleanup_old_articles",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
    },
}
