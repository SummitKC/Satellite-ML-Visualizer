"""Authenticated, rate-limited client for the Space-Track.org API.

Space-Track is the only source of *historical* TLEs for objects that have
already decayed, which is what makes the SATCAT decay dates usable as
training labels (CelesTrak's feeds only carry the current catalog).

Their published caps are 30 requests/minute and 300/hour, and exceeding
them can get an account suspended, so every request goes through
_RateLimiter rather than relying on callers to pace themselves.
"""

import asyncio
import logging
import time
from collections import deque
from types import TracebackType

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
QUERY_BASE = "https://www.space-track.org/basicspacedata/query"


class SpaceTrackError(RuntimeError):
    """Raised for authentication and query failures against Space-Track."""


class _RateLimiter:
    """Paces requests to stay under both a per-minute and per-hour cap.

    The lock is held across the sleep so that concurrent callers queue up
    behind one another instead of all waking at once and bursting past the
    cap together.
    """

    def __init__(self, per_minute: int, per_hour: int) -> None:
        self._per_minute = per_minute
        self._per_hour = per_hour
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()

                while self._calls and now - self._calls[0] >= 3600:
                    self._calls.popleft()

                minute_calls = [t for t in self._calls if now - t < 60]

                wait = 0.0
                if len(minute_calls) >= self._per_minute:
                    wait = max(wait, minute_calls[0] + 60 - now)
                if len(self._calls) >= self._per_hour:
                    wait = max(wait, self._calls[0] + 3600 - now)

                if wait <= 0:
                    self._calls.append(now)
                    return

                logger.info("Space-Track rate cap reached; waiting %.0fs", wait)
                await asyncio.sleep(wait)


class SpaceTrackClient:
    """Async context manager holding an authenticated Space-Track session."""

    def __init__(self) -> None:
        settings = get_settings()
        self._identity = settings.spacetrack_identity
        self._password = settings.spacetrack_password
        self._limiter = _RateLimiter(
            settings.spacetrack_requests_per_minute,
            settings.spacetrack_requests_per_hour,
        )
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "SpaceTrackClient":
        if not self._identity or not self._password:
            raise SpaceTrackError(
                "Space-Track credentials missing. Set SPACETRACK_IDENTITY and "
                "SPACETRACK_PASSWORD in backend/.env"
            )

        # Historical queries return large payloads and are slow server-side.
        self._client = httpx.AsyncClient(timeout=300.0, follow_redirects=True)
        try:
            await self._login()
        except Exception:
            await self._client.aclose()
            raise
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _login(self) -> None:
        assert self._client is not None

        response = await self._client.post(
            LOGIN_URL,
            data={"identity": self._identity, "password": self._password},
        )

        # A bad password comes back as 200 with a JSON error body, not a 4xx.
        if response.status_code != 200 or "Failed" in response.text:
            raise SpaceTrackError(
                "Space-Track login failed; check SPACETRACK_IDENTITY/PASSWORD"
            )

        logger.info("Authenticated to Space-Track as %s", self._identity)

    async def query(self, path: str) -> list[dict]:
        """Run one /basicspacedata/query request, returning decoded rows."""
        assert self._client is not None, "use SpaceTrackClient as a context manager"

        await self._limiter.acquire()
        response = await self._client.get(f"{QUERY_BASE}/{path}")

        if response.status_code == 429:
            logger.warning("Space-Track returned 429; backing off 60s before retry")
            await asyncio.sleep(60)
            await self._limiter.acquire()
            response = await self._client.get(f"{QUERY_BASE}/{path}")

        response.raise_for_status()

        try:
            payload = response.json()
        except ValueError as e:
            raise SpaceTrackError(
                f"Space-Track returned a non-JSON response: {response.text[:200]}"
            ) from e

        if not isinstance(payload, list):
            raise SpaceTrackError(f"Unexpected Space-Track response shape: {payload}")

        return payload
