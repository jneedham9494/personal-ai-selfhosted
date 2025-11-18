#!/usr/bin/env node

import dotenv from 'dotenv';
import https from 'https';

dotenv.config();

console.log('🤖 Telegram Chat ID Helper');
console.log('===========================\n');

const botToken = process.argv[2] || process.env.TELEGRAM_BOT_TOKEN;

if (!botToken || botToken === 'your_telegram_bot_token_here') {
    console.log('❌ Please provide your Telegram bot token');
    console.log('Usage: node scripts/get-telegram-chat-id.js YOUR_BOT_TOKEN');
    console.log('Or set TELEGRAM_BOT_TOKEN in your .env file');
    process.exit(1);
}

console.log('🔍 Fetching recent messages for your bot...');
console.log('💡 Make sure you\'ve sent at least one message to your bot first!\n');

const url = `https://api.telegram.org/bot${botToken}/getUpdates`;

https.get(url, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const response = JSON.parse(data);
            
            if (!response.ok) {
                console.error('❌ Error from Telegram API:', response.description);
                return;
            }
            
            if (response.result.length === 0) {
                console.log('❌ No messages found!');
                console.log('💡 Send a message to your bot first, then run this script again.');
                return;
            }
            
            console.log('✅ Found messages! Here are your chat details:\n');
            
            const uniqueChats = new Map();
            
            response.result.forEach(update => {
                if (update.message && update.message.chat) {
                    const chat = update.message.chat;
                    uniqueChats.set(chat.id, chat);
                }
            });
            
            uniqueChats.forEach((chat, chatId) => {
                console.log(`📱 Chat ID: ${chatId}`);
                console.log(`👤 Name: ${chat.first_name || ''} ${chat.last_name || ''}`.trim());
                console.log(`📝 Username: @${chat.username || 'none'}`);
                console.log(`🔒 Type: ${chat.type}`);
                console.log('');
            });
            
            if (uniqueChats.size === 1) {
                const chatId = Array.from(uniqueChats.keys())[0];
                console.log(`✨ Use this Chat ID in your configuration: ${chatId}`);
                console.log('');
                console.log('📋 To add to .env file:');
                console.log(`TELEGRAM_CHAT_ID=${chatId}`);
                console.log('');
                console.log('🔐 To add to 1Password:');
                console.log('Update the "Telegram Chat ID" field in your AI Assistant Credentials');
            }
            
        } catch (error) {
            console.error('❌ Failed to parse response:', error.message);
        }
    });
    
}).on('error', (error) => {
    console.error('❌ Request failed:', error.message);
});