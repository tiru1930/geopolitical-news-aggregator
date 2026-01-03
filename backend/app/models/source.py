from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class SourceType(str, enum.Enum):
    RSS = "rss"
    API = "api"
    SCRAPE = "scrape"


class SourceCategory(str, enum.Enum):
    NEWS_AGENCY = "news_agency"
    THINK_TANK = "think_tank"
    GOVERNMENT = "government"
    MILITARY = "military"
    ACADEMIC = "academic"


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, unique=True)
    url = Column(String(2000), nullable=False)
    feed_url = Column(String(2000), nullable=True)  # RSS feed URL if applicable

    source_type = Column(Enum(SourceType), default=SourceType.RSS)
    category = Column(Enum(SourceCategory), default=SourceCategory.NEWS_AGENCY)

    # Source metadata
    country = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    description = Column(String(1000), nullable=True)

    # Reliability and bias
    reliability_score = Column(Integer, default=5)  # 1-10 scale
    bias_rating = Column(String(50), nullable=True)  # e.g., "center", "left-leaning"

    # Fetching configuration
    is_active = Column(Boolean, default=True)
    fetch_interval_minutes = Column(Integer, default=30)
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    last_fetch_status = Column(String(50), nullable=True)  # success, failed, timeout

    # Articles relationship
    articles = relationship("Article", back_populates="source", lazy="dynamic")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Source {self.id}: {self.name}>"
