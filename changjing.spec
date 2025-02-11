# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

block_cipher = None

# 收集 OpenCV 的动态链接库
opencv_binaries = collect_dynamic_libs('cv2')
# 收集 numpy 的数据文件
numpy_data = collect_data_files('numpy')

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=opencv_binaries,
    datas=[
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
    ] + numpy_data,
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL',
        'requests',
        'werkzeug.middleware.proxy_fix',
        'jinja2.ext',
        'flask',
        'werkzeug',
        'numpy.core._methods',
        'numpy.lib.format',
        'numpy.random',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
        'PIL._imaging',
        'PIL.Image',
        'engineio.async_drivers.threading',
        'jinja2.ext.do',
        'jinja2.ext.loopcontrols',
        'flask.cli',
        'flask.json',
        'flask.json.tag',
        'flask.templating',
        'flask.wrappers',
        'flask.sessions',
        'flask.signals',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoSceneAnalysis',
    debug=True,  # 添加调试信息
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
    icon='app/static/icon.ico'
) 