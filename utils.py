import sys

def eprint(*args):
  print("flangd: {}".format(*args), file=sys.stderr)
  sys.stderr.flush()

def parse_uri(uri):
  if uri == None:
    return None
  scheme, document_path = uri.split('://')
  if scheme != 'file':
    return None
  return document_path
