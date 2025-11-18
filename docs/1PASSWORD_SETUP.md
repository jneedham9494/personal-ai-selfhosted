# 1Password Setup Guide

Complete guide for setting up 1Password integration with your Personal AI Assistant.

## Prerequisites

✅ 1Password CLI installed (`op` command available)
✅ 1Password desktop app installed
✅ Active 1Password account

## Setup Steps

### Step 1: Enable Desktop App Integration

1. Open **1Password desktop app**
2. Go to **Settings** (⌘, on Mac) → **Developer**
3. Enable **"Connect with 1Password CLI"**
4. Verify connection:
   ```bash
   op account list
   ```
   You should see your account details.

### Step 2: Create Vault and Credentials

**Manually create:**

1. Open 1Password app
2. Create new vault: **"Personal AI Assistant"**
3. Create new item: **"AI Assistant Credentials"** (type: Password)
4. Add these fields:
   - **Anthropic API Key** (concealed) - Your Claude API key
   - **Telegram Bot Token** (concealed) - From @BotFather
   - **Telegram Chat ID** (text) - Your chat ID
   - **Obsidian Vault Path** (text) - Path to your vault
   - **Ollama Host** (text) - `http://localhost:11434`

### Step 3: Add Your Credentials

Edit the "AI Assistant Credentials" item in 1Password:

#### Get Claude API Key (Optional)
1. Visit https://console.anthropic.com/
2. Sign up/login
3. Go to API Keys → Create Key
4. Copy and paste into 1Password field

#### Get Telegram Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow instructions (name + username)
4. Copy token to 1Password

#### Get Telegram Chat ID
1. Set your bot token temporarily:
   ```bash
   export TEMP_BOT_TOKEN="your_bot_token_here"
   ```
2. Start a chat with your bot on Telegram
3. Send any message
4. Get your chat ID:
   ```bash
   curl "https://api.telegram.org/bot${TEMP_BOT_TOKEN}/getUpdates" | python -m json.tool
   ```
5. Find `chat.id` in the response and save to 1Password

### Step 4: Configure Environment

Create `.env.1password` in project root:

```bash
# 1Password secret references
ANTHROPIC_API_KEY=op://Personal AI Assistant/AI Assistant Credentials/Anthropic API Key
TELEGRAM_BOT_TOKEN=op://Personal AI Assistant/AI Assistant Credentials/Telegram Bot Token
TELEGRAM_CHAT_ID=op://Personal AI Assistant/AI Assistant Credentials/Telegram Chat ID
OBSIDIAN_VAULT_PATH=op://Personal AI Assistant/AI Assistant Credentials/Obsidian Vault Path
OLLAMA_HOST=op://Personal AI Assistant/AI Assistant Credentials/Ollama Host
```

### Step 5: Run with 1Password

#### Using `op run` (Recommended)

```bash
# Backend
cd backend
op run --env-file=../.env.1password -- uvicorn main:app --reload

# Or create a script
./scripts/run-with-op.sh
```

#### Traditional .env Fallback

If 1Password unavailable, copy `.env.example` to `.env` and fill in values manually.

## Secret Reference Format

```bash
ANTHROPIC_API_KEY=op://VAULT_NAME/ITEM_NAME/FIELD_NAME
```

Format: `op://VAULT_NAME/ITEM_NAME/FIELD_NAME`

## Updating Credentials

### Via 1Password App
1. Open 1Password
2. Find "AI Assistant Credentials"
3. Edit fields
4. Restart the application

### Via CLI
```bash
op item edit "AI Assistant Credentials" \
  --vault "Personal AI Assistant" \
  "Anthropic API Key"="sk-ant-new-key-here"
```

### Quick Edit Alias
Add to `~/.zshrc` or `~/.bashrc`:
```bash
alias ai-edit='op item edit "AI Assistant Credentials" --vault "Personal AI Assistant"'
```

Then use:
```bash
ai-edit "Anthropic API Key"="new-value"
```

## Testing Your Setup

### Test 1Password Connection
```bash
op whoami
op vault list
op item get "AI Assistant Credentials" --vault "Personal AI Assistant"
```

### Test Secret Injection
```bash
op run --env-file=.env.1password -- env | grep ANTHROPIC
```
Should show your API key (be careful in shared terminals!)

### Test Application Start
```bash
cd backend
op run --env-file=../.env.1password -- uvicorn main:app --reload
```

Look for:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Configuration loaded from 1Password
```

## Troubleshooting

### "No accounts configured"
- Enable desktop app integration in 1Password Settings → Developer
- Restart terminal after enabling

### "Item not found"
- Check vault name: `op vault list`
- Check item name: `op item list --vault "Personal AI Assistant"`
- Ensure exact spelling and quotes

### "Failed to read secret"
- Verify field names match exactly
- Use `op item get "AI Assistant Credentials"` to see all fields
- Field names are case-sensitive

### Desktop app integration not working
- Restart 1Password app
- Restart terminal
- Check: System Settings → Privacy & Security → 1Password has permissions

## Security Best Practices

✅ **DO:**
- Use `op run` for local development (cleanest)
- Rotate API keys quarterly
- Use separate items for dev/prod credentials
- Enable 1Password Travel Mode when traveling

❌ **DON'T:**
- Commit `.env` file with real credentials
- Share screen with 1Password unlocked
- Use production credentials in development
- Store API keys in code comments

## Backup & Recovery

1. **1Password handles backups automatically**
2. **Export vault** (occasionally):
   ```bash
   op vault export "Personal AI Assistant" --output backup.1pux
   ```
3. **Store recovery kit** in secure physical location
4. **Document vault structure** (this file!)

## Next Steps

Once setup is complete:
1. Start the backend with `op run`
2. Configure Telegram bot token in 1Password
3. Message your Telegram bot
4. Check Obsidian vault for saved conversations
