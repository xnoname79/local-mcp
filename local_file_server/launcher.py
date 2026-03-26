"""
AINow Local File Server — Standalone launcher
User chạy file này (hoặc binary), nhập folder path, server tự start.
"""
import os
import sys
import webbrowser

def get_root_dir():
    """Prompt user for root directory or use command line arg."""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("=" * 50)
        print("  AINow Local File Server")
        print("=" * 50)
        print()
        print("This server allows your AI agent to read files")
        print("from a folder on your computer.")
        print()
        path = input("Enter folder path to share: ").strip()

    # Expand ~ and resolve
    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    if not os.path.isdir(path):
        print(f"\nError: '{path}' is not a valid directory.")
        input("Press Enter to exit...")
        sys.exit(1)

    return path


def main():
    root_dir = get_root_dir()
    os.environ["ROOT_DIR"] = root_dir

    port = int(os.environ.get("PORT", "8765"))

    print(f"\nSharing folder: {root_dir}")
    print(f"Server running at: http://localhost:{port}")
    print(f"Health check:      http://localhost:{port}/health")
    print()
    print("Keep this window open while using AINow.")
    print("Press Ctrl+C to stop.\n")

    import uvicorn
    from local_file_server.server import app

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
