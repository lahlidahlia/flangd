# flangd README

flangd is a Fortran language server written in Python, using f18 as the feature
provider.

## Features

Currently implemented Go To Definition, Document Symbols and Diagnostics (with
my fork of f18).

## Requirements


This package requires [f18](https://github.com/flang-compiler/f18).

Diagnostic feature requires [my fork of f18](https://github.com/tinlun/f18/tree/master)

This package also requires the following extensions to be installed:
 * [Modern Fortran](https://marketplace.visualstudio.com/items?itemName=krvajalm.linter-gfortran) or [fortran](https://marketplace.visualstudio.com/items?itemName=Gimly81.fortran)

You must also have Python3 installed.

Note that flangd only works on Linux (because f18 is only available on Linux).

## Installation

This extension is only available for Linux. You can also use this extension if
you are using Windows Subsystem for Linux, though the steps are a bit more
convoluted.

### Linux
In the root of this repository:
```
code --install-extension flangd-0.0.1.vsix
```

### WSL using Remote-WSL
Assuming you already have WSL installed.

Install the [Remote-WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) for VS Code.


-----------------------------------------------------------------------------------------------------------

## Working with Markdown

**Note:** You can author your README using Visual Studio Code.  Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux)
* Toggle preview (`Shift+CMD+V` on macOS or `Shift+Ctrl+V` on Windows and Linux)
* Press `Ctrl+Space` (Windows, Linux) or `Cmd+Space` (macOS) to see a list of Markdown snippets

### For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
