from .text_parser import parse_text
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .xlsx_parser import parse_xlsx

PARSERS = {
    # Text / code files
    ".txt": parse_text,
    ".md": parse_text,
    ".json": parse_text,
    ".csv": parse_text,
    ".py": parse_text,
    ".js": parse_text,
    ".ts": parse_text,
    ".tsx": parse_text,
    ".jsx": parse_text,
    ".html": parse_text,
    ".css": parse_text,
    ".scss": parse_text,
    ".yaml": parse_text,
    ".yml": parse_text,
    ".toml": parse_text,
    ".xml": parse_text,
    ".sql": parse_text,
    ".sh": parse_text,
    ".bash": parse_text,
    ".env": parse_text,
    ".gitignore": parse_text,
    ".dockerignore": parse_text,
    ".go": parse_text,
    ".rs": parse_text,
    ".java": parse_text,
    ".c": parse_text,
    ".cpp": parse_text,
    ".h": parse_text,
    ".rb": parse_text,
    ".php": parse_text,
    ".swift": parse_text,
    ".kt": parse_text,
    ".dart": parse_text,
    ".r": parse_text,
    ".lua": parse_text,
    # Rich documents
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".xlsx": parse_xlsx,
}
