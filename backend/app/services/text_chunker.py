def chunk_pages(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[dict]:
    """Split page text into overlapping chunks with source metadata."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be zero or greater and less than chunk_size.")

    chunks = []

    for page in pages:
        text = page["text"]
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunks.append(
                    {
                        "text": chunk_text,
                        "source": page["source"],
                        "page_number": page["page_number"],
                        "chunk_index": chunk_index,
                        "start_char": start,
                        "end_char": end,
                    }
                )
                chunk_index += 1

            if end == len(text):
                break

            start = end - overlap

    return chunks
