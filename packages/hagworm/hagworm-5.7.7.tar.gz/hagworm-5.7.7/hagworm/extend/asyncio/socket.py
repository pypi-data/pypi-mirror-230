# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import typing
import signal
import socket
import asyncio
import base64
import msgpack

from typing import List

from ...extend.asyncio.base import Utils, install_uvloop
from ...extend.interface import RunnableInterface

from ..error import RouterError


DEFAULT_LIMIT = 0xffffff


async def recv_msg(reader, timeout=None):

    result = None

    with Utils.suppress(asyncio.TimeoutError):

        data = await asyncio.wait_for(reader.readline(), timeout)

        if data:
            result = msgpack.loads(
                base64.b64decode(data)
            )

    return result


async def send_msg(writer, data):

    writer.writelines(
        [
            base64.b64encode(
                msgpack.dumps(data)
            ),
            b'\n',
        ]
    )

    await writer.drain()


class UnixSocketServer:

    def __init__(self, client_connected_cb, path, limit=DEFAULT_LIMIT):

        self._client_connected_cb = client_connected_cb

        self._path = path
        self._limit = limit

        self._server = None

    async def open(self):

        if os.path.exists(self._path):
            os.remove(self._path)

        self._server = await asyncio.start_unix_server(
            self._client_connected_cb, self._path, limit=self._limit
        )

        await self._server.start_serving()

    async def close(self):

        if self._server is not None:
            self._server.close()
            self._server = None


class UnixSocketClient:

    def __init__(self, path, limit=DEFAULT_LIMIT):

        self._path = path
        self._limit = limit

        self._reader = None
        self._writer = None

    @property
    def reader(self):
        return self._reader

    @property
    def writer(self):
        return self._writer

    async def open(self):

        self._reader, self._writer = await asyncio.open_unix_connection(
            self._path,
            limit=self._limit
        )

    async def close(self):

        self._reader = None

        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

    async def recv_msg(self, timeout=None):

        return await recv_msg(self._reader, timeout)

    async def send_msg(self, data):

        return await send_msg(self._writer, data)


class Router:

    def __init__(self, root=r''):

        self._root = root
        self._reg_func = {}

    def __repr__(self):

        return self._reg_func.__repr__()

    def __call__(self, method, *args, **kwargs):

        func = self._reg_func.get(method)

        if not func:
            raise RouterError(f'{method} not exists')

        return func(*args, **kwargs)

    def _reg(self, method, func):

        _method = f'{self._root}{method}'

        if _method in self._reg_func:
            raise RouterError(f'{method} has exists')

        self._reg_func[_method] = func

    def reg(self, method):

        def _reg_func(func):
            self._reg(method, func)
            return func

        return _reg_func

    def items(self):

        return self._reg_func.items()

    def include(self, router):

        for method, func in router.items():
            self._reg(method, func)


class SocketConfig:

    __slots__ = [r'client_connected_cb', r'address', r'family', r'backlog', r'reuse_port', r'buffer_limit']

    def __init__(self, client_connected_cb, address, family, backlog, reuse_port, buffer_limit):

        self.client_connected_cb = client_connected_cb
        self.address = address
        self.family = family
        self.backlog = backlog
        self.reuse_port = reuse_port
        self.buffer_limit = buffer_limit


class AsyncTcpServer(RunnableInterface):

    def __init__(
            self, client_connected_cb, address, *,
            family=socket.AF_INET, backlog=None, reuse_port=True, buffer_limit=DEFAULT_LIMIT,
            on_startup=None, on_shutdown=None
    ):

        self._listeners: List[SocketConfig] = [
            SocketConfig(
                client_connected_cb, address,
                family, backlog, reuse_port, buffer_limit
            )
        ]

        self._on_startup = on_startup
        self._on_shutdown = on_shutdown

        self._servers: typing.List[asyncio.AbstractServer] = []

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    async def __aenter__(self):

        for server in self._servers:
            await server.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, _traceback):

        for server in self._servers:
            await server.__aexit__(exc_type, exc_value, _traceback)

    def add_listener(
            self, client_connected_cb, address, *,
            family=socket.AF_INET, backlog=None, reuse_port=True, buffer_limit=DEFAULT_LIMIT
    ):

        self._listeners.append(
            SocketConfig(
                client_connected_cb, address,
                family, backlog, reuse_port, buffer_limit
            )
        )

    def run(self, *, debug=None):

        Utils.print_slogan()

        install_uvloop()

        asyncio.run(self._run(), debug=debug)

    async def _run(self):

        if self._on_startup is not None:
            await self._on_startup()

        for config in self._listeners:

            if config.family == socket.AF_UNIX:

                _socket_server = await asyncio.start_unix_server(
                    config.client_connected_cb, config.address, limit=config.buffer_limit
                )

                Utils.log.success(f'unix server [pid:{Utils.getpid()}] startup complete: {config.address}')

            else:

                _socket = socket.create_server(
                    config.address, family=config.family, backlog=config.backlog, reuse_port=config.reuse_port
                )

                _socket_server = await asyncio.start_server(
                    config.client_connected_cb,
                    limit=config.buffer_limit, sock=_socket
                )

                Utils.log.success(f'socket server [pid:{Utils.getpid()}] startup complete: {config.address}')

            self._servers.append(_socket_server)

        async with self:
            await asyncio.gather(*(_server.wait_closed() for _server in self._servers))

        if self._on_shutdown is not None:
            await self._on_shutdown()

    def _exit(self, *_):

        for _server in self._servers:
            _server.close()
