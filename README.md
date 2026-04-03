# Boostcamp MCP Server (Python)

A Model Context Protocol (MCP) server for the [Boostcamp API](https://github.com/Alex-Keyes/boostcamp-api) built using [FastMCP](https://github.com/jlowin/fastmcp).

## Features

-   **Get Bootcamps**: List bootcamps with filtering and pagination.
-   **Radius Search**: Find bootcamps near a zipcode.
-   **Courses & Reviews**: Access associated courses and reviews.
-   **Create Bootcamp**: Protected endpoint to add new listings.

## Token Authentication

The Boostcamp API uses **JWT (JSON Web Tokens)** for protected routes (like `create_bootcamp`).

1.  **Login**: Use the API's `/api/v1/auth/login` endpoint to get a token.
2.  **Configuration**: Set the `BOOSTCAMP_AUTH_TOKEN` environment variable.
3.  **Usage**: The server automatically adds the `Authorization: Bearer <token>` header to protected requests.

## Setup

### Prerequisites

-   [uv](https://github.com/astral-sh/uv) installed.

### Configuration

Set environment variables in a `.env` file:

```env
BOOSTCAMP_API_URL=http://localhost:5000/api/v1
BOOSTCAMP_AUTH_TOKEN=your_jwt_token_here
```

## Gemini / Claude Configuration

Add the following to your MCP configuration file (e.g., `gemini.config.json`):

```json
{
  "mcpServers": {
    "boostcamp": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "/Users/alexkeyes/Projects/boostcamp-mcp",
        "mcp",
        "run",
        "/Users/alexkeyes/Projects/boostcamp-mcp/src/boostcamp_mcp/server.py"
      ],
      "env": {
        "BOOSTCAMP_API_URL": "http://localhost:5000/api/v1",
        "BOOSTCAMP_AUTH_TOKEN": "your_jwt_token_here"
      }
    }
  }
}
```

## Development

Run the server locally for testing:

```bash
uv run src/boostcamp_mcp/server.py
```
