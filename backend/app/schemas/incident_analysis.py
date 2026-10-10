from pydantic import BaseModel

class IncidentAnalysisResponse(BaseModel):
    incident_id: int
    summary: str
    possible_causes: list[str]
    troubleshooting_steps: list[str]
    missing_information: list[str]