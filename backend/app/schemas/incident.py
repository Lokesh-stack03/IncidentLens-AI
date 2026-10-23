from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime
from typing import Optional


class IncidentCreate(BaseModel):
    integration_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    error_message: str = Field(min_length=1)
    status_code: Optional[int] = Field(
        default=None,
        ge=100,
        le=599,
    )
    endpoint: Optional[str] = None
    status: Literal["OPEN", "INVESTIGATING", "RESOLVED"] = "OPEN"


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    integration_id: int
    title: str
    error_message: str
    status_code: Optional[int] = None
    endpoint: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
