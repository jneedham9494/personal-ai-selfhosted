import TelegramBot from 'node-telegram-bot-api';
import { ObsidianService } from '../services/obsidian.js';

export class TelegramBotService {
    constructor(token, obsidianService, claudeService = null, nudgingService = null) {
        this.bot = new TelegramBot(token, { polling: true });
        this.obsidian = obsidianService;
        this.claude = claudeService;
        this.nudging = nudgingService;
        this.activeConversations = new Map(); // Track ongoing conversations
        this.authorizedUsers = new Set(); // For security
        
        this.setupCommands();
        this.setupMessageHandlers();
    }

    setupCommands() {
        // Set bot commands for better UX
        this.bot.setMyCommands([
            { command: 'start', description: 'Start the AI assistant' },
            { command: 'help', description: 'Show available commands' },
            { command: 'project', description: 'Switch to a project context' },
            { command: 'goal', description: 'Switch to a goal context' },
            { command: 'progress', description: 'Update project/goal progress' },
            { command: 'new', description: 'Start a new conversation' },
            { command: 'context', description: 'Show current context' },
            { command: 'search', description: 'Search your notes' },
            { command: 'today', description: 'Show today\'s note' },
            { command: 'clear', description: 'Clear conversation context' },
            { command: 'status', description: 'Show system status' }
        ]);

        console.log('✅ Telegram bot commands configured');
    }

