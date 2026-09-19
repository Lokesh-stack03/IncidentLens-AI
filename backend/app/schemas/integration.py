from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class IntegrationCreate(BaseModel):
    name: str
    base_url:str
    http_method: str = "GET"
    is_active: bool=True
class IntegrationResponse(BaseModel):
    id: int
    name: str
    base_url:str
    http_method: str
    is_active:bool
    created_at: datetime
