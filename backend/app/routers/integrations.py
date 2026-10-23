from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.crud import intigrations as crud
from backend.app.schemas import integration as schemas
from backend.app.services.incident_service import execute_and_create_incident

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


@router.get("/", response_model=list[schemas.IntegrationResponse])
def list_integrations(db: Session = Depends(get_db)):
    return crud.get_integrations(db)


@router.post(
    "/", response_model=schemas.IntegrationResponse, status_code=status.HTTP_201_CREATED
)
def create_integration(
    integration: schemas.IntegrationCreate, db: Session = Depends(get_db)
):
    return crud.create_integration(db, integration)


@router.get("/{integration_id}", response_model=schemas.IntegrationResponse)
def get_integration(integration_id: int, db: Session = Depends(get_db)):
    db_integration = crud.get_integration(db, integration_id)
    if not db_integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )
    return db_integration


@router.put("/{integration_id}", response_model=schemas.IntegrationResponse)
def update_integration(
    integration_id: int,
    integration: schemas.IntegrationCreate,
    db: Session = Depends(get_db),
):
    db_integration = crud.update_integration(db, integration_id, integration)
    if not db_integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )
    return db_integration


@router.delete("/{integration_id}", response_model=schemas.IntegrationResponse)
def delete_integration(integration_id: int, db: Session = Depends(get_db)):
    from backend.app.database.models import Incident

    if db.query(Incident).filter(Incident.integration_id == integration_id).first():
        raise HTTPException(409, "Delete this integration's incidents first.")
    db_integration = crud.delete_integration(db, integration_id)

    if not db_integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )

    return db_integration


@router.post("/{integration_id}/execute")
def execute_integration(integration_id: int, db: Session = Depends(get_db)):
    integration = crud.get_integration(db, integration_id)

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )

    if not integration.is_active:
        raise HTTPException(400, "Activate this integration before executing it.")
    return execute_and_create_incident(db, integration)
