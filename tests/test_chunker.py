import pytest

from backend.app.services.text_chunker import chunk_pages


def test_chunks_preserve_overlap_and_metadata():
    pages = [
        {
            "text": "ABCDEFGHIJKLMNOPQRST",
            "source": "sample.pdf",
            "page_number": 3,
        }
    ]

    chunks = chunk_pages(pages, chunk_size=10, overlap=3)

    assert [chunk["text"] for chunk in chunks] == [
        "ABCDEFGHIJ",
        "HIJKLMNOPQ",
        "OPQRST",
    ]

    assert [chunk["chunk_index"] for chunk in chunks] == [0, 1, 2]
    assert [chunk["start_char"] for chunk in chunks] == [0, 7, 14]
    assert [chunk["end_char"] for chunk in chunks] == [10, 17, 20]

    for chunk in chunks:
        assert chunk["source"] == "sample.pdf"
        assert chunk["page_number"] == 3

    assert chunks[0]["text"][-3:] == chunks[1]["text"][:3]
    assert chunks[1]["text"][-3:] == chunks[2]["text"][:3]


@pytest.mark.parametrize(
    "chunk_size, overlap",
    [
        (0, 0),
        (-1, 0),
        (10, -1),
        (10, 10),
        (10, 11),
    ],
)
def test_invalid_chunk_settings_raise_error(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_pages(
            [],
            chunk_size=chunk_size,
            overlap=overlap,
        )
