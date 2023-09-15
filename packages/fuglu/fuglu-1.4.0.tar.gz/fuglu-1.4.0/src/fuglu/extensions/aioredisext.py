import logging
import socket
import datetime
from typing import AsyncIterator, Optional, Dict, Awaitable, Union

try:
    import asyncio
    import redis.asyncio as aioredis

    from redis import __version__ as redisversion
    STATUS = f"redis.asyncio installed, redis version: {redisversion}"
    ENABLED = True
except ImportError:
    STATUS = "redis.asyncio not installed"
    ENABLED = False
    aioredis = None
    redisversion = 'unkonwn'


AIOREDIS_TIMEOUT = 10.0
AIOEDIS_MAXATTEMPTS = 3
REDIS_POOL_TIMEOUT = 10
REDIS_POOL_MAXCON = 200

RETRY_ON_EXCS = (aioredis.ConnectionError,
                 aioredis.TimeoutError,
                 asyncio.exceptions.CancelledError,
                 asyncio.exceptions.TimeoutError,
                 )


class AIORedisBaseBackend:
    def __init__(self, backendconfig: str):
        super().__init__()
        self._url = backendconfig
        self._pool = None
        self._redis = None
        self.logger = logging.getLogger(f"fuglu.extensions.AIORedisBaseBackend")

    async def _get_redis(self, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None):
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        if self._pool is None:
            self.logger.debug(f"New redis pool({self._url})")
            try:
                # linux only
                socket_keepalive_options = {
                    socket.TCP_KEEPIDLE: 1,
                    socket.TCP_KEEPCNT:  5,
                    socket.TCP_KEEPINTVL: 3,
                }
            except:
                socket_keepalive_options = {}
            self._pool = aioredis.BlockingConnectionPool(timeout=REDIS_POOL_TIMEOUT,
                                                         max_connections=REDIS_POOL_MAXCON,
                                                         socket_timeout=2,
                                                         socket_keepalive=True,
                                                         socket_connect_timeout=2.0,
                                                         socket_keepalive_options=socket_keepalive_options,
                                                         retry_on_timeout=True,
                                                         ).from_url(url=self._url)
        if self._redis is None:
            self.logger.debug(f"New redis instance connecting to pool(url={self._url})")
            self._redis = await aioredis.StrictRedis(connection_pool=self._pool)
        return self._redis

    async def get_redis(self, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None):
        if not self._redis:
            timeout = timeout if timeout else AIOREDIS_TIMEOUT
            attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
            while attempts:
                attempts -= 1
                try:
                    await self._get_redis(timeout=timeout)
                except RETRY_ON_EXCS as e:
                    typestring = str(type(e)).replace("<", "").replace(">", "")
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'get_redis' - retry ({typestring}: {str(e)})")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'get_redis' ({typestring}: {str(e)})")
                except Exception as e:
                    typestring = str(type(e)).replace("<", "").replace(">", "")
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'get_redis' - retry ({typestring}: {str(e)})")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'get_redis': ({typestring}: {str(e)})", exc_info=e)

        return self._redis

    async def hgetall(self, key: bytes, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[bytes]:
        keydata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis(timeout=timeout)
                keydata = await asyncio.wait_for(r.hgetall(key), timeout=timeout)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hgetall' - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hgetall' ({typestring}: {str(e)})")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hgetall' - retry ({typestring}: {str(e)})")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hgetall': ({typestring}: {str(e)})", exc_info=e)
        return keydata

    async def scan_iter(self, match: str = "*", count: int = 250, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Optional[AsyncIterator]:
        iterator = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis(timeout=timeout)
                #iterator = await asyncio.wait_for(r.scan_iter(match=match, count=count), timeout=timeout)
                iterator = r.scan_iter(match=match, count=count)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'scan_iter' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'scan_iter' ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'scan_iter' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'scan_iter' ({typestring}) {str(e)}", exc_info=e)
        if iterator:
            yield iterator

    async def hset(self, key: bytes, mapping: Dict, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Awaitable:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis(timeout=timeout)
                outdata = await asyncio.wait_for(r.hset(key, mapping=mapping), timeout=timeout)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hset' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hset' ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hset' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hset' ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def hmset(self, key: bytes, mapping: Dict, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Awaitable:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis(timeout=timeout)
                outdata = await asyncio.wait_for(r.hmset(key, mapping=mapping), timeout=timeout)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hmset' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hmset' ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hmset' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hmset' ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def hincrby(self, key: bytes, field: bytes, increment: Union[int, float] = 1, timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Awaitable:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis(timeout=timeout)
                if isinstance(increment, int):
                    outdata = await asyncio.wait_for(r.hincrby(key, field, amount=increment), timeout=timeout)
                else:
                    outdata = await asyncio.wait_for(r.hincrbyfloat(key, field, amount=increment), timeout=timeout)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hincrby' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hincrby' ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'hincrby' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'hincrby' ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def expire(self, key: bytes, time: Union[int, datetime.datetime], timeout: Optional[float] = None, timeout_attempts: Optional[int] = None) -> Awaitable:
        outdata = None
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        attempts = timeout_attempts if timeout_attempts else AIOEDIS_MAXATTEMPTS
        while attempts:
            attempts -= 1
            try:
                r = await self._get_redis(timeout=timeout)
                outdata = await asyncio.wait_for(r.expire(key, time), timeout=timeout)
                attempts = 0  # no more attempts
            except RETRY_ON_EXCS as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'expire' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'expire' ({typestring}) {str(e)}")
            except Exception as e:
                typestring = str(type(e)).replace("<", "").replace(">", "")
                self._redis = None
                if attempts:
                    self.logger.warning(f"Connection error in 'expire' - retry ({typestring}) {str(e)}")
                    await asyncio.sleep(0.1)
                else:
                    self.logger.error(f"Connection error in 'expire' ({typestring}) {str(e)}", exc_info=e)
        return outdata

    async def close(self, timeout: Optional[float] = None):
        """Close open connections and pools"""
        timeout = timeout if timeout else AIOREDIS_TIMEOUT
        if self._redis:
            for url, red in self._redis.items():
                try:
                    await asyncio.wait_for(red.close(close_connection_pool=False), timeout=timeout)
                except Exception as e:
                    typestring = str(type(e)).replace("<", "").replace(">", "")
                    self.logger.warning(f"Problem closing redis connection: ({typestring}) {str(e)}")
            self._redis = None

        if self._pool:
            for url, pool in self._pool.items():
                try:
                    await asyncio.wait_for(pool.disconnect(), timeout=timeout)
                except Exception as e:
                    typestring = str(type(e)).replace("<", "").replace(">", "")
                    self.logger.warning(f"Problem closing redis pool: ({typestring}) {str(e)}")
            self._pool = None

    def __del__(self):
        """destructor - make sure connections are all closed"""
        self.close(timeout=3.0)