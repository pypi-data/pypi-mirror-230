import difflib
from pygls.lsp import (
    CodeAction,
    CodeActionKind,
    WorkspaceEdit,
    TextEdit
)
from ..util import load_document, load_document_source


def process_quick_fix(ls, diag, text_document):
    if diag.message.__contains__("Unknown object"):
        obj = diag.message.split('"')[1]
        obj_type = diag.message.split('"')[3]

        diag.range.end.character = diag.range.start.character + obj.__len__()

        new_text = determine_fix(
            obj, obj_type, load_document_source(ls, text_document.uri)
        )
        if new_text == None:
            return None

        fix = CodeAction(
            title="Fix typo",
            kind=CodeActionKind.QuickFix,
            edit=WorkspaceEdit(
                changes={
                    text_document.uri: [TextEdit(range=diag.range, new_text=new_text)]
                }
            ),
        )
        return [fix]


def find(lst, str):
    return [i for i, x in enumerate(lst) if x.lower() == str.lower()]


def determine_fix(obj, obj_type, source):
    obj_type = obj_type.replace("Type", "")
    source_list = source.split()
    indexes = find(source_list, obj_type)

    possibilities = []
    for ind in indexes:
        possibilities.append(source_list[ind + 1])

    matches = difflib.get_close_matches(obj, possibilities)
    return matches[0] if matches.__len__() > 0 else None
