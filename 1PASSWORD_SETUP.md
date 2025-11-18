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

Run the automated setup:
```bash
npm run setup:1password
```

This will:
- Create a vault called "Personal AI Assistant"
- Create an item called "AI Assistant Credentials" with placeholder fields
- Set up the correct field structure

**OR manually create:**

1. Open 1Password app
2. Create new vault: **"Personal AI Assistant"**
3. Create new item: **"AI Assistant Credentials"** (type: Password)
4. Add these fields:
   - **Claude API Key** (concealed) - Your Anthropic API key
   - **Telegram Bot Token** (concealed) - From @BotFather
   - **Telegram Chat ID** (text) - Your chat ID
   - **Obsidian Vault Path** (text) - `/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/personalai`

### Step 3: Add Your Credentials

Edit the "AI Assistant Credentials" item in 1Password:

#### Get Claude API Key
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
```bash
# Temporarily export bot token
export TEMP_BOT_TOKEN="your_bot_token_here"

# Run helper script
npm run get-chat-id $TEMP_BOT_TOKEN

# Then message your bot on Telegram
# Copy the chat ID to 1Password
```

### Step 4: Choose Your Running Method

You now have **3 ways** to run the assistant:

#### Option A: `op run` (Recommended - Cleanest)
```bash
npm run dev:op        # Development with watch mode
npm run start:op      # Production mode
```
- ✅ Keeps 1Password logic out of code
- ✅ Secrets injected at runtime
- ✅ Most secure

#### Option B: Code-based loading
```bash
npm run dev:1password    # Development
npm run start:1password  # Production
```
- ✅ Works without `op run` wrapper
- ✅ Good for background services
- ⚠️ Loads secrets into Node.js process

#### Option C: Traditional .env
```bash
npm run dev    # Uses .env file
npm run start
```
- ✅ Fallback if 1Password unavailable
- ⚠️ Credentials stored in plaintext file

## Secret Reference Format

The `.env.1password` file uses 1Password secret references:

```bash
ANTHROPIC_API_KEY=op://Personal AI Assistant/AI Assistant Credentials/Claude API Key
```

Format: `op://VAULT_NAME/ITEM_NAME/FIELD_NAME`

## Updating Credentials

### Via 1Password App
1. Open 1Password
2. Find "AI Assistant Credentials"
3. Edit fields
4. Restart the assistant

### Via CLI
```bash
op item edit "AI Assistant Credentials" \
  --vault "Personal AI Assistant" \
  "Claude API Key"="sk-ant-new-key-here"
```

### Quick Edit Alias
Add to `~/.zshrc` or `~/.bashrc`:
```bash
alias ai-edit='op item edit "AI Assistant Credentials" --vault "Personal AI Assistant"'
```

Then use:
```bash
ai-edit "Claude API Key"="new-value"
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
npm run dev:op
```

Look for:
```
✅ Configuration loaded from 1Password
✅ Obsidian vault found
✅ Telegram bot started
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
1. Test with: `npm run dev:op`
2. Message your Telegram bot
3. Check Obsidian vault for saved conversations
4. Verify nudging system is active

Need help? Check the main README.md or run:
```bash
npm run setup:complete  # Interactive setup wizard
```