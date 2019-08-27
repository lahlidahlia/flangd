from compiler import Compiler
from utils import *
import os
import shutil
import tempfile
class Workspace:
  def __init__(self, user_root_uri):
    self.user_root = parse_uri(user_root_uri) + '/'
    self.root = tempfile.mkdtemp(prefix='flangd_') + self.user_root
    self.compilation_order = []
    self.compiler = Compiler(self.root, self.user_root)
    
    eprint("copying: " + self.user_root + " to " + self.root)
    shutil.copytree(self.user_root, self.root)
    if os.path.exists(self.root + '/compilation_order.txt'):
      with open(self.root + '/compilation_order.txt', 'r') as f:
        line = f.readline().rstrip()
        self.compilation_order = line.split(' ')

    if self.compilation_order:
      eprint("Compilation order: " + str(self.compilation_order))
      for f in self.compilation_order:
        self.compiler.compile(f)

  def save_file(self, file, content):
    success = self.compiler.check_compilation(content)
    if not success:
      return False
    with open(file, 'w') as f:
      f.write(content)
    return True

  def get_definitions(self, file, line, column):
    extra_flags = ['-fget-definitions', str(line), str(column)]
    rcode, output = self.compiler.compile(file, extra_flags=extra_flags)
    if rcode == 1:
      return None
    output = output.split(' ')
    start = (int(output[0]), int(output[1]))
    end = (int(output[2]), int(output[3]))
    return (start, end)
