# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from coredis import lock, StrictRedis, StrictRedisCluster

from .base import Utils

from ..error import catch_error, catch_warning
from ..interface import AsyncContextManager
from .ntp import AsyncNTPClient
from .transaction import Transaction


REDIS_ERROR_RETRY_COUNT = 0x10
REDIS_POOL_WATER_LEVEL_WARNING_LINE = 0x10


class LuaLock(AsyncContextManager, lock.LuaLock):

    def __init__(
            self, redis, name, timeout=None, sleep=0.1,
            blocking=False, blocking_timeout=None, thread_local=True
    ):
        super().__init__(
            redis, name, timeout=timeout, sleep=sleep,
            blocking=blocking, blocking_timeout=blocking_timeout, thread_local=thread_local
        )

    async def _context_release(self):
        with catch_warning():
            await self.release()

    async def acquire(self, blocking=None, blocking_timeout=None):
        if self.local.get() is None:
            return await super().acquire(blocking, blocking_timeout)
        else:
            return await super().extend(self.timeout)

    async def release(self):
        if self.local.get() is not None:
            await super().release()


class ClusterLock(AsyncContextManager, lock.ClusterLock):

    def __init__(
            self, redis, name, timeout=None, sleep=0.1,
            blocking=False, blocking_timeout=None, thread_local=True
    ):
        super().__init__(
            redis, name, timeout=timeout, sleep=sleep,
            blocking=blocking, blocking_timeout=blocking_timeout, thread_local=thread_local
        )

    async def _context_release(self):
        with catch_warning():
            await self.release()

    async def acquire(self, blocking=None, blocking_timeout=None):
        if self.local.get() is None:
            return await super().acquire(blocking, blocking_timeout)
        else:
            return await super().extend(self.timeout)

    async def release(self):
        if self.local.get() is not None:
            await super().release()


class _PoolMixin(AsyncContextManager):

    def __init__(self, min_connections=0):

        self._name = Utils.uuid1()[:8]
        self._key_prefix = None
        self._min_connections = min_connections if min_connections else 0

    async def _context_release(self):

        pass

    def set_key_prefix(self, value):

        self._key_prefix = value

    def get_safe_key(self, key, *args, **kwargs):

        if self._key_prefix:
            _key = f'{self._key_prefix}:{key}'
        else:
            _key = key

        if args or kwargs:
            _key = f'{_key}:{Utils.params_sign(*args, **kwargs)}'

        return _key

    def reset(self):

        self.connection_pool.disconnect()

        self._init_connection()

        Utils.log.info(
            f"Redis connection pool reset ({self._name}): "
            f"{len(self.connection_pool._available_connections)}/{self.connection_pool.max_connections}"
        )

    def close(self):

        self.connection_pool.disconnect()
        self.connection_pool.reset()

    async def get_obj(self, name):

        result = await super().get(name)

        return Utils.pickle_loads(result) if result else result

    async def getset_obj(self, name, value):

        value = Utils.pickle_dumps(value)

        result = await super().getset(name, value)

        return Utils.pickle_loads(result) if result else result

    async def set_obj(self, name, value, ex=3600, px=None, nx=False, xx=False):

        value = Utils.pickle_dumps(value)

        return await super().set(name, value, ex=ex, px=px, nx=nx, xx=xx)


class StrictRedisPool(_PoolMixin, StrictRedis):
    """StrictRedis连接管理
    """

    def __init__(
            self,
            host, port=6379, db=0, password=None,
            min_connections=0, max_connections=32,
            max_idle_time=43200, idle_check_interval=1,
            **kwargs
    ):

        StrictRedis.__init__(
            self,
            host, port, db,
            password=password, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            **kwargs
        )

        _PoolMixin.__init__(self, min(min_connections, max_connections))

    def _init_connection(self):

        connections = []

        with catch_error():
            for _ in range(self._min_connections):
                connections.append(
                    self.connection_pool.get_connection()
                )

        with catch_error():
            for connection in connections:
                self.connection_pool.release(connection)

    async def initialize(self):

        self._init_connection()

        config = self.connection_pool.connection_kwargs

        Utils.log.info(
            f"Redis Pool [{config[r'host']}:{config[r'port']}] ({self._name}) initialized: "
            f"{self.get_created_connections()}/{self.connection_pool.max_connections}"
        )

        return self

    def get_created_connections(self):

        return self.connection_pool._created_connections

    def allocate_lock(self, name, *, timeout=None, sleep=0.1, blocking_timeout=None, thread_local=True):

        return self.lock(
            name, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout,
            lock_class=LuaLock, thread_local=thread_local
        )