    setupMessageHandlers() {
        // Handle /start command
        this.bot.onText(/\/start/, (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            
            this.authorizedUsers.add(userId);
            
            const welcomeMessage = `🤖 **Personal AI Assistant**

Welcome! I'm your intelligent assistant that saves all our conversations to your Obsidian vault.

**Available commands:**
/help - Show this help message
/search <query> - Search your notes
/today - Show today's note
/clear - Clear conversation context
/status - Show system status

Just send me any message to start chatting! All conversations are automatically saved to your **AI-Conversations** folder in Obsidian.`;

            this.bot.sendMessage(chatId, welcomeMessage, { parse_mode: 'Markdown' });
            console.log(`👋 New user started: ${userId}`);
        });

        // Handle /help command
        this.bot.onText(/\/help/, (msg) => {
            const chatId = msg.chat.id;

            const helpMessage = `🔧 **AI Assistant Commands**

**Project & Goal Management:**
• \`/project <name>\` - Create/switch to a project
• \`/goal <name>\` - Create/switch to a goal
• \`/progress <0-100> [note]\` - Update progress
• \`/context\` - Show current context
• \`/new\` - Start a fresh conversation

**Chat Commands:**
• Just type anything to chat with Claude AI
• Conversations are auto-saved to Obsidian
• All conversations link to your projects/goals

**Utility Commands:**
• \`/search <query>\` - Search your notes
• \`/today\` - View/edit today's daily note
• \`/clear\` - Reset conversation context
• \`/status\` - Check system status

**Features:**
✅ Auto-creates project/goal files in Obsidian
✅ Bi-directional linking between conversations & projects
✅ Progress tracking with visual indicators
✅ Weekly & mid-week review prompts
✅ Action items automatically extracted
✅ Habit tracking for goals (edit in Obsidian)`;

            this.bot.sendMessage(chatId, helpMessage, { parse_mode: 'Markdown' });
        });

        // Handle /search command
        this.bot.onText(/\/search (.+)/, async (msg, match) => {
            const chatId = msg.chat.id;
            const query = match[1];

            if (!this.isAuthorized(msg.from.id)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            try {
                this.bot.sendMessage(chatId, `🔍 Searching for: "${query}"...`);
                
                const results = await this.obsidian.searchNotes(query);
                
                if (results.length === 0) {
                    this.bot.sendMessage(chatId, `❌ No notes found for "${query}"`);
                    return;
                }

                let message = `📋 **Found ${results.length} result(s):**\n\n`;
                
                results.slice(0, 5).forEach((result, index) => {
                    message += `**${index + 1}. ${result.file}**\n`;
                    message += `${result.excerpt}\n\n`;
                });

                if (results.length > 5) {
                    message += `... and ${results.length - 5} more results`;
                }

                this.bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
                
            } catch (error) {
                console.error('Search error:', error);
                this.bot.sendMessage(chatId, '❌ Error searching notes');
            }
        });

        // Handle /today command
        this.bot.onText(/\/today/, async (msg) => {
            const chatId = msg.chat.id;

            if (!this.isAuthorized(msg.from.id)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            try {
                const todaysNote = await this.obsidian.getTodaysNote();
                const preview = todaysNote.content.substring(0, 500);
                
                const message = `📅 **Today's Note**\n\n${preview}${todaysNote.content.length > 500 ? '...' : ''}`;
                
                this.bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
                
            } catch (error) {
                console.error('Today note error:', error);
                this.bot.sendMessage(chatId, '❌ Error retrieving today\'s note');
            }
        });

        // Handle /project command
        this.bot.onText(/\/project(?:\s+(.+))?/, async (msg, match) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            const projectName = match[1]?.trim();

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            if (!projectName) {
                this.bot.sendMessage(chatId, '📋 Usage: /project <project name>\n\nExample: /project Personal AI Assistant');
                return;
            }

            // Save current conversation if it exists
            if (this.activeConversations.has(userId)) {
                const currentConv = this.activeConversations.get(userId);
                if (currentConv.messages.length > 0) {
                    await this.saveConversationToObsidian(userId, currentConv);
                }
            }

            // Create or get project file in Obsidian
            try {
                await this.obsidian.createProject({ name: projectName });
                this.bot.sendMessage(chatId, `📋 Project file created/loaded in Obsidian!`);
            } catch (error) {
                console.error('Error creating project:', error);
            }

            // Create new conversation with project context
            this.activeConversations.set(userId, {
                messages: [],
                startTime: new Date(),
                topic: projectName,
                contextType: 'project',
                contextName: projectName,
                contextDescription: null
            });

            this.bot.sendMessage(chatId, `📋 Switched to project: **${projectName}**\n\nAll messages will now be saved under this project context. Use /context to check current context or /new to start fresh.`, { parse_mode: 'Markdown' });
        });

        // Handle /goal command
        this.bot.onText(/\/goal(?:\s+(.+))?/, async (msg, match) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            const goalName = match[1]?.trim();

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            if (!goalName) {
                this.bot.sendMessage(chatId, '🎯 Usage: /goal <goal name>\n\nExample: /goal Learn Spanish');
                return;
            }

            // Save current conversation if it exists
            if (this.activeConversations.has(userId)) {
                const currentConv = this.activeConversations.get(userId);
                if (currentConv.messages.length > 0) {
                    await this.saveConversationToObsidian(userId, currentConv);
                }
            }

            // Create or get goal file in Obsidian
            try {
                await this.obsidian.createGoal({ name: goalName });
                this.bot.sendMessage(chatId, `🎯 Goal file created/loaded in Obsidian!`);
            } catch (error) {
                console.error('Error creating goal:', error);
            }

            // Create new conversation with goal context
            this.activeConversations.set(userId, {
                messages: [],
                startTime: new Date(),
                topic: goalName,
                contextType: 'goal',
                contextName: goalName,
                contextDescription: null
            });

            this.bot.sendMessage(chatId, `🎯 Switched to goal: **${goalName}**\n\nAll messages will now be saved under this goal context. Use /context to check current context or /new to start fresh.`, { parse_mode: 'Markdown' });
        });

        // Handle /new command
        this.bot.onText(/\/new/, async (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            // Save current conversation if it exists
            if (this.activeConversations.has(userId)) {
                const currentConv = this.activeConversations.get(userId);
                if (currentConv.messages.length > 0) {
                    await this.saveConversationToObsidian(userId, currentConv);
                    this.bot.sendMessage(chatId, '💾 Previous conversation saved!');
                }
            }

            // Create fresh conversation
            this.activeConversations.set(userId, {
                messages: [],
                startTime: new Date(),
                topic: null,
                contextType: null,
                contextName: null,
                contextDescription: null
            });

            this.bot.sendMessage(chatId, '✨ Started a new conversation!\n\nUse /project or /goal to set a context, or just start chatting.');
        });

        // Handle /context command
        this.bot.onText(/\/context/, (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            const conversation = this.activeConversations.get(userId);

            if (!conversation) {
                this.bot.sendMessage(chatId, '💬 No active conversation.\n\nStart chatting or use /project or /goal to set a context.');
                return;
            }

            const contextIcon = conversation.contextType === 'project' ? '📋' : conversation.contextType === 'goal' ? '🎯' : '💬';
            const contextType = conversation.contextType || 'general';
            const contextName = conversation.contextName || 'None';
            const messageCount = conversation.messages.length;
            const duration = Math.round((Date.now() - conversation.startTime.getTime()) / 60000);

            const contextInfo = `${contextIcon} **Current Context**

**Type:** ${contextType}
**Name:** ${contextName}
**Messages:** ${messageCount}
**Duration:** ${duration} minutes
**Started:** ${conversation.startTime.toLocaleTimeString()}

Use /project or /goal to switch context
Use /new to start fresh conversation`;

            this.bot.sendMessage(chatId, contextInfo, { parse_mode: 'Markdown' });
        });

        // Handle /progress command
        this.bot.onText(/\/progress(?:\s+(\d+)(?:\s+(.+))?)?/, async (msg, match) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            const progressPercent = match[1] ? parseInt(match[1]) : null;
            const note = match[2]?.trim();

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            const conversation = this.activeConversations.get(userId);

            if (!conversation || !conversation.contextName || (!conversation.contextType === 'project' && !conversation.contextType === 'goal')) {
                this.bot.sendMessage(chatId, '⚠️ No active project or goal context.\n\nUse /project or /goal to set a context first.');
                return;
            }

            if (progressPercent === null) {
                this.bot.sendMessage(chatId, '📊 Usage: /progress <percentage> [note]\n\nExample: /progress 50 Completed initial research phase');
                return;
            }

            if (progressPercent < 0 || progressPercent > 100) {
                this.bot.sendMessage(chatId, '❌ Progress must be between 0 and 100');
                return;
            }

            try {
                await this.obsidian.updateProjectProgress(
                    conversation.contextName,
                    progressPercent,
                    note || ''
                );

                const statusEmoji = progressPercent === 100 ? '✅' : progressPercent >= 75 ? '🟢' : progressPercent >= 50 ? '🟡' : '🔵';
                this.bot.sendMessage(chatId, `${statusEmoji} Progress updated for **${conversation.contextName}**: ${progressPercent}%${note ? `\n\n📝 ${note}` : ''}`, { parse_mode: 'Markdown' });

            } catch (error) {
                console.error('Error updating progress:', error);
                this.bot.sendMessage(chatId, '❌ Error updating progress');
            }
        });

