from sqlalchemy.orm import Session
from backend.app.schemas import integration as schemas
from backend.app.database import models
def create_integration(db: Session, integration: schemas.IntegrationCreate):
    db_integration = models.Integration(
        name=integration.name,
        base_url=integration.base_url,
        http_method=integration.http_method,
        is_active=integration.is_active
    )
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    return db_integration
def get_integration(db: Session, integration_id: int):
    return (
        db.query(models.Integration).filter(models.Integration.id == integration_id).first()
    )
def get_integrations(db: Session):
    return (
        db.query(models.Integration).all()
    )

def update_integration(db: Session,integration_id: int, integration: schemas.IntegrationCreate):
    db_integration = db.query(models.Integration).filter(models.Integration.id == integration_id).first()
    if db_integration:
       db_integration.name = integration.name
       db_integration.base_url = integration.base_url
       db_integration.http_method = integration.http_method
       db_integration.is_active = integration.is_active
       db.commit()
       db.refresh(db_integration)
    return db_integration
def delete_integration(db: Session, integration_id: int):
    db_integration = db.query(models.Integration).filter(models.Integration.id == integration_id).first()
    if db_integration:
        db.delete(db_integration)
        db.commit()
    return db_integration
