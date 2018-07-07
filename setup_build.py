from glob import glob
from cx_Freeze import setup, Executable

import sys, os
sys.path.append('./bigglesworth/editorWidgets')

WIN, OSX = 0, 1
platform = WIN if sys.platform=='win32' else OSX

MAJ_VERSION, MIN_VERSION, REV_VERSION = 0, 0, 0

def read_version():
    with open('bigglesworth/version.py', 'rb') as version_file:
        exec(version_file.read())
    return MAJ_VERSION, MIN_VERSION, REV_VERSION
v = read_version()

versionDot = '{}.{}.{}'.format(*v)
versionComma = '{},{},{}'.format(*v)
description = 'Editor/librarian for Blofeld'

if os.path.exists('versionInfo'):
    with open('versionInfo', 'r') as vi:
        versionDotFile = vi.readline().strip('\r\n')
        build = int(vi.readline().strip('\r\n'))
else:
    versionDotFile = versionDot
    build = 0
if versionDot != versionDotFile:
    build = '0'
else:
    build = str(build + 1)

with open('versionInfo', 'w') as vi:
    vi.write(versionDot + '\n')
    vi.write(build + '\n')

versionDot += '.' + build
versionComma += ',' + build

print('\nBuilding version {}\n\n'.format(versionDot))
resData = '''

1 VERSIONINFO
FILEVERSION {versionComma}
PRODUCTVERSION {versionComma}
FILEOS 0x40004
FILETYPE 0x1
{{
BLOCK "StringFileInfo"
{{
	BLOCK "040904E4"
	{{
		VALUE "LegalCopyright", ""
		VALUE "InternalName", "Bigglesworth.exe"
		VALUE "FileVersion", "{versionDot}"
		VALUE "CompanyName", ""
		VALUE "OriginalFilename", "Bigglesworth.exe"
		VALUE "ProductVersion", "{versionDot}"
		VALUE "FileDescription", "{description}"
		VALUE "LegalTrademarks", ""
		VALUE "Comments", ""
		VALUE "ProductName", "Bigglesworth"
	}}
}}

BLOCK "VarFileInfo"
{{
	VALUE "Translation", 0x0409 0x04E4  
}}
}}
'''.format(versionComma=versionComma, versionDot=versionDot, description=description)


files = [
    'bigglesworth/presets/blofeld_fact_200801.mid', 
    'bigglesworth/presets/blofeld_fact_200802.mid', 
    'bigglesworth/presets/blofeld_fact_201200.mid', 
    ]

files.extend(glob('bigglesworth/ui/*.ui'))
files.extend(glob('resources/*.svg'))
files.extend(glob('resources/*.png'))
#files.extend(glob('bigglesworth/editorWidgets/*py'))
#files.extend(glob('bigglesworth/editorWidgets/*json'))

files = zip(files, files)
files.append(('bigglesworth/editorWidgets/pianokbmap.json', 'pianokbmap.json'))

includes = ['atexit', 'PyQt4.QtSql', 
#   custom widgets
    'colorselectbutton', 
    'combo', 
    'dial', 
    'frame', 
    'pianokeyboard', 
    'slider', 
    'squarebutton', 
    'stackedwidget', 
    ]


if platform == WIN:
    base = 'Win32GUI'

    executables = [
#        Executable('Bigglesworth.py', base=base, icon='resources/bigglesworth_icon.ico')
        Executable('Bigglesworth.py', base=base), 
        Executable('Bigglesworth.py', base='Console', targetName='BigglesworthDebug.exe')
    ]

else:
    base = None

    files.append(('/opt/local/libexec/qt4/share/plugins/sqldrivers', 'sqldrivers'))

    executables = [
        Executable('Bigglesworth.py', base=base, targetName = 'Bigglesworth'), 
        Executable('Bigglesworth.py', base='Console', targetName='BigglesworthDebug')
    ]

buildOptions = dict(packages = [], excludes = [], includes = includes, include_files = files)
macbuildOptions = {'iconfile': 'resources/bigglesworth_icon.icns', 'bundle_name': 'BigglesworthBeta'}
dmgOptions = {'applications_shortcut': True}

setup(name='Bigglesworth',
      version = versionDot,
      description = description,
      options = dict(build_exe = buildOptions, bdist_mac = macbuildOptions),
      executables = executables)

if platform == WIN:
    with open('build/winResource.rc', 'w') as winFile:
        winFile.write(resData)
    

