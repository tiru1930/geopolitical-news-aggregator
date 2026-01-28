from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RelevanceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ArticleBase(BaseModel):
    title: str
    url: str
    original_content: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    image_url: Optional[str] = None


class ArticleCreate(ArticleBase):
    source_id: int


class ArticleSummary(BaseModel):
    what_happened: Optional[str] = None
    why_matters: Optional[str] = None
    india_implications: Optional[str] = None
    future_developments: Optional[str] = None


class ArticleResponse(ArticleBase):
    id: int
    source_id: int
    source_name: Optional[str] = None

    # AI-generated summaries
    summary_bullets: Optional[str] = None  # 5-line bullet point summary
    summary_what_happened: Optional[str] = None
    summary_why_matters: Optional[str] = None
    summary_india_implications: Optional[str] = None
    summary_future_developments: Optional[str] = None

    # Relevance
    relevance_level: RelevanceLevel
    relevance_score: float
    geo_score: float
    military_score: float
    diplomatic_score: float
    economic_score: float
    is_priority: bool = False  # True for India & neighboring countries

    # Classification
    region: Optional[str] = None
    country: Optional[str] = None
    theme: Optional[str] = None
    domain: Optional[str] = None
    entities: List[Dict[str, Any]] = []

    # Status
    is_processed: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    articles: List[ArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ArticleFilters(BaseModel):
    region: Optional[str] = None
    country: Optional[str] = None
    theme: Optional[str] = None
    domain: Optional[str] = None
    relevance_level: Optional[RelevanceLevel] = None
    source_id: Optional[int] = None
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
