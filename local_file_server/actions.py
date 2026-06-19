"""
Action thực thi trên máy user (mở web, ghi note). Mọi action đều được FE hỏi user xác
nhận TRƯỚC khi gọi tới đây, và endpoint yêu cầu token (xem server.py). Module này lo
phần validate chặt + thực thi.

Nguyên tắc bảo mật:
- Chỉ whitelist đúng các action định nghĩa sẵn (mở URL http/https, ghi file .txt/.md).
- KHÔNG bao giờ exec lệnh tùy ý.
- Ghi note jail trong ROOT_DIR (thư mục user tự chọn) qua _safe_resolve (chống
  path-traversal). User đã chủ động chọn folder này nên note nằm ngay chỗ họ làm việc.
"""
import webbrowser
from urllib.parse import urlparse

from .file_tools import _safe_resolve

# Đuôi file cho phép ghi (note dạng text). Mở rộng sau nếu cần.
WRITE_NOTE_ALLOWED_EXTS = {".txt", ".md"}

# Giới hạn kích thước nội dung note (~1MB).
MAX_NOTE_BYTES = 1 * 1024 * 1024


def open_url(url: str) -> dict:
    """Mở URL bằng trình duyệt mặc định. Chỉ chấp nhận http/https (chặn file://,
    javascript:, data:... để không bị lợi dụng đọc file local / chạy script)."""
    url = (url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Chỉ cho phép URL http hoặc https")
    if not parsed.netloc:
        raise ValueError("URL không hợp lệ")

    opened = webbrowser.open(url)
    if not opened:
        raise ValueError("Không mở được trình duyệt")
    return {"status": "ok", "url": url}


def write_note(root_dir: str, path: str, content: str, overwrite: bool = False) -> dict:
    """Ghi file text trong ROOT_DIR (thư mục user chọn). Jail path, whitelist đuôi,
    giới hạn size, không ghi đè ngầm.

    `path` là đường dẫn tương đối trong ROOT_DIR; đường dẫn tuyệt đối / leo thư mục bị
    _safe_resolve chặn."""
    target = _safe_resolve(root_dir, path)  # raises ValueError nếu path-traversal

    if target.suffix.lower() not in WRITE_NOTE_ALLOWED_EXTS:
        allowed = ", ".join(sorted(WRITE_NOTE_ALLOWED_EXTS))
        raise ValueError(f"Chỉ cho phép ghi file: {allowed}")

    data = (content or "").encode("utf-8")
    if len(data) > MAX_NOTE_BYTES:
        raise ValueError(f"Nội dung quá lớn (> {MAX_NOTE_BYTES // (1024*1024)}MB)")

    if target.exists() and not overwrite:
        raise FileExistsError("File đã tồn tại (bật overwrite để ghi đè)")

    # Tạo thư mục cha nếu chưa có (vẫn trong jail vì target đã qua _safe_resolve).
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)

    return {"status": "ok", "path": path, "bytes": len(data)}
