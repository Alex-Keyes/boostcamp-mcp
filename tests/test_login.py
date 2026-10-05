"""Login output feeds the existing provider without a persisted password."""
import base64
import json
import importlib
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from dotenv import dotenv_values
from boostcampapi import BoostcampAPI, BoostcampEndpoints

from boostcamp_mcp.auth import FirebaseTokenProvider


def jwt(exp):
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"

login_module = importlib.import_module("boostcamp_mcp.login")


@pytest.mark.asyncio
async def test_login_to_expiry_to_automatic_refresh(tmp_path, monkeypatch, capsys):
    """Exercise real library login, .env persistence, and provider renewal."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(login_module, "env_path", Path(".env"))
    now = [1_000]
    requests = []

    class Response:
        status = 200

        async def json(self):
            return {"idToken": jwt(2_000), "refreshToken": "login-refresh-secret"}

    class Session:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        @asynccontextmanager
        async def post(self, url, **kwargs):
            assert url == BoostcampEndpoints.FIREBASE_LOGIN_URL
            assert kwargs["json"]["password"] == "test-password-secret"
            yield Response()

    with patch("boostcampapi.boostcampapi.ClientSession", return_value=Session()), \
         patch("builtins.input", return_value="test-user@example.com"), \
         patch("getpass.getpass", return_value="test-password-secret"):
        await login_module.login()

    values = dotenv_values(".env")
    assert values == {"BOOSTCAMP_AUTH_TOKEN": jwt(2_000),
                      "BOOSTCAMP_REFRESH_TOKEN": "login-refresh-secret"}
    assert not Path(".boostcamp").exists()
    output = capsys.readouterr().out
    assert "test-password-secret" not in output
    assert "login-refresh-secret" not in output
    assert "test-user@example.com" not in Path(".env").read_text()

    def refresh(request):
        requests.append(request)
        assert b"refresh_token=login-refresh-secret" in request.content
        return httpx.Response(200, json={"id_token": jwt(4_000), "refresh_token": "rotated"})

    provider = FirebaseTokenProvider(
        clock=lambda: now[0],
        client_factory=lambda **kwargs: httpx.AsyncClient(
            transport=httpx.MockTransport(refresh), **kwargs),
    )
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    provider.configure_from_environment()
    assert await provider.get_token() == jwt(2_000)
    assert requests == []
    now[0] = 2_001
    assert await provider.get_token() == jwt(4_000)
    provider.configure_from_environment()
    assert await provider.get_token() == jwt(4_000)
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_missing_refresh_token_leaves_existing_env_untouched(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(login_module, "env_path", Path(".env"))
    Path(".env").write_text("BOOSTCAMP_REFRESH_TOKEN=previous-token\n")

    async def token_only_login(self, email, password, save_session=True):
        assert save_session is False
        self.set_token("new-id-token")

    with patch.object(BoostcampAPI, "login", token_only_login), \
         patch("builtins.input", return_value="test-user@example.com"), \
         patch("getpass.getpass", return_value="test-password-secret"):
        await login_module.login()

    assert Path(".env").read_text() == "BOOSTCAMP_REFRESH_TOKEN=previous-token\n"
    assert "No refresh token" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_login_exception_does_not_print_credentials(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(login_module, "env_path", Path(".env"))

    async def failed_login(*args, **kwargs):
        raise RuntimeError("test-password-secret login-refresh-secret")

    with patch.object(BoostcampAPI, "login", failed_login), \
         patch("builtins.input", return_value="test-user@example.com"), \
         patch("getpass.getpass", return_value="test-password-secret"):
        await login_module.login()

    assert not Path(".env").exists()
    output = capsys.readouterr().out
    assert "test-password-secret" not in output
    assert "login-refresh-secret" not in output
