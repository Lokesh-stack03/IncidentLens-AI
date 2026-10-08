from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from backend.app.schemas import incident as schemas
from backend.app.database.database import get_db
from backend.app.crud import incident as crud
from google.genai import errors

from backend.app.schemas.incident_analysis import IncidentAnalysisResponse
from backend.app.services.gemini_service import analyze_incident

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"]
)


@router.post(
    "/",
    response_model=schemas.IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_incident(
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db)
):
    return crud.create_incident(db, incident)


@router.get(
    "/",
    response_model=list[schemas.IncidentResponse]
)
def get_incidents(
    db: Session = Depends(get_db)
):
    return crud.get_incidents(db)


@router.get(
    "/{incident_id}",
    response_model=schemas.IncidentResponse
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    db_incident = crud.get_incident(db, incident_id)

    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return db_incident


@router.put(
    "/{incident_id}",
    response_model=schemas.IncidentResponse
)
def update_incident(
    incident_id: int,
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db)
):
    db_incident = crud.update_incident(
        db,
        incident_id,
        incident
    )

    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return db_incident


@router.delete(
    "/{incident_id}",
    response_model=schemas.IncidentResponse
)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    db_incident = crud.delete_incident(db, incident_id)

    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return db_incident
@router.post(
    "/{incident_id}/analyze",
    response_model=IncidentAnalysisResponse
)
def analyze_incident_endpoint(
    incident_id: int,
    db: Session = Depends(get_db)
):
    db_incident = crud.get_incident(db, incident_id)

    if db_incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    try:
        analysis = analyze_incident(
            incident_id=db_incident.id,
            title=db_incident.title,
            error_message=db_incident.error_message,
            status_code=db_incident.status_code,
        )

    except errors.APIError as exc:
        print(f"Gemini API error code: {exc.code}")
        if exc.code in (429, 503):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=(
                    f"Gemini returned error {exc.code}. "
                    "AI analysis is currently unavailable."
                )
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider could not complete the analysis."
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider returned an empty or invalid analysis."
        ) from exc

    return analysis