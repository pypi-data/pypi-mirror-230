import json
import re

from pygls.lsp.types.language_features import completion
from textx.exceptions import TextXError, TextXSyntaxError
from textx import metamodel_for_language
from ..util import load_snippets, load_document, get_model_from_source
from .validate import construct_diagnostic, validate
from pygls.lsp import (
    CompletionList,
    CompletionItem,
    CompletionParams,
    CompletionItemKind,
    InsertTextFormat,
)


def filter_snippets(doc, position, snippets: json):
    trigger_character = doc.lines[position.line][position.character - 1]
    snippets_final = {}
    for k in snippets.keys():
        if k.startswith(trigger_character):
            snippets_final[k] = snippets[k]
    return snippets_final


def check_snippet(snippet, metamodel, model, offset):

    # Replaces dynamic parts of the snippet body with a hardcoded variable name to prevent false syntax errors
    snippet_body = snippet["body"].replace("${0}", "")
    test_body = re.sub("\${([0-9]:[A-Za-z]*|[0-9])}", "var1", snippet_body)
    test_source = model[: offset - 1] + test_body + model[offset:]

    try:
        metamodel.model_from_str(test_source)
    except TextXError as err:
        if err.__class__ == TextXSyntaxError:
            return False

    return True


def resolve_completion_items(server, snippets, position, doc):

    mm = metamodel_for_language("pyflies")
    offset = doc.offset_at_position(position)
    completion_items = []

    for snippet in snippets.values():

        if check_snippet(snippet, mm, doc.source, offset) is False:
            continue

        completion_items.append(
            CompletionItem(
                label=snippet["prefix"],
                kind=CompletionItemKind.Snippet,
                insert_text=snippet["body"],
                insert_text_format=InsertTextFormat.Snippet,
            )
        )

    return completion_items


def process_completions(server, params: CompletionParams):

    doc = load_document(server, params.text_document.uri)
    snippets = filter_snippets(doc, params.position, load_snippets())
    completion_items = resolve_completion_items(server, snippets, params.position, doc)

    return CompletionList(is_incomplete=False, items=completion_items)
