"""Keep document text, source metadata, and vectors together."""

from pathlib import Path
from uuid import uuid4

import chromadb
from backend.app.core.config import settings


def get_collection():
    storage_path = Path(settings.CHROMA_PATH)
    if not storage_path.is_absolute():
        storage_path = Path(__file__).resolve().parents[3] / storage_path
    client = chromadb.PersistentClient(path=str(storage_path))
    return client.get_or_create_collection(
        name="document_chunks", embedding_function=None
    )


def store_chunks(chunks: list[str | dict], source: str) -> list[str]:
    """Save text strings or chunk dictionaries with their page metadata."""
    if not source.strip():
        raise ValueError("Source cannot be empty")
    if not chunks:
        return []
    texts = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk in chunks]
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Chunks must contain nonempty text strings")

    from backend.app.services.embedding import generate_embeddings

    embeddings = generate_embeddings(texts)
    ids = [uuid4().hex for _ in texts]
    metadata = []
    for index, chunk in enumerate(chunks):
        item = {"source": source, "chunk_index": index}
        if isinstance(chunk, dict):
            item["page_number"] = chunk["page_number"]
        metadata.append(item)
    get_collection().add(
        ids=ids, documents=texts, embeddings=embeddings, metadatas=metadata
    )
    return ids


def search_similar_chunks(query: str, top_k: int = 3) -> dict:
    """Return nearby chunks and distances; smaller distances mean closer matches."""
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be at least 1")

    from backend.app.services.embedding import generate_embeddings

    query_embedding = generate_embeddings([query])[0]
    return get_collection().query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )


def list_documents() -> list[dict]:
    results = get_collection().get(include=["metadatas"])
    counts = {}
    for metadata in results["metadatas"]:
        source = metadata["source"]
        counts[source] = counts.get(source, 0) + 1
    return [
        {"source": source, "chunk_count": count}
        for source, count in sorted(counts.items())
    ]
