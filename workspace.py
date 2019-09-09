from compiler import Compiler
from utils import *
import os
import shutil
import tempfile
from file import File


class Workspace:
    def __init__(self, user_root_uri):
        self.user_root = parse_uri(user_root_uri) + '/'
        self.compiler = Compiler(self.user_root)
        self.files = {}
        compilation_order = []

        if os.path.exists(self.user_root + '/compilation_order.txt'):
            with open(self.user_root + '/compilation_order.txt', 'r') as f:
                line = f.readline().rstrip()
                compilation_order = line.split(' ')

        if compilation_order:
            eprint("Compilation order: " + str(compilation_order))
            for f in compilation_order:
                self.compiler.compile(f)

    def save_file(self, path, content, new=False):
        if new:
            self.files[path] = File(path, content, self.compiler)
        else:
            if path in self.files:
                self.files[path].update_content(content)

    def get_symbols(self, path):
        if path in self.files:
            return self.files[path].get_symbols()
        else:
            return None

    def get_definition(self, path, line, column):
        if path in self.files:
            return self.files[path].get_definition(line, column)
        else:
            return None

    def rel_path(self, path):
        # Normalize absolute path to be relative to user's root dir.
        path = path.replace(self.user_root, '', 1)
        path.lstrip('/')
        return path
