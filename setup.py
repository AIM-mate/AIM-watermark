from distutils.core import setup
import py2exe

setup(
    data_files=[('',['Logo_aim-drive.ico'])],
    options={'py2exe': {'bundle_files': 2, 'compressed': True}},
    zipfile=None,
    windows=[{'script':'tkinter_app.py',
        'icon_resources': [(1, 'Logo_aim-drive.ico')],
        'dest_base': 'Watermark AIM'}
    ]
)
