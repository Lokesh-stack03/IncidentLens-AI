from unittest.mock import Mock

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