#!/usr/bin/python
# -*- coding: UTF-8 -*-
from os import getcwd, path, system, remove
import sys

IMPORT_CODE = 'import py_client\nclient = py_client.get_client()\n'


def main(app_file):
    if path.isfile(app_file):
        with open(app_file) as file_handler:
            content = file_handler.read()
            name = path.basename(app_file)
            tmp_file = path.join(path.dirname(__file__), name)
            with open(tmp_file, 'w') as file_writer:
                file_writer.write(IMPORT_CODE)
                file_writer.write(content)
            print('-------------- init ------------\n')
            print('copy <{}> to <{}>'.format(app_file, tmp_file))
            system(sys.executable + ' ' + tmp_file)
            print('created app with ' + name)
            remove(tmp_file)
    else:
        print(app_file + ' is not a file')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        APP_FILE = sys.argv[1]
        main(APP_FILE)
    else:
        print('app_file required')
