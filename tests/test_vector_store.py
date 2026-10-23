import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend.app.services import vector_store


@pytest.mark.parametrize(
    "query, top_k", [(" ", 3), ("timeout", 0), ("timeout", 1.5), ("timeout", True)]
)
def test_invalid_search_does_not_open_collection(monkeypatch, query, top_k):
    get_collection = Mock()
    monkeypatch.setattr(vector_store, "get_collection", get_collection)

    with pytest.raises(ValueError):
        vector_store.search_similar_chunks(query, top_k)

    get_collection.assert_not_called()


def test_search_passes_embedding_and_returns_results(monkeypatch):
    embed = Mock(return_value=[[0.1, 0.2]])
    monkeypatch.setitem(
        sys.modules,
        "backend.app.services.embedding",
        SimpleNamespace(generate_embeddings=embed),
    )
    collection = Mock()
    collection.query.return_value = {"documents": [["Restart the service"]]}
    monkeypatch.setattr(vector_store, "get_collection", lambda: collection)

    result = vector_store.search_similar_chunks("timeout", top_k=2)

    embed.assert_called_once_with(["timeout"])
    collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2]],
        n_results=2,
        include=["documents", "metadatas", "distances"],
    )
    assert result == collection.query.return_value


def test_store_chunks_preserves_text_and_source(monkeypatch):
    embed = Mock(return_value=[[0.1, 0.2], [0.3, 0.4]])
    monkeypatch.setitem(
        sys.modules,
        "backend.app.services.embedding",
        SimpleNamespace(generate_embeddings=embed),
    )
    collection = Mock()
    monkeypatch.setattr(vector_store, "get_collection", lambda: collection)

    ids = vector_store.store_chunks(["timeout", "unauthorized"], "guide.pdf")

    assert len(set(ids)) == 2
    embed.assert_called_once_with(["timeout", "unauthorized"])
    collection.add.assert_called_once_with(
        ids=ids,
        documents=["timeout", "unauthorized"],
        embeddings=[[0.1, 0.2], [0.3, 0.4]],
        metadatas=[
            {"source": "guide.pdf", "chunk_index": 0},
            {"source": "guide.pdf", "chunk_index": 1},
        ],
    )


def test_collection_can_store_and_search_explicit_embeddings(tmp_path, monkeypatch):
    client = vector_store.chromadb.PersistentClient(path=str(tmp_path))
    monkeypatch.setattr(
        vector_store.chromadb, "PersistentClient", lambda **kwargs: client
    )
    collection = vector_store.get_collection()
    collection.add(ids=["chunk-1"], documents=["timeout"], embeddings=[[1.0, 0.0]])

    results = collection.query(query_embeddings=[[1.0, 0.0]], n_results=1)

    assert results["ids"] == [["chunk-1"]]
