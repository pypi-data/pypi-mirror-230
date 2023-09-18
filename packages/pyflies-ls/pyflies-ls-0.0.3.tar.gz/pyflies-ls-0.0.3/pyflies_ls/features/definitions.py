from turtle import screensize
from unittest import case
from textx import metamodel_for_language
from lsprotocol import types as lsp
from ..util import get_model_from_source


def determine_position_from_type(type):
    if type == "pyflies.ScreenType":
        return "screen ".__len__()
    elif type == "pyflies.TestType":
        return "test ".__len__()
    else:
        return 0


def pos_to_range(position, type, name_len):
    char_pos = determine_position_from_type(type)

    return lsp.Range(
        start=lsp.Position(line=position[0] - 1, character=char_pos),
        end=lsp.Position(line=position[0] - 1, character=char_pos + name_len),
    )


def resolve_definition(model, param_name, uri):
    m = get_model_from_source(model)

    defs = [x for x in m.routine_types if x.name == param_name]
    var_defs = [x for x in m.vars if x.name == param_name]
    defs.extend(var_defs)
    return lsp.Location(
        uri=uri,
        range=pos_to_range(
            m._tx_parser.pos_to_linecol(defs[0]._tx_position),
            defs[0]._tx_fqn,
            param_name.__len__(),
        ),
    )
