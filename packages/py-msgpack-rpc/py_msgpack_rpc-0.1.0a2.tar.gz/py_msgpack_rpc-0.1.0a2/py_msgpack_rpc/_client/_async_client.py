"""Implementation of AsyncClient."""

import asyncio
import logging
import typing

import msgpack

from py_msgpack_rpc._exceptions import ServerError
from py_msgpack_rpc._messages import MessageType, Request, Response, parse_message

LOGGER = logging.getLogger(__name__)


MAX_MESSAGE_ID = pow(2, 32) - 1


class ClientProtocol(asyncio.Protocol):
    """Protocol of client."""

    def __init__(self) -> None:
        self._unpacker = msgpack.Unpacker()

        self._response_futures: typing.Dict[int, asyncio.Future[Response]] = {}

        self._sent_messages: asyncio.Queue[bytes] = asyncio.Queue()
        self._writer: typing.Optional[asyncio.Task[None]] = None

        self._closed_event = asyncio.Event()

    def connection_made(self, transport: asyncio.Transport) -> None:  # type: ignore[override]
        """Handle the condition that a connection is established.

        Args:
            transport (asyncio.Transport): Transport.
        """
        self._writer = asyncio.get_running_loop().create_task(
            self._write_data(transport)
        )
        LOGGER.debug("Connected to %s", transport.get_extra_info("peername"))

    def connection_lost(self, exc: Exception | None) -> None:
        """Handle the condition that a connection is lost.

        Args:
            exc (Exception | None): Exception.
        """
        if self._writer is not None:
            self._writer.cancel()
        self._closed_event.set()

    def data_received(self, data: bytes) -> None:
        """Handle the condition that some data is received.

        Args:
            data (bytes): Received data.
        """
        self._unpacker.feed(data)
        for message_data in self._unpacker:
            asyncio.get_running_loop().create_task(self._process_message(message_data))

    async def send_request(
        self, request: Request, response_future: asyncio.Future[Response]
    ) -> None:
        """Send a request.

        Args:
            request (Request): Request.
            response_future (asyncio.Future[Response]): Future object to receive the response.
        """
        self._response_futures[request.message_id] = response_future
        self._sent_messages.put_nowait(
            msgpack.packb(
                [
                    MessageType.REQUEST.value,
                    request.message_id,
                    request.method_name,
                    request.parameters,
                ]
            )
        )

    async def wait_closed(self) -> None:
        """Wait for connection closed."""
        await self._closed_event.wait()

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
        if isinstance(message, Response):
            await self._process_response(message)
            return
        LOGGER.debug("Ignore an invalid message.")

    async def _process_response(self, response: Response) -> None:
        """Process a response.

        Args:
            response (Response): Response.
        """
        self._response_futures[response.message_id].set_result(response)


class AsyncClient:
    """Class of asynchronous clients.

    Args:
        transport (asyncio.Transport): Transport.
        protocol (ClientProtocol): Protocol.

    Note:
        This class should be created using AsyncClientBuilder class.
    """

    def __init__(self, transport: asyncio.Transport, protocol: ClientProtocol) -> None:
        self._transport = transport
        self._protocol = protocol

        self._next_message_id = 0

    async def __aenter__(self) -> typing.Self:
        """Function for "async with" statement.

        Returns:
            AsyncClient: This instance.
        """
        return self

    async def __aexit__(self, *_) -> None:
        """Function for "async with" statement."""
        self._transport.close()
        await self._protocol.wait_closed()

    async def call(self, method_name: str, *parameters: typing.Any) -> typing.Any:
        """Call a method.

        Arguments after method_name is treated as parameters of the method.

        Args:
            method_name (str): Method name.

        Raises:
            ServerError: When an error occurred in servers.

        Returns:
            typing.Any: Result.
        """
        response_future: asyncio.Future[Response] = asyncio.Future()
        await self._protocol.send_request(
            request=Request(
                message_id=self._prepare_message_id(),
                method_name=method_name,
                parameters=parameters,
            ),
            response_future=response_future,
        )
        response = await response_future
        if response.error is not None:
            raise ServerError(response.error)
        return response.result

    def _prepare_message_id(self) -> int:
        """Prepare a message ID.

        Returns:
            int: Message ID.
        """
        res = self._next_message_id
        if self._next_message_id >= MAX_MESSAGE_ID:
            self._next_message_id = 0
        else:
            self._next_message_id = self._next_message_id + 1
        return res


class AsyncClientBuilder:
    """Class to create asynchronous clients."""

    def __init__(self) -> None:
        self._host: typing.Optional[str] = None
        self._port: typing.Optional[int] = None

    def connect_tcp(self, host: str, port: int) -> None:
        """Connect to an endpoint of TCP.

        Args:
            host (str): Host name or IP address.
            port (int): Port number.
        """
        self._host = host
        self._port = port

    async def build(self) -> AsyncClient:
        """Create a client.

        Returns:
            AsyncClient: Client.
        """
        assert self._host is not None
        assert self._port is not None

        transport, protocol = await asyncio.get_running_loop().create_connection(
            ClientProtocol,
            host=self._host,
            port=self._port,
        )

        self._host = None
        self._port = None

        return AsyncClient(transport=transport, protocol=protocol)
