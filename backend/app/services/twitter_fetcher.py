"""
Twitter/X News Fetcher

Requires Twitter API v2 access (Basic tier: $100/month or Free tier with limits)
Get credentials at: https://developer.twitter.com/

Environment variables needed:
- TWITTER_BEARER_TOKEN
- TWITTER_API_KEY (optional)
- TWITTER_API_SECRET (optional)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.article import Article
from app.models.source import Source

logger = logging.getLogger(__name__)


# Strategic Twitter accounts to follow
STRATEGIC_TWITTER_ACCOUNTS = [
    # Indian Defence & Strategic
    {"username": "indiannavy", "name": "Indian Navy", "category": "military"},
    {"username": "IAaborunda", "name": "Indian Air Force", "category": "military"},
    {"username": "adaborunda", "name": "Indian Army", "category": "military"},
    {"username": "MEAIndia", "name": "Ministry of External Affairs", "category": "government"},
    {"username": "DefenceMinIndia", "name": "Ministry of Defence India", "category": "government"},
    {"username": "PMOIndia", "name": "PM Office India", "category": "government"},

    # US Defence & State
    {"username": "DeptofDefense", "name": "US Department of Defense", "category": "military"},
    {"username": "StateDept", "name": "US State Department", "category": "government"},
    {"username": "ABORUNCPACOM", "name": "US Indo-Pacific Command", "category": "military"},
    {"username": "PentagonPresSec", "name": "Pentagon Press Secretary", "category": "military"},

    # Think Tanks & Analysts
    {"username": "ABORUNCIISS", "name": "IISS", "category": "think_tank"},
    {"username": "CABORUNSIS", "name": "CSIS", "category": "think_tank"},
    {"username": "BrookingsInst", "name": "Brookings", "category": "think_tank"},
    {"username": "Carnegie_India", "name": "Carnegie India", "category": "think_tank"},
    {"username": "aborunfp", "name": "Foreign Policy Magazine", "category": "news_agency"},

    # Regional
    {"username": "MFA_China", "name": "China MFA", "category": "government"},
    {"username": "ForeignOfficePK", "name": "Pakistan Foreign Office", "category": "government"},

    # Defence Journalists
    {"username": "ShivAroor", "name": "Shiv Aroor", "category": "journalist"},
    {"username": "aaborunnilNayyar", "name": "Anil Nayyar", "category": "journalist"},
]


class TwitterFetcher:
    """
    Fetches tweets from strategic accounts using Twitter API v2
    """

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: str = None):
        self.bearer_token = bearer_token or getattr(settings, 'twitter_bearer_token', None)
        if not self.bearer_token:
            logger.warning("Twitter bearer token not configured")

    def _make_request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make authenticated request to Twitter API"""
        if not self.bearer_token:
            return None

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Twitter API error: {e}")
            return None

    def get_user_id(self, username: str) -> Optional[str]:
        """Get Twitter user ID from username"""
        data = self._make_request(f"users/by/username/{username}")
        if data and "data" in data:
            return data["data"]["id"]
        return None

    def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 10,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Fetch recent tweets from a user"""
        start_time = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "max_results": min(max_results, 100),
            "start_time": start_time,
            "tweet.fields": "created_at,public_metrics,entities,context_annotations",
            "expansions": "referenced_tweets.id",
            "exclude": "retweets,replies"  # Only original tweets
        }

        data = self._make_request(f"users/{user_id}/tweets", params)

        if data and "data" in data:
            return data["data"]
        return []

    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Search for tweets matching a query

        Example queries:
        - "India China border" -is:retweet
        - "QUAD summit" lang:en
        - "South China Sea" (military OR navy)
        """
        start_time = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "query": f"{query} -is:retweet lang:en",
            "max_results": min(max_results, 100),
            "start_time": start_time,
            "tweet.fields": "created_at,public_metrics,author_id,entities",
            "expansions": "author_id",
            "user.fields": "name,username,verified"
        }

        data = self._make_request("tweets/search/recent", params)

        if data and "data" in data:
            return data["data"]
        return []

    def fetch_strategic_tweets(self, db: Session) -> Dict[str, int]:
        """
        Fetch tweets from all strategic accounts and save as articles
        """
        results = {}

        for account in STRATEGIC_TWITTER_ACCOUNTS:
            username = account["username"]
            try:
                user_id = self.get_user_id(username)
                if not user_id:
                    continue

                tweets = self.get_user_tweets(user_id, max_results=5, hours_back=24)
                saved = 0

                for tweet in tweets:
                    # Check if tweet is significant (has engagement)
                    metrics = tweet.get("public_metrics", {})
                    if metrics.get("like_count", 0) < 10:
                        continue  # Skip low-engagement tweets

                    # Create unique URL
                    tweet_url = f"https://twitter.com/{username}/status/{tweet['id']}"

                    # Check if already exists
                    existing = db.query(Article).filter(Article.url == tweet_url).first()
                    if existing:
                        continue

                    # Get or create source
                    source = db.query(Source).filter(
                        Source.name == f"Twitter: @{username}"
                    ).first()

                    if not source:
                        from app.models.source import SourceType, SourceCategory
                        source = Source(
                            name=f"Twitter: @{username}",
                            url=f"https://twitter.com/{username}",
                            source_type=SourceType.API,
                            category=SourceCategory(account.get("category", "news_agency")),
                            is_active=True
                        )
                        db.add(source)
                        db.commit()

                    # Create article from tweet
                    article = Article(
                        title=tweet["text"][:200] + ("..." if len(tweet["text"]) > 200 else ""),
                        url=tweet_url,
                        original_content=tweet["text"],
                        published_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                        author=f"@{username}",
                        source_id=source.id,
                        is_processed=0
                    )
                    db.add(article)
                    saved += 1

                db.commit()
                results[username] = saved

            except Exception as e:
                logger.error(f"Error fetching tweets from @{username}: {e}")
                results[username] = 0

        return results


# Strategic search queries for geopolitical news
STRATEGIC_SEARCH_QUERIES = [
    '"India China" (border OR LAC OR military)',
    '"Indo Pacific" (QUAD OR AUKUS OR security)',
    '"South China Sea" (military OR navy OR dispute)',
    '"Pakistan" (terrorism OR military OR nuclear)',
    '"Taiwan Strait" (China OR military OR tension)',
    '"Indian Ocean" (navy OR maritime OR security)',
    '"North Korea" (missile OR nuclear OR Kim)',
    '"Russia Ukraine" (war OR military OR NATO)',
    '"Middle East" (Iran OR Israel OR conflict)',
]


def fetch_twitter_search(db: Session, bearer_token: str = None) -> Dict[str, int]:
    """Fetch tweets from strategic search queries"""
    fetcher = TwitterFetcher(bearer_token)
    results = {}

    for query in STRATEGIC_SEARCH_QUERIES:
        try:
            tweets = fetcher.search_tweets(query, max_results=10, hours_back=12)
            # Process tweets similar to above
            results[query[:30]] = len(tweets)
        except Exception as e:
            logger.error(f"Error searching '{query}': {e}")
            results[query[:30]] = 0

    return results
