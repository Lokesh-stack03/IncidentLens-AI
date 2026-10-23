"""PDF upload and semantic search endpoints."""

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf.errors import PdfReadError

from backend.app.services.document_loader import load_pdf
from backend.app.services.text_chunker import chunk_pages
from backend.app.services import vector_store

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


@router.get("/")
def get_documents():
    return vector_store.list_documents()


@router.post("/upload", status_code=201)
def upload_document(file: UploadFile = File(...)):
    filename = Path((file.filename or "").replace("\\", "/")).name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please select a PDF file.")
    content = file.file.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "PDF must be 10 MB or smaller.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(400, "This file is not a valid PDF.")
    try:
        with TemporaryDirectory() as folder:
            path = Path(folder) / filename
            path.write_bytes(content)
            pages = load_pdf(path)
            chunks = chunk_pages(pages)
        ids = vector_store.store_chunks(chunks, filename)
    except (ValueError, PdfReadError) as exc:
        raise HTTPException(400, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            503, "Document processing is unavailable. Check the model and storage."
        ) from exc
    return {"source": filename, "page_count": len(pages), "chunk_count": len(ids)}


@router.post("/search")
def search_documents(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(400, "Search query cannot be empty.")
    try:
        results = vector_store.search_similar_chunks(request.query, request.top_k)
    except OSError as exc:
        raise HTTPException(
            503, "Search is unavailable. Check the model and storage."
        ) from exc
    return [
        {"id": chunk_id, "text": text, "metadata": metadata, "distance": distance}
        for chunk_id, text, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


@router.delete("/")
def delete_document(source: str):
    collection = vector_store.get_collection()
    existing = collection.get(where={"source": source})
    if not existing["ids"]:
        raise HTTPException(404, "Document not found.")
    collection.delete(ids=existing["ids"])
    return {"deleted_chunks": len(existing["ids"])}
