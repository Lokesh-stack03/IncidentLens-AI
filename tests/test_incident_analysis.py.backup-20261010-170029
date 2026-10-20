from unittest.mock import Mock
from google.genai import errors
import pytest
from fastapi import HTTPException

from backend.app.routers import incident_router


def test_missing_incident_does_not_call_gemini(monkeypatch):
    fake_db = Mock()
    fake_lookup = Mock(return_value=None)
    fake_gemini = Mock()

    monkeypatch.setattr(
        incident_router.crud,
        "get_incident",
        fake_lookup,
    )

    monkeypatch.setattr(
        incident_router,
        "analyze_incident",
        fake_gemini,
    )

    with pytest.raises(HTTPException) as caught:
        incident_router.analyze_incident_endpoint(
            incident_id=999,
            db=fake_db,
        )

    assert caught.value.status_code == 404
    fake_gemini.assert_not_called()
def test_existing_incident_returns_analysis(monkeypatch):
    # 1. Create a fake database session.
    fake_db = Mock()

    # 2. Create an incident that the fake database will return.
    fake_incident = Mock(
        id=4,
        title="Simulated API request timeout",
        error_message="Test scenario: request timed out after 10 seconds.",
        status_code=None,
    )

    # 3. Create the analysis that the fake Gemini function will return.
    expected_analysis = incident_router.IncidentAnalysisResponse(
        incident_id=4,
        summary="A simulated API request timed out after 10 seconds.",
        possible_causes=[
            "The server may have been slow to respond."
        ],
        troubleshooting_steps=[
            "Check server logs around the time of the request."
        ],
        missing_information=[
            "The target API endpoint."
        ],
    )

    # 4. Set up fake functions with predictable return values.
    fake_lookup = Mock(return_value=fake_incident)
    fake_gemini = Mock(return_value=expected_analysis)

    # 5. Temporarily replace the real functions.
    monkeypatch.setattr(
        incident_router.crud,
        "get_incident",
        fake_lookup,
    )

    monkeypatch.setattr(
        incident_router,
        "analyze_incident",
        fake_gemini,
    )

    # 6. Run the endpoint function.
    result = incident_router.analyze_incident_endpoint(
        incident_id=4,
        db=fake_db,
    )

    # 7. Check the database lookup.
    fake_lookup.assert_called_once_with(fake_db, 4)

    # 8. Check the information passed to Gemini.
    fake_gemini.assert_called_once_with(
        incident_id=4,
        title="Simulated API request timeout",
        error_message="Test scenario: request timed out after 10 seconds.",
        status_code=None,
    )

    # 9. Check the returned analysis.
    assert result == expected_analysis
    assert result.incident_id == 4
@pytest.mark.parametrize("provider_code", [429, 503])
def test_gemini_unavailable_returns_503(monkeypatch, provider_code):
    # Create a fake database session and an existing incident.
    fake_db = Mock()

    fake_incident = Mock(
        id=4,
        title="Simulated API request timeout",
        error_message="Test scenario: request timed out after 10 seconds.",
        status_code=None,
    )

    fake_lookup = Mock(return_value=fake_incident)

    # Create the error that our fake Gemini function will raise.
    provider_error = errors.APIError(
        code=provider_code,
        response_json={
            "error": {
                "code": provider_code,
                "message": "Simulated provider failure",
            }
        },
    )

    fake_gemini = Mock(side_effect=provider_error)

    # Temporarily replace the real database lookup and Gemini call.
    monkeypatch.setattr(
        incident_router.crud,
        "get_incident",
        fake_lookup,
    )

    monkeypatch.setattr(
        incident_router,
        "analyze_incident",
        fake_gemini,
    )

    # The endpoint should convert the Gemini error into HTTPException.
    with pytest.raises(HTTPException) as caught:
        incident_router.analyze_incident_endpoint(
            incident_id=4,
            db=fake_db,
        )

    # Check the status code and helpful message.
    assert caught.value.status_code == 503
    assert caught.value.detail == (
        f"Gemini returned error {provider_code}. "
        "AI analysis is currently unavailable."
    )

    fake_lookup.assert_called_once_with(fake_db, 4)
    fake_gemini.assert_called_once()