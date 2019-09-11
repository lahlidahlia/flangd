import subprocess
from utils import *
import tempfile


class Compiler:
    def __init__(self, user_root):
        self.user_root = user_root
        self.mod_loc = tempfile.TemporaryDirectory(prefix='flangd_mod_')
        self.compiler = 'f18'
        self.default_flags = ['-fparse-only', '-fdebug-semantics']

    def compile(self, file, extra_flags=[]):
        command = self.construct_command(file, extra_flags)
        eprint("Compilation command: {}".format(command))
        output = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return_code = output.returncode
        stdout = output.stdout.decode('utf-8')
        stderr = output.stderr.decode('utf-8')
        return (return_code, stdout, stderr)

    def compile_content(self, content, extra_flags=[], suffix='.f90'):
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix) as f:
            f.write(content)
            f.flush()
            eprint(f.name)
            return self.compile(f.name, extra_flags)

    def construct_command(self, file, extra_flags):
        return [self.compiler] + ['-module', self.mod_loc.name] + \
            self.default_flags + extra_flags + \
            ["-I" + self.mod_loc.name] + [file]

    def rel_path(self, path):
        # Normalize absolute path to be relative to user's root dir.
        path = path.replace(self.user_root, '', 1)
        path.lstrip('/')
        return path
