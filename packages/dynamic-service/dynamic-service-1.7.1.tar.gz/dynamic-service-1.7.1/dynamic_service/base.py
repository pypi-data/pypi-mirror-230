# base.py

import os
from pathlib import Path

__all__ = [
    "root",
    "source",
    "assets",
    "icons",
    "dependencies"
]

def root() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    try:
        if os.getcwd() in os.environ['VIRTUAL_ENV']:
            path = Path(__file__).parent

        else:
            raise KeyError
        # end if

    except KeyError:
        if os.getcwd() not in (
                path := str(Path(__file__).parent)
        ):
            path = os.getcwd()
        # end if
    # end try

    return str(path)
# end root

def source() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(root()) / Path("source"))
# end source

def dependencies() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(root()) / Path("dependencies"))
# end dependencies

def assets() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(source()) / Path("assets"))
# end assets

def icons() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(assets()) / Path("icon"))
# end icons