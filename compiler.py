import subprocess
from utils import *

class Compiler:
  def __init__(self, root, user_root):
    self.root = root
    self.user_root = user_root
    self.mod_loc = self.root
    self.compiler = 'f18'
    self.default_flags = ['-fparse-only', '-fdebug-semantics']

  def compile(self, file, extra_flags=[], is_abs=False):
    command = self.construct_command(file, extra_flags, is_abs)
    eprint("Compilation commands: " + str(command))
    output = subprocess.run(command, stdout=subprocess.PIPE)
    return_code = output.returncode
    output = output.stdout.decode('utf-8')
    return (return_code, output)

  def construct_command(self, file, extra_flags, is_abs):
    if not is_abs:
      file = self.rel_path(file)
      file = self.root + file
    return [self.compiler] + ['-module', self.mod_loc] + self.default_flags \
           + extra_flags + ["-I" + self.mod_loc] + [file]

  def check_compilation(self, content):
    tmp_file = self.mkstmp()
    with open(tmp_file, 'w') as f:
      f.write(content)
    code, _ = self.compile(tmp_file, is_abs=True)
    return True if code == 0 else False

  def rel_path(self, path):
  # Normalize absolute path to be relative to user's root dir.
    path = path.replace(self.user_root, '', 1)
    path.lstrip('/')
    return path
