import asyncio
import base64
import json
import os
import time
from collections.abc import Callable

import httpx
from boostcampapi import BoostcampEndpoints

REFRESH_SKEW_SECONDS = 60


class TokenRefreshError(Exception):
    """Raised when usable Boostcamp credentials cannot be obtained."""


class FirebaseTokenProvider:
    def __init__(self, id_token: str | None = None, refresh_token: str | None = None, *,
                 clock: Callable[[], float] = time.time,
                 client_factory: Callable[..., httpx.AsyncClient] = httpx.AsyncClient) -> None:
        self._id_token = id_token
        self._refresh_token = refresh_token
        self._configured_id_token = id_token
        self._configured_refresh_token = refresh_token
        self._clock = clock
        self._client_factory = client_factory
        self._lock = asyncio.Lock()

    def configure_from_environment(self) -> None:
        """Pick up credential changes without persisting refreshed tokens to disk."""
        id_token = os.getenv("BOOSTCAMP_AUTH_TOKEN") or None
        refresh_token = os.getenv("BOOSTCAMP_REFRESH_TOKEN") or None
        if id_token and id_token != self._configured_id_token:
            self._id_token = id_token
            self._configured_id_token = id_token
        if refresh_token and refresh_token != self._configured_refresh_token:
            self._refresh_token = refresh_token
            self._configured_refresh_token = refresh_token

    def _is_expired(self, token: str) -> bool:
        """Read the unverified JWT expiry; authentication is still done by Firebase."""
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            expires_at = float(json.loads(base64.urlsafe_b64decode(payload))["exp"])
        except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            # Preserve support for opaque/static tokens that the API can validate.
            return False
        return expires_at <= self._clock() + REFRESH_SKEW_SECONDS

    async def get_token(self, *, force_refresh: bool = False) -> str:
        if self._id_token and not force_refresh and not self._is_expired(self._id_token):
            return self._id_token
        if not self._refresh_token:
            if self._id_token:
                raise TokenRefreshError(
                    "The Boostcamp ID token has expired and no refresh token is configured. "
                    "Set BOOSTCAMP_REFRESH_TOKEN or run 'uv run login' again."
                )
            raise TokenRefreshError(
                "No Boostcamp credentials are configured. Set BOOSTCAMP_REFRESH_TOKEN "
                "or run 'uv run login'."
            )
        async with self._lock:
            if self._id_token and not force_refresh and not self._is_expired(self._id_token):
                return self._id_token
            return await self._refresh()

    async def _refresh(self) -> str:
        url = ("https://securetoken.googleapis.com/v1/token"
               f"?key={BoostcampEndpoints.FIREBASE_API_KEY}")
        try:
            async with self._client_factory(timeout=10) as client:
                response = await client.post(
                    url,
                    data={"grant_type": "refresh_token", "refresh_token": self._refresh_token},
                )
                response.raise_for_status()
                payload = response.json()
            id_token = payload["id_token"]
            if not isinstance(id_token, str) or not id_token:
                raise KeyError("id_token")
            self._id_token = id_token
            rotated_refresh_token = payload.get("refresh_token")
            if isinstance(rotated_refresh_token, str) and rotated_refresh_token:
                self._refresh_token = rotated_refresh_token
            return id_token
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise TokenRefreshError(
                "Firebase token refresh failed. Check BOOSTCAMP_REFRESH_TOKEN and authenticate again."
            ) from exc
