"""An RPC library implementing MessagePack RPC in Python."""

from py_msgpack_rpc._client._async_client import AsyncClient, AsyncClientBuilder
from py_msgpack_rpc._server._async_server import AsyncServer, AsyncServerBuilder

all_exports: list = [
    AsyncClient,
    AsyncClientBuilder,
    AsyncServer,
    AsyncServerBuilder,
]
for e in all_exports:
    e.__module__ == __name__  # pylint: disable=pointless-statement

__all__ = [e.__name__ for e in all_exports]

del all_exports
del e
