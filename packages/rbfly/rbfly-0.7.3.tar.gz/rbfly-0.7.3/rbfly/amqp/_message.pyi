#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2023 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from ..types import AMQPBody, AMQPAppProperties, AMQPMap

class MessageCtx:
    body: AMQPBody

    # RabbitMQ Streams extension
    stream_offset: int
    stream_timestamp: float
    stream_publish_id: int

    annotations: AMQPMap
    app_properties: AMQPAppProperties

    def __init__(
        self,
        body: AMQPBody,
        *,
        annotations: AMQPMap={},
        app_properties: AMQPAppProperties={},
        stream_offset: int=0,
        stream_timestamp: float=0,
        stream_publish_id: int=0,
    ) -> None: ...

def encode_amqp(buffer: bytearray, message: MessageCtx) -> int: ...
def decode_amqp(buffer: bytes) -> MessageCtx: ...

def set_message_ctx(msg: MessageCtx) -> None: ...
def get_message_ctx() -> MessageCtx: ...

# vim: sw=4:et:ai
