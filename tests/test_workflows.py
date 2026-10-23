"""Exercise the HTTP features with a fresh database for every test."""

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from pypdf import PdfWriter

from backend.app.routers import documents, incident_router
from backend.app.services import api_executor, gemini_service


def integration(client, **changes):
    data = {"name": "Payments", "base_url": "https://example.com/health", **changes}
    response = client.post("/api/v1/integrations/", json=data)
    assert response.status_code == 201
    return response.json()


def test_integration_crud_and_validation(client):
    item = integration(client)
    path = f"/api/v1/integrations/{item['id']}"
    assert client.get(path).json()["name"] == "Payments"
    assert len(client.get("/api/v1/integrations/").json()) == 1
    assert (
        client.put(path, json={**item, "name": "Billing"}).json()["name"] == "Billing"
    )
    assert (
        client.post(
            "/api/v1/integrations/", json={"name": "", "base_url": "file:///tmp/a"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/integrations/",
            json={
                "name": "API",
                "base_url": "https://example.com",
                "http_method": "BAD",
            },
        ).status_code
        == 422
    )
    assert client.delete(path).status_code == 200
    for method in (client.get, client.delete):
        assert method(path).status_code == 404
    assert client.put(path, json=item).status_code == 404


def test_execution_creates_incident_and_can_be_resolved(client, monkeypatch):
    item = integration(client)
    mock_request = Mock(
        return_value=SimpleNamespace(status_code=500, text="Server error")
    )
    monkeypatch.setattr(api_executor.requests, "request", mock_request)
    execution = client.post(f"/api/v1/integrations/{item['id']}/execute")
    assert execution.status_code == 200
    assert execution.json()["incident_created"] is True
    event = execution.json()["incident"]
    path = f"/api/v1/incidents/{event['id']}"
    assert client.get(path).status_code == 200
    assert len(client.get("/api/v1/incidents/").json()) == 1
    assert client.delete(f"/api/v1/integrations/{item['id']}").status_code == 409
    assert (
        client.put(path, json={**event, "status": "INVESTIGATING"}).json()["status"]
        == "INVESTIGATING"
    )
    assert (
        client.put(path, json={**event, "status": "RESOLVED"}).json()["status"]
        == "RESOLVED"
    )
    assert client.put(path, json={**event, "status": "INVALID"}).status_code == 422
    assert client.delete(path).status_code == 200
    assert client.get(path).status_code == 404
    assert client.delete(path).status_code == 404
    assert client.put(path, json=event).status_code == 404
    assert client.delete(f"/api/v1/integrations/{item['id']}").status_code == 200


def test_success_inactive_and_missing_execution(client, monkeypatch):
    item = integration(client)
    monkeypatch.setattr(
        api_executor.requests,
        "request",
        lambda **kwargs: SimpleNamespace(status_code=200, text="OK"),
    )
    assert (
        client.post(f"/api/v1/integrations/{item['id']}/execute").json()[
            "incident_created"
        ]
        is False
    )
    inactive = integration(client, is_active=False)
    assert (
        client.post(f"/api/v1/integrations/{inactive['id']}/execute").status_code == 400
    )
    assert client.post("/api/v1/integrations/999/execute").status_code == 404


def test_manual_incident_and_analysis(client, monkeypatch):
    item = integration(client)
    body = {
        "integration_id": item["id"],
        "title": "Test timeout",
        "error_message": "Simulated timeout",
    }
    event = client.post("/api/v1/incidents/", json=body)
    assert event.status_code == 201
    event = event.json()
    analysis = {
        "incident_id": event["id"],
        "summary": "Simulated timeout",
        "possible_causes": ["Slow server"],
        "troubleshooting_steps": ["Check logs"],
        "missing_information": [],
    }
    monkeypatch.setattr(incident_router, "analyze_incident", lambda **kwargs: analysis)
    path = f"/api/v1/incidents/{event['id']}/analyze"
    assert client.post(path).json() == analysis
    monkeypatch.setattr(
        incident_router,
        "analyze_incident",
        Mock(side_effect=RuntimeError("Configure Gemini")),
    )
    assert client.post(path).status_code == 503
    monkeypatch.setattr(
        incident_router,
        "analyze_incident",
        Mock(side_effect=ValueError("Invalid response")),
    )
    assert client.post(path).status_code == 502
    assert client.post("/api/v1/incidents/999/analyze").status_code == 404
    assert (
        client.post(
            "/api/v1/incidents/", json={**body, "integration_id": 999}
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"/api/v1/incidents/{event['id']}", json={**body, "integration_id": 999}
        ).status_code
        == 404
    )


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.Timeout(),
        requests.exceptions.ConnectionError(),
        requests.exceptions.RequestException("bad request"),
    ],
)
def test_executor_handles_network_errors(monkeypatch, error):
    monkeypatch.setattr(api_executor.requests, "request", Mock(side_effect=error))
    result = api_executor.execute_api(
        SimpleNamespace(http_method="GET", base_url="https://example.com")
    )
    assert result["success"] is False
    assert result["status_code"] is None
    assert result["error"]


