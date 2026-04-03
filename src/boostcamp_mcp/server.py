import os
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

from pathlib import Path

# Load .env from current directory
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

API_URL = os.getenv("BOOSTCAMP_API_URL", "http://localhost:5000/api/v1")
AUTH_TOKEN = os.getenv("BOOSTCAMP_AUTH_TOKEN", "")

# Initialize FastMCP
mcp = FastMCP("boostcamp")

def get_headers():
    # Reload env in case it changed during runtime
    load_dotenv(dotenv_path=env_path)
    token = os.getenv("BOOSTCAMP_AUTH_TOKEN", "")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

@mcp.tool()
async def get_bootcamps(
    page: Optional[int] = None,
    limit: Optional[int] = None,
    select: Optional[str] = None,
    sort: Optional[str] = None
) -> str:
    """
    Get all bootcamps with filtering and pagination.
    - page: Page number
    - limit: Limit per page
    - select: Fields to select (comma separated)
    - sort: Fields to sort by
    """
    params = {}
    if page: params["page"] = page
    if limit: params["limit"] = limit
    if select: params["select"] = select
    if sort: params["sort"] = sort

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/bootcamps", params=params)
        return response.text

@mcp.tool()
async def get_bootcamp(id: str) -> str:
    """Get a single bootcamp by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/bootcamps/{id}")
        return response.text

@mcp.tool()
async def get_courses(bootcamp_id: Optional[str] = None) -> str:
    """Get all courses, optionally filtered by bootcamp ID."""
    url = f"{API_URL}/bootcamps/{bootcamp_id}/courses" if bootcamp_id else f"{API_URL}/courses"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

@mcp.tool()
async def get_reviews(bootcamp_id: Optional[str] = None) -> str:
    """Get all reviews, optionally filtered by bootcamp ID."""
    url = f"{API_URL}/bootcamps/{bootcamp_id}/reviews" if bootcamp_id else f"{API_URL}/reviews"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

@mcp.tool()
async def get_bootcamps_radius(zipcode: str, distance: int) -> str:
    """Get bootcamps within a radius of a zipcode (in miles)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/bootcamps/radius/{zipcode}/{distance}")
        return response.text

@mcp.tool()
async def create_bootcamp(
    name: str,
    description: str,
    website: str,
    phone: str,
    email: str,
    address: str,
    careers: List[str],
    housing: bool = False,
    job_assistance: bool = False,
    job_guarantee: bool = False,
    accept_gi: bool = False
) -> str:
    """
    Create a new bootcamp (Requires Publisher/Admin roles).
    - careers: List of careers (e.g. ["Web Development", "UI/UX"])
    """
    data = {
        "name": name,
        "description": description,
        "website": website,
        "phone": phone,
        "email": email,
        "address": address,
        "careers": careers,
        "housing": housing,
        "jobAssistance": job_assistance,
        "jobGuarantee": job_guarantee,
        "acceptGi": accept_gi
    }
    
    async with httpx.AsyncClient() as client:
        headers = get_headers()
        response = await client.post(f"{API_URL}/bootcamps", json=data, headers=headers)
        return response.text

def main():
    mcp.run()

if __name__ == "__main__":
    main()
