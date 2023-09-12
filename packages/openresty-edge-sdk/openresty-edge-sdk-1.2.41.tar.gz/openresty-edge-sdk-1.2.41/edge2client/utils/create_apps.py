#!/usr/bin/python
# -*- coding: UTF-8 -*-
from os import getcwd, path, system, remove, walk
import sys

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)

IMPORT_CODE = 'import py_client\nclient = py_client.get_client()\n'
COMMON_TLDS = ['com', 'net', 'cn', 'org', 'edu']


def gen_n_run(name, root):
    app_file = path.join(root, name)
    with open(app_file) as file_handler:
        content = file_handler.read()
        tmp_file = path.join(path.dirname(__file__), name)
        with open(tmp_file, 'w') as file_writer:
            file_writer.write(IMPORT_CODE)
            file_writer.write(content)

        print('\n-------------- init ------------')
        print('copy <{}> to <{}>'.format(app_file, tmp_file))

        n = system(sys.executable + ' ' + tmp_file)
        if n == 0:
            print('created app with ' + name)
        remove(tmp_file)


def main():
    global_config_file_path = path.join(getcwd(), "global.ini")
    if not path.isfile(global_config_file_path):
        print('ERROR: global.ini: No such File or Directory')
        return 1

    apps_dir = py_client.get_apps_dir()

    if len(sys.argv) > 1 and sys.argv[1]:
        apps_dir = sys.argv[1]

    if not path.isdir(apps_dir):
        return

    for root, dirs, files in walk(apps_dir):
        for name in files:
            gen_n_run(name, root)


if __name__ == '__main__':
    main()
