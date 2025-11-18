# Personal AI Assistant

An intelligent AI assistant system that integrates with Obsidian and messaging platforms for seamless cross-device knowledge management and proactive life coaching.

## 🚀 Features

- **🤖 Telegram Bot Interface**: Chat with Claude AI via Telegram
- **📝 Obsidian Integration**: Auto-save conversations and daily notes
- **🔔 Proactive Nudging**: Smart reminders based on your patterns
- **🔐 1Password Support**: Secure credential management
- **📱 Cross-Device Sync**: Works on iPhone and Mac via iCloud
- **🔍 Knowledge Search**: Find information across your notes
- **⏰ Smart Scheduling**: Context-aware reminders and check-ins

## 📦 Quick Setup

### Prerequisites
- Node.js 18+ installed
- Obsidian app installed (Mac & iPhone)
- Telegram account
- 1Password app (optional, for secure credentials)

### Installation

```bash
# Clone or download the project
cd personal-ai-assistant

# Install dependencies (already done)
npm install

# Run complete setup guide
node scripts/complete-setup-guide.js
```

### Configuration

#### Option 1: Environment Variables (.env file)
```bash
# Edit .env file
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_telegram_chat_id
ANTHROPIC_API_KEY=your_claude_api_key
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
```

#### Option 2: 1Password (Recommended)
```bash
# Setup 1Password integration
npm run setup:1password

# Enable CLI in 1Password app:
# Settings → Developer → Enable "Connect with 1Password CLI"
```

### Get Your Credentials

1. **Telegram Bot Token**:
   - Message @BotFather on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token

2. **Get Chat ID**:
   ```bash
   npm run get-chat-id YOUR_BOT_TOKEN
   ```

3. **Claude API Key**:
   - Visit https://console.anthropic.com/
   - Create account and generate API key

### Start the Assistant

```bash
# With .env file
npm run dev

# With 1Password
npm run dev:1password
```

## 🎯 Usage

### Telegram Commands
- **Chat naturally** - AI responds and saves to Obsidian
- `/help` - Show available commands
- `/search <query>` - Search your Obsidian notes
- `/today` - View today's daily note
- `/status` - Check system status
- `/clear` - Reset conversation context

### Obsidian Integration
- **Conversations**: Auto-saved in `AI-Conversations/` folder
- **Daily Notes**: Created in `Daily-Notes/` folder
- **Templates**: Available in `Templates/` folder
- **Real-time sync** via iCloud or Obsidian Sync

**Vault Location**: Default vault is stored in iCloud:
```bash
/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi
```
This enables seamless syncing between Mac and iPhone.

**Common Folders:**
- `Projects/` - Active and archived projects (trip planning, goals, etc.)
- `AI-Conversations/` - Auto-saved Telegram bot conversations
- `Daily-Notes/` - Daily journal entries
- `Templates/` - Note templates
- `Archive/` - Completed projects and old notes
  - `Archive/2025-Trips/` - Archived trip planning files

**Finding Files:**
Use Spotlight search to quickly locate files:
```bash
# Find all markdown files in vault
mdfind -onlyin "/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi" "*.md"

# Search for specific content
mdfind "trip OR travel" | grep PersonalAi
```

### Proactive Features
- **Morning motivation** (9 AM)
- **Afternoon check-ins** (2 PM) 
- **Evening reflections** (7 PM)
- **Context-aware nudges** based on your conversations
- **Goal reminders** from your notes
- **Wellness suggestions** when stressed

## 🛠 Available Scripts

```bash
npm run setup              # Basic setup help
npm run setup:1password    # 1Password integration setup
npm run get-chat-id        # Get Telegram chat ID
npm run test-obsidian      # Test Obsidian integration
npm run dev                # Start with .env
npm run dev:1password      # Start with 1Password
npm run start              # Production mode
```

## 📂 Project Structure

```
src/
├── bots/
│   └── telegram.js        # Telegram bot implementation
├── services/
│   ├── obsidian.js        # Obsidian vault integration
│   ├── claude.js          # Claude API client
│   ├── nudging.js         # Proactive reminder system
│   └── onepassword.js     # 1Password integration
└── index.js               # Main application

scripts/
├── setup.js               # Basic setup
├── setup-1password.js     # 1Password setup
├── get-telegram-chat-id.js # Telegram chat ID helper
└── complete-setup-guide.js # Full setup guide
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Required
OBSIDIAN_VAULT_PATH=/path/to/vault

# Telegram (required for chat)
TELEGRAM_BOT_TOKEN=bot_token
TELEGRAM_CHAT_ID=chat_id

# Claude API (optional but recommended)
ANTHROPIC_API_KEY=claude_key

# Nudging System
NUDGING_ENABLED=true
NUDGING_HOURS_START=8
NUDGING_HOURS_END=22

# Server
PORT=3000
NODE_ENV=development
```

### 1Password Vault Structure
```
Personal AI Assistant/
└── AI Assistant Credentials
    ├── Claude API Key
    ├── Telegram Bot Token
    ├── Telegram Chat ID
    └── Obsidian Vault Path
```

## 🔒 Security

- **1Password Integration**: Secure credential storage
- **User Authorization**: Bot only responds to configured users
- **Local Processing**: Conversations stored locally in Obsidian
- **Rate Limiting**: Built-in API rate limiting
- **Error Handling**: Graceful failure handling

## 🆘 Troubleshooting

### Common Issues

1. **"Obsidian vault not found"**
   - Check `OBSIDIAN_VAULT_PATH` in configuration
   - Ensure vault exists and is accessible

2. **"1Password CLI not signed in"**
   - Enable desktop app integration in 1Password settings
   - Or manually add account with `op account add`

3. **"Telegram bot not responding"**
   - Verify bot token is correct
   - Check chat ID matches your Telegram user
   - Ensure bot has been started with `/start`

4. **"Claude API errors"**
   - Verify API key is valid
   - Check billing/credits in Anthropic console
   - Rate limiting may be in effect

### Getting Help

```bash
# Test individual components
npm run test-obsidian      # Test Obsidian integration
npm run configure-obsidian # Configure Obsidian paths
node scripts/complete-setup-guide.js # Full setup guide
```

## 🎉 What You Get

Once configured, you'll have:

- ✅ **Smart AI conversations** via Telegram
- ✅ **Automatic note-taking** in Obsidian  
- ✅ **Cross-device synchronization**
- ✅ **Proactive life coaching** and reminders
- ✅ **Secure credential management**
- ✅ **Knowledge base search** and insights
- ✅ **Daily reflection prompts**
- ✅ **Context-aware suggestions**

Your personal AI assistant that learns your patterns and helps you stay organized and motivated across all your devices!