import pytest
from pypdf import PdfWriter

from backend.app.services.document_loader import load_pdf


def test_missing_pdf_raises_error(tmp_path):
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        load_pdf(missing_file)


def test_blank_pdf_raises_error(tmp_path):
    blank_file = tmp_path / "blank.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)

    with blank_file.open("wb") as pdf_file:
        writer.write(pdf_file)

    with pytest.raises(ValueError, match="No extractable text found"):
        load_pdf(blank_file)
