from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertFrequency(str, Enum):
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class AlertBase(BaseModel):
    name: str
    regions: List[str] = []
    countries: List[str] = []
    themes: List[str] = []
    domains: List[str] = []
    keywords: List[str] = []
    min_relevance: str = "medium"
    frequency: AlertFrequency = AlertFrequency.DAILY
    is_active: bool = True
    email_enabled: bool = True


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    regions: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    min_relevance: Optional[str] = None
    frequency: Optional[AlertFrequency] = None
    is_active: Optional[bool] = None
    email_enabled: Optional[bool] = None


class AlertResponse(AlertBase):
    id: int
    user_id: int
    last_triggered_at: Optional[datetime] = None
    trigger_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
