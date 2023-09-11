import enum
import socket
from datetime import datetime
from typing import Any, List, Optional

import pydantic

from .base import Base


class Parameter(Base):
    key: str
    default: Optional[str] = None
    value: Optional[str] = None
    type: str


class Info(Base):
    type: str
    version: str
    parameters: List[Parameter]


class Database(Base):
    user: str
    password: str
    netloc: str
    port: int
    dbname: str

    @property
    def url(self):
        return f"postgresql://{self.user}:{self.password}@{self.netloc}:{self.port}"


class SocketType(str, enum.Enum):
    REQUESTER = "REQUESTER"
    REPLIER = "REPLIER"
    PUBLISHER = "PUBLISHER"
    SUBSCRIBER = "SUBSCRIBER"


class SocketConfig(Base):
    socket_type: SocketType = SocketType.REPLIER
    host: str = socket.gethostbyname(socket.gethostname())
    port: int = 0
    listen: bool = True
    recv_timeout: int = 20000
    send_timeout: int = 20000


class Service(Base):
    name: str
    created_at: datetime
    image: str
    status: str
    message: str | None = None
    service_type: str | None = None
    Parameters: List[Parameter] = []


class Instance(Base):
    id: str
    service: str
    service_type: str
    created_at: datetime
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    host: str | None = None
    port: int | None = None
    scope: str | None = None
    key: str


class Request(Base):
    task: str
    data: Optional[Any] = None
    error: Optional[str] = None

    @pydantic.field_validator("data")
    def validate_data(cls, v):
        if v is None:
            return v
        if type(v) is dict:
            return v
        return v.model_dump()


class Response(Base):
    task: str
    error: Optional[str] = None
    data: Optional[Any] = None

    @pydantic.field_validator("data")
    def validate_data(cls, v):
        if v is None:
            return v
        if type(v) is dict:
            return v
        return v.model_dump()