class StrictRedisClusterPool(_PoolMixin, StrictRedisCluster):
    """StrictRedisCluster连接管理
    """

    def __init__(
            self,
            host=None, port=None, startup_nodes=None, password=None,
            min_connections=0, max_connections=32,
            max_idle_time=43200, idle_check_interval=1,
            **kwargs
    ):

        StrictRedisCluster.__init__(
            self,
            host, port, startup_nodes,
            password=password, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            **kwargs
        )

        _PoolMixin.__init__(self, min(min_connections, max_connections))

    def _init_connection(self):

        connections = []

        with catch_error():
            for _ in range(self._min_connections):
                connections.append(
                    self.connection_pool.get_connection_by_key(Utils.uuid1())
                )

        with catch_error():
            for connection in connections:
                self.connection_pool.release(connection)

    async def initialize(self):

        await self.connection_pool.initialize()

        self._init_connection()

        nodes = self.connection_pool.nodes.nodes

        Utils.log.info(
            f"Redis Cluster Pool {list(nodes.keys())} ({self._name}) initialized: "
            f"{self.get_created_connections()}/{self.connection_pool.max_connections}"
        )

        return self

    def get_created_connections(self):

        return sum(self.connection_pool._created_connections_per_node.values())

    def allocate_lock(self, name, *, timeout=None, sleep=0.1, blocking_timeout=None, thread_local=True):

        return self.lock(
            name, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout,
            lock_class=ClusterLock, thread_local=thread_local
        )


class RedisDelegate:
    """Redis功能组件
    """

    def __init__(self):

        self._redis_pool = None

    @property
    def redis_pool(self):

        return self._redis_pool

    async def init_redis_single(
            self,
            host, port=6379, db=0, password=None, *,
            min_connections=0, max_connections=32,
            max_idle_time=43200, idle_check_interval=1,
            **kwargs
    ):

        self._redis_pool = await StrictRedisPool(
            host, port, db, password=password,
            min_connections=min_connections, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            **kwargs
        ).initialize()

        return self._redis_pool

    async def init_redis_cluster(
            self,
            host=None, port=None, startup_nodes=None, password=None, *,
            min_connections=0, max_connections=32,
            max_idle_time=43200, idle_check_interval=1,
            **kwargs
    ):

        self._redis_pool = await StrictRedisClusterPool(
            host, port, startup_nodes, password=password,
            min_connections=min_connections, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            **kwargs
        ).initialize()

        return self._redis_pool

    def set_redis_key_prefix(self, value):

        self._redis_pool.set_key_prefix(value)

    async def redis_health(self):

        result = False

        with catch_error():
            result = bool(await self._redis_pool.info())

        return result

    def reset_redis_pool(self):

        self._redis_pool.reset()

    def close_redis_pool(self):

        self._redis_pool.close()

    def get_redis_client(self):

        return self._redis_pool


class ShareCache(AsyncContextManager):
    """共享缓存，使用with进行上下文管理

    基于分布式锁实现的一个缓存共享逻辑，保证在分布式环境下，同一时刻业务逻辑只执行一次，其运行结果会通过缓存被共享

    """

    def __init__(self, redis_client, share_key, lock_timeout=60, lock_blocking_timeout=60):

        self._redis_client = redis_client
        self._share_key = redis_client.get_safe_key(share_key)

        self._lock = self._redis_client.allocate_lock(
            redis_client.get_safe_key(f'share_cache:{share_key}'),
            timeout=lock_timeout, blocking_timeout=lock_blocking_timeout
        )

        self.result = None

    async def _context_release(self):

        await self.release()

    async def get(self):

        result = await self._redis_client.get_obj(self._share_key)

        if result is None:

            if await self._lock.acquire():
                result = await self._redis_client.get_obj(self._share_key)

        return result

    async def set(self, value, expire=None):

        return await self._redis_client.set_obj(self._share_key, value, expire)

    async def release(self):

        if self._lock:
            await self._lock.release()

        self._redis_client = self._lock = None


class PeriodCounter:

    MIN_EXPIRE = 60

    def __init__(self, redis_client, key_prefix, time_slice: int, *, ntp_client: AsyncNTPClient = None):

        self._redis_client = redis_client

        self._key_prefix = key_prefix
        self._time_slice = time_slice

        self._ntp_client = ntp_client

    def _get_key(self) -> str:

        timestamp = Utils.timestamp() if self._ntp_client is None else self._ntp_client.timestamp

        time_period = Utils.math.floor(timestamp / self._time_slice)

        return self._redis_client.get_safe_key(f'{self._key_prefix}:{time_period}')

    async def _execute(self, key: str, val: int) -> int:

        res = None

        async with await self._redis_client.pipeline(transaction=False) as pipeline:
            await pipeline.incrby(key, val)
            await pipeline.expire(key, max(self._time_slice, self.MIN_EXPIRE))
            res, _ = await pipeline.execute()

        return res

    async def incr(self, val: int = 1):

        return await self._execute(self._get_key(), val)

    async def incr_with_trx(self, val: int = 1) -> (int, Transaction):

        _key = self._get_key()

        res = await self._execute(_key, val)

        if res is not None:
            trx = Transaction()
            trx.add_rollback_callback(self._execute, _key, -val)
        else:
            trx = None

        return res, trx

    async def decr(self, val: int = 1) -> int:

        return await self._execute(self._get_key(), -val)

    async def decr_with_trx(self, val: int = 1) -> (int, Transaction):

        _key = self._get_key()

        res = await self._execute(_key, -val)

        if res is not None:
            trx = Transaction()
            trx.add_rollback_callback(self._execute, _key, val)
        else:
            trx = None

        return res, trx
