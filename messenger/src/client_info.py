import socket
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ClientInfo:
    address: Any
    socket: socket.SocketType
    username: Optional[str] = None
