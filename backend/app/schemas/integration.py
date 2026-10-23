from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal
from urllib.parse import urlsplit
from datetime import datetime
from typing import Optional


class IntegrationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    base_url: str = Field(max_length=500)
    http_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"] = "GET"
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, value):
        url = urlsplit(value)
        if (
            url.scheme not in ("http", "https")
            or not url.hostname
            or url.username
            or url.password
        ):
            raise ValueError("Use an HTTP or HTTPS URL without credentials")
        return value


class IntegrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    base_url: str
    http_method: str
    is_active: bool
    created_at: datetime
