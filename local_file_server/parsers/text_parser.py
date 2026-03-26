MAX_TEXT_BYTES = 50 * 1024  # 50KB


def parse_text(file_path: str) -> tuple[str, bool]:
    """Read a text file. Returns (content, truncated)."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(MAX_TEXT_BYTES + 1)
    truncated = len(content) > MAX_TEXT_BYTES
    if truncated:
        content = content[:MAX_TEXT_BYTES]
    return content, truncated
