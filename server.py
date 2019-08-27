from utils import *
import subprocess
import json
import fileinput
import sys
from workspace import Workspace

class Server:
  def __init__(self):
    self.handler = {
      'initialize': self.on_initialize,
      'textDocument/definition': self.on_definition,
      'textDocument/didSave': self.on_did_save,
      'textDocument/didChange': self.on_did_change,
    }
    self.root_uri = None
    self.workspace = None


  def read_header_length(self, line):
    value = line.split("Content-Length: ")[1]
    value = value.strip()
    return int(value)

  def read_request(self):
      line = sys.stdin.readline() 
      length = self.read_header_length(line)
      while line != "\r\n":
        line = sys.stdin.readline()
      body = json.loads(sys.stdin.read(length))
      if body['method'] != 'initialize':
        eprint("Request body:")
        eprint("----------------")
        eprint(json.dumps(body, indent=2))
        eprint("----------------")
      return body.get('id', None), body['method'], body['params']

  def handle_request(self, id, method, params):
    eprint("Handling request with id {} and method {}".format(id, method))
    body = {
      "jsonrpc": "2.0",
      "id": id,
    }
    body['result'] = self.handler.get(method, lambda *args: None)(params)
    body = json.dumps(body, separators=(",", ":"))
    if id == None:
      # No id means no need to respond.
      return
    content_length = len(body)
    response = (
        "Content-Length: {0}\r\n"
        "Content-Type: application/vscode-jsonrpc; charset=utf8\r\n\r\n"
        "{1}".format(content_length, body))
    sys.stdout.write(response)
    sys.stdout.flush()

    if method == "initialize":
      return
    eprint("Response")
    eprint("================")
    eprint(response)
    eprint("================")

  def on_initialize(self, params):
    self.root_uri = params['rootUri']
    self.workspace = Workspace(self.root_uri)
    return {
      "capabilities": {
        "textDocumentSync": 1,
        #"completionProvider": {
        #    "resolveProvider": False,
        #    "triggerCharacters": ["%"]
        #},
        "definitionProvider": True,
        #"documentSymbolProvider": True,
        #"referencesProvider": True,
        #"hoverProvider": True,
        #"implementationProvider": True,
        #"renameProvider": True,
        #"workspaceSymbolProvider": True,
      }
    }

  def on_definition(self, params):
    document_uri = params['textDocument']['uri']
    line = params['position']['line'] + 1
    column = params['position']['character'] + 1

    document = parse_uri(document_uri)
    if not document:
      return None

    output = self.workspace.get_definitions(document, line, column)
    if not output:
      return None
    start, end = output
    document = "file://" + document
    start = {"line": start[0] - 1, "character": start[1] - 1}
    end = {"line": end[0] - 1, "character": end[1] - 1}
    return {
      "uri": document,
      "range": {
        "start": start,
        "end": end,
      },
    }

  def on_did_save(self, params):
    pass

  def on_did_change(self, params):
    pass

  def run(self):
    while True:
      id, body, params = self.read_request()
      self.handle_request(id, body, params)
      sys.stderr.flush()
