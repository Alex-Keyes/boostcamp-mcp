# Boostcamp MCP Server

A Model Context Protocol (MCP) server for integrating with the [Boostcamp](https://www.boostcamp.app/) fitness platform. This server provides seamless access to your training history, workout programs, custom exercises, and analytics through Claude Desktop and Claude Code.

**Built with the [boostcamp-api Python library](https://github.com/Alex-Keyes/boostcamp-api)** - A library for interacting with Boostcamp's private API.

## 🚀 Quick Start

### 1. Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Alex-Keyes/boostcamp-mcp.git
   cd boostcamp-mcp
   ```

2. **Install dependencies**:
   Using `uv`:
   ```bash
   uv sync
   ```

3. **Configure Claude Desktop**:
   Add this to your Claude Desktop configuration file:

   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "Boostcamp": {
         "command": "uv",
         "args": [
           "run",
           "--with",
           "mcp[cli]",
           "--with-editable",
           "/path/to/your/boostcamp-mcp",
           "mcp",
           "run",
           "/path/to/your/boostcamp-mcp/src/boostcamp_mcp/server.py"
         ]
       }
     }
   }
   ```

   **Important**: Replace `/path/to/your/boostcamp-mcp` with your actual path!

4. **Restart Claude Desktop**

### 2. One-Time Authentication Setup

**Important**: For security, authentication is performed via a standalone script to generate a session.

Open Terminal and run:

```bash
cd /path/to/your/boostcamp-mcp
uv run login
```

Follow the prompts:
- Enter your Boostcamp email and password.
- The script will securely authenticate and save your session locally.
- Session tokens are stored in a `.env` file and `.boostcamp/` directory (automatically ignored by git).

### 3. Start Using

Once authenticated, use these tools directly in Claude:
- `get_my_profile` - View your profile and general stats.
- `list_enrolled_programs` - See your current active programs.
- `get_training_history` - Review your past workouts.
- `get_home_summary` - Get your dashboard streak and totals.

## ✨ Features

### 📊 Fitness Analytics
- **Home Summary**: Get total workouts, total weight moved, and current week streak.
- **Volume Charts**: Access training volume data over time.
- **Muscle Distribution**: See which muscle groups you've been targeting.

### 🏋️ Workout Management
- **Program Details**: Fetch full workout plans, including sets, reps, and coach notes.
- **Enrolled Programs**: Track your progress in active training plans.
- **Custom Exercises**: Access exercises you've manually created.

### 📚 Content & Discovery
- **Program Catalog**: Search and list all available programs on the platform.
- **Blog Access**: Read the latest articles and training guides from the Boostcamp blog.

## 🛠️ Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_my_profile` | Get user profile and settings | None |
| `list_enrolled_programs` | List your active programs | None |
| `get_training_history` | Get detailed workout history | `timezone_offset` |
| `get_payment_history` | View your subscription/orders | None |
| `list_custom_exercises` | List your unique exercises | None |
| `list_all_programs` | Search the program catalog | `page`, `page_size`, `keyword` |
| `get_program_details` | Get full plan for a program ID | `program_id` |
| `list_blogs` | List recent blog posts | `page`, `page_size` |
| `get_home_summary` | Dashboard stats (streak/totals) | `timezone_offset` |
| `get_home_chart` | Training volume chart data | `timezone_offset` |
| `get_home_muscle` | Muscle group distribution | `timezone_offset` |

## 🔧 Troubleshooting

### Authentication Issues
If you see "Authentication Error" or token expiration messages:
1. Run the login command: `uv run login`
2. Restart your MCP client (Claude Desktop or Claude Code).

### Session Management
- Sessions are stored in `.boostcamp/session.pickle`.
- The `BOOSTCAMP_AUTH_TOKEN` is saved to your local `.env`.
- **Security Note**: Never commit your `.env` or `.boostcamp/` folder. They are included in `.gitignore` by default.

## 📄 License

MIT License
