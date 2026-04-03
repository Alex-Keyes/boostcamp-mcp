# Boostcamp MCP Server (Python)

A Model Context Protocol (MCP) server for the [Boostcamp API](https://github.com/Alex-Keyes/boostcamp-api) built using [FastMCP](https://github.com/jlowin/fastmcp).

## Features

-   **Get Bootcamps**: List bootcamps with filtering and pagination.
-   **Radius Search**: Find bootcamps near a zipcode.
-   **Courses & Reviews**: Access associated courses and reviews.
-   **Create Bootcamp**: Protected endpoint to add new listings.

## Token Authentication

The Boostcamp API uses **JWT (JSON Web Tokens)** for protected routes. You can authenticate easily using the built-in login script:

1.  **Configure API URL**: Ensure `BOOSTCAMP_API_URL` is set in your `.env` file (defaults to `http://localhost:5000/api/v1`).
2.  **Run Login**:
    ```bash
    uv run login
    ```
3.  **Enter Credentials**: Follow the prompts to enter your email and password.
4.  **Automatic Setup**: The script will fetch the JWT and save it to your `.env` file as `BOOSTCAMP_AUTH_TOKEN`. The MCP server will automatically pick this up on every request.

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
