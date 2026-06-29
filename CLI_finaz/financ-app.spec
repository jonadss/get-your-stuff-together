# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['scr/main.py'],
    pathex=['scr'],          # scr/ im sys.path damit relative imports klappen
    binaries=[],
    datas=[('defaults/categories.json', 'defaults')],
    hiddenimports=[
        'pandas',
        'tabulate',
        'rich',
        'prompt_toolkit',
        '_paths',
        'ui_toolkit',
        'ui_styles',
        'request',
        'startup_check',
        'import_csv',
        'bank_csv_bereinigen',
        'categories',
        'budget',
        'debts',
        'evaluation',
    ],
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
    name='financ-app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # CLI-App braucht Konsole
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
