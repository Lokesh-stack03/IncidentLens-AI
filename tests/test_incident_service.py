from unittest.mock import patch
from types import SimpleNamespace

from backend.app.services.incident_service import execute_and_create_incident


@patch("backend.app.services.incident_service.create_incident")
@patch("backend.app.services.incident_service.detect_failure")
@patch("backend.app.services.incident_service.execute_api")
def test_success_does_not_create_incident(
    mock_execute_api, mock_detect_failure, mock_create_incident
):
    integration = SimpleNamespace(
        id=1, base_url="https://example.com", http_method="GET"
    )

    mock_execute_api.return_value = {
        "success": True,
        "status_code": 200,
        "response": "OK",
    }

    mock_detect_failure.return_value = {"failed": False, "failure_type": None}

    result = execute_and_create_incident(None, integration)

    assert result["success"] is True
    assert result["incident_created"] is False

    mock_create_incident.assert_not_called()


@patch("backend.app.services.incident_service.create_incident")
@patch("backend.app.services.incident_service.detect_failure")
@patch("backend.app.services.incident_service.execute_api")
def test_failure_creates_incident(
    mock_execute_api, mock_detect_failure, mock_create_incident
):
    integration = SimpleNamespace(
        id=1, base_url="https://example.com/api", http_method="GET"
    )

    mock_execute_api.return_value = {
        "success": False,
        "status_code": 500,
        "error": "Internal Server Error",
    }

    mock_detect_failure.return_value = {"failed": True, "failure_type": "SERVER_ERROR"}

    mock_create_incident.return_value = SimpleNamespace(
        id=10, integration_id=1, status="OPEN"
    )

    result = execute_and_create_incident(None, integration)

    assert result["success"] is False
    assert result["incident_created"] is True
    assert result["failure_type"] == "SERVER_ERROR"

    mock_create_incident.assert_called_once()
