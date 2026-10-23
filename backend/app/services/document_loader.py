from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str | Path) -> list[dict]:
    """Extract nonempty text pages with their source information."""

    # Convert the supplied filename into a Path object.
    path = Path(file_path)

    # Check that the supplied path points to a file.
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    # Check the file extension.
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    pages = []

    # Open the PDF in binary reading mode.
    with path.open("rb") as pdf_file:
        reader = PdfReader(pdf_file)

        # Password handling is outside this first version.
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported.")

        # Read each page and keep its original page number.
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            # Skip pages that contain no extractable text.
            if not text:
                continue

            pages.append(
                {
                    "text": text,
                    "source": path.name,
                    "page_number": page_number,
                }
            )

    if not pages:
        raise ValueError(
            "No extractable text found. " "The PDF may be empty or require OCR."
        )

    return pages
