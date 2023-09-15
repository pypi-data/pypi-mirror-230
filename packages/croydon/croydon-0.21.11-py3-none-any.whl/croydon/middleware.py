from typing import Dict, Any, Optional
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


REQUEST_CACHE_CONTEXT_KEY = "request_cache"

req_cache_ctx: ContextVar[Optional[Dict[str, Any]]] = ContextVar(REQUEST_CACHE_CONTEXT_KEY, default=None)


class RequestCacheMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        req_cache = req_cache_ctx.set({})
        response = await call_next(request)
        req_cache_ctx.reset(req_cache)
        return response
