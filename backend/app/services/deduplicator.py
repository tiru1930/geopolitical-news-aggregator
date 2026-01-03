import re
import logging
from typing import List, Optional
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.article import Article

logger = logging.getLogger(__name__)


class Deduplicator:
    """
    Detects and handles duplicate news articles using
    title similarity and URL matching.
    """

    def __init__(self, db: Session, similarity_threshold: float = 0.8):
        self.db = db
        self.similarity_threshold = similarity_threshold

    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        # Convert to lowercase
        title = title.lower()

        # Remove common prefixes/suffixes
        prefixes = ["breaking:", "update:", "exclusive:", "watch:", "live:"]
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):]

        # Remove special characters and extra whitespace
        title = re.sub(r'[^\w\s]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()

        return title

    def calculate_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity ratio between two titles"""
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)

        return SequenceMatcher(None, norm1, norm2).ratio()

    def find_duplicates(self, title: str, url: str,
                        hours_lookback: int = 72) -> List[Article]:
        """
        Find potential duplicate articles for a given title.

        Args:
            title: Title to check
            url: URL to check (exact match)
            hours_lookback: How many hours back to check

        Returns:
            List of potentially duplicate articles
        """
        duplicates = []

        # Check for exact URL match first
        url_match = self.db.query(Article).filter(Article.url == url).first()
        if url_match:
            duplicates.append(url_match)
            return duplicates

        # Get recent articles for title comparison
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)

        recent_articles = self.db.query(Article).filter(
            Article.created_at >= cutoff_time
        ).all()

        # Check title similarity
        for article in recent_articles:
            similarity = self.calculate_similarity(title, article.title)
            if similarity >= self.similarity_threshold:
                duplicates.append(article)

        return duplicates

    def is_duplicate(self, title: str, url: str) -> bool:
        """Quick check if an article is a duplicate"""
        duplicates = self.find_duplicates(title, url)
        return len(duplicates) > 0

    def mark_duplicates(self, article_ids: List[int], primary_id: int):
        """Mark articles as duplicates of a primary article"""
        # This could be extended to track duplicate relationships
        # For now, we simply don't save duplicates during fetch
        pass

    def cleanup_old_articles(self, days: int = 90) -> int:
        """Remove articles older than specified days"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        deleted = self.db.query(Article).filter(
            Article.created_at < cutoff_time
        ).delete()

        self.db.commit()
        logger.info(f"Deleted {deleted} old articles")

        return deleted

    def get_duplicate_stats(self) -> dict:
        """Get statistics about potential duplicates in the database"""
        # This is a simplified check - in production you'd want
        # more sophisticated duplicate detection

        total = self.db.query(Article).count()

        # Count articles with very similar titles (using first 50 chars)
        # This is approximate
        duplicates_estimate = self.db.query(
            func.substr(Article.title, 1, 50),
            func.count(Article.id)
        ).group_by(
            func.substr(Article.title, 1, 50)
        ).having(
            func.count(Article.id) > 1
        ).count()

        return {
            "total_articles": total,
            "potential_duplicate_groups": duplicates_estimate
        }
