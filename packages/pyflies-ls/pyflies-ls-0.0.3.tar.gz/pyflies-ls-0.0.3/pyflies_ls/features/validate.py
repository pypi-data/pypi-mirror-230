from typing import List, Union

from textx.exceptions import TextXError
from textx import metamodel_for_language
from pyflies.exceptions import PyFliesException
from lsprotocol import types as lsp

def construct_diagnostic(msg, col, line):
    return lsp.Diagnostic(
        range=lsp.Range(
            start=lsp.Position(line=line - 1, character=col - 1),
            end=lsp.Position(line=line - 1, character=col),
        ),
        message=msg,
        source="pyFlies LS",
    )


def validate(model: str) -> List[PyFliesException]:
    """Validates given model.

    NOTE: For now returned list will contain maximum one error, since textX does not
          have built-in error recovery mechanism.

    Args:
        model: model
        file_path: A path to the `model` file
        project_root: A path to the root directory where to look for other models
    Returns:
        A list of textX errors or empty list if model is valid
    Raises:
        None

    """
    errors = []
    try:
        mm = metamodel_for_language("pyflies")
        mm.model_from_str(model)
    except PyFliesException as err:
        # TODO: How to determine col and line for PyFliesException
        errors.append(construct_diagnostic(err.args[0], 1, 1))
    except TextXError as err:
        msg = err.message
        col = err.col
        line = err.line

        errors.append(construct_diagnostic(msg, col, line))
    except Exception as e:
        print(e)
    return errors
