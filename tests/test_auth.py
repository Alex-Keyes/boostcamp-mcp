import asyncio
import base64
import json
import os
import unittest
from unittest.mock import patch

import httpx

from boostcamp_mcp.auth import FirebaseTokenProvider, TokenRefreshError


def jwt(exp: int) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


def client_factory(handler):
    transport = httpx.MockTransport(handler)
    return lambda **kwargs: httpx.AsyncClient(transport=transport, **kwargs)


class FirebaseTokenProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_token_does_not_refresh(self):
        def unexpected_request(request):
            raise AssertionError("refresh should not be called")
        provider = FirebaseTokenProvider(jwt(2_000), "refresh-secret", clock=lambda: 1_000,
                                         client_factory=client_factory(unexpected_request))
        self.assertEqual(await provider.get_token(), jwt(2_000))

    async def test_expired_and_nearly_expired_tokens_are_refreshed(self):
        for expires_at in (1_000, 1_059):
            with self.subTest(expires_at=expires_at):
                def refresh(request):
                    self.assertEqual(request.url.host, "securetoken.googleapis.com")
                    self.assertIn(b"grant_type=refresh_token", request.content)
                    self.assertIn(b"refresh_token=refresh-secret", request.content)
                    return httpx.Response(200, json={"id_token": jwt(3_000), "refresh_token": "rotated"})
                provider = FirebaseTokenProvider(jwt(expires_at), "refresh-secret", clock=lambda: 1_000,
                                                 client_factory=client_factory(refresh))
                self.assertEqual(await provider.get_token(), jwt(3_000))

    async def test_concurrent_callers_share_refresh(self):
        requests = 0
        def refresh(request):
            nonlocal requests
            requests += 1
            return httpx.Response(200, json={"id_token": jwt(3_000)})
        provider = FirebaseTokenProvider(jwt(900), "refresh-secret", clock=lambda: 1_000,
                                         client_factory=client_factory(refresh))
        self.assertEqual(await asyncio.gather(provider.get_token(), provider.get_token()), [jwt(3_000)] * 2)
        self.assertEqual(requests, 1)

    async def test_refresh_failure_is_safe(self):
        def reject(request):
            return httpx.Response(400, json={"error": {"message": "contains refresh-secret"}})
        provider = FirebaseTokenProvider(jwt(900), "refresh-secret", clock=lambda: 1_000,
                                         client_factory=client_factory(reject))
        with self.assertRaises(TokenRefreshError) as error:
            await provider.get_token()
        self.assertNotIn("refresh-secret", str(error.exception))

    async def test_malformed_refresh_response_fails_safely(self):
        def malformed(request):
            return httpx.Response(200, json={"expires_in": "3600"})
        provider = FirebaseTokenProvider(jwt(900), "refresh-secret", clock=lambda: 1_000,
                                         client_factory=client_factory(malformed))
        with self.assertRaises(TokenRefreshError):
            await provider.get_token()

    async def test_rotated_credentials_are_kept_in_memory(self):
        seen_refresh_tokens = []
        responses = iter([{"id_token": jwt(3_000), "refresh_token": "rotated"}, {"id_token": jwt(4_000)}])
        def refresh(request):
            seen_refresh_tokens.append(request.content)
            return httpx.Response(200, json=next(responses))
        provider = FirebaseTokenProvider(clock=lambda: 1_000, client_factory=client_factory(refresh))
        with patch.dict(os.environ, {"BOOSTCAMP_AUTH_TOKEN": jwt(900),
                                     "BOOSTCAMP_REFRESH_TOKEN": "refresh-secret"}):
            provider.configure_from_environment()
            await provider.get_token()
            provider.configure_from_environment()
            await provider.get_token(force_refresh=True)
        self.assertIn(b"refresh_token=refresh-secret", seen_refresh_tokens[0])
        self.assertIn(b"refresh_token=rotated", seen_refresh_tokens[1])

    async def test_expired_token_without_refresh_token_has_actionable_error(self):
        provider = FirebaseTokenProvider(jwt(900), clock=lambda: 1_000)
        with self.assertRaisesRegex(TokenRefreshError, "BOOSTCAMP_REFRESH_TOKEN"):
            await provider.get_token()


if __name__ == "__main__":
    unittest.main()
