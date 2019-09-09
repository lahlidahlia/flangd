from utils import *
import subprocess
import json
import fileinput
import sys
from workspace import Workspace
import os


class Server:
    def __init__(self):
        self.handler = {
            'initialize': self.on_initialize,
            'textDocument/definition': self.on_definition,
            'textDocument/didOpen': self.on_did_open,
            'textDocument/didSave': self.on_did_save,
            'textDocument/didChange': self.on_did_change,
            'textDocument/documentSymbol': self.on_document_symbol,
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
        # if body['method'] != 'initialize':
        #eprint("Request body:")
        # eprint("----------------")
        #eprint(json.dumps(body, indent=2))
        # eprint("----------------")
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

        # if method == "initialize":
        #  return
        # eprint("Response")
        # eprint("================")
        # eprint(response)
        # eprint("================")

    def on_initialize(self, params):
        eprint("which f18: " + subprocess.run(["which", "f18"],
                                              stdout=subprocess.PIPE).stdout.decode('utf-8'))
        self.root_uri = params['rootUri']
        self.workspace = Workspace(self.root_uri)
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": True,
                    "save": {
                        "includeText": True
                    }
                },
                # "completionProvider": {
                #    "resolveProvider": False,
                #    "triggerCharacters": ["%"]
                # },
                "definitionProvider": True,
                "documentSymbolProvider": True,
                # "referencesProvider": True,
                # "hoverProvider": True,
                # "implementationProvider": True,
                # "renameProvider": True,
                # "workspaceSymbolProvider": True,
            }
        }

    def on_definition(self, params):
        document_uri = params['textDocument']['uri']
        line = params['position']['line'] + 1
        column = params['position']['character'] + 1

        document = parse_uri(document_uri)
        if not document:
            return None

        output = self.workspace.get_definition(document, line, column)

        if not output:
            return None
        path, line, startColumn, endColumn = output
        document = "file://" + path
        return {
            "uri": document,
            "range": {
                "start": {"line": line - 1, "character": startColumn - 1},
                "end": {"line": line - 1, "character": endColumn - 1},
            },
        }

    def sync_document(self, params, new=False):
        textDocument = params['textDocument']
        # if textDocument['languageId'] != 'Fortran':
        #   return None
        document = parse_uri(textDocument['uri'])
        if not document:
            return None
        content = textDocument['text']
        self.workspace.save_file(document, content, new)

    def on_did_open(self, params):
        self.sync_document(params, new=True)

    def on_did_save(self, params):
        self.sync_document(params)

    def on_did_change(self, params):
        self.sync_document(params)

    def on_document_symbol(self, params):
        document_uri = params['textDocument']['uri']
        document = parse_uri(document_uri)
        if not document:
            return None
        output = self.workspace.get_symbols(document)
        if not output:
            return None
        documentSymbols = []
        for symbol, info in output.items():
            if len(info) == 1:
                eprint("Skipping symbol: " + symbol)
                continue
            path, line, startColumn, endColumn = info
            document = "file://" + path
            start = {"line": line - 1, "character": startColumn - 1}
            end = {"line": line - 1, "character": endColumn - 1}
            documentSymbol = {
                "name": symbol,
                "kind": 6,
                "location": {
                    "uri": document,
                    "range": {
                        "start": start,
                        "end": end,
                    }
                }
            }
            documentSymbols.append(documentSymbol)
        return documentSymbols

    def run(self):
        while True:
            id, body, params = self.read_request()
            self.handle_request(id, body, params)
            sys.stderr.flush()
