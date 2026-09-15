# -*- mode: python -*-
import os, sys
# spec の置き場所から解決する (= 個人の home path を repo に焼かない)。
# SPECPATH は PyInstaller が spec 実行時に注入する = spec を置いた dir。
p = SPECPATH if 'SPECPATH' in globals() else os.path.abspath(os.getcwd())
a = Analysis(['LSBattle3D.py'],
             pathex=[p],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
a.datas = []
def add_data(root, to, remove=[]):
    global add_data, a
    lis = os.listdir(root)
    for name in lis:
        full_name = os.path.join(root, name)
        if os.path.isdir(full_name):
            add_data(full_name, os.path.join(to, name), remove)
        elif os.path.isfile(full_name):
            n, ext = os.path.splitext(name)
            if ext in remove:continue
            a.datas += [(os.path.join(to, name), os.path.join(root, name), "DATA")]

# for i in ["img", "script", "config"]:
#     add_data(os.path.join(p, "../", i), i, [".mqo"])

r = ['bz2', 'cPickle', 'openssl']
binaries = []
for i in a.binaries:
        for n in r:
            if n in i[0]:
                break
        else:
            binaries.append(i)
binaries = binaries + [("SDL2.dll", os.path.abspath(os.path.join(p, "resources/bin/nt/SDL2.dll")), 'BINARY')]
a.binaries = binaries
a.zipfiles = []
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='LSBattle3D.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
