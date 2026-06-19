# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['local_file_server', 'local_file_server.server', 'local_file_server.file_tools', 'local_file_server.actions', 'local_file_server.config', 'local_file_server.parsers', 'local_file_server.parsers.text_parser', 'local_file_server.parsers.pdf_parser', 'local_file_server.parsers.docx_parser', 'local_file_server.parsers.xlsx_parser', 'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'fastapi', 'pdfplumber', 'docx', 'openpyxl']
hiddenimports += collect_submodules('pdfplumber')
hiddenimports += collect_submodules('pdfminer')


a = Analysis(
    ['local_file_server/gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ainow-file-server-linux',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
