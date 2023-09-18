"""Implementation of messages."""

import collections.abc
import dataclasses
import enum
import typing

from py_msgpack_rpc._exceptions import InvalidMessage


class MessageType(enum.Enum):
    """Types of messages."""

    REQUEST = 0
    RESPONSE = 1
    NOTIFICATION = 2


@dataclasses.dataclass
class Request:
    """Class of requests.

    Attributes:
        message_id (int): Message ID.
        method_name (str): Method name.
        parameters (collections.abc.Collection[typing.Any]): Parameters.
    """

    message_id: int
    method_name: str
    parameters: collections.abc.Collection[typing.Any]


@dataclasses.dataclass
class Response:
    """Class of responses.

    Attributes:
        message_id (int): Message ID.
        error (typing.Any): Error. None if no error.
        result (typing.Any): Result.
    """

    message_id: int
    error: typing.Any
    result: typing.Any


def parse_message(data: typing.Any) -> typing.Union[Request, Response]:
    """Parse a message.

    Args:
        data (typing.Any): Deserialized data.

    Raises:
        InvalidMessage: For invalid message data.

    Returns:
        typing.Union[Request, Response]: Parsed message.
    """
    message_type = data[0]
    if message_type == MessageType.REQUEST.value:
        return Request(
            message_id=data[1],
            method_name=data[2],
            parameters=data[3],
        )
    if message_type == MessageType.RESPONSE.value:
        return Response(
            message_id=data[1],
            error=data[2],
            result=data[3],
        )
    raise InvalidMessage("Invalid message.")
