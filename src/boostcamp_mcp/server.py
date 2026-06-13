import os
import json
import asyncio
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Callable, Coroutine
from pathlib import Path

# Import the actual library and exceptions
from boostcampapi import BoostcampAPI, BoostcampAuthException, RequestFailedException

from boostcamp_mcp import history

# Load .env from current directory
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

# Initialize FastMCP
mcp = FastMCP("boostcamp")

def get_api_client():
    """Initialize the API client with the saved token."""
    # Reload env in case it changed (e.g. after login)
    load_dotenv(dotenv_path=env_path, override=True)
    token = os.getenv("BOOSTCAMP_AUTH_TOKEN", "")
    return BoostcampAPI(token=token)

async def handle_api_call(func: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs) -> str:
    """Helper to handle common API call errors."""
    api = get_api_client()
    try:
        result = await func(api, *args, **kwargs)
        return str(result)
    except BoostcampAuthException as e:
        return f"Authentication Error: {str(e)}. Please run 'uv run login' again."
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
    timezone_offset: int = -300,
) -> str:
    """Get the user's workout history, filtered and paginated to stay compact.

    Args:
        start_date: Only workouts on/after this date, "YYYY-MM-DD" (inclusive).
        end_date: Only workouts on/before this date, "YYYY-MM-DD" (inclusive).
        detail: "summary" (date, program, exercises, total volume — default) or
            "full" (adds every set with weight/reps/RPE).
        page: 1-based page number, newest workouts first.
        page_size: Workouts per page. Capped at 100 for summary, 25 for full.
        timezone_offset: Timezone offset in minutes (default -300 / EST).

    Returns JSON with `workouts`, `pagination` (incl. has_more), `filters`, and
    a `hint` describing how to fetch more (next page, date range, or full detail).
    """
    try:
        # Surface validation errors as clean strings before the network call.
        history.validate_params(start_date, end_date, detail, page, page_size)
    except ValueError as e:
        return f"Error: {e}"

    api = get_api_client()
    try:
        raw = await api.get_training_history(timezone_offset)
    except BoostcampAuthException as e:
        return (f"Authentication Error: {str(e)}. "
                "Please run 'uv run login' again.")
    except Exception as e:
        return f"Error: {str(e)}"

    result = history.shape_history(
        raw, start_date=start_date, end_date=end_date, detail=detail,
        page=page, page_size=page_size)
    return json.dumps(result, indent=2)

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
async def get_home_summary(timezone_offset: int = -300) -> str:
    """Get dashboard summary statistics (total workouts, weight, streak)."""
    return await handle_api_call(lambda api: api.get_home_summary(timezone_offset))

@mcp.tool()
async def get_home_programs(timezone_offset: int = -300) -> str:
    """Get a summary of active/recent user programs."""
    return await handle_api_call(lambda api: api.get_home_programs(timezone_offset))

@mcp.tool()
async def get_home_chart(timezone_offset: int = -300) -> str:
    """Get training volume chart data."""
    return await handle_api_call(lambda api: api.get_home_chart(timezone_offset))

@mcp.tool()
async def get_home_muscle(timezone_offset: int = -300) -> str:
    """Get muscle group distribution data."""
    return await handle_api_call(lambda api: api.get_home_muscle(timezone_offset))

def main():
    mcp.run()

if __name__ == "__main__":
    main()
