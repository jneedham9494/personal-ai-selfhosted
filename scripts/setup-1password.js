#!/usr/bin/env node

import { OnePasswordService } from '../src/services/onepassword.js';

console.log('🔐 1Password Setup for Personal AI Assistant');
console.log('=============================================\n');

async function setup1Password() {
    try {
        const onePassword = new OnePasswordService();
        
        console.log('🔍 Checking 1Password CLI...');
        await onePassword.initialize();
        
        console.log('🏗️ Setting up vault and credentials...');
        await onePassword.setupAIAssistantVault();
        
        console.log('\n🎉 1Password setup complete!');
        console.log('=====================================');
        console.log('✅ Vault "Personal AI Assistant" created');
        console.log('✅ Credentials template created');
        console.log('');
        console.log('📝 Next steps:');
        console.log('1. Set up your Telegram bot:');
        console.log('   • Open Telegram and message @BotFather');
        console.log('   • Send /newbot and follow instructions');
        console.log('   • Copy the bot token');
        console.log('');
        console.log('2. Get your Chat ID:');
        console.log('   • Start a chat with your new bot');
        console.log('   • Send any message to your bot');
        console.log('   • Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates');
        console.log('   • Look for "chat":{"id":YOUR_CHAT_ID and copy that number');
        console.log('');
        console.log('3. Update 1Password:');
        console.log('   • Open 1Password app');
        console.log('   • Go to "Personal AI Assistant" vault');
        console.log('   • Edit "AI Assistant Credentials" item');
        console.log('   • Add your real tokens:');
        console.log('     - Claude API Key (from console.anthropic.com)');
        console.log('     - Telegram Bot Token (from @BotFather)');
        console.log('     - Telegram Chat ID (from the getUpdates URL)');
        console.log('');
        console.log('🚀 Then run: npm run dev:1password');
        
    } catch (error) {
        console.error('❌ Setup failed:', error.message);
        
        if (error.message.includes('not signed in')) {
            console.log('\n💡 Please sign in to 1Password CLI first:');
            console.log('   op signin');
            console.log('   Then run this setup again.');
        }
        
        process.exit(1);
    }
}

setup1Password();