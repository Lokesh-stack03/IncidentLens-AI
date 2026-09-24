from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IncidentCreate(BaseModel):
    integration_id: int
    title: str
    error_message: str
    status_code: Optional[int] = None
    endpoint: Optional[str] = None
    status: str = "OPEN"


class IncidentResponse(BaseModel):
    id: int
    integration_id: int
    title: str
    error_message: str
    status_code: Optional[int] = None
    endpoint: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime