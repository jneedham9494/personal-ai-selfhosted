# Personal AI Assistant - Project Constitution

> Standards and patterns extracted from existing codebase

## Project Overview

**Purpose:** Personal AI assistant that integrates Claude AI with Telegram and Obsidian for cross-device knowledge management.

**Tech Stack:**
- Runtime: Node.js 18+ with ES Modules
- AI: Anthropic Claude API (claude-3-haiku-20240307)
- Messaging: Telegram Bot API (node-telegram-bot-api)
- Storage: Obsidian vault (markdown files with YAML frontmatter)
- Security: 1Password CLI for credential management
- Testing: Jest

---

## Code Patterns

### File Organization
```
src/
├── index.js           # Application entry, service orchestration
├── bots/              # Platform-specific bot implementations
│   └── telegram.js    # Telegram bot service
├── services/          # Core business logic services
│   ├── claude.js      # Claude AI integration
│   ├── obsidian.js    # Obsidian vault management
│   ├── nudging.js     # Proactive reminder system
│   └── onepassword.js # Credential management
└── utils/             # Shared utilities (currently empty)
```

### Naming Conventions
- **Files:** lowercase with hyphens (e.g., `one-password.js`) - currently using camelCase
- **Classes:** PascalCase with "Service" suffix (e.g., `ClaudeService`)
- **Methods:** camelCase with verb prefixes (e.g., `setupWatcher`, `generateResponse`)
- **Constants:** Environment variables are SCREAMING_SNAKE_CASE

### Module Pattern
- ES Modules (`import`/`export`)
- Named exports for classes
- Services are singletons created in index.js
- Dependencies injected via constructor

### Async Patterns
- All I/O operations use async/await
- Promises wrapped in try/catch blocks
- Console logging for operation status (with emoji prefixes)

---

## Error Handling Standards

### Current Pattern
```javascript
try {
    // operation
    console.log('✅ Success message');
} catch (error) {
    console.error('❌ Error message:', error.message);
    // graceful handling or re-throw
}
```

### API Error Handling
- Check specific status codes (401, 429)
- Return user-friendly error messages
- Log technical details internally

### Graceful Degradation
- Services continue when dependencies unavailable
- Claude API key missing → bot works without AI
- 1Password unavailable → fall back to .env

---

## Configuration Management

### Priority Order
1. Command-line flags (`--use-1password`)
2. 1Password vault (if enabled)
3. `.env` file (fallback)

### Required Configuration
- `OBSIDIAN_VAULT_PATH` - Absolute path to vault

### Optional Configuration
- `TELEGRAM_BOT_TOKEN` - Bot disabled if missing
- `ANTHROPIC_API_KEY` - AI disabled if missing
- `TELEGRAM_CHAT_ID` - Nudging disabled if missing

---

## Obsidian Integration Standards

### Folder Structure in Vault
- `AI-Conversations/` - Auto-saved conversations
- `Daily-Notes/` - Daily journal entries
- `Templates/` - Note templates
- `Prompts/` - File-based prompt input
- `Projects/` - Project/goal tracking

### File Naming
```
YYYY-MM-DD-<sanitized-topic>-HHMMSS.md
```

### Frontmatter Schema
```yaml
type: ai-conversation | project | goal
date: ISO 8601 timestamp
platform: telegram | obsidian
topic: string
category: work | personal | learning | health | finance | creative | general
mood: stressed | excited | focused | confused | reflective | neutral
priority: high | medium | low
tags: array
```

### Cross-Linking
- Conversations link to daily notes
- Projects/goals have related_conversations array
- Bi-directional linking via Obsidian wiki syntax

---

## Telegram Bot Standards

### Command Structure
- All commands registered via `setMyCommands()`
- Handler pattern: `bot.onText(/regex/, handler)`
- Commands return user-friendly messages with markdown

### Authorization
- Users must `/start` before using bot
- `authorizedUsers` Set tracks authorized user IDs
- All protected handlers check `isAuthorized()`

### Conversation Context
- Stored per-user in `activeConversations` Map
- Auto-saved every 4 messages or 5 minutes
- Can be cleared with `/clear` command

---

## Claude API Standards

### Rate Limiting
- In-memory sliding window (50 requests/minute)
- Tracked in `rateLimiter.requests` array
- Check before each request

### Response Generation
- Default model: `claude-3-haiku-20240307`
- Default max_tokens: 1000
- Default temperature: 0.7
- Custom system prompt for personal assistant context

---

## Testing Standards

### Current State
- Jest configured but limited tests
- `scripts/test-obsidian-integration.js` for manual testing

### Required Testing
- Unit tests for service methods
- Integration tests for Telegram commands
- Mock external services (Claude API, 1Password CLI)

---

## Logging Standards

### Emoji Prefixes
- `🤖` - AI/bot related
- `📁` - File operations
- `✅` - Success
- `❌` - Error
- `⚠️` - Warning
- `🔍` - Search/analysis
- `💾` - Save operations
- `🔐` - Security/credentials
- `🔔` - Notifications/nudges
- `📤` - Outbound messages

### Log Levels
- `console.log()` - Info/success
- `console.error()` - Errors with context
- No debug logging currently

---

## Security Practices

### Credential Handling
- Never hardcode secrets
- Use 1Password CLI or environment variables
- Validate API keys on startup

### User Input
- Basic validation for commands
- Sanitize topic names for filenames
- No SQL injection risk (file-based storage)

### Authorization
- Telegram user IDs tracked in memory Set
- No persistent user management

---

## Future Improvements Needed

### Critical
- [ ] Add comprehensive test suite
- [ ] Implement proper error types
- [ ] Add input validation throughout
- [ ] Persistent user authorization

### Important
- [ ] TypeScript migration
- [ ] Database for scalability
- [ ] Webhook-based Telegram (vs polling)
- [ ] Structured logging

### Nice to Have
- [ ] Web dashboard
- [ ] Multiple AI provider support
- [ ] Voice message transcription
- [ ] Calendar integration

---

*Last updated: 2025-11-18*
*Generated by SpecKit Retrofit*
