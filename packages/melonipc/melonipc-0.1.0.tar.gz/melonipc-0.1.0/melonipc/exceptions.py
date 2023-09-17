from typing import Any, Text


class BaseIPCException(Exception):
    """A base exception handler for IPC."""

    def __init__(self, *args: Any) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self) -> Text:
        return self.message  # type: ignore


class DuplicateConnection(BaseIPCException):
    """
    You have attempted to connect with a duplicated identifier.
    Please try again with a unique one or provide the correct override key.
    """


class DuplicateRoute(BaseIPCException):
    """
    You are attempting to register multiple routes with the same name.
    Consider setting the route_name argument to something unique.
    """


class UnhandledWebsocketType(BaseIPCException):
    """Found a websocket type we can't handle."""


class UnknownRoute(BaseIPCException):
    """The route you requested does not exist."""


class UnknownClient(BaseIPCException):
    """The client you requested is not currently connected."""


class RequestFailed(BaseIPCException):
    """This request resulted in an error on the end client."""

    def __init__(self, data: Any) -> None:
        super().__init__()
        self.response_data = data

    def __str__(self) -> str:
        return self.message + "\n\n" + self.response_data  # type: ignore
