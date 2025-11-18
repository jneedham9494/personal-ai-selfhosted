#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🤖 Personal AI Assistant Setup');
console.log('================================\n');

// Check if .env exists
const envPath = path.join(__dirname, '..', '.env');
const envExamplePath = path.join(__dirname, '..', '.env.example');

if (!fs.existsSync(envPath)) {
    console.log('📋 Creating .env file from template...');
    fs.copyFileSync(envExamplePath, envPath);
    console.log('✅ .env file created!\n');
} else {
    console.log('📋 .env file already exists\n');
}

console.log('🔧 Next Steps:');
console.log('==============');
console.log('1. Edit the .env file with your configuration:');
console.log('   - Get Claude API key from: https://console.anthropic.com/');
console.log('   - Create Telegram bot with @BotFather');
console.log('   - Set your Obsidian vault path');
console.log('');
console.log('2. To create a Telegram bot:');
console.log('   - Message @BotFather on Telegram');
console.log('   - Send /newbot');
console.log('   - Follow instructions to get your bot token');
console.log('   - Start a chat with your bot to get your chat ID');
console.log('');
console.log('3. Run the assistant:');
console.log('   npm run dev');
console.log('');
console.log('🎉 Setup complete! Edit .env and start the assistant.');