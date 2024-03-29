from utils import *
import subprocess
import json
import fileinput
import sys
from workspace import Workspace
import os


class Server:
    def __init__(self, f18_path, f18_args):
        self.handler = {
            'initialize': self.on_initialize,
            'initialized': self.after_initialize,
            'textDocument/definition': self.on_definition,
            'textDocument/didOpen': self.on_did_open,
            'textDocument/didSave': self.on_did_save,
            'textDocument/didChange': self.on_did_change,
            'textDocument/didClose': self.on_did_close,
            'textDocument/documentSymbol': self.on_document_symbol,
        }
        self.root_uri = None
        self.workspace = None
        self.f18_path = f18_path
        self.f18_args = f18_args

    def run(self):
        while True:
            id, body, params = self.read_request()
            self.handle_request(id, body, params)
            sys.stderr.flush()

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
        return body.get('id', None), body['method'], body['params']

    def handle_request(self, id, method, params):
        response = self.handler.get(method, lambda *args: None)(params)
        if id == None:
            eprint("Received notification with method {}".format(method))
        else:
            eprint("Handling request with id {} and method {}".format(
                id, method))
            self.respond_request(response, id)

    def on_initialize(self, params):
        self.root_uri = params['rootUri']
        self.workspace = Workspace(self.root_uri, self.f18_path, self.f18_args)
        return {
            'capabilities': {
                'textDocumentSync': {
                    'openClose': True,
                    'change': 1,
                    'save': {
                        'includeText': True
                    },
                },
                'definitionProvider': True,
                'documentSymbolProvider': True,
                # 'completionProvider': {
                #    'resolveProvider': False,
                #    'triggerCharacters': ['%']
                # },

                # 'referencesProvider': True,
                # 'hoverProvider': True,
                # 'implementationProvider': True,
                # 'renameProvider': True,
                # 'workspaceSymbolProvider': True,
            }
        }

    def after_initialize(self, params):
        f18_path = subprocess.run(
            ["which", self.f18_path], stdout=subprocess.PIPE).stdout.decode('utf-8')
        which_f18_msg = "which f18: " + f18_path
        eprint(which_f18_msg)
        if f18_path:
            self.send_notification('window/showMessage', {
                'type': 3,  # Info
                'message': "flangd started successfully!\n"
            })
            self.send_notification('window/showMessage', {
                'type': 3,  # Info
                'message': which_f18_msg
            })
        else:
            self.send_notification('window/showMessage', {
                'type': 3,  # Info
                'message': "Invalid f18 location. Specify path in settings."
            })
        return None

    def on_did_open(self, params):
        document = parse_uri(params['textDocument']['uri'])
        if not document:
            return None
        content = params['textDocument']['text']
        diagnostics = self.workspace.save_file(document, content, new=True)
        self.send_diagnostics(diagnostics, document)

    def on_did_save(self, params):
        document = parse_uri(params['textDocument']['uri'])
        if not document:
            return None
        content = params['text']
        diagnostics = self.workspace.save_file(document, content, new=False)
        self.send_diagnostics(diagnostics, document)

    def on_did_change(self, params):
        document = parse_uri(params['textDocument']['uri'])
        if not document:
            return None
        changes = params['contentChanges']
        for change in changes:
            content = change['text']
            diagnostics = self.workspace.save_file(document,
                                                   content,
                                                   new=False)
            self.send_diagnostics(diagnostics, document)

    def on_did_close(self, params):
        document = parse_uri(params['textDocument']['uri'])
        self.workspace.close_file(document)
        self.clear_diagnostics(document)

    def clear_diagnostics(self, document):
        self.send_diagnostics(None, document)

    def send_diagnostics(self, diagnostics, document):
        result_diagnostics = []
        if diagnostics:
            for diag in diagnostics:
                path, startLine, startColumn, endLine, endColumn, code, message = diag
                code = 1 if code == 'error' else 'warning'
                path = 'file://' + path
                result_diagnostics.append({
                    'code': code,
                    'message': message,
                    "range": {
                        "start": {
                            "line": startLine - 1,
                            "character": startColumn - 1
                        },
                        "end": {
                            "line": endLine - 1,
                            "character": endColumn - 1
                        }
                    }
                })
            params = {
                'uri': 'file://' + document,
                'diagnostics': result_diagnostics,
            }
        else:
            params = {
                'uri': 'file://' + document,
                'diagnostics': [],
            }
        self.send_notification('textDocument/publishDiagnostics', params)

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
                "start": {
                    "line": line - 1,
                    "character": startColumn - 1
                },
                "end": {
                    "line": line - 1,
                    "character": endColumn - 1
                },
            },
        }

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
                eprint('Skipping symbol: ' + symbol)
                continue
            path, line, startColumn, endColumn = info
            document = 'file://' + path
            start = {'line': line - 1, 'character': startColumn - 1}
            end = {'line': line - 1, 'character': endColumn - 1}
            documentSymbol = {
                'name': symbol,
                'kind': 6,
                'location': {
                    'uri': document,
                    'range': {
                        'start': start,
                        'end': end,
                    }
                }
            }
            documentSymbols.append(documentSymbol)
        return documentSymbols

    def respond_request(self, result, id):
        body = {
            'jsonrpc': '2.0',
            'id': id,
        }
        body['result'] = result
        self.send(body)

    def send_notification(self, method, params):
        self.send_request(method, params, None)

    def send_request(self, method, params, id):
        body = {
            'jsonrpc': '2.0',
            'method': method,
        }
        if id != None:
            body['id'] = id
        body['params'] = params
        # eprint("Sending request with method {} and id {}.".format(
        #     method, id))
        self.send(body)

    def send(self, body):
        body = json.dumps(body, separators=(",", ":"))
        content_length = len(body)
        response = (
            "Content-Length: {0}\r\n"
            "Content-Type: application/vscode-jsonrpc; charset=utf8\r\n\r\n"
            "{1}".format(content_length, body))
        sys.stdout.write(response)
        sys.stdout.flush()