"""Implementation of AsyncServer."""

import asyncio
import logging
import socket
import typing

import msgpack

from py_msgpack_rpc._messages import MessageType, Request, parse_message
from py_msgpack_rpc._server._method_executor import MethodExecutor

LOGGER = logging.getLogger(__name__)


class ServerProtocol(asyncio.Protocol):
    """Protocol of servers.

    Args:
        method_executor (MethodExecutor): An instance of MethodExecutor.
    """

    def __init__(self, method_executor: MethodExecutor) -> None:
        self._unpacker = msgpack.Unpacker()

        self._method_executor = method_executor

        self._sent_messages: asyncio.Queue[bytes] = asyncio.Queue()
        self._writer: typing.Optional[asyncio.Task[None]] = None

    def connection_made(self, transport: asyncio.Transport) -> None:  # type: ignore[override]
        """Handle the condition that a connection is established.

        Args:
            transport (asyncio.Transport): Transport.
        """
        self._writer = asyncio.get_running_loop().create_task(
            self._write_data(transport)
        )
        LOGGER.debug(
            "Accepted connection from %s", transport.get_extra_info("peername")
        )

    def connection_lost(self, exc: Exception | None) -> None:
        """Handle the condition that a connection is lost.

        Args:
            exc (Exception | None): Exception.
        """
        if self._writer is not None:
            self._writer.cancel()

    def data_received(self, data: bytes) -> None:
        """Handle the condition that some data is received.

        Args:
            data (bytes): Received data.
        """
        self._unpacker.feed(data)
        for message_data in self._unpacker:
            asyncio.get_running_loop().create_task(self._process_message(message_data))

    async def _write_data(self, transport: asyncio.Transport) -> None:
        """Write data.

        Args:
            transport (asyncio.Transport): Transport.
        """
        while True:
            message = await self._sent_messages.get()
            transport.write(message)

    async def _process_message(self, message_data: typing.Any) -> None:
        """Process a message.

        Args:
            message_data (typing.Any): Data of the message.
        """
        message = parse_message(message_data)
        if isinstance(message, Request):
            await self._process_request(message)
            return
        LOGGER.debug("Ignore an invalid message.")

    async def _process_request(self, request: Request) -> None:
        """Process a request.

        Args:
            request (Request): Request.
        """
        response = await self._method_executor.process_request(request)
        self._sent_messages.put_nowait(
            msgpack.packb(
                [
                    MessageType.RESPONSE.value,
                    response.message_id,
                    response.error,
                    response.result,
                ]
            )
        )


class AsyncServer:
    """Class of asynchronous servers.

    Args:
        server (asyncio.Server): Server in asyncio library.

    Note:
        This class should be created using AsyncServerBuilder class.
    """

    def __init__(self, server: asyncio.Server) -> None:
        self._server = server

    async def __aenter__(self) -> typing.Self:
        """Function for "async with" statement.

        Returns:
            AsyncServer: This instance.
        """
        await self._server.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        """Function for "async with" statement."""
        await self._server.__aexit__(*args)

    async def run(self) -> None:
        """Run this server."""
        await self._server.serve_forever()

    def local_endpoints(self) -> typing.List[typing.Tuple[str, int]]:
        """Get the local endpoints.

        Returns:
            typing.List[typing.Tuple[str, int]]: Addresses of local endpoints. (IP address and port number.)
        """
        return [AsyncServer._get_address(socket) for socket in self._server.sockets]

    @staticmethod
    def _get_address(sock: socket.socket) -> typing.Tuple[str, int]:
        """Get address of a socket.

        Args:
            sock (socket.socket): Socket.

        Returns:
            typing.Tuple[str, int]: Address. (IP address and port number.)
        """
        address = sock.getsockname()
        return (address[0], address[1])


class AsyncServerBuilder:
    """Class to create asynchronous servers."""

    def __init__(self) -> None:
        self._executor = MethodExecutor()
        self._host: typing.Optional[str] = None
        self._port: typing.Optional[int] = None

    def add_method(self, method_name: str, method_function: typing.Callable) -> None:
        """Add a method.

        Args:
            method_name (str): Method name.
            method_function (typing.Callable): Function of the method.
        """
        self._executor.add_method(
            method_name=method_name, method_function=method_function
        )

    def listen_tcp(self, host: str, port: int) -> None:
        """Listen to an endpoint of TCP.

        Args:
            host (str): Host name or IP address.
            port (int): Port number.
        """
        self._host = host
        self._port = port

    async def build(self, *, start: bool = True) -> AsyncServer:
        """Create a server.

        Args:
            start (bool): Start the server. Defaults to True.

        Returns:
            AsyncServer: Server.
        """
        assert self._host is not None
        assert self._port is not None

        executor = self._executor
        asyncio_server = await asyncio.get_running_loop().create_server(
            lambda: ServerProtocol(method_executor=executor),
            host=self._host,
            port=self._port,
            start_serving=start,
        )

        self._executor = MethodExecutor()
        self._host = None
        self._port = None

        return AsyncServer(asyncio_server)
