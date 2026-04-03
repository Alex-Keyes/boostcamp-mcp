# Boostcamp MCP Server (Python)

A Model Context Protocol (MCP) server for [Boostcamp](https://www.boostcamp.app/), built as a wrapper around the [boostcamp-api](https://github.com/Alex-Keyes/boostcamp-api) library using [FastMCP](https://github.com/jlowin/fastmcp).

This architecture is identical to the Monarch Money MCP: the server imports the API logic directly as a dependency, so no separate API server needs to be running.

## Features

-   **Profile**: Get user profile and fitness stats using `get_my_profile`.
-   **Programs**: List enrolled programs using `list_enrolled_programs`.

## Token Authentication

Boostcamp uses Firebase-based authentication. The `login` script handles this for you:

1.  **Run Login**:
    ```bash
    uv run login
    ```
2.  **Enter Credentials**: Enter your Boostcamp email and password.
3.  **Automatic Setup**: The script fetches your `FirebaseIdToken` and saves it to your `.env` file as `BOOSTCAMP_AUTH_TOKEN`. The MCP server will use this token for all requests.

## Setup

### Prerequisites

-   [uv](https://github.com/astral-sh/uv) installed.

### Gemini / Claude Configuration

Add the following to your MCP configuration file:

```json
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
    "BOOSTCAMP_AUTH_TOKEN": "your_saved_token_here"
  }
}
```

Note: You can omit `BOOSTCAMP_AUTH_TOKEN` from the `env` section if you have a `.env` file in the project directory, as the server will load it automatically.
can omit `BOOSTCAMP_AUTH_TOKEN` from the `env` section if you have a `.env` file in the project directory, as the server will load it automatically.
