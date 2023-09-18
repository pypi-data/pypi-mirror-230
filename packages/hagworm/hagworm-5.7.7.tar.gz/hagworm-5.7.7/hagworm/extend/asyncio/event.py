# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from .base import Utils, AsyncCirculatorForSecond, FuncWrapper, FutureWithTimeout

from ..event import EventDispatcher as _EventDispatcher
from ..error import catch_error


class EventDispatcher(_EventDispatcher):
    """支持异步函数的事件总线
    """

    def _gen_observer(self):

        return FuncWrapper()


class DistributedEvent(EventDispatcher):
    """Redis实现的消息广播总线
    """

    def __init__(self, redis_client, channel_name, channel_count):

        super().__init__()

        self._redis_client = redis_client

        self._channels = [f'event_bus_{Utils.md5_u32(channel_name)}_{index}' for index in range(channel_count)]

        for channel in self._channels:
            Utils.create_task(self._event_listener(channel))

    async def _event_listener(self, channel):

        async for _ in AsyncCirculatorForSecond():

            with catch_error():

                receiver = self._redis_client.pubsub(ignore_subscribe_messages=True)

                try:

                    await receiver.subscribe(channel)

                    Utils.log.info(f'event bus channel({channel}) receiver created')

                    while True:

                        message = await receiver.get_message(timeout=10)

                        if message:
                            await self._event_assigner(message)

                except Exception as err:

                    Utils.log.warning(str(err))

                finally:

                    await receiver.close()

    async def _event_assigner(self, message):

        data = Utils.msgpack_decode(message[r'data'])

        _type = data.get(r'type', r'')
        args = data.get(r'args', [])
        kwargs = data.get(r'kwargs', {})

        if _type in self._observers:
            self._observers[_type](*args, **kwargs)

    def _gen_observer(self):

        return FuncWrapper()

    async def dispatch(self, _type, *args, **kwargs):

        channel = self._channels[Utils.md5_u32(_type) % len(self._channels)]

        message = {
            r'type': _type,
            r'args': args,
            r'kwargs': kwargs,
        }

        await self._redis_client.publish(channel, Utils.msgpack_encode(message))

    def gen_event_waiter(self, event_type, delay_time):

        return EventWaiter(self, event_type, delay_time)


class EventWaiter(FutureWithTimeout):
    """带超时的临时消息接收器
    """

    def __init__(self, dispatcher, event_type, delay_time):

        super().__init__(delay_time)

        self._dispatcher = dispatcher
        self._event_type = event_type

        self._dispatcher.add_listener(self._event_type, self._event_handler)

    def set_result(self, result):

        if self.done():
            return

        super().set_result(result)

        self._dispatcher.remove_listener(self._event_type, self._event_handler)

    def _event_handler(self, *args, **kwargs):

        if not self.done():
            self.set_result({r'args': args, r'kwargs': kwargs})
