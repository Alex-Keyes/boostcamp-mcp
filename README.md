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
           "--directory",
           "/path/to/your/boostcamp-mcp",
           "--with",
           "fastmcp",
           "--with-editable",
           "/path/to/your/boostcamp-mcp",
           "fastmcp",
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

This command supports Boostcamp accounts with an email and password. Follow the prompts:
- Enter your Boostcamp email and password.
- The script will securely authenticate and save your session locally.
- The ID token is stored in the local `.env` file (automatically ignored by git).

#### Google, passkey, and other OAuth accounts

If your account has no password, copy Firebase's `refreshToken` from your authenticated
Boostcamp browser session and add it to `.env`:

```dotenv
BOOSTCAMP_REFRESH_TOKEN=your-refresh-token
```

Restart the MCP server after initially changing `.env`. The server exchanges the refresh
token for Firebase ID tokens and refreshes them automatically before they expire.

**Security:** A refresh token is a long-lived credential equivalent to a password. Never
commit it, share it in an issue, or include it in logs or screenshots.

### 3. Start Using

Once authenticated, use these tools directly in Claude:
- `get_my_profile` - View your profile and general stats.
- `list_enrolled_programs` - See your current active programs.
- `get_training_history` - Review your past workouts (filter by date range, page through history, or request full set-by-set detail).
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
| `get_training_history` | Workout history, compact by default. Returns JSON with pagination metadata and a `has_more` flag so large histories can be walked in chunks. | `start_date`, `end_date`, `detail`, `page`, `page_size`, `timezone_offset` |
| `get_payment_history` | View your subscription/orders | None |
| `list_custom_exercises` | List your unique exercises | None |
| `list_all_programs` | Search the program catalog | `page`, `page_size`, `keyword` |
| `get_program_details` | Get full plan for a program ID | `program_id` |
| `list_blogs` | List recent blog posts | `page`, `page_size` |
| `get_home_summary` | Dashboard stats (streak/totals) | `timezone_offset` |
| `get_home_chart` | Training volume chart data | `timezone_offset` |
| `get_home_muscle` | Muscle group distribution | `timezone_offset` |

### Working with training history

`get_training_history` is built to keep responses small enough for any MCP
client. By default it returns a **summary** of your **50 most recent** workouts
(date, program, exercises, and total volume) plus pagination metadata:

```json
{
  "workouts": [ { "date": "2026-06-10", "program_name": "...",
                  "exercises": ["Squat (Barbell)", "..."],
                  "total_volume": 11570, "volume_unit": "lbs" } ],
  "pagination": {"page": 1, "page_size": 50, "total": 231,
                 "returned": 50, "has_more": true},
  "filters": {"start_date": null, "end_date": null, "detail": "summary"},
  "hint": "231 workouts match. Showing 50 (page 1, summary). Use page=2 ..."
}
```

- **Filter by date:** `start_date` / `end_date` as `YYYY-MM-DD` (inclusive),
  e.g. *"my workouts since 2026-04-07"*.
- **Page through history:** bump `page` while `pagination.has_more` is `true`
  (`page_size` caps at 100 for summary, 25 for full).
- **Get every set and rep:** `detail="full"` adds per-exercise records with each
  set's weight, reps, target, and RPE. Use a small `page_size` here.

Supersets are flattened: each exercise inside a superset is listed individually
(with its sets counted toward `total_volume`), and in `full` detail those
exercises carry a `superset` id so the grouping is still visible.

## 🔧 Troubleshooting

### Authentication Issues
If you see "Authentication Error" or token expiration messages:
1. For Google, passkey, or OAuth authentication, check or replace `BOOSTCAMP_REFRESH_TOKEN`.
2. For email/password authentication, run `uv run login` again.
3. Restart your MCP client (Claude Desktop or Claude Code).

### Credential Management
- `BOOSTCAMP_AUTH_TOKEN` remains supported, but Firebase ID tokens expire after about one hour.
- `BOOSTCAMP_REFRESH_TOKEN` enables unattended automatic ID-token refresh.
- Credentials are read from your local `.env` and are never written to logs.
- **Security Note**: Never commit your `.env`. It is included in `.gitignore` by default.

## 📄 License

MIT License
