import os
import asyncio
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
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

@mcp.tool()
async def get_my_profile() -> str:
    """Get the current user's profile and settings from Boostcamp."""
    api = get_api_client()
    try:
        profile = await api.get_user_profile()
        return str(profile)
    except BoostcampAuthException as e:
        return f"Authentication Error: {str(e)}. Please run 'uv run login' again."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def list_enrolled_programs() -> str:
    """List all fitness programs the user is currently enrolled in."""
    api = get_api_client()
    try:
        programs = await api.list_user_programs()
        return str(programs)
    except BoostcampAuthException as e:
        return f"Authentication Error: {str(e)}. Please run 'uv run login' again."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
