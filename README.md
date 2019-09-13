# flangd README

flangd is a Fortran language server written in Python, using f18 as the feature
provider. It is a work in progress, and has limited features. If you have
any issues at all, please make an issue.

## Features

Currently implemented Go To Definition, Document Symbols and Diagnostics (with
my fork of f18) (https://github.com/tinlun/f18/tree/master).

## Requirements


This package requires [f18](https://github.com/flang-compiler/f18).

Diagnostic feature requires [my fork of f18](https://github.com/tinlun/f18/tree/master).

This package also requires the following extensions to be installed:
 * [Modern Fortran](https://marketplace.visualstudio.com/items?itemName=krvajalm.linter-gfortran) or [fortran](https://marketplace.visualstudio.com/items?itemName=Gimly81.fortran)

You must also have Python3 installed.

Note that flangd only works on Linux (because f18 is only available on Linux).

## Installation

This extension is only available for Linux. You can also use this extension if
you are using Windows Subsystem for Linux, though the steps are a bit more
convoluted.

### Linux:
In the root of this repository:
```
code --install-extension flangd-0.0.1.vsix
```

### WSL using Remote-WSL:
Assuming you already have WSL installed.

Install the [Remote-WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) for VS Code.

Copy the `tinlun.flangd-0.0.1` directory into `~/.vscode-server/extensions`

Launch VS Code in WSL mode.

### Then, for all methods:
Check that you have flangd installed by going to VS Code settings (`Ctrl + ,`)
and searching for flangd. If the extension was installed correctly, some settings
should show up there.

While the settings are up, **set the correct path to flangd and f18.** If you
don't set these paths correctly, flangd will blow up on you.

Once set, reload the VS Code window by `F1` > `Developer: Reload Window`.

Then try opening a fortran document. If done correctly, there should be a text
notification that pops up telling you which f18 flangd is using.
