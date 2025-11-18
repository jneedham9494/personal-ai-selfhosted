#!/usr/bin/env node

import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { ObsidianService } from './services/obsidian.js';
import { ClaudeService } from './services/claude.js';
import { TelegramBotService } from './bots/telegram.js';
import { OnePasswordService } from './services/onepassword.js';
import { NudgingService } from './services/nudging.js';

// Load environment variables as fallback
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🤖 Personal AI Assistant Starting...');
console.log('=====================================\n');

// Initialize services
let obsidianService;
let claudeService;
let telegramBot;
let onePasswordService;
let nudgingService;
let config = {};

async function loadConfiguration() {
    console.log('🔧 Loading configuration...');
    
    // Try 1Password first, fallback to .env
    const use1Password = process.argv.includes('--use-1password') || process.env.USE_1PASSWORD === 'true';
    
    if (use1Password) {
        try {
            onePasswordService = new OnePasswordService();
            await onePasswordService.initialize();
            config = await onePasswordService.loadConfiguration();
            console.log('✅ Configuration loaded from 1Password');
        } catch (error) {
            console.log('⚠️ 1Password failed, falling back to .env file');
            console.log(`   Error: ${error.message}`);
            config = process.env;
        }
    } else {
        console.log('📄 Using .env file configuration');
        config = process.env;
    }

    // Validate required configuration
    const requiredVars = ['OBSIDIAN_VAULT_PATH'];
    const missingVars = requiredVars.filter(varName => 
        !config[varName] || 
        config[varName] === '/path/to/your/obsidian/vault' ||
        config[varName] === 'your_obsidian_vault_path_here'
    );

    if (missingVars.length > 0) {
        console.error('❌ Missing required configuration:');
        missingVars.forEach(varName => {
            console.error(`   - ${varName}`);
        });
        
        if (use1Password && onePasswordService) {
            console.error('\n💡 Update your credentials in 1Password:');
            onePasswordService.printSetupInstructions();
        } else {
            console.error('\nPlease edit your .env file or use --use-1password flag');
            console.error('Run: npm run setup for help\n');
        }
        process.exit(1);
    }

    console.log(`✅ Configuration validated`);
    console.log(`📁 Obsidian vault: ${config.OBSIDIAN_VAULT_PATH}`);
    console.log(`🚀 Server port: ${config.PORT || 3000}\n`);
}

async function startServices() {
    try {
        await loadConfiguration();
        
        console.log('⏳ Starting services...');

        // Initialize Obsidian service
        console.log('📁 Initializing Obsidian...');
        obsidianService = new ObsidianService(config.OBSIDIAN_VAULT_PATH);
        await obsidianService.initialize();

        // Initialize Claude service
        console.log('🧠 Initializing Claude API...');
        claudeService = new ClaudeService(config.ANTHROPIC_API_KEY);

        // Set up Obsidian prompt watcher for file-based interactions
        console.log('💭 Setting up Obsidian prompt watcher...');
        obsidianService.setupPromptWatcher(claudeService);
        console.log('✅ Prompt system ready - create notes in Prompts/ folder to chat with Claude');

        // Initialize Telegram bot if configured
        if (config.TELEGRAM_BOT_TOKEN && config.TELEGRAM_BOT_TOKEN !== 'your_telegram_bot_token_here') {
            console.log('📱 Initializing Telegram bot...');
            telegramBot = new TelegramBotService(
                config.TELEGRAM_BOT_TOKEN,
                obsidianService,
                claudeService
            );
            console.log('✅ Telegram bot started and ready for messages!');
            console.log(`💬 Bot configured for chat ID: ${config.TELEGRAM_CHAT_ID || 'Not specified'}`);

            // Initialize nudging service if chat ID is configured
            if (config.TELEGRAM_CHAT_ID && config.TELEGRAM_CHAT_ID !== 'your_telegram_chat_id_here') {
                console.log('🔔 Initializing proactive nudging system...');
                nudgingService = new NudgingService(
                    obsidianService,
                    telegramBot,
                    claudeService,
                    {
                        enabled: config.NUDGING_ENABLED !== 'false',
                        startHour: parseInt(config.NUDGING_HOURS_START) || 8,
                        endHour: parseInt(config.NUDGING_HOURS_END) || 22,
                        chatId: config.TELEGRAM_CHAT_ID
                    }
                );
                await nudgingService.start();
                console.log('✅ Nudging system active - smart reminders enabled!');
            } else {
                console.log('⚠️ Nudging system disabled - no chat ID configured');
            }
        } else {
            console.log('⚠️ Telegram bot not configured');
            if (onePasswordService) {
                console.log('   Update "Telegram Bot Token" in 1Password');
            } else {
                console.log('   Add TELEGRAM_BOT_TOKEN to .env file');
            }
        }

        console.log('\n🎉 Personal AI Assistant is running!');
        console.log('=====================================');
        
        if (telegramBot) {
            console.log('📱 Chat with your bot on Telegram to get started');
            console.log('💬 All conversations will be saved to your Obsidian vault');
            if (nudgingService) {
                console.log('🔔 Smart nudging and reminders are active');
            }
        } else {
            console.log('🔧 Configure Telegram bot to start chatting');
        }
        
        if (onePasswordService) {
            console.log('🔐 Credentials managed by 1Password');
        }
        
        console.log('📊 Press Ctrl+C to stop the assistant\n');

    } catch (error) {
        console.error('❌ Failed to start services:', error.message);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down Personal AI Assistant...');
    
    if (nudgingService) {
        await nudgingService.stop();
    }
    
    if (telegramBot) {
        await telegramBot.stop();
    }
    
    if (obsidianService) {
        await obsidianService.close();
    }
    
    console.log('✅ Shutdown complete. Goodbye!');
    process.exit(0);
});

// Handle unhandled errors
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
    process.exit(1);
});

// Start the application
startServices();