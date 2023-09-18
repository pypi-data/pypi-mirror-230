# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import yarl
import typing
import asyncio
import aio_pika

from abc import abstractmethod

from ...extend.asyncio.pool import ObjectInterface, ObjectPool


class _ProducerBase(ObjectInterface):

    @staticmethod
    async def create_connection(
            url: yarl.URL, timeout: aio_pika.abc.TimeoutType = None, **kwargs
    ) -> aio_pika.RobustConnection:

        connection: aio_pika.RobustConnection = aio_pika.RobustConnection(url, **kwargs)

        await connection.connect(timeout)

        return connection

    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection):

        self._connection: aio_pika.abc.AbstractRobustConnection = connection
        self._channel: typing.Union[aio_pika.abc.AbstractRobustChannel, None] = None
        self._exchange: typing.Union[aio_pika.abc.AbstractExchange, None] = None

    @abstractmethod
    async def open(self, *args, **kwargs):

        raise NotImplementedError()

    async def close(self, with_connection=False):

        await self._channel.close()

        if with_connection is True:
            await self._connection.close()

    async def publish(self, message, routing_key, **kwargs):

        return await self._exchange.publish(
            message if isinstance(message, aio_pika.Message) else aio_pika.Message(message),
            routing_key, **kwargs
        )


class RabbitMQProducer(_ProducerBase):
    """RabbitMQ发布者
    """

    async def open(
        self, *,
        channel_number: int = None, publisher_confirms: bool = True, on_return_raises: bool = False
    ):

        self._channel = await self._connection.channel(channel_number, publisher_confirms, on_return_raises)
        self._exchange = self._channel.default_exchange


class RabbitMQProducerForExchange(_ProducerBase):
    """RabbitMQ交换机发布者
    """

    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection, exchange_name: str):

        super().__init__(connection)

        self._exchange_name: str = exchange_name

    async def open(
            self, *,
            exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.FANOUT, exchange_config: typing.Dict = None,
            channel_number: int = None, publisher_confirms: bool = True, on_return_raises: bool = False
    ):

        if exchange_config is None:
            exchange_config = {}

        self._channel = await self._connection.channel(channel_number, publisher_confirms, on_return_raises)
        self._exchange = await self._channel.declare_exchange(self._exchange_name, exchange_type, **exchange_config)

##################################################

class _ProducerPoolBase(ObjectPool):

    def __init__(
            self, pool_size: int, url: yarl.URL,
            timeout: aio_pika.abc.TimeoutType = None, **kwargs
    ):

        super().__init__(pool_size)

        self._connection = aio_pika.RobustConnection(url, **kwargs)

        asyncio.create_task(self._connection.connect(timeout))

    @abstractmethod
    def _create(self) -> ObjectInterface:

        raise NotImplementedError()

    async def close(self):

        await super().close()

        await self._connection.close()

    async def publish(self, message, routing_key=r'', **kwargs):

        async with self.get() as producer:
            return await producer.publish(
                message if isinstance(message, aio_pika.Message) else aio_pika.Message(message),
                routing_key, **kwargs
            )


class RabbitMQProducerPool(_ProducerPoolBase):
    """RabbitMQ发布者连接池
    """

    def _create(self) -> RabbitMQProducer:

        return RabbitMQProducer(self._connection)

    async def open(
        self, *,
        channel_number: int = None, publisher_confirms: bool = True, on_return_raises: bool = False
    ):

        await self._connection.ready()

        await super().open(
            channel_number=channel_number,
            publisher_confirms=publisher_confirms,
            on_return_raises=on_return_raises
        )


class RabbitMQProducerForExchangePool(_ProducerPoolBase):
    """RabbitMQ交换机发布者连接池
    """

    def __init__(
            self, pool_size: int, url: yarl.URL, exchange_name: str,
            timeout: aio_pika.abc.TimeoutType = None, **kwargs
    ):

        super().__init__(pool_size, url, timeout, **kwargs)

        self._exchange_name: str = exchange_name

    def _create(self) -> RabbitMQProducerForExchange:

        return RabbitMQProducerForExchange(self._connection, self._exchange_name)

    async def open(
            self, *,
            exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.FANOUT, exchange_config: typing.Dict = None,
            channel_number: int = None, publisher_confirms: bool = True, on_return_raises: bool = False
    ):

        await self._connection.ready()

        await super().open(
            exchange_type=exchange_type,
            exchange_config=exchange_config,
            channel_number=channel_number,
            publisher_confirms=publisher_confirms,
            on_return_raises=on_return_raises
        )
