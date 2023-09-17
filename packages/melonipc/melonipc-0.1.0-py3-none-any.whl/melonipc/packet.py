from typing import TypedDict, Any, Optional, Literal, Type, Dict, TypeAlias

from .exceptions import (
    BaseIPCException,
    DuplicateConnection,
    UnhandledWebsocketType,
)


PacketType: TypeAlias = Literal[
    "IDENTIFY", "REQUEST", "SUCCESS_RESPONSE", "FAILURE_RESPONSE"
]
IdentifyType: TypeAlias = Literal["IDENTIFY"]


custom_close_codes: Dict[int, Type[BaseIPCException]] = {
    4102: DuplicateConnection,
    3001: UnhandledWebsocketType,
}


class Packet(TypedDict):
    data: Any
    type: PacketType
    identifier: str


class RequestPacket(TypedDict):
    route: str
    arguments: Dict[str, Any]


class IdentifyDataPacket(TypedDict):
    override_key: Optional[str]
    secret_key: str


class IdentifyPacket(TypedDict):
    identifier: str
    type: IdentifyType
    data: IdentifyDataPacket
