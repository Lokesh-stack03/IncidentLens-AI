import uuid

import chromadb

from backend.app.services import vector_store
from backend.app.services.vector_store import store_chunks, search_similar_chunks


def test_semantic_search(tmp_path, monkeypatch):
    client = chromadb.PersistentClient(path=str(tmp_path))
    collection = client.get_or_create_collection(
        name="document_chunks", embedding_function=None
    )
    monkeypatch.setattr(vector_store, "get_collection", lambda: collection)
    source = f"search_test_{uuid.uuid4().hex}.pdf"

    chunks = [
        "An API timeout occurs when the server does not respond within the configured time.",
        "HTTP 401 means unauthorized access.",
        "HTTP 500 indicates a server-side error.",
    ]

    store_chunks(chunks, source=source)

    results = search_similar_chunks("Why did my API request time out?", top_k=3)

    assert len(results["documents"][0]) > 0
    assert len(results["documents"][0]) <= 3
    assert len(results["distances"][0]) == len(results["documents"][0])
    assert results["documents"][0][0] == chunks[0]
    assert results["metadatas"][0][0]["source"] == source
