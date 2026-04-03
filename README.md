# Boostcamp MCP Server

A Model Context Protocol (MCP) server for the [Boostcamp API](https://github.com/Alex-Keyes/boostcamp-api).

This server allows AI clients like Claude to interact with the Boostcamp directory application, enabling them to search for bootcamps, view courses, and manage listings.

## Features

-   **Get Bootcamps**: List all bootcamps with filtering, sorting, and pagination.
-   **Search by Radius**: Find bootcamps within a certain distance from a zipcode.
-   **View Courses**: Explore courses offered by bootcamps.
-   **Read Reviews**: See user feedback for different bootcamps.
-   **Create Bootcamp**: Add new bootcamp listings (requires authentication).

## Setup

### Prerequisites

-   [Node.js](https://nodejs.org/) (v18 or later)
-   A running instance of the [Boostcamp API](https://github.com/Alex-Keyes/boostcamp-api).

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Alex-Keyes/boostcamp-mcp
    cd boostcamp-mcp
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Build the project:
    ```bash
    npm run build
    ```

### Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file to match your setup:

```env
BOOSTCAMP_API_URL=http://localhost:5000/api/v1
BOOSTCAMP_AUTH_TOKEN=your_jwt_token_here
```

## Usage

### Connecting to Claude Desktop

Add the following to your Claude Desktop configuration (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "boostcamp": {
      "command": "node",
      "args": ["/absolute/path/to/boostcamp-mcp/dist/index.js"],
      "env": {
        "BOOSTCAMP_API_URL": "http://localhost:5000/api/v1",
        "BOOSTCAMP_AUTH_TOKEN": "your_jwt_token_here"
      }
    }
  }
}
```

## Tools

| Tool | Description |
| :--- | :--- |
| `get_bootcamps` | Get all bootcamps with filtering and pagination. |
| `get_bootcamp` | Get a single bootcamp by ID. |
| `get_courses` | Get all courses (optionally filter by bootcamp). |
| `get_reviews` | Get all reviews (optionally filter by bootcamp). |
| `get_bootcamps_radius` | Get bootcamps within a radius of a zipcode. |
| `create_bootcamp` | Create a new bootcamp (Requires Publisher/Admin roles). |

## Development

Run the server in development mode:

```bash
npm run dev
```

The server communicates via `stdio`.

## License

MIT
