MAX_TEXT_BYTES = 50 * 1024


def parse_pdf(file_path: str) -> tuple[str, bool]:
    """Extract text from a PDF file."""
    try:
        import pdfplumber
    except ImportError:
        return "[Error: pdfplumber not installed. Run: pip install pdfplumber]", False

    pages = []
    total_len = 0
    truncated = False
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if total_len + len(text) > MAX_TEXT_BYTES:
                remaining = MAX_TEXT_BYTES - total_len
                pages.append(text[:remaining])
                truncated = True
                break
            pages.append(text)
            total_len += len(text)
    return "\n\n".join(pages), truncated
