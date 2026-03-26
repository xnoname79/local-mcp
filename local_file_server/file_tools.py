import os
from pathlib import Path

from .parsers import PARSERS

MAX_FILE_SIZE_MB = 10
MAX_FILES_LIST = 500


def _safe_resolve(root_dir: str, sub_path: str) -> Path:
    """Resolve path safely within root_dir. Raises ValueError on traversal."""
    root = Path(root_dir).resolve()
    target = (root / sub_path).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError(f"Path traversal detected: {sub_path}")
    return target


def list_files(
    root_dir: str, sub_path: str = "", recursive: bool = False
) -> list[dict]:
    """List files in a directory."""
    target = _safe_resolve(root_dir, sub_path)
    if not target.is_dir():
        return []

    items = []
    count = 0

    if recursive:
        for entry in target.rglob("*"):
            if count >= MAX_FILES_LIST:
                break
            if entry.name.startswith("."):
                continue
            rel = str(entry.relative_to(Path(root_dir).resolve()))
            stat = entry.stat()
            items.append(
                {
                    "name": entry.name,
                    "path": rel,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": entry.suffix.lower() if entry.is_file() else "directory",
                    "isDirectory": entry.is_dir(),
                }
            )
            count += 1
    else:
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
            if count >= MAX_FILES_LIST:
                break
            if entry.name.startswith("."):
                continue
            rel = str(entry.relative_to(Path(root_dir).resolve()))
            stat = entry.stat()
            items.append(
                {
                    "name": entry.name,
                    "path": rel,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": entry.suffix.lower() if entry.is_file() else "directory",
                    "isDirectory": entry.is_dir(),
                }
            )
            count += 1

    return items


def read_file(root_dir: str, file_path: str) -> dict:
    """Read and parse a file."""
    target = _safe_resolve(root_dir, file_path)

    if not target.is_file():
        return {"path": file_path, "content": "[Error: File not found]", "type": "", "size": 0, "truncated": False}

    size = target.stat().st_size
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return {
            "path": file_path,
            "content": f"[Error: File too large ({size // (1024*1024)}MB > {MAX_FILE_SIZE_MB}MB limit)]",
            "type": target.suffix.lower(),
            "size": size,
            "truncated": False,
        }

    ext = target.suffix.lower()
    parser = PARSERS.get(ext)
    if not parser:
        return {
            "path": file_path,
            "content": f"[Unsupported file type: {ext}]",
            "type": ext,
            "size": size,
            "truncated": False,
        }

    content, truncated = parser(str(target))
    return {
        "path": file_path,
        "content": content,
        "type": ext,
        "size": size,
        "truncated": truncated,
    }


def search_files(root_dir: str, query: str, sub_path: str = "") -> list[dict]:
    """Search for content across text files."""
    target = _safe_resolve(root_dir, sub_path)
    if not target.is_dir():
        return []

    query_lower = query.lower()
    results = []
    text_extensions = {k for k, v in PARSERS.items() if v.__module__.endswith("text_parser")}

    for entry in target.rglob("*"):
        if not entry.is_file() or entry.name.startswith("."):
            continue
        if entry.suffix.lower() not in text_extensions:
            continue
        if entry.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            continue

        try:
            with open(entry, "r", encoding="utf-8", errors="replace") as f:
                matches = []
                for i, line in enumerate(f, 1):
                    if query_lower in line.lower():
                        matches.append({"lineNumber": i, "lineContent": line.rstrip()[:200]})
                    if len(matches) >= 10:
                        break
                if matches:
                    rel = str(entry.relative_to(Path(root_dir).resolve()))
                    results.append({"path": rel, "matches": matches})
        except Exception:
            continue

        if len(results) >= 20:
            break

    return results
