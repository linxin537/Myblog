import time
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60

        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > window_start
        ]

        limit = 10 if request.url.path.endswith("/login") or request.url.path.endswith("/register") else self.requests_per_minute

        if len(self.requests[client_ip]) >= limit:
            return Response(
                content='{"code": 9999, "message": "请求过于频繁，请稍后再试", "data": null}',
                status_code=429,
                media_type="application/json",
            )

        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response
