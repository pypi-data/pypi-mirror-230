from typing import Dict, Any, Optional
from unittest import IsolatedAsyncioTestCase
from contextvars import ContextVar, Token
from ..context import ctx
from ..config import DatabaseConfig
from ..cache import TraceCache, RequestLocalCache
from ..middleware import REQUEST_CACHE_CONTEXT_KEY


custom_cache_ctxvar: ContextVar[Optional[Dict[str, Any]]] = ContextVar(REQUEST_CACHE_CONTEXT_KEY, default=None)


class MongoMockTest(IsolatedAsyncioTestCase):

    token: Optional[Token[Dict[str, Any]]] = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if not ctx.initialised:
            from ..config import BaseConfig
            cfg = BaseConfig()
            ctx.from_config(cfg, ".")
        ctx.db.reconfigure(DatabaseConfig(), mock=True)

        # aiomcache conflicts with async tests as it seems to run
        # in its own async loop. This leads to "got Future attached to a different loop"
        # errors.
        #
        # Since mongo tests do not use memcached explicitly we override
        # all caches to avoid using MemcachedCache
        #
        # RequestLocalCache is created using a custom contextvar so that
        # L2 Cache resets after each test rather than after each request
        #
        # TraceCache does not store any data but is able to track its methods calls
        ctx._cache_l1 = TraceCache()
        ctx._cache_l2 = RequestLocalCache(custom_cache_ctxvar)

    async def asyncSetUp(self) -> None:
        self.token = custom_cache_ctxvar.set({})

    async def asyncTearDown(self) -> None:
        custom_cache_ctxvar.reset(self.token)
        self.token = None

