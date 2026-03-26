#!/bin/bash
# Build AINow File Server — standalone binary with GUI
# Usage: ./build_binary.sh [--cli]
#   --cli  Build CLI version (no GUI, for servers/headless)
#   default: Build GUI version (Tkinter)

set -e
cd "$(dirname "$0")"

MODE="gui"
if [ "$1" = "--cli" ]; then
  MODE="cli"
fi

echo "==================================="
echo "  AINow File Server — Build"
echo "  Mode: $MODE"
echo "==================================="

pip install pyinstaller 2>/dev/null

COMMON_ARGS=(
  --onefile
  --hidden-import=local_file_server
  --hidden-import=local_file_server.server
  --hidden-import=local_file_server.file_tools
  --hidden-import=local_file_server.parsers
  --hidden-import=local_file_server.parsers.text_parser
  --hidden-import=local_file_server.parsers.pdf_parser
  --hidden-import=local_file_server.parsers.docx_parser
  --hidden-import=local_file_server.parsers.xlsx_parser
  --hidden-import=uvicorn
  --hidden-import=uvicorn.logging
  --hidden-import=uvicorn.loops
  --hidden-import=uvicorn.loops.auto
  --hidden-import=uvicorn.protocols
  --hidden-import=uvicorn.protocols.http
  --hidden-import=uvicorn.protocols.http.auto
  --hidden-import=uvicorn.protocols.websockets
  --hidden-import=uvicorn.protocols.websockets.auto
  --hidden-import=uvicorn.lifespan
  --hidden-import=uvicorn.lifespan.on
  --hidden-import=fastapi
  --hidden-import=pdfplumber
  --hidden-import=docx
  --hidden-import=openpyxl
  --collect-submodules=pdfplumber
  --collect-submodules=pdfminer
)

# Detect OS for naming
OS_NAME="linux"
EXTRA_ARGS=()
if [[ "$OSTYPE" == "darwin"* ]]; then
  OS_NAME="macos"
  if [ "$MODE" = "gui" ]; then
    EXTRA_ARGS+=(--windowed)
  fi
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OS" == "Windows_NT" ]]; then
  OS_NAME="windows"
  if [ "$MODE" = "gui" ]; then
    EXTRA_ARGS+=(--windowed)
  fi
fi

BINARY_NAME="ainow-file-server-${OS_NAME}"
ENTRY_POINT="local_file_server/gui.py"
if [ "$MODE" = "cli" ]; then
  BINARY_NAME="ainow-file-server-${OS_NAME}-cli"
  ENTRY_POINT="local_file_server/launcher.py"
fi

echo ""
echo "Building: $BINARY_NAME"
echo "Entry: $ENTRY_POINT"
echo ""

pyinstaller \
  "${COMMON_ARGS[@]}" \
  "${EXTRA_ARGS[@]}" \
  --name "$BINARY_NAME" \
  "$ENTRY_POINT"

echo ""
echo "Build complete!"
echo "Binary: dist/$BINARY_NAME"
echo ""
echo "To run: ./dist/$BINARY_NAME"