def test_document_upload_list_search_delete(client, monkeypatch):
    # Test HTTP orchestration without downloading a model.
    monkeypatch.setattr(
        documents,
        "load_pdf",
        lambda path: [
            {
                "text": "Timeout: check server logs",
                "source": path.name,
                "page_number": 1,
            }
        ],
    )
    store = Mock(return_value=["chunk-1"])
    monkeypatch.setattr(documents.vector_store, "store_chunks", store)
    response = client.post(
        "/api/v1/documents/upload", files={"file": ("runbook.pdf", b"%PDF-1.4 fake")}
    )
    assert response.status_code == 201
    assert response.json()["chunk_count"] == 1
    assert store.call_args.args[0][0]["page_number"] == 1
    monkeypatch.setattr(
        documents.vector_store,
        "list_documents",
        lambda: [{"source": "runbook.pdf", "chunk_count": 1}],
    )
    assert client.get("/api/v1/documents/").json()[0]["source"] == "runbook.pdf"
    monkeypatch.setattr(
        documents.vector_store,
        "search_similar_chunks",
        lambda *args: {
            "ids": [["chunk-1"]],
            "documents": [["Check logs"]],
            "metadatas": [[{"source": "runbook.pdf", "page_number": 1}]],
            "distances": [[0.2]],
        },
    )
    assert (
        client.post("/api/v1/documents/search", json={"query": "timeout"}).json()[0][
            "text"
        ]
        == "Check logs"
    )
    assert (
        client.post("/api/v1/documents/search", json={"query": " "}).status_code == 400
    )
    assert (
        client.post(
            "/api/v1/documents/search", json={"query": "timeout", "top_k": 0}
        ).status_code
        == 422
    )
    collection = Mock()
    collection.get.return_value = {"ids": ["chunk-1"]}
    monkeypatch.setattr(documents.vector_store, "get_collection", lambda: collection)
    assert (
        client.delete("/api/v1/documents/?source=runbook.pdf").json()["deleted_chunks"]
        == 1
    )
    collection.delete.assert_called_once_with(ids=["chunk-1"])
    collection.get.return_value = {"ids": []}
    assert client.delete("/api/v1/documents/?source=missing.pdf").status_code == 404


def test_reject_invalid_documents(client):
    assert (
        client.post(
            "/api/v1/documents/upload", files={"file": ("notes.txt", b"hello")}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/documents/upload", files={"file": ("fake.pdf", b"hello")}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/documents/upload",
            files={"file": ("large.pdf", b"%PDF-" + b"x" * (10 * 1024 * 1024))},
        ).status_code
        == 413
    )
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    content = BytesIO()
    writer.write(content)
    assert (
        client.post(
            "/api/v1/documents/upload",
            files={"file": ("blank.pdf", content.getvalue())},
        ).status_code
        == 400
    )


def test_gemini_parses_response_and_preserves_incident_id(monkeypatch):
    fake = Mock()
    fake.models.generate_content.return_value.text = '{"incident_id":999,"summary":"Test","possible_causes":[],"troubleshooting_steps":[],"missing_information":[]}'
    context = Mock()
    context.__enter__ = Mock(return_value=fake)
    context.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(gemini_service.genai, "Client", lambda **kwargs: context)
    assert gemini_service.analyze_incident(1, "Test", "timeout", None).incident_id == 1
    fake.models.generate_content.return_value.text = ""
    with pytest.raises(ValueError):
        gemini_service.analyze_incident(1, "Test", "timeout", None)
    monkeypatch.setattr(gemini_service.settings, "GEMINI_API_KEY", "")
    with pytest.raises(RuntimeError):
        gemini_service.analyze_incident(1, "Test", "timeout", None)
