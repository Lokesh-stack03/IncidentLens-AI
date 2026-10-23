from backend.app.schemas import incident as schemas
from backend.app.database import models
from sqlalchemy.orm import Session


def create_incident(db: Session, incident: schemas.IncidentCreate):
    db_incident = models.Incident(
        integration_id=incident.integration_id,
        title=incident.title,
        error_message=incident.error_message,
        status_code=incident.status_code,
        endpoint=incident.endpoint,
        status=incident.status,
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


def get_incident(db: Session, incident_id: int):
    return db.query(models.Incident).filter(models.Incident.id == incident_id).first()


# Get Incidents


def get_incidents(db: Session):
    return db.query(models.Incident).all()


# Update Incident


def update_incident(db: Session, incident_id: int, incident: schemas.IncidentCreate):
    db_incident = (
        db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    )
    if db_incident:
        db_incident.integration_id = incident.integration_id
        db_incident.title = incident.title
        db_incident.error_message = incident.error_message
        db_incident.status_code = incident.status_code
        db_incident.endpoint = incident.endpoint
        db_incident.status = incident.status
        db.commit()
        db.refresh(db_incident)
        return db_incident


def delete_incident(db: Session, incident_id: int):
    db_incident = (
        db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    )
    if db_incident:
        db.delete(db_incident)
        db.commit()
    return db_incident
