from backend.app.services.embedding import generate_embeddings


def test_generate_embeddings():
    tests = ["API request timed out", "Service returned HTTP 500"]
    embeddings = generate_embeddings(tests)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
