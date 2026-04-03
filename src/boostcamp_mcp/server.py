import os
import asyncio
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from pathlib import Path

# Important: Import the actual library we just linked
from boostcampapi import BoostcampAPI

# Load .env from current directory
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

# Initialize FastMCP
mcp = FastMCP("boostcamp")

def get_api_client():
    """Initialize the API client with the saved token."""
    token = os.getenv("BOOSTCAMP_AUTH_TOKEN", "")
    # Note: Depending on the library version, it might take token in __init__ or via login
    return BoostcampAPI(token=token)

@mcp.tool()
async def get_my_profile() -> str:
    """Get the current user's profile information."""
    api = get_api_client()
    try:
        profile = await api.get_profile()
        return str(profile)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_my_programs() -> str:
    """List the fitness programs the user is currently enrolled in."""
    api = get_api_client()
    try:
        programs = await api.get_programs()
        return str(programs)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_program_details(program_id: str) -> str:
    """Get detailed information about a specific fitness program."""
    api = get_api_client()
    try:
        details = await api.get_program(program_id)
        return str(details)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_my_workouts(limit: int = 10) -> str:
    """Get recent workout history."""
    api = get_api_client()
    try:
        workouts = await api.get_workouts(limit=limit)
        return str(workouts)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
