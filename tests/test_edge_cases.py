from pathlib import Path
from unittest.mock import Mock

import pytest
from google.genai import errors
from pypdf import PdfWriter

from backend.app.routers import documents, incident_router
from backend.app.services import embedding, vector_store
from backend.app.services.document_loader import load_pdf


def test_pdf_preserves_source_and_page_numbers():
    pages = load_pdf(Path(__file__).resolve().parents[1] / "sample.pdf")
    assert pages
    assert all(
        page["source"] == "sample.pdf" and page["text"].strip() for page in pages
    )
    assert pages[0]["page_number"] == 1


def test_pdf_rejects_wrong_extension_and_encryption(tmp_path):
    wrong = tmp_path / "notes.txt"
    wrong.write_text("hello")
    with pytest.raises(ValueError, match="Only PDF"):
        load_pdf(wrong)
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("password")
    encrypted = tmp_path / "encrypted.pdf"
    with encrypted.open("wb") as file:
        writer.write(file)
    with pytest.raises(ValueError, match="Encrypted"):
        load_pdf(encrypted)


def test_empty_embeddings_do_not_load_model(monkeypatch):
    model = Mock()
    monkeypatch.setattr(embedding, "get_model", model)
    assert embedding.generate_embeddings([]) == []
    model.assert_not_called()


@pytest.mark.parametrize(
    "chunks, source", [([""], "guide.pdf"), ([42], "guide.pdf"), (["text"], " ")]
)
def test_store_rejects_invalid_chunks(chunks, source):
    with pytest.raises(ValueError):
        vector_store.store_chunks(chunks, source)


def test_vector_page_metadata_and_document_grouping(monkeypatch):
    collection = Mock()
    collection.get.return_value = {
        "metadatas": [{"source": "guide.pdf"}, {"source": "guide.pdf"}]
    }
    monkeypatch.setattr(vector_store, "get_collection", lambda: collection)
    monkeypatch.setattr(embedding, "generate_embeddings", lambda texts: [[1.0, 0.0]])
    assert vector_store.store_chunks([], "guide.pdf") == []
    vector_store.store_chunks([{"text": "Check logs", "page_number": 2}], "guide.pdf")
    assert collection.add.call_args.kwargs["metadatas"][0]["page_number"] == 2
    assert vector_store.list_documents() == [{"source": "guide.pdf", "chunk_count": 2}]


def test_document_processing_unavailable(client, monkeypatch):
    monkeypatch.setattr(documents, "load_pdf", Mock(side_effect=OSError("unavailable")))
    assert (
        client.post(
            "/api/v1/documents/upload", files={"file": ("guide.pdf", b"%PDF-1.4 fake")}
        ).status_code
        == 503
    )
    monkeypatch.setattr(
        vector_store,
        "search_similar_chunks",
        Mock(side_effect=OSError("model missing")),
    )
    assert (
        client.post("/api/v1/documents/search", json={"query": "timeout"}).status_code
        == 503
    )


def test_other_provider_error_is_bad_gateway(client, monkeypatch):
    item = client.post(
        "/api/v1/integrations/", json={"name": "API", "base_url": "https://example.com"}
    ).json()
    incident = client.post(
        "/api/v1/incidents/",
        json={
            "integration_id": item["id"],
            "title": "Test",
            "error_message": "Failure",
        },
    ).json()
    error = errors.APIError(
        code=400, response_json={"error": {"code": 400, "message": "Bad model"}}
    )
    monkeypatch.setattr(incident_router, "analyze_incident", Mock(side_effect=error))
    assert client.post(f"/api/v1/incidents/{incident['id']}/analyze").status_code == 502


def test_root(client):
    assert client.get("/").json()["status"] == "success"
