"""
Cấu hình chia sẻ cho AINow File Server.

Quản lý file config ~/.ainow-file-server.json (dùng chung bởi server.py + gui.py) và
token bí mật bảo vệ các action endpoint (/actions/*). Token sinh 1 lần lúc cài, lưu
vào config, user dán vào AINow để FE gửi kèm header X-AINow-Token.
"""
import json
import os
import secrets
from pathlib import Path

CONFIG_FILE = os.path.join(Path.home(), ".ainow-file-server.json")

# Header FE gửi kèm khi gọi action endpoint.
TOKEN_HEADER = "X-AINow-Token"


def load_config() -> dict:
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(data: dict):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_or_create_token() -> str:
    """Trả token hiện có; nếu chưa có thì sinh mới (token_urlsafe 32 byte) và lưu lại.
    Idempotent — gọi nhiều lần vẫn ra cùng 1 token (cho tới khi user xoá config)."""
    config = load_config()
    token = config.get("token")
    if not token:
        token = secrets.token_urlsafe(32)
        config["token"] = token
        save_config(config)
    return token
