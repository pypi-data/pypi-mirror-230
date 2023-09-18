import imp
import re
from textx import get_children
from lsprotocol import types as lsp
from ..util import get_model_from_source

def pos_to_range(position, name_len):
    return lsp.Range(
        start=lsp.Position(line=position[0] - 1, character=position[1] - 1),
        end=lsp.Position(line=position[0] - 1, character=position[1] - 1 + name_len),
    )

def is_routine(name, m):
    return ([x for x in m.routine_types if x.name == name]) != 0


def is_var(name, m):
    return ([x for x in m.vars if x.name == name]) != 0


def routine_or_var(param_name, m):
    routines = [x for x in m.routine_types if x.name == param_name]
    vars = [x for x in m.vars if x.name == param_name]
    if len(routines) == 0 and len(vars) == 0:
        return False
    else:
        return True


def fetch_vars(m, name):
    return [
        x._tx_position
        for x in get_children(lambda x: hasattr(x, "name") and x.name == name, m)
    ]


def fetch_routines(m, name):
    from_root = [
        x._tx_position
        for x in get_children(lambda x: hasattr(x, "name") and x.name == name, m)
    ]
    from_flow = [
        x._tx_position
        for x in get_children(
            lambda x: x.__class__.__name__ in ["Test", "Screen"]
            and x.type.name == name,
            m,
        )
    ]
    from_root.extend(from_flow)
    return from_root


def resolve_references(model, param_name, uri):
    m = get_model_from_source(model)

    occurences = []
    if is_routine(param_name, m):
        occurences.extend(fetch_routines(m, param_name))
    elif is_var(param_name, m):
        occurences.extend(fetch_vars(m, param_name))
    else:
        return None

    refs = []
    for o in occurences:
        refs.append(
            lsp.Location(
                uri=uri,
                range=pos_to_range(
                    m._tx_parser.pos_to_linecol(o), param_name.__len__()
                ),
            )
        )

    return refs
