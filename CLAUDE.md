# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Personal AI Assistant system that integrates Claude AI with Telegram and Obsidian for cross-device knowledge management. The system features:
- Telegram bot interface for chatting with Claude
- Automatic conversation saving to Obsidian vault
- Proactive nudging/reminder system based on conversation patterns
- 1Password integration for secure credential management

## Architecture

### Core Services (src/services/)

**ObsidianService** (`obsidian.js`):
- Manages vault folder structure: `AI-Conversations/`, `Daily-Notes/`, `Templates/`
- All conversations auto-saved with frontmatter metadata (type, date, platform, topic, tags)
- File watcher (`chokidar`) monitors vault changes in real-time
- Search uses simple string matching across all markdown files
- Daily notes created on-demand with template structure

**ClaudeService** (`claude.js`):
- Wraps Anthropic SDK using `claude-3-haiku-20240307` model by default
- Built-in rate limiting: max 50 requests/minute tracked in memory
- System prompt configures Claude as personal assistant aware of Obsidian integration
- `analyzeConversationPatterns()` method used by nudging system for mood/goal analysis

**NudgingService** (`nudging.js`):
- Cron-based proactive messaging system (morning 9am, afternoon 2pm, evening 7pm)
- Analyzes recent conversations (last 24h) for patterns: mood, topics, goals, stress indicators
- Context-aware nudge generation based on keywords and time of day
- Daily limit (default 5 nudges/day) with 2-hour cooldown per nudge type
- Probabilistic sending based on priority (high: 80%, medium: 50%, low: 30%)

**OnePasswordService** (`onepassword.js`):
- Loads credentials from 1Password item "AI Assistant Credentials" in vault "Personal AI Assistant"
- Falls back to .env if 1Password unavailable

### Bot Implementation (src/bots/)

**TelegramBotService** (`telegram.js`):
- Polling-based bot using `node-telegram-bot-api`
- Commands: `/start`, `/help`, `/search <query>`, `/today`, `/clear`, `/status`
- Conversation context stored per-userId in memory Map
- Auto-saves to Obsidian every 4 messages or after 5 minutes
- Simple topic extraction from first user message (first 5 words)
- Authorization tracked via Set of user IDs (added on `/start`)

### Application Entry (src/index.js)

Startup sequence:
1. Load config (1Password → .env fallback)
2. Initialize ObsidianService (creates folder structure)
3. Initialize ClaudeService (validates API key)
4. Initialize TelegramBotService (sets up commands/handlers)
5. Initialize NudgingService (schedules cron jobs if chat ID configured)

Graceful shutdown handles SIGINT, stops all services in reverse order.

## Common Commands

### Development
```bash
npm run dev                    # Start with .env config (uses node --watch)
npm run dev:1password          # Start with 1Password config
npm start                      # Production mode (no watch)
```

### Testing
```bash
npm test                       # Run Jest tests
npm run test-obsidian          # Test Obsidian integration specifically
```

### Setup/Configuration
```bash
npm run setup                  # Basic setup guide
npm run setup:1password        # 1Password integration setup
npm run setup:complete         # Full interactive setup wizard
npm run get-chat-id            # Get Telegram chat ID helper
npm run configure-obsidian     # Configure Obsidian vault path
```

## Environment Variables

Required:
- `OBSIDIAN_VAULT_PATH` - Absolute path to Obsidian vault

Optional:
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `TELEGRAM_CHAT_ID` - Your Telegram user chat ID
- `ANTHROPIC_API_KEY` - Claude API key
- `NUDGING_ENABLED` - Enable/disable nudging (default: true)
- `NUDGING_HOURS_START` - Start hour for nudges (default: 8)
- `NUDGING_HOURS_END` - End hour for nudges (default: 22)
- `PORT` - Server port (default: 3000)
- `USE_1PASSWORD` - Use 1Password for config (or pass `--use-1password` flag)

## Obsidian Vault Location

**Default Vault Path:**
```
/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi
```

**Folder Structure:**
- `Projects/` - Active projects (goals, trip planning, etc.)
- `Archive/` - Completed projects
  - `Archive/2025-Trips/` - Archived trip files
- `AI-Conversations/` - Auto-saved Telegram conversations
- `Daily-Notes/` - Daily journal entries
- `Templates/` - Note templates

**Quick File Search:**
Use `mdfind` (Spotlight CLI) to locate files when bash `ls`/`find` commands fail due to iCloud permissions:
```bash
# Find specific file
mdfind -name "Asia-Trip" | grep PersonalAi

# Search by content
mdfind "trip OR travel" | grep PersonalAi

# Find all markdown files in vault
mdfind -onlyin "/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi" "*.md"
```

## Key Patterns

### Message Flow
1. User sends message → Telegram webhook
2. `handleConversationMessage()` adds to conversation context
3. Claude generates response via `generateResponse()`
4. Response sent to user and added to context
5. Periodic save to Obsidian as markdown file

### Conversation Context
- Stored per-user in Map: `{ messages: [], startTime: Date, topic: string }`
- Messages format: `{ role: 'user'|'assistant', content: string, timestamp: Date }`
- Context cleared with `/clear` command or on restart (in-memory only)

### Obsidian File Naming
Pattern: `YYYY-MM-DD-<sanitized-topic>-HHMMSS.md`
- Date from ISO string split on 'T'
- Topic sanitized: remove non-alphanumeric, replace spaces with hyphens
- Time from ISO timestamp (colons replaced with hyphens)

### Nudging Analysis
Simple keyword-based pattern detection:
- **Topics**: work, fitness, learning, projects
- **Mood indicators**: stressed (negative keywords) vs energetic (positive keywords)
- **Goals**: sentences containing "want to", "need to", "should", "plan to", "goal"
- Analysis runs every 60 minutes (configurable)

## Error Handling

- Claude API errors (429, 401) caught and user-friendly messages returned
- Obsidian file operations wrapped in try-catch, errors logged but don't crash
- Unhandled rejections/exceptions logged and exit process
- Missing config validation on startup prevents silent failures

## Dependencies

Key packages:
- `@anthropic-ai/sdk` - Claude API client
- `node-telegram-bot-api` - Telegram bot framework
- `chokidar` - File watching
- `gray-matter` - Frontmatter parsing
- `cron` - Scheduled jobs
- `dotenv` - Environment variables
- `natural` - NLP utilities (not actively used)