// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as vscodelc from 'vscode-languageclient';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
  console.log('Congratulations, your extension "flangd" is now active!');
  const conf = vscode.workspace.getConfiguration('flangd', null);
  const flangdPath = conf.get<string>('flangdPath') || 'flangd.py';
  const f18Path = conf.get<string>('f18Path') || 'f18';
  const f18Args = conf.get<string>('f18Args') || '';
  const flangd: vscodelc.Executable = {
    command : flangdPath,
    args : [f18Path, f18Args]
  };
  const serverOptions: vscodelc.ServerOptions = flangd;
  const clientOptions: vscodelc.LanguageClientOptions = {
    documentSelector: [
      { scheme: 'file', language: 'fortran' },
      { scheme: 'file', language: 'fortran-modern' },
      { scheme: 'file', language: 'fortran_fixed-form' },
      { scheme: 'file', language: 'FortranFreeForm' },
    ],
  };
  const flangdClient = new vscodelc.LanguageClient(
      'flangd', serverOptions, clientOptions);
  console.log('Flang Language Server is now active!');
  context.subscriptions.push(flangdClient.start());
  context.subscriptions.push(vscode.commands.registerCommand(
      'flangd.activate', async () => {}));
}

// this method is called when your extension is deactivated
export function deactivate() {}
