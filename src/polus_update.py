import threading

import PyInstaller.__main__
from os import rename
from os.path import dirname, realpath, join


def pyinstaller_thread():
    PyInstaller.__main__.run([
        'polus.spec',
        'y'
    ])


if __name__ == '__main__':
    pyinstaller_thread()
    app_version = '1.1.1'
    script_path = str(dirname(realpath(__file__))).replace('polus_update.py', '')
    dist_path = join(dirname(realpath(__file__)), 'dist')
    old, new = join(dist_path, 'polus'), join(dist_path, f'DFS Polus [{app_version}]')
    rename(old, new)
    print(f'DFS Polus updated successfully!\n\n{new}')
