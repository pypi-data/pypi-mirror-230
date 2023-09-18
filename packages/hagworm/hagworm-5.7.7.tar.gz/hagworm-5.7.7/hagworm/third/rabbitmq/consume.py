# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import yarl
import asyncio
import aio_pika

from ...extend.asyncio.pool import ObjectInterface, ObjectPool


class RabbitMQConsumer(ObjectInterface):
    """RabbitMQ消费者
    """

    @staticmethod
    async def create_connection(
            url: yarl.URL, timeout: aio_pika.abc.TimeoutType = None, **kwargs
    ) -> aio_pika.RobustConnection:

        connection: aio_pika.RobustConnection = aio_pika.RobustConnection(url, **kwargs)

        await connection.connect(timeout)

        return connection

    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection, queue_name: str):

        self._connection: aio_pika.abc.AbstractRobustConnection = connection
        self._channel: typing.Union[aio_pika.abc.AbstractRobustChannel, None] = None

        self._queue: typing.Union[aio_pika.abc.AbstractRobustQueue, None] = None
        self._queue_name: str = queue_name

    @property
    def queue_name(self) -> str:

        return self._queue_name

    async def open(
            self, *,
            consume_func=None, consume_no_ack=False, channel_qos_config=None, queue_config=None
    ):

        if channel_qos_config is None:
            channel_qos_config = {r'prefetch_count': 1}

        if queue_config is None:
            queue_config = {}

        self._channel = await self._connection.channel()

        await self._channel.set_qos(**channel_qos_config)

        self._queue = await self._channel.declare_queue(self._queue_name, **queue_config)

        if consume_func is not None:
            await self._queue.consume(consume_func, no_ack=consume_no_ack)

    async def close(self, with_connection=False):

        await self._channel.close()

        if with_connection is True:
            await self._connection.close()

    async def get(self, *, no_ack=False, timeout=1) -> aio_pika.abc.AbstractIncomingMessage:

        return await self._queue.get(no_ack=no_ack, timeout=timeout)


class RabbitMQConsumerForExchange(RabbitMQConsumer):
    """RabbitMQ注册到交换机的消费者
    """

    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection, queue_name: str, exchange_name: str):
        
        super().__init__(connection, queue_name)

        self._exchange: typing.Union[aio_pika.abc.AbstractExchange, None] = None
        self._exchange_name: str = exchange_name

    @property
    def exchange_name(self) -> str:

        return self._exchange_name

    async def open(
            self, *,
            consume_func=None, consume_no_ack=False, channel_qos_config=None, queue_config=None, routing_key=None
    ):

        await super().open(
            consume_func=consume_func, consume_no_ack=consume_no_ack,
            channel_qos_config=channel_qos_config, queue_config=queue_config
        )

        self._exchange = await self._channel.get_exchange(self._exchange_name)

        await self._queue.bind(self._exchange, routing_key)

##################################################

class RabbitMQConsumerPool(ObjectPool):
    """RabbitMQ消费者连接池
    """

    def __init__(
            self, pool_size: int, url: yarl.URL, queue_name: str,
            timeout: aio_pika.abc.TimeoutType = None, **kwargs
    ):

        super().__init__(pool_size)

        self._queue_name: str = queue_name

        self._connection: aio_pika.RobustConnection = aio_pika.RobustConnection(url, **kwargs)

        asyncio.create_task(self._connection.connect(timeout))

    @property
    def queue_name(self) -> str:

        return self._queue_name

    def _create(self) -> RabbitMQConsumer:

        return RabbitMQConsumer(self._connection, self._queue_name)

    async def open(
            self, *,
            consume_func=None, consume_no_ack=False, channel_qos_config=None, queue_config=None,
    ):

        await self._connection.ready()

        await ObjectPool.open(
            self,
            consume_func=consume_func, consume_no_ack=consume_no_ack,
            channel_qos_config=channel_qos_config, queue_config=queue_config,
        )

    async def close(self):

        await super().close()

        await self._connection.close()

    async def get(self, *, no_ack=False, timeout=1) -> aio_pika.abc.AbstractIncomingMessage:

        async with super().get() as consumer:
            return await consumer.get(no_ack=no_ack, timeout=timeout)


class RabbitMQConsumerForExchangePool(RabbitMQConsumerPool):
    """RabbitMQ交换机消费者连接池
    """

    def __init__(
            self, pool_size: int, url: yarl.URL, queue_name: str, exchange_name: str,
            timeout: aio_pika.abc.TimeoutType = None, **kwargs
    ):

        super().__init__(pool_size, url, queue_name, timeout, **kwargs)

        self._exchange_name: str = exchange_name

    def _create(self) -> RabbitMQConsumerForExchange:

        return RabbitMQConsumerForExchange(self._connection, self._queue_name, self._exchange_name)

    async def open(
            self, *,
            consume_func=None, consume_no_ack=False, channel_qos_config=None, queue_config=None,
            routing_key=None
    ):

        await self._connection.ready()

        await ObjectPool.open(
            self,
            consume_func=consume_func, consume_no_ack=consume_no_ack,
            channel_qos_config=channel_qos_config, queue_config=queue_config, routing_key=routing_key
        )
