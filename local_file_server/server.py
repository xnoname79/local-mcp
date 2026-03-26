import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import file_tools

app = FastAPI(title="AINow Local File Server")

# CORS — allow FE dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mutable config
_config = {
    "root_dir": os.environ.get("ROOT_DIR", os.path.expanduser("~")),
}


class ConfigUpdate(BaseModel):
    root_dir: str


@app.get("/health")
def health():
    return {"status": "ok", "root_dir": _config["root_dir"]}


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
