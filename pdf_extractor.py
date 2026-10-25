"""
pdf_extractor.py
────────────────
Helper utilities for extracting clean text from uploaded PDF resumes.
"""

import pdfplumber
import re
from io import BytesIO


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract and clean raw text from a Streamlit UploadedFile (PDF).

    Args:
        uploaded_file: Streamlit's UploadedFile object (BytesIO-compatible).

    Returns:
        A single cleaned string containing all visible text from the PDF.

    Raises:
        ValueError: If the PDF contains no extractable text (e.g., scanned image).
    """
    raw_pages: list[str] = []

    # Read bytes from the uploaded file buffer
    pdf_bytes = BytesIO(uploaded_file.read())

    with pdfplumber.open(pdf_bytes) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                raw_pages.append(page_text)

    if not raw_pages:
        raise ValueError(
            "No extractable text found in the PDF. "
            "Make sure your resume is not a scanned image."
        )

    full_text = "\n".join(raw_pages)
    return _clean_text(full_text)


def _clean_text(text: str) -> str:
    """
    Normalize whitespace and remove junk characters from extracted PDF text.
    """
    # Collapse multiple blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove non-printable / control characters (keep newlines & tabs)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", "", text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()


def word_count(text: str) -> int:
    """Return approximate word count of a string."""
    return len(text.split())
