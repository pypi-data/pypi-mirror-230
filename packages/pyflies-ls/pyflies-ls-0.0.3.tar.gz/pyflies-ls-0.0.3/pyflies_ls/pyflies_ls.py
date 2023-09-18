from typing import List, Optional, Union
from pygls.server import LanguageServer
from lsprotocol import types as lsp
from .features.validate import validate
from .features.completion import process_completions
from .features.code_actions import process_quick_fix
from .features.definitions import resolve_definition
from .features.references import resolve_references
from .util import load_document, get_entire_string_from_index, load_document_source


class PyfliesLanguageServer(LanguageServer):
    """
    Represents a language server for pyFlies language.

    This is the entry point for all communications with the client(s).
    It uses custom pygls LanguageServer.
    """

    def __init__(self):
        super().__init__("pyflies_ls", "0.0.3")


def _validate(ls, params):

    source = load_document_source(ls, params.text_document.uri)
    diagnostics = validate(source) if source else []

    ls.publish_diagnostics(params.text_document.uri, diagnostics)


pyflies_server = PyfliesLanguageServer()


@pyflies_server.feature(lsp.TEXT_DOCUMENT_COMPLETION)
def completions(ls, params: lsp.TextDocumentCompletionRequest):
    """Returns completion items."""

    return process_completions(ls, params)


@pyflies_server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: lsp.DidChangeTextDocumentParams):
    """
    Text document did change notification.
    The method calls validation on the document in which the change occured.
    """
    _validate(ls, params)


@pyflies_server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: lsp.DidOpenTextDocumentParams):
    """
    Text document did open notification.
    The method calls validation on the opened document.
    """
    _validate(ls, params)


@pyflies_server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
def definitions(ls, params: lsp.DefinitionParams):
    text_doc = load_document(ls, params.text_document.uri)
    name = get_entire_string_from_index(
        text_doc.offset_at_position(params.position), text_doc.source
    )
    defs = resolve_definition(text_doc.source, name, params.text_document.uri)
    return [defs]


@pyflies_server.feature(lsp.TEXT_DOCUMENT_REFERENCES)
def references(ls, params: lsp.ReferenceParams):
    text_doc = load_document(ls, params.text_document.uri)
    name = get_entire_string_from_index(
        text_doc.offset_at_position(params.position), text_doc.source
    )
    refs = resolve_references(text_doc.source, name, params.text_document.uri)
    return refs


@pyflies_server.feature(
    lsp.TEXT_DOCUMENT_CODE_ACTION, lsp.CodeActionOptions(code_action_kinds=[lsp.CodeActionKind.Refactor])
)
def code_actions(
    ls, params: lsp.CodeActionParams
) -> Optional[List[Union[lsp.Command, lsp.CodeAction]]]:
    diag = params.context.diagnostics
    if diag.__len__() == 0:
        return None
    else:
        return process_quick_fix(ls, diag[0], params.text_document)


@pyflies_server.command("pyflies_ls/ping")
def _cmd_ping(ls, params) -> None:
    """Prevent server going into IDLE state on windows (?)."""
    pass