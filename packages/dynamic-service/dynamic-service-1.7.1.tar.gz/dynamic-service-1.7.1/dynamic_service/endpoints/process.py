# process.py

from typing import Any

import dill
import codecs

from dynamic_service.endpoints.exceptions import (
    SerializationExceptions, UnSerializableObjectError
)

__all__ = [
    "loads",
    "dumps",
    "decode",
    "encode",
    "copy"
]

def dumps(data) -> str:
    """
    Encodes the object commands to a bytes string.

    :param data: The data to dump.

    :return: The bytes string commands.
    """

    try:
        return dill.dumps(data)

    except SerializationExceptions:
        raise UnSerializableObjectError(data)
    # end try
# end dumps

def loads(data: str) -> Any:
    """
    Decodes the object commands from a bytes string, to the object.

    :param data: The commands to load into a string.

    :return: The bytes string commands as object.
    """

    return dill.loads(data)
# end loads

def decode(data: str) -> bytes:
    """
    Decodes the object from a string.

    :param data: The commands to load into a string.

    :return: The object's commands.
    """

    return loads(codecs.decode(data.encode(), "base64"))
# end decode

def copy(data: Any) -> Any:
    """
    Copies the object.

    :param data: The data to load into a copy.

    :return: The object's copy.
    """

    return loads(dumps(data))
# end copy

def encode(data: Any) -> str:
    """
    Encodes the object into a string.

    :param data: The data to load into a copy.

    :return: An encoded string for the commands.
    """

    return codecs.encode(dumps(data), "base64").decode()
# end encode