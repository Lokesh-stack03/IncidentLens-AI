from backend.app.services.api_executor import execute_api
from backend.app.services.failure_detector import detect_failure
from backend.app.crud.incident import create_incident
from backend.app.schemas.incident import IncidentCreate


def execute_and_create_incident(db, integration):
    """
    Execute an integration API request.
    If it fails, automatically create an Incident.
    """

    # Step 1: Execute the API
    result = execute_api(integration)

    # Step 2: Detect failure
    failure = detect_failure(result)

    # Step 3: If there is no failure, return the result
    if not failure["failed"]:
        return {"success": True, "incident_created": False, "result": result}

    # Step 4: Build Incident data
    incident_data = IncidentCreate(
        integration_id=integration.id,
        title="API request failed",
        error_message=result.get("error", "API request failed"),
        status_code=result.get("status_code"),
        endpoint=integration.base_url,
        status="OPEN",
    )

    # Step 5: Save Incident to database
    incident = create_incident(db, incident_data)

    # Step 6: Return execution result
    return {
        "success": False,
        "incident_created": True,
        "failure_type": failure["failure_type"],
        "incident": incident,
    }
