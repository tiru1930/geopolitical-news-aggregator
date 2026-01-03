from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    RSS = "rss"
    API = "api"
    SCRAPE = "scrape"


class SourceCategory(str, Enum):
    NEWS_AGENCY = "news_agency"
    THINK_TANK = "think_tank"
    GOVERNMENT = "government"
    MILITARY = "military"
    ACADEMIC = "academic"


class SourceBase(BaseModel):
    name: str
    url: str
    feed_url: Optional[str] = None
    source_type: SourceType = SourceType.RSS
    category: SourceCategory = SourceCategory.NEWS_AGENCY
    country: Optional[str] = None
    language: str = "en"
    description: Optional[str] = None
    reliability_score: int = 5
    bias_rating: Optional[str] = None
    is_active: bool = True
    fetch_interval_minutes: int = 30


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    feed_url: Optional[str] = None
    source_type: Optional[SourceType] = None
    category: Optional[SourceCategory] = None
    country: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    reliability_score: Optional[int] = None
    bias_rating: Optional[str] = None
    is_active: Optional[bool] = None
    fetch_interval_minutes: Optional[int] = None


class SourceResponse(SourceBase):
    id: int
    last_fetched_at: Optional[datetime] = None
    last_fetch_status: Optional[str] = None
    article_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
