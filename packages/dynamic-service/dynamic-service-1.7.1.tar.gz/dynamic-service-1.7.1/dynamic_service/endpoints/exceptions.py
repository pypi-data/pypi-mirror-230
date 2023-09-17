# exceptions.py

from typing import Any, Optional

import dill

__all__ = [
    "UnSerializableObjectError",
    "UnDeserializableObjectError",
    "SerializationExceptions"
]

SerializationExceptions = (
    TypeError, ValueError, AttributeError,
    dill.PicklingError, dill.PickleError
)

class UnSerializableObjectError(ValueError):
    """A class to represent an exception."""

    def __init__(self, data: Optional[Any] = None) -> None:
        """
        Defines the class attributes.

        :param data: The commands to collect for the exception.
        """

        message = f" {repr(data)} of type {type(data)}" if data is not None else ""

        super().__init__(
            f"Couldn't serialize the object{message}. "
            f"Probably due to the object having weak "
            f"references or C-type pointers."
        )
    # end __init__
# end UnSerializableObjectError

class UnDeserializableObjectError(ValueError):
    """A class to represent an exception."""

    def __init__(self, data: Optional[Any] = None) -> None:
        """
        Defines the class attributes.

        :param data: The commands to collect for the exception.
        """

        message = f" {repr(data)} of type {type(data)}" if data is not None else ""

        super().__init__(
            f"Couldn't deserialize the object{message}. "
            f"Probably due to the object having weak "
            f"references or C-type pointers."
        )
    # end __init__
# end UnDeserializableObjectError