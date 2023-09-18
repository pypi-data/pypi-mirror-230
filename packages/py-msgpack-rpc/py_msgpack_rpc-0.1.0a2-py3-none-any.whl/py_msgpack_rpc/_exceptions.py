"""Exceptions of py-msgpack-rpc."""


class InvalidMessage(RuntimeError):
    """Exception raised for invalid messages."""


class ServerError(RuntimeError):
    """Exception raised when an error occurred in a server requested by a client in use."""