        // Handle /clear command
        this.bot.onText(/\/clear/, (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            this.activeConversations.delete(userId);
            this.bot.sendMessage(chatId, '🔄 Conversation context cleared!');
        });

        // Handle /status command
        this.bot.onText(/\/status/, (msg) => {
            const chatId = msg.chat.id;

            if (!this.isAuthorized(msg.from.id)) {
                this.bot.sendMessage(chatId, '❌ Unauthorized access');
                return;
            }

            const claudeStats = this.claude ? this.claude.getUsageStats() : null;
            const nudgingStats = this.nudging ? this.nudging.getStats() : null;

            const status = `📊 **System Status**

🤖 Telegram Bot: ✅ Online
📁 Obsidian: ✅ Connected
🧠 Claude API: ${claudeStats?.configured ? '✅ Connected' : '❌ Not configured'}
${claudeStats ? `   Rate limit: ${claudeStats.rateLimitRemaining}/${50} requests remaining` : ''}
🔔 Nudging System: ${nudgingStats?.enabled ? '✅ Active' : '❌ Disabled'}
${nudgingStats ? `   Today's nudges: ${nudgingStats.nudgesToday}/${nudgingStats.maxPerDay}` : ''}
${nudgingStats ? `   Active hours: ${nudgingStats.activeHours}` : ''}
${nudgingStats ? `   Currently: ${nudgingStats.isActiveNow ? '🟢 Active' : '🔴 Inactive'}` : ''}
👥 Active conversations: ${this.activeConversations.size}
💾 Vault: ${this.obsidian.vaultPath}

🕐 Server time: ${new Date().toLocaleString()}`;

            this.bot.sendMessage(chatId, status, { parse_mode: 'Markdown' });
        });

        // Handle regular messages (chat with Claude)
        this.bot.on('message', async (msg) => {
            // Skip if it's a command
            if (msg.text && msg.text.startsWith('/')) return;

            const chatId = msg.chat.id;
            const userId = msg.from.id;

            if (!this.isAuthorized(userId)) {
                this.bot.sendMessage(chatId, '❌ Please start with /start first');
                return;
            }

            try {
                await this.handleConversationMessage(msg);
            } catch (error) {
                console.error('Message handling error:', error);
                this.bot.sendMessage(chatId, '❌ Sorry, I encountered an error processing your message');
            }
        });

        console.log('✅ Telegram message handlers configured');
    }

    async handleConversationMessage(msg) {
        const chatId = msg.chat.id;
        const userId = msg.from.id;
        const userMessage = msg.text || msg.caption || '[Voice/Media message]';

        // Get or create conversation context
        if (!this.activeConversations.has(userId)) {
            this.activeConversations.set(userId, {
                messages: [],
                startTime: new Date(),
                topic: null,
                contextType: null, // 'project', 'goal', or null for general
                contextName: null, // name of the project/goal
                contextDescription: null
            });
        }

        const conversation = this.activeConversations.get(userId);
        
        // Add user message to conversation
        conversation.messages.push({
            role: 'user',
            content: userMessage,
            timestamp: new Date()
        });

        // Send typing indicator
        this.bot.sendChatAction(chatId, 'typing');

        if (this.claude) {
            // Get AI response
            try {
                const response = await this.claude.generateResponse(conversation.messages);
                
                // Add AI response to conversation
                conversation.messages.push({
                    role: 'assistant',
                    content: response,
                    timestamp: new Date()
                });

                // Extract topic from first exchange if not set
                if (!conversation.topic && conversation.messages.length >= 2) {
                    conversation.topic = await this.extractTopic(conversation.messages);
                }

                // Send response to user
                this.bot.sendMessage(chatId, response, { parse_mode: 'Markdown' });

                // Save conversation to Obsidian periodically (every 4 messages or after 5 minutes)
                if (conversation.messages.length % 4 === 0 || 
                    (Date.now() - conversation.startTime.getTime()) > 5 * 60 * 1000) {
                    await this.saveConversationToObsidian(userId, conversation);
                }

            } catch (error) {
                console.error('Claude API error:', error);
                this.bot.sendMessage(chatId, '🤖 Claude is temporarily unavailable. Your message has been saved.');
                
                // Still save to Obsidian even without AI response
                await this.saveConversationToObsidian(userId, conversation);
            }
        } else {
            // Claude not configured, just acknowledge and save
            this.bot.sendMessage(chatId, '📝 Message received and saved to Obsidian! (Claude API not configured yet)');
            await this.saveConversationToObsidian(userId, conversation);
        }
    }

    async saveConversationToObsidian(userId, conversation) {
        try {
            const conversationData = {
                platform: 'telegram',
                messages: conversation.messages,
                topic: conversation.topic || 'Telegram Conversation',
                metadata: {
                    userId: userId,
                    startTime: conversation.startTime,
                    messageCount: conversation.messages.length,
                    contextType: conversation.contextType,
                    contextName: conversation.contextName,
                    relatedProjects: conversation.contextType === 'project' && conversation.contextName ? [conversation.contextName] : []
                }
            };

            const savedPath = await this.obsidian.saveConversation(conversationData, this.claude);
            console.log(`💾 Saved conversation for user ${userId}`);

            // Link conversation back to project/goal file if context is set
            if (conversation.contextName && (conversation.contextType === 'project' || conversation.contextType === 'goal')) {
                const filename = savedPath.split('/').pop();
                await this.obsidian.linkConversationToProject(
                    conversation.contextName,
                    filename,
                    conversation.topic || 'Conversation'
                );
            }

        } catch (error) {
            console.error('Error saving to Obsidian:', error);
        }
    }

    async extractTopic(messages) {
        // Simple topic extraction - in reality, could use Claude for this
        const firstUserMessage = messages.find(m => m.role === 'user')?.content || '';
        const words = firstUserMessage.split(' ').slice(0, 5).join(' ');
        return words.length > 0 ? words : 'General Chat';
    }

    isAuthorized(userId) {
        return this.authorizedUsers.has(userId);
    }

    // Method to send proactive messages (for nudging system)
    async sendNotification(chatId, message) {
        try {
            await this.bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
            console.log(`📤 Sent notification to ${chatId}`);
        } catch (error) {
            console.error('Error sending notification:', error);
        }
    }

    async stop() {
        console.log('🛑 Stopping Telegram bot...');
        await this.bot.stopPolling();
        console.log('✅ Telegram bot stopped');
    }
}