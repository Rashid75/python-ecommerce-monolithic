"""Security headers and rate limiting.

Both are about what happens before a request reaches any business logic:
what a browser is told it may do with the response, and how often one
caller may ask at all.
"""

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import audit


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Tell the browser what it may not do with this response.

    This API returns JSON to programs, so most of these headers are
    guarding against the response being treated as something else.
    """

    def __init__(self, app: Any, *, production: bool) -> None:
        super().__init__(app)
        self._production = production

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)

        # Stop a browser guessing the content type. Without it, a JSON
        # response containing attacker-chosen text can be sniffed as HTML
        # and executed as a page.
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Nothing here should ever be framed. Old header and modern CSP
        # directive together, because support differs.
        response.headers.setdefault("X-Frame-Options", "DENY")

        # Do not send this URL to whatever a user navigates to next. API
        # paths contain ids.
        response.headers.setdefault("Referrer-Policy", "no-referrer")

        if self._production:
            # Production only, for two reasons. HSTS over plain HTTP is
            # meaningless and, once a browser has seen it, that host is
            # HTTPS-only for the max-age - which breaks local development
            # on http://localhost for a long time.
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
            # Strict CSP for an API that returns only JSON. Not applied
            # outside production because /docs loads Swagger from a CDN,
            # and the docs are disabled in production anyway.
            response.headers.setdefault(
                "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
            )
        return response


class RateLimiter:
    """A fixed-window counter, per key, in this process's memory.

    Deliberately simple, and its limits are worth stating plainly:

    It counts per process. Two workers mean twice the effective limit, and
    a restart forgets everything. It is therefore a guard against brute
    force and accidental floods, not a quota system, and not a defence
    against a distributed attacker.

    The project rules rule out Redis, which is what a shared counter would
    need. That is the right trade here - a per-process limit stops the
    attacks this application actually faces, and pretending otherwise would
    be worse than saying so.
    """

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] < cutoff:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            return True


limiter = RateLimiter()

# path prefix -> (requests, seconds). Tight where a failure is cheap for an
# attacker and expensive for us, loose everywhere else.
LIMITS: tuple[tuple[str, int, float], ...] = (
    # Sign-in is the password-guessing surface. Argon2 makes each attempt
    # costly for the server too, so this protects availability as well.
    ("/api/v1/auth/login", 10, 60.0),
    # Account creation, to stop a script filling the users table.
    ("/api/v1/users", 5, 60.0),
    # The webhook is unauthenticated by design. Verifying a signature is
    # cheap but not free, and this bounds what an unsigned flood costs.
    ("/api/v1/webhooks", 120, 60.0),
    # Checkout holds locks and writes several tables. One client should
    # not be able to start hundreds at once.
    ("/api/v1/orders", 60, 60.0),
)


def _client_key(request: Request) -> str:
    """Who to count against.

    request.client.host is the peer address, which behind a proxy is the
    proxy. Step 73 puts Nginx in front and sets X-Forwarded-For; until the
    application is told which proxies to trust, honouring that header would
    let any caller claim any address and bypass this entirely. So: the peer
    address, and a note in the deployment step that this must be revisited
    together with proxy trust.
    """
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Refuse a caller that is asking too often."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        for prefix, limit, window in LIMITS:
            if not request.url.path.startswith(prefix):
                continue
            # Only POST. Reading an order list is not the surface any of
            # these limits exist for, and rate-limiting reads would make
            # an ordinary customer hit a wall while browsing.
            if request.method != "POST":
                continue
            key = f"{prefix}:{_client_key(request)}"
            if not limiter.allow(key, limit, window):
                audit("ratelimit.blocked", path=prefix, limit=limit, window_seconds=window)
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please slow down.",
                        "code": "rate_limited",
                    },
                    # Tells a well-behaved client when to come back, and
                    # says nothing about who else is being counted.
                    headers={"Retry-After": str(int(window))},
                )
            break
        return await call_next(request)
