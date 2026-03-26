"""
AINow File Server — Desktop GUI
Cross-platform Tkinter app. User chọn folder → Start → server chạy background.
"""
import json
import logging
import os
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, scrolledtext

CONFIG_FILE = os.path.join(Path.home(), ".ainow-file-server.json")
DEFAULT_PORT = 8765


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


class LogHandler(logging.Handler):
    """Redirect uvicorn logs to the GUI text widget."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(msg)


class AINowFileServerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AINow File Server")
        self.root.geometry("520x460")
        self.root.minsize(420, 380)
        self.root.resizable(True, True)

        self.server_thread = None
        self.server_running = False
        self.uvicorn_server = None

        config = load_config()
        self.last_folder = config.get("root_dir", str(Path.home()))

        self._build_ui()
        self._apply_theme()

    def _apply_theme(self):
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#4a90d9"
        entry_bg = "#16213e"
        btn_bg = "#0f3460"
        btn_fg = "#ffffff"
        log_bg = "#0d1117"

        self.root.configure(bg=bg)

        for widget in [self.title_label, self.folder_label, self.status_label, self.log_label]:
            widget.configure(bg=bg, fg=fg)

        self.folder_entry.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        self.log_text.configure(bg=log_bg, fg="#a0d0a0", insertbackground=fg)

        self.browse_btn.configure(bg=btn_bg, fg=btn_fg, activebackground=accent)
        self.start_btn.configure(bg="#1b7a3d", fg=btn_fg, activebackground="#22a34a")
        self.stop_btn.configure(bg="#8b2020", fg=btn_fg, activebackground="#b03030")

        self.status_dot.configure(bg=bg)

        for frame in [self.top_frame, self.folder_frame, self.status_frame,
                       self.btn_frame, self.log_frame]:
            frame.configure(bg=bg)

    def _build_ui(self):
        # Title
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill="x", padx=12, pady=(12, 4))
        self.title_label = tk.Label(
            self.top_frame, text="AINow File Server",
            font=("Helvetica", 16, "bold"),
        )
        self.title_label.pack(side="left")

        # Folder picker
        self.folder_frame = tk.Frame(self.root)
        self.folder_frame.pack(fill="x", padx=12, pady=4)
        self.folder_label = tk.Label(self.folder_frame, text="Shared Folder:", font=("Helvetica", 10))
        self.folder_label.pack(anchor="w")

        entry_row = tk.Frame(self.folder_frame)
        entry_row.pack(fill="x", pady=(4, 0))
        self.folder_entry = tk.Entry(entry_row, font=("Courier", 10))
        self.folder_entry.pack(side="left", fill="x", expand=True)
        self.folder_entry.insert(0, self.last_folder)

        self.browse_btn = tk.Button(
            entry_row, text=" Browse ", command=self._browse_folder,
            font=("Helvetica", 9),
        )
        self.browse_btn.pack(side="right", padx=(6, 0))
        entry_row.configure(bg=self.root.cget("bg"))

        # Status
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(fill="x", padx=12, pady=(8, 4))

        self.status_dot = tk.Canvas(self.status_frame, width=12, height=12, highlightthickness=0)
        self.status_dot.pack(side="left")
        self._draw_dot("red")

        self.status_label = tk.Label(
            self.status_frame, text="  Stopped",
            font=("Helvetica", 10),
        )
        self.status_label.pack(side="left")

        # Buttons
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill="x", padx=12, pady=4)

        self.start_btn = tk.Button(
            self.btn_frame, text="  Start  ", command=self._start_server,
            font=("Helvetica", 10, "bold"), width=10,
        )
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(
            self.btn_frame, text="  Stop  ", command=self._stop_server,
            font=("Helvetica", 10, "bold"), width=10, state="disabled",
        )
        self.stop_btn.pack(side="left")

        # Log
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        self.log_label = tk.Label(self.log_frame, text="Log:", font=("Helvetica", 10))
        self.log_label.pack(anchor="w")

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, height=10, font=("Courier", 9),
            state="disabled", wrap="word",
        )
        self.log_text.pack(fill="both", expand=True, pady=(4, 0))

    def _draw_dot(self, color):
        self.status_dot.delete("all")
        self.status_dot.create_oval(2, 2, 10, 10, fill=color, outline=color)

    def _log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}\n"

        def _append():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", line)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        self.root.after(0, _append)

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_entry.get())
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def _start_server(self):
        folder = self.folder_entry.get().strip()
        if not folder or not os.path.isdir(folder):
            self._log("Error: Invalid folder path")
            return

        os.environ["ROOT_DIR"] = folder
        save_config({"root_dir": folder, "port": DEFAULT_PORT})

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.folder_entry.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self._draw_dot("#22c55e")
        self.status_label.configure(text=f"  Running on port {DEFAULT_PORT}")
        self._log(f"Starting server on port {DEFAULT_PORT}...")
        self._log(f"Sharing: {folder}")

        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

    def _run_server(self):
        import uvicorn

        # Setup log handler to redirect to GUI
        log_handler = LogHandler(self._log)
        log_handler.setFormatter(logging.Formatter("%(message)s"))

        config = uvicorn.Config(
            "local_file_server.server:app",
            host="127.0.0.1",
            port=DEFAULT_PORT,
            log_level="info",
        )
        self.uvicorn_server = uvicorn.Server(config)

        # Redirect uvicorn access log
        access_logger = logging.getLogger("uvicorn.access")
        access_logger.addHandler(log_handler)
        error_logger = logging.getLogger("uvicorn.error")
        error_logger.addHandler(log_handler)

        self.server_running = True
        self._log("Server started successfully")

        try:
            self.uvicorn_server.run()
        except Exception as e:
            self._log(f"Server error: {e}")
        finally:
            self.server_running = False
            self.root.after(0, self._on_server_stopped)

    def _stop_server(self):
        if self.uvicorn_server:
            self._log("Stopping server...")
            self.uvicorn_server.should_exit = True

    def _on_server_stopped(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.folder_entry.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self._draw_dot("red")
        self.status_label.configure(text="  Stopped")
        self._log("Server stopped")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        self.root.destroy()


def main():
    app = AINowFileServerApp()
    app.run()


if __name__ == "__main__":
    main()
