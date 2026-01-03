from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.alert import Alert, AlertFrequency
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter()


# For now, we'll use a simple user_id = 1 for demo purposes
# In production, this would come from authentication
DEFAULT_USER_ID = 1


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(db: Session = Depends(get_db)):
    """Get all alerts for the current user"""
    alerts = db.query(Alert).filter(
        Alert.user_id == DEFAULT_USER_ID
    ).order_by(Alert.created_at.desc()).all()

    return [
        AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            name=alert.name,
            regions=alert.regions or [],
            countries=alert.countries or [],
            themes=alert.themes or [],
            domains=alert.domains or [],
            keywords=alert.keywords or [],
            min_relevance=alert.min_relevance,
            frequency=alert.frequency,
            is_active=alert.is_active,
            email_enabled=alert.email_enabled,
            last_triggered_at=alert.last_triggered_at,
            trigger_count=alert.trigger_count,
            created_at=alert.created_at,
            updated_at=alert.updated_at
        )
        for alert in alerts
    ]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a single alert by ID"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == DEFAULT_USER_ID
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse(
        id=alert.id,
        user_id=alert.user_id,
        name=alert.name,
        regions=alert.regions or [],
        countries=alert.countries or [],
        themes=alert.themes or [],
        domains=alert.domains or [],
        keywords=alert.keywords or [],
        min_relevance=alert.min_relevance,
        frequency=alert.frequency,
        is_active=alert.is_active,
        email_enabled=alert.email_enabled,
        last_triggered_at=alert.last_triggered_at,
        trigger_count=alert.trigger_count,
        created_at=alert.created_at,
        updated_at=alert.updated_at
    )


@router.post("/", response_model=AlertResponse)
async def create_alert(alert_data: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    alert = Alert(
        user_id=DEFAULT_USER_ID,
        name=alert_data.name,
        regions=alert_data.regions,
        countries=alert_data.countries,
        themes=alert_data.themes,
        domains=alert_data.domains,
        keywords=alert_data.keywords,
        min_relevance=alert_data.min_relevance,
        frequency=AlertFrequency(alert_data.frequency),
        is_active=alert_data.is_active,
        email_enabled=alert_data.email_enabled
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return AlertResponse(
        id=alert.id,
        user_id=alert.user_id,
        name=alert.name,
        regions=alert.regions or [],
        countries=alert.countries or [],
        themes=alert.themes or [],
        domains=alert.domains or [],
        keywords=alert.keywords or [],
        min_relevance=alert.min_relevance,
        frequency=alert.frequency,
        is_active=alert.is_active,
        email_enabled=alert.email_enabled,
        last_triggered_at=alert.last_triggered_at,
        trigger_count=alert.trigger_count,
        created_at=alert.created_at,
        updated_at=alert.updated_at
    )


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == DEFAULT_USER_ID
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    update_data = alert_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "frequency":
                value = AlertFrequency(value)
            setattr(alert, field, value)

    db.commit()
    db.refresh(alert)

    return AlertResponse(
        id=alert.id,
        user_id=alert.user_id,
        name=alert.name,
        regions=alert.regions or [],
        countries=alert.countries or [],
        themes=alert.themes or [],
        domains=alert.domains or [],
        keywords=alert.keywords or [],
        min_relevance=alert.min_relevance,
        frequency=alert.frequency,
        is_active=alert.is_active,
        email_enabled=alert.email_enabled,
        last_triggered_at=alert.last_triggered_at,
        trigger_count=alert.trigger_count,
        created_at=alert.created_at,
        updated_at=alert.updated_at
    )


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == DEFAULT_USER_ID
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()

    return {"message": "Alert deleted successfully"}


@router.post("/{alert_id}/toggle")
async def toggle_alert(alert_id: int, db: Session = Depends(get_db)):
    """Toggle alert active status"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == DEFAULT_USER_ID
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_active = not alert.is_active
    db.commit()

    return {"is_active": alert.is_active}
