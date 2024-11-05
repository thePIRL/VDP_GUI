# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['VDP_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['nibabel==5.2.0', 'numpy==1.24.4', 'openpyxl==3.1.2', 'Pillow==10.2.0', 'PySimpleGUI==4.60.5', 'scipy==1.12.0'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VDP_GUI',
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
    icon=['pirl.ico'],
)
