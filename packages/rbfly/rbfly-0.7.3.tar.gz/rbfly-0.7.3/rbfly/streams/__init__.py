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

"""
Library for RabbitMQ Streams using Python asyncio.
"""

from ..amqp import MessageCtx, get_message_ctx
from ..types import AMQPScalar, AMQPBody, AMQPAppProperties, Symbol
from .client import StreamsClient, streams_client, connection
from .offset import Offset, OffsetType
from ._client import Publisher, PublisherBatchFast, PublisherBatchLimit, \
    PublisherConstr, Subscriber, stream_messsage_ctx, \
    PublisherBatch, PublisherBatchMem

import typing as tp

__all__ = [
    'connection',

    # client api
    'StreamsClient', 'streams_client', 'Offset', 'OffsetType',

    # publisher and subscriber api
    'Publisher', 'PublisherBatchFast', 'PublisherBatchMemLimit', 'PublisherConstr',
    'Subscriber',
    # deprecated
    'PublisherBatch', 'PublisherBatchLimit',

    'AMQPBody', 'Symbol',

    # message context API
    'MessageCtx', 'stream_messsage_ctx', 'get_message_ctx',
]

# vim: sw=4:et:ai
