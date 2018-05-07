#!/usr/bin/env python3.6

import sys
from importlib import import_module
from os import walk
from os.path import relpath, splitext

from andreas.app import app
from andreas.commands.dbcommands import dropdb, populatedb, resetdb, updatedb

for dirpath, dirnames, filenames in walk(app.root_path + '/andreas'):
    for filename in filenames:
        if filename[-3:] == '.py' and filename != '__init__.py':
            module_path = relpath(dirpath, app.root_path).replace('/', '.') + '.' + splitext(filename)[0]
            import_module(module_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        functions = [
            populatedb,
            updatedb,
            dropdb,
            resetdb,
        ]
        for func in functions:
            if func.__name__ == sys.argv[1]:
                exit(func(*sys.argv[2:]))
    
    app.run()