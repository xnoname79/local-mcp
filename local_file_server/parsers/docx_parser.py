MAX_TEXT_BYTES = 50 * 1024


def parse_docx(file_path: str) -> tuple[str, bool]:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
    except ImportError:
        return "[Error: python-docx not installed. Run: pip install python-docx]", False

    doc = Document(file_path)
    paragraphs = []
    total_len = 0
    truncated = False
    for para in doc.paragraphs:
        text = para.text
        if total_len + len(text) > MAX_TEXT_BYTES:
            remaining = MAX_TEXT_BYTES - total_len
            paragraphs.append(text[:remaining])
            truncated = True
            break
        paragraphs.append(text)
        total_len += len(text)
    return "\n".join(paragraphs), truncated
