import os
import asyncio
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Callable, Coroutine
from pathlib import Path

# Import the actual library and exceptions
from boostcampapi import BoostcampAPI, BoostcampAuthException, RequestFailedException

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

async def re_login() -> bool:
    """Attempt to re-login using stored credentials."""
    load_dotenv(dotenv_path=env_path, override=True)
    email = os.getenv("BOOSTCAMP_EMAIL", "")
    password = os.getenv("BOOSTCAMP_PASSWORD", "")
    if not email or not password:
        return False
    try:
        from dotenv import set_key
        api = BoostcampAPI()
        await api.login(email, password)
        if api.token:
            set_key(str(env_path), "BOOSTCAMP_AUTH_TOKEN", api.token)
            return True
    except Exception:
        pass
    return False

async def handle_api_call(func: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs) -> str:
    """Helper to handle common API call errors, with automatic re-login."""
    api = get_api_client()
    try:
        result = await func(api, *args, **kwargs)
        return str(result)
    except BoostcampAuthException:
        # Token expired — try re-login with stored credentials
        if await re_login():
            api = get_api_client()
            try:
                result = await func(api, *args, **kwargs)
                return str(result)
            except Exception as e:
                return f"Error after re-login: {str(e)}"
        return "Authentication Error: Token expired and no stored credentials found. Please run 'uv run login' again."
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
async def get_training_history(timezone_offset: int = -300) -> str:
    """Get the user's training history. Default timezone offset is -300."""
    return await handle_api_call(lambda api: api.get_training_history(timezone_offset))

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
