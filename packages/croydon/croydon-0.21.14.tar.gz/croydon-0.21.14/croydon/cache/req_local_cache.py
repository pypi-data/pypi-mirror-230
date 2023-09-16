from typing import Optional, Any, Dict
from contextvars import ContextVar
from .abc import AbstractCache
from croydon.middleware import req_cache_ctx


class RequestLocalCache(AbstractCache):
    NAME = "RequestLocalCache"

    _ctxvar: ContextVar[Dict[str, Any]]

    def __init__(self, ctxvar: Optional[ContextVar[Optional[Dict[str, Any]]]] = None):
        if ctxvar is None:
            ctxvar = req_cache_ctx
        self._ctxvar = ctxvar

    async def initialise(self) -> None:
        pass

    async def get(self, key: str) -> Optional[Any]:
        cache = self._ctxvar.get()
        if cache is None:
            return None
        return cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        cache = self._ctxvar.get()
        if cache is None:
            return
        cache[key] = value
        self._ctxvar.set(cache)

    async def has(self, key: str) -> bool:
        cache = self._ctxvar.get()
        if cache is None:
            return False
        return key in cache

    async def delete(self, key: str) -> bool:
        had = await self.has(key)
        if had:
            cache = self._ctxvar.get()
            del cache[key]
            self._ctxvar.set(cache)
        return had
