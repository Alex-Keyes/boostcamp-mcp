"""Tool-level tests: the server wires the token provider, API client and shaping together."""
import json

import pytest
from boostcampapi import BoostcampAuthException

from boostcamp_mcp import server


def _call(tool):
    """FastMCP may wrap decorated tools; fall back to the underlying function."""
    return getattr(tool, "fn", tool)


RAW_HISTORY = {
    "data": {
        "2026-06-10": [{
            "name": "Dave Minimum Dose",
            "title": "Week 7 · Day 1",
            "finished_at": "2026-06-10 21:08:23",
            "records": [{
                "name": "Squat (Barbell)",
                "sets": [{"value": "100", "amount": "5", "valueEmpty": False,
                          "amountEmpty": False, "skipped": False, "weight_unit": "kg"}],
            }],
        }],
    },
}


class FakeAPI:
    def __init__(self, history=RAW_HISTORY, fail_auth=False):
        self.history = history
        self.fail_auth = fail_auth
        self.offsets = []

    async def get_training_history(self, timezone_offset):
        self.offsets.append(timezone_offset)
        if self.fail_auth:
            raise BoostcampAuthException("expired")
        return self.history

    async def get_home_summary(self, timezone_offset):
        self.offsets.append(timezone_offset)
        return {"total_workouts": 3, "is_active": True, "streak": None}


@pytest.fixture
def fake_clients(monkeypatch):
    """Patch get_api_client to hand out queued FakeAPI instances."""
    clients = []
    calls = []

    async def get_api_client(*, force_refresh=False):
        calls.append(force_refresh)
        return clients.pop(0)

    monkeypatch.setattr(server, "get_api_client", get_api_client)
    return clients, calls


async def test_training_history_returns_shaped_json(fake_clients):
    clients, _ = fake_clients
    api = FakeAPI()
    clients.append(api)

    result = json.loads(await _call(server.get_training_history)(timezone_offset=60))

    assert api.offsets == [60]
    assert result["pagination"]["total"] == 1
    workout = result["workouts"][0]
    assert workout["exercises"] == ["Squat (Barbell)"]
    assert workout["total_volume"] == 500.0
    assert workout["volume_unit"] == "kg"


async def test_training_history_validates_before_network(fake_clients):
    clients, calls = fake_clients

    result = await _call(server.get_training_history)(start_date="10/01/2026")

    assert result.startswith("Error: start_date must be YYYY-MM-DD")
    assert calls == []


async def test_training_history_retries_with_refreshed_token(fake_clients, monkeypatch):
    clients, calls = fake_clients
    monkeypatch.setenv("BOOSTCAMP_REFRESH_TOKEN", "refresh-secret")
    clients.extend([FakeAPI(fail_auth=True), FakeAPI()])

    result = json.loads(await _call(server.get_training_history)(timezone_offset=0))

    assert calls == [False, True]
    assert result["pagination"]["total"] == 1


async def test_timezone_offset_defaults_to_local(fake_clients, monkeypatch):
    clients, _ = fake_clients
    api = FakeAPI()
    clients.append(api)
    monkeypatch.setattr(server, "_local_timezone_offset", lambda: 120)

    await _call(server.get_home_summary)()

    assert api.offsets == [120]


async def test_api_results_are_serialized_as_json(fake_clients):
    clients, _ = fake_clients
    clients.append(FakeAPI())

    result = await _call(server.get_home_summary)(timezone_offset=0)

    # Valid JSON (true/null), not a Python repr (True/None).
    assert json.loads(result) == {"total_workouts": 3, "is_active": True, "streak": None}


def test_local_timezone_offset_is_whole_minutes():
    offset = server._local_timezone_offset()
    assert isinstance(offset, int)
    assert -14 * 60 <= offset <= 14 * 60
