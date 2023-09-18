import json
from textx import metamodel_for_language


def load_document(ls, uri):
    return ls.workspace.get_document(uri)


def load_document_source(ls, uri):
    return load_document(ls, uri).source


def get_model_from_source(model):
    mm = metamodel_for_language("pyflies")
    return mm.model_from_str(model)


def load_snippets():
    snippets = {}
    with open("snippets/pyflies-snippets.json") as json_file:
        snippets = json.load(json_file)
    return snippets


def get_entire_string_from_index(ind, source):
    start_ind = ind
    if source[start_ind] == ' ':
        start_ind -= 1

    while source[start_ind].isalnum() or source[start_ind] == '_':
        start_ind -= 1

    end_ind = ind
    while source[end_ind].isalnum() or source[end_ind] == '_':
        end_ind += 1

    return source[start_ind + 1 : end_ind]
