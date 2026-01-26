from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RelevanceLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# India and neighboring countries - highest priority
INDIA_NEIGHBOR_COUNTRIES = [
    "India", "Pakistan", "China", "Bangladesh", "Nepal",
    "Sri Lanka", "Myanmar", "Afghanistan", "Maldives", "Bhutan"
]


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    # Basic article info
    title = Column(String(500), nullable=False, index=True)
    original_content = Column(Text, nullable=True)
    url = Column(String(2000), unique=True, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    author = Column(String(255), nullable=True)
    image_url = Column(String(2000), nullable=True)

    # Source relationship
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source = relationship("Source", back_populates="articles")

    # AI-generated content
    summary_what_happened = Column(Text, nullable=True)
    summary_why_matters = Column(Text, nullable=True)
    summary_india_implications = Column(Text, nullable=True)
    summary_future_developments = Column(Text, nullable=True)

    # Relevance scoring
    relevance_level = Column(Enum(RelevanceLevel), default=RelevanceLevel.LOW)
    relevance_score = Column(Float, default=0.0)
    geo_score = Column(Float, default=0.0)
    military_score = Column(Float, default=0.0)
    diplomatic_score = Column(Float, default=0.0)
    economic_score = Column(Float, default=0.0)

    # Priority flag - True for India and neighboring countries
    is_priority = Column(Boolean, default=False, index=True)

    # Classification
    region = Column(String(100), nullable=True, index=True)  # e.g., "Indo-Pacific", "South Asia"
    country = Column(String(100), nullable=True, index=True)
    theme = Column(String(100), nullable=True, index=True)  # e.g., "Great Power Competition"
    domain = Column(String(50), nullable=True, index=True)  # land, maritime, air, cyber, space

    # Extracted entities (JSON array)
    entities = Column(JSON, default=list)  # [{type: "country", name: "China"}, ...]

    # Processing status
    is_processed = Column(Integer, default=0)  # 0: pending, 1: processed, 2: failed
    processing_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Article {self.id}: {self.title[:50]}...>"
