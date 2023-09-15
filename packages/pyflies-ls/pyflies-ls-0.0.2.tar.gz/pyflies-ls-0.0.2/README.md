# _pyflies-LS_

pyflies-LS is a language server that provides smartness for [pyflies](https://github.com/pyflies/pyflies) language.

It is expected to use this package in conbination with some IDE extension for pyflies.
An example for this would be [vscode-pyflies](https://github.com/pyflies/vscode-pyflies) extension for Visual Studio Code.

## Features

pyflies Language Server contains all logic for providing features like:

- _Code completion_
- _Code validation and error reporting_
- _Quick fix for typos_
- _Find all refernces_
- _Go to definition_

The server uses  _[pygls](https://github.com/openlawlibrary/pygls)_ to expose all functionalities over
_[Language Server Protocol](https://microsoft.github.io/language-server-protocol/specification)_.