import typing as tp
from collections import deque

from ..types import AMQPBody, AMQPAppProperties
from ..amqp import MessageCtx
from .client import StreamsClient
from .offset import Offset

class PublisherConstr(tp.Protocol):
    name: str
    stream: str
    message_id: int

    _id: int

    def __init__(
        self,
        client: StreamsClient, stream: str, id: int, name: str, message_id: int
    ) -> None: ...

class PublisherTrait:
    name: str
    stream: str
    message_id: int

    _id: int

    def __init__(
        self,
        client: StreamsClient, stream: str, id: int, name: str, message_id: int
    ) -> None: ...

    def _next_message_id(self) -> int: ...

class Publisher(PublisherTrait):
    @tp.overload
    async def send(self, message: AMQPBody) -> None: ...

    @tp.overload
    async def send(self, message: MessageCtx) -> None: ...

class PublisherBatchTrait(PublisherTrait):
    _data: list[MessageCtx]

class PublisherBatchFast(PublisherBatchTrait):
    @tp.overload
    def batch(self, message: AMQPBody) -> None: ...

    @tp.overload
    def batch(self, message: MessageCtx) -> None: ...

    async def flush(self) -> None: ...

class PublisherBatchLimit(PublisherBatchTrait):
    @tp.overload
    async def batch(self, message: AMQPBody, *, max_len: int) -> None: ...

    @tp.overload
    async def batch(self, message: MessageCtx, *, max_len: int) -> None: ...

    async def flush(self) -> None: ...

# NOTE: deprecated
class PublisherBatch(PublisherBatchFast): ...
class PublisherBatchMem(PublisherBatchLimit): ...

class PublisherBin(PublisherTrait):
    async def send(self, message: bytes) -> None: ...

class PublisherBinBatch(PublisherBatchTrait):
    def batch(self, message: bytes) -> None: ...
    async def flush(self) -> None: ...

class Subscriber:
    _stream: str
    _subscription_id: int
    _offset: Offset
    _timeout: float
    _amqp: bool
    _last_message: MessageCtx | None
    _messages: deque[MessageCtx] | None

    def __init__(
        self,
        client: StreamsClient,
        stream: str,
        subscription_id: int,
        offset: Offset,
        timeout: float,
        amqp: bool,
    ) -> None:
        ...

    def _next_message_offset(self) -> Offset: ...
    def __aiter__(self) -> tp.AsyncIterator[MessageCtx]: ...

def stream_messsage_ctx(
    body: AMQPBody,
    *,
    publish_id: int | None=None,
    app_properties: AMQPAppProperties={},
) -> MessageCtx: ...

# vim: sw=4:et:ai
