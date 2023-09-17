import json
import logging
import secrets
import traceback
from typing import Dict, Literal, Any, cast, Optional, Union

from starlette.websockets import WebSocket
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from .exceptions import (
    UnknownClient,
    RequestFailed,
    BaseIPCException,
    DuplicateConnection,
)
from .packet import (
    Packet,
    RequestPacket,
    IdentifyPacket,
)

log: logging.Logger = logging.getLogger(__name__)


class Server:
    def __init__(
        self,
        *,
        using_fastapi_websockets: bool = False,
        override_key: Optional[str] = None,
        secret_key: str = "",
    ) -> None:
        self._connections: Dict[str, Any] = {}
        self._secret_key: str = secret_key
        self._override_key: Optional[str] = (
            override_key if override_key is not None else secrets.token_hex(64)
        )
        self.using_fastapi_websockets: bool = using_fastapi_websockets

    def connection(self, identifier: str) -> None:
        self._connections.pop(identifier, None)

    async def _send(
        self, content: str, conn: Union[WebSocket, WebSocketClientProtocol]
    ) -> None:
        if self.using_fastapi_websockets:
            await conn.send_text(content)  # type: ignore
        else:
            await conn.send(content)  # type: ignore

    async def _recv(self, conn: Union[WebSocket, WebSocketClientProtocol]) -> str:
        if self.using_fastapi_websockets:
            from starlette.websockets import WebSocketDisconnect

            try:
                return await conn.receive_text()  # type: ignore
            except WebSocketDisconnect:
                raise RequestFailed("Websocket disconnected while waiting for recieve.")

        return await conn.recv()  # type: ignore

    async def request(
        self, route: str, *, client_identifier: str = "DEFAULT", **kwargs: Any
    ) -> Any:
        conn = self._connections.get(client_identifier)
        if not conn:
            raise UnknownClient

        await self._send(
            json.dumps(
                Packet(
                    identifier=client_identifier,
                    type="REQUEST",
                    data=RequestPacket(route=route, arguments=kwargs),
                )
            ),
            conn,
        )
        d = await self._recv(conn)
        packet: Packet = json.loads(d)
        if packet["type"] == "FAILURE_RESPONSE":
            raise RequestFailed(packet["data"])

        return packet["data"]

    async def request_all(self, route: str, **kwargs: Any) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        for i, conn in self._connections.items():
            try:
                await self._send(
                    json.dumps(
                        Packet(
                            identifier=i,
                            type="REQUEST",
                            data=RequestPacket(route=route, arguments=kwargs),
                        )
                    ),
                    conn,
                )
                d = await self._recv(conn)
                packet: Packet = json.loads(d)
                if packet["type"] == "FAILURE_RESPONSE":
                    results[i] = RequestFailed(packet["data"])
                else:
                    results[i] = packet["data"]
            except ConnectionClosedOK as e:
                results[i] = RequestFailed("Connection Closed")
                log.error(
                    "request_all connection closed: %s, %s",
                    i,
                    "".join(traceback.format_exception(e)),
                )
            except ConnectionClosedError as e:
                results[i] = RequestFailed(
                    f"Connection closed with error: {e.code}|{e.reason}"
                )
                log.error(
                    "request_all connection closed with error: %s, %s",
                    i,
                    "".join(traceback.format_exception(e)),
                )
            except Exception as e:
                results[i] = RequestFailed("Request failed.")
                log.error(
                    "request_all connection threw: %s, %s",
                    i,
                    "".join(traceback.format_exception(e)),
                )

        return results

    async def parse_identify(
        self, packet: Packet, websocket: Union[WebSocket, WebSocketClientProtocol]  # type: ignore
    ) -> str:
        try:
            identifier: str = packet.get("identifier")
            ws_type: Literal["IDENTIFY"] = packet["type"]  # type: ignore
            if ws_type != "IDENTIFY":
                await websocket.close(
                    code=4101, reason=f"Expected IDENTIFY, received {ws_type}"
                )
                raise BaseIPCException(
                    f"Unexpected ws response type, expected IDENTIFY, received {ws_type}"
                )

            packet: IdentifyPacket = cast(IdentifyPacket, packet)
            secret_key = packet["data"]["secret_key"]
            if secret_key != self._secret_key:
                await websocket.close(code=4100, reason=f"Invalid secret key.")
                raise BaseIPCException(
                    f"Client attempted to connect with an incorrect secret key."
                )

            override_key = packet["data"].get("override_key")
            if identifier in self._connections and (
                not override_key or override_key != self._override_key
            ):
                await websocket.close(
                    code=4102, reason="Duplicate identifier on IDENTIFY"
                )
                raise DuplicateConnection("Identify failed.")

            self._connections[identifier] = websocket
            await self._send(
                json.dumps(Packet(identifier=identifier, type="IDENTIFY", data=None)),
                websocket,
            )
            return identifier
        except Exception as e:
            raise BaseIPCException("Identify failed") from e
