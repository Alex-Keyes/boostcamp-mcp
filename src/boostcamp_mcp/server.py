import json
import os
from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

# Import the actual library and exceptions
from boostcampapi import BoostcampAPI, BoostcampAuthException

from boostcamp_mcp import history
from boostcamp_mcp.auth import FirebaseTokenProvider, TokenRefreshError

# Load .env from current directory
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

# Initialize FastMCP
mcp = FastMCP("boostcamp")
token_provider = FirebaseTokenProvider()

def _local_timezone_offset() -> int:
    """Minutes east of UTC for this machine's current local time (DST-aware)."""
    offset = datetime.now().astimezone().utcoffset()
    return int(offset.total_seconds() // 60) if offset is not None else 0


def _resolve_timezone_offset(timezone_offset: Optional[int]) -> int:
    return _local_timezone_offset() if timezone_offset is None else timezone_offset


def _to_json(result: Any) -> str:
    """Serialize API results as JSON so clients get parseable output, not a Python repr."""
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False, default=str)


async def get_api_client(*, force_refresh: bool = False) -> BoostcampAPI:
    """Initialize the API client with the saved token."""
    # Reload env in case it changed (e.g. after login)
    load_dotenv(dotenv_path=env_path, override=True)
    token_provider.configure_from_environment()
    token = await token_provider.get_token(force_refresh=force_refresh)
    return BoostcampAPI(token=token)


async def handle_api_call(func: Callable[[BoostcampAPI], Awaitable[Any]]) -> str:
    """Run an API call with token refresh/retry and return JSON or an error string."""
    try:
        api = await get_api_client()
        return _to_json(await func(api))
    except BoostcampAuthException:
        if os.getenv("BOOSTCAMP_REFRESH_TOKEN"):
            try:
                api = await get_api_client(force_refresh=True)
                return _to_json(await func(api))
            except (BoostcampAuthException, TokenRefreshError):
                pass
        return "Authentication Error: check BOOSTCAMP_REFRESH_TOKEN or run 'uv run login' again."
    except TokenRefreshError as e:
        return f"Authentication Error: {e}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_my_profile() -> str:
    """Get the current user's profile and settings from Boostcamp."""
    return await handle_api_call(lambda api: api.get_user_profile())


@mcp.tool()
async def list_enrolled_programs() -> str:
    """List all fitness programs the user is currently enrolled in."""
    return await handle_api_call(lambda api: api.list_user_programs())


@mcp.tool()
async def get_training_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    detail: str = "summary",
    page: int = 1,
    page_size: int = 50,
    timezone_offset: Optional[int] = None,
) -> str:
    """Get the user's workout history, filtered and paginated to stay compact.

    Args:
        start_date: Only workouts on/after this date, "YYYY-MM-DD" (inclusive).
        end_date: Only workouts on/before this date, "YYYY-MM-DD" (inclusive).
        detail: "summary" (date, program, exercises, total volume — default) or
            "full" (adds every set with weight/reps/RPE).
        page: 1-based page number, newest workouts first.
        page_size: Workouts per page. Capped at 100 for summary, 25 for full.
        timezone_offset: Timezone offset in minutes east of UTC (e.g. -300 for
            US Eastern, 60 for Central European). Defaults to this computer's
            local timezone.

    Returns JSON with `workouts`, `pagination` (incl. has_more), `filters`, and
    a `hint` describing how to fetch more (next page, date range, or full detail).
    """
    try:
        # Surface validation errors as clean strings before the network call.
        history.validate_params(start_date, end_date, detail, page, page_size)
    except ValueError as e:
        return f"Error: {e}"

    offset = _resolve_timezone_offset(timezone_offset)

    async def fetch(api: BoostcampAPI) -> dict:
        raw = await api.get_training_history(offset)
        return history.shape_history(
            raw, start_date=start_date, end_date=end_date, detail=detail,
            page=page, page_size=page_size)

    return await handle_api_call(fetch)


@mcp.tool()
async def get_payment_history() -> str:
    """Get the user's payment history."""
    return await handle_api_call(lambda api: api.get_payment_history())


@mcp.tool()
async def list_custom_exercises() -> str:
    """List the custom exercises created by the user."""
    return await handle_api_call(lambda api: api.list_custom_exercises())


@mcp.tool()
async def list_all_programs(page: int = 1, page_size: int = 10, keyword: Optional[str] = None) -> str:
    """List all available programs with pagination and optional keyword search."""
    return await handle_api_call(lambda api: api.list_all_programs(page, page_size, keyword))


@mcp.tool()
async def get_program_details(program_id: str) -> str:
    """Get detailed information about a specific program by its ID."""
    return await handle_api_call(lambda api: api.get_program_details(program_id))


@mcp.tool()
async def list_blogs(page: int = 1, page_size: int = 10) -> str:
    """List blog posts with pagination."""
    return await handle_api_call(lambda api: api.list_blogs(page, page_size))


@mcp.tool()
async def get_home_summary(timezone_offset: Optional[int] = None) -> str:
    """Get dashboard summary statistics (total workouts, weight, streak).

    Args:
        timezone_offset: Timezone offset in minutes east of UTC. Defaults to
            this computer's local timezone.
    """
    offset = _resolve_timezone_offset(timezone_offset)
    return await handle_api_call(lambda api: api.get_home_summary(offset))


@mcp.tool()
async def get_home_programs(timezone_offset: Optional[int] = None) -> str:
    """Get a summary of active/recent user programs.

    Args:
        timezone_offset: Timezone offset in minutes east of UTC. Defaults to
            this computer's local timezone.
    """
    offset = _resolve_timezone_offset(timezone_offset)
    return await handle_api_call(lambda api: api.get_home_programs(offset))


@mcp.tool()
async def get_home_chart(timezone_offset: Optional[int] = None) -> str:
    """Get training volume chart data.

    Args:
        timezone_offset: Timezone offset in minutes east of UTC. Defaults to
            this computer's local timezone.
    """
    offset = _resolve_timezone_offset(timezone_offset)
    return await handle_api_call(lambda api: api.get_home_chart(offset))


@mcp.tool()
async def get_home_muscle(timezone_offset: Optional[int] = None) -> str:
    """Get muscle group distribution data.

    Args:
        timezone_offset: Timezone offset in minutes east of UTC. Defaults to
            this computer's local timezone.
    """
    offset = _resolve_timezone_offset(timezone_offset)
    return await handle_api_call(lambda api: api.get_home_muscle(offset))


def main():
    mcp.run()


if __name__ == "__main__":
    main()
