import os

from fastapi import FastAPI, Query, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import file_tools, actions
from .config import get_or_create_token, TOKEN_HEADER

app = FastAPI(title="AINow File Server")

# CORS — chỉ cho phép origin của AINow (web + dev). KHÔNG dùng "*" nữa: server này
# chạy ở localhost máy user, mở toác = bất kỳ web nào cũng gọi được action endpoint.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://([a-z0-9-]+\.)*getainow\.site$|^http://(localhost|127\.0\.0\.1):\d+$",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", TOKEN_HEADER],
)

# Token bí mật bảo vệ action endpoint. Sinh 1 lần, lưu trong ~/.ainow-file-server.json.
_TOKEN = get_or_create_token()

# Mutable config
_config = {
    "root_dir": os.environ.get("ROOT_DIR", os.path.expanduser("~")),
}


def _require_token(token: str = Header(None, alias=TOKEN_HEADER)):
    """Guard cho /actions/* — các thao tác có side-effect (mở web, ghi file) trên máy
    user. Đọc file (/files/*) tạm chưa bắt buộc token (ít rủi ro hơn); sẽ siết sau."""
    if token != _TOKEN:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


class ConfigUpdate(BaseModel):
    root_dir: str


class OpenUrlRequest(BaseModel):
    url: str
    reason: str = ""


class WriteNoteRequest(BaseModel):
    path: str
    content: str
    overwrite: bool = False


@app.get("/health")
def health():
    # requires_token cho FE biết server có yêu cầu token cho action (luôn true từ bản này).
    return {"status": "ok", "root_dir": _config["root_dir"], "requires_token": True}


@app.get("/config")
def get_config():
    return _config


@app.post("/config")
def update_config(body: ConfigUpdate):
    path = os.path.expanduser(body.root_dir)
    if not os.path.isdir(path):
        return {"error": f"Directory not found: {path}"}
    _config["root_dir"] = path
    return {"status": "ok", "root_dir": path}


@app.get("/files")
def list_files(
    path: str = Query("", description="Subdirectory relative to root"),
    recursive: bool = Query(False),
):
    try:
        items = file_tools.list_files(_config["root_dir"], path, recursive)
        return {"files": items, "root_dir": _config["root_dir"], "path": path}
    except ValueError as e:
        return {"error": str(e), "files": []}


@app.get("/files/read")
def read_file(path: str = Query(..., description="File path relative to root")):
    try:
        result = file_tools.read_file(_config["root_dir"], path)
        return result
    except ValueError as e:
        return {"error": str(e)}


@app.get("/files/search")
def search_files(
    query: str = Query(..., description="Search query"),
    path: str = Query("", description="Subdirectory to search in"),
):
    try:
        results = file_tools.search_files(_config["root_dir"], query, path)
        return {"results": results, "query": query}
    except ValueError as e:
        return {"error": str(e), "results": []}


# ── Actions (side-effect trên máy user) — đều cần token, luôn được FE hỏi user trước ──

@app.post("/actions/open-url")
def open_url(body: OpenUrlRequest, token: str = Header(None, alias=TOKEN_HEADER)):
    _require_token(token)
    try:
        return actions.open_url(body.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/actions/write-note")
def write_note(body: WriteNoteRequest, token: str = Header(None, alias=TOKEN_HEADER)):
    _require_token(token)
    try:
        # Ghi note vào ROOT_DIR (thư mục user chọn) — cùng nơi đọc file.
        return actions.write_note(_config["root_dir"], body.path, body.content, body.overwrite)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
