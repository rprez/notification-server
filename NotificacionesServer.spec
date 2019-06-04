# -*- mode: python -*-

block_cipher = None


a = Analysis(['uteNotiServer.py'],
             pathex=['C:\\Repositorios\\UteAntelmMmgt'],
             binaries=[],
             datas=[('gui/imagenes/*','gui/imagenes') , ('driver/jsonkeymap.json','driver'),('udpserverconfig.json','udpserverconfig.json')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='notiserver',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='uteNotiServer')
