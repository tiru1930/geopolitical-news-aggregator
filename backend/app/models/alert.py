from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AlertFrequency(str, enum.Enum):
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="alerts")

    name = Column(String(255), nullable=False)

    # Filter criteria (all optional, combined with AND)
    regions = Column(JSON, default=list)  # ["Indo-Pacific", "South Asia"]
    countries = Column(JSON, default=list)  # ["China", "Pakistan"]
    themes = Column(JSON, default=list)  # ["Great Power Competition"]
    domains = Column(JSON, default=list)  # ["maritime", "cyber"]
    keywords = Column(JSON, default=list)  # ["nuclear", "missile"]
    min_relevance = Column(String(10), default="medium")  # low, medium, high

    # Notification settings
    frequency = Column(Enum(AlertFrequency), default=AlertFrequency.DAILY)
    is_active = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)

    # Tracking
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Alert {self.id}: {self.name}>"
