"""Implementation of MethodExecutor."""

import logging
import typing

from py_msgpack_rpc._messages import Request, Response

LOGGER = logging.getLogger(__name__)


class MethodExecutor:
    """Class to execute methods."""

    def __init__(self) -> None:
        self._methods: typing.Dict[str, typing.Callable] = {}

    def add_method(self, method_name: str, method_function: typing.Callable) -> None:
        """Add a method.

        Args:
            method_name (str): Method name.
            method_function (typing.Callable): Function of the method.
        """
        LOGGER.debug('Register a method "%s"', method_name)
        self._methods[method_name] = method_function

    async def process_request(self, request: Request) -> Response:
        """Process a request.

        Args:
            request (Request): Request.

        Returns:
            Response: Response.
        """
        try:
            LOGGER.debug("Request %s (id: %s)", request.method_name, request.message_id)
            result = self._methods[request.method_name](*(request.parameters))
            return Response(
                message_id=request.message_id,
                error=None,
                result=result,
            )
        except Exception as exception:  # pylint: disable=broad-exception-caught
            LOGGER.debug(
                "Error in request %s (id: %s)",
                request.method_name,
                request.message_id,
                exc_info=True,
            )
            return Response(
                message_id=request.message_id,
                error=exception.args,
                result=None,
            )
