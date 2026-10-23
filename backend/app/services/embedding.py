from functools import lru_cache

# load embedding model


@lru_cache(maxsize=1)
def get_model():
    """Load the model only when an upload or search first needs it."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embeddings(texts: list[str]):
    """
    Convert a list of text chunks into numerical vectors.
    """
    if not texts:
        return []
    embeddings = get_model().encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
