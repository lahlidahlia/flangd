#!/usr/bin/env python3
import json
import server
import sys
from utils import *

if __name__ == '__main__':
  f18_path = sys.argv[1]
  f18_args = sys.argv[2]
  s = server.Server(f18_path, f18_args)
  s.run()
