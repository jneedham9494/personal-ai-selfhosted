import cron from 'cron';
import { ClaudeService } from './claude.js';

export class NudgingService {
    constructor(obsidianService, telegramBot, claudeService, config = {}) {
        this.obsidian = obsidianService;
        this.telegram = telegramBot;
        this.claude = claudeService;
        
        this.config = {
            enabled: config.enabled !== false,
            startHour: config.startHour || 8,
            endHour: config.endHour || 22,
            chatId: config.chatId,
            maxNudgesPerDay: config.maxNudgesPerDay || 5,
            analysisInterval: config.analysisInterval || 60 // minutes
        };
        
        this.nudgeHistory = new Map(); // Track nudges sent
        this.analysisJob = null;
        this.nudgePatterns = [];
        
        console.log('🔔 Nudging service initialized');
    }

    async start() {
        if (!this.config.enabled || !this.config.chatId) {
            console.log('⚠️ Nudging service disabled or no chat ID configured');
            return;
        }

        console.log('🚀 Starting proactive nudging system...');
        
        // Schedule periodic analysis
        this.analysisJob = new cron.CronJob(
            `0 */${this.config.analysisInterval} * * * *`, // Every X minutes
            () => this.performAnalysis(),
            null,
            true
        );

        // Schedule specific nudge times
        this.scheduleRegularNudges();
        
        console.log('✅ Nudging system active');
        console.log(`⏰ Analysis runs every ${this.config.analysisInterval} minutes`);
        console.log(`🕐 Active hours: ${this.config.startHour}:00 - ${this.config.endHour}:00`);
    }

    scheduleRegularNudges() {
        // Morning motivation (9 AM)
        new cron.CronJob(
            '0 0 9 * * *',
            () => this.sendMorningNudge(),
            null,
            true
        );

        // Afternoon check-in (2 PM)
        new cron.CronJob(
            '0 0 14 * * *',
            () => this.sendAfternoonNudge(),
            null,
            true
        );

        // Evening reflection (7 PM)
        new cron.CronJob(
            '0 0 19 * * *',
            () => this.sendEveningNudge(),
            null,
            true
        );

        // Weekly review (Sunday 6 PM)
        new cron.CronJob(
            '0 0 18 * * 0',
            () => this.sendWeeklyReview(),
            null,
            true
        );

        // Mid-week check (Wednesday 10 AM)
        new cron.CronJob(
            '0 0 10 * * 3',
            () => this.sendMidWeekCheck(),
            null,
            true
        );

        console.log('📅 Regular nudge schedule configured (including weekly reviews)');
    }

    async performAnalysis() {
        if (!this.isActiveHour()) return;

        try {
            console.log('🔍 Performing conversation analysis for nudging...');
            
            // Get recent conversations
            const recentConversations = await this.getRecentConversations();
            
            if (recentConversations.length === 0) return;

            // Analyze patterns
            const analysis = await this.analyzeConversationPatterns(recentConversations);
            
            // Generate nudges based on analysis
            const nudges = await this.generateContextualNudges(analysis);
            
            // Send appropriate nudges
            for (const nudge of nudges) {
                if (await this.shouldSendNudge(nudge)) {
                    await this.sendNudge(nudge);
                }
            }

        } catch (error) {
            console.error('❌ Analysis error:', error.message);
        }
    }

    async getRecentConversations() {
        try {
            // Get conversations from last 24 hours
            const results = await this.obsidian.searchNotes('');
            
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            
            return results.filter(result => {
                const fileDate = this.extractDateFromFilename(result.file);
                return fileDate && fileDate > yesterday;
            });

        } catch (error) {
            console.error('Error getting recent conversations:', error);
            return [];
        }
    }

    extractDateFromFilename(filename) {
        const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
        return dateMatch ? new Date(dateMatch[1]) : null;
    }

    async analyzeConversationPatterns(conversations) {
        const patterns = {
            mood: 'neutral',
            topics: [],
            energy: 'normal',
            goals: [],
            challenges: [],
            timePatterns: {}
        };

        // Simple pattern analysis (can be enhanced with Claude)
        let totalMessages = 0;
        const topics = new Set();
        const goalKeywords = ['want to', 'need to', 'should', 'plan to', 'goal', 'achieve'];
        const stressKeywords = ['stressed', 'overwhelmed', 'tired', 'difficult', 'hard'];
        const energyKeywords = ['excited', 'motivated', 'energetic', 'productive'];

        for (const conv of conversations) {
            const content = conv.excerpt.toLowerCase();
            totalMessages++;

            // Extract topics (simple keyword matching)
            if (content.includes('work') || content.includes('job')) topics.add('work');
            if (content.includes('exercise') || content.includes('workout')) topics.add('fitness');
            if (content.includes('read') || content.includes('book')) topics.add('learning');
            if (content.includes('project')) topics.add('projects');

            // Analyze mood indicators
            if (stressKeywords.some(word => content.includes(word))) {
                patterns.mood = 'stressed';
            } else if (energyKeywords.some(word => content.includes(word))) {
                patterns.mood = 'energetic';
            }

            // Extract goals
            goalKeywords.forEach(keyword => {
                if (content.includes(keyword)) {
                    const sentences = content.split(/[.!?]/);
                    sentences.forEach(sentence => {
                        if (sentence.includes(keyword)) {
                            patterns.goals.push(sentence.trim());
                        }
                    });
                }
            });
        }

        patterns.topics = Array.from(topics);
        patterns.messageCount = totalMessages;

        return patterns;
    }

    async generateContextualNudges(analysis) {
        const nudges = [];
        const now = new Date();
        const hour = now.getHours();

        // Generate nudges based on patterns
        if (analysis.mood === 'stressed') {
            nudges.push({
                type: 'wellness',
                message: "🌱 I noticed you might be feeling a bit overwhelmed. How about a 5-minute break or some deep breathing?",
                priority: 'high'
            });
        }

        if (analysis.topics.includes('fitness') && hour > 16) {
            nudges.push({
                type: 'activity',
                message: "💪 You mentioned fitness earlier - perfect time for a quick workout or walk!",
                priority: 'medium'
            });
        }

        if (analysis.goals.length > 0 && hour > 10 && hour < 15) {
            const randomGoal = analysis.goals[Math.floor(Math.random() * analysis.goals.length)];
            nudges.push({
                type: 'goal_reminder',
                message: `🎯 Quick reminder about: "${randomGoal.substring(0, 100)}..." - any progress today?`,
                priority: 'medium'
            });
        }

        if (analysis.messageCount === 0 && hour > 12) {
            nudges.push({
                type: 'check_in',
                message: "👋 How's your day going? I'm here if you need to chat about anything!",
                priority: 'low'
            });
        }

        return nudges;
    }

    async shouldSendNudge(nudge) {
        const today = new Date().toDateString();
        
        // Check daily limit
        const todayNudges = this.nudgeHistory.get(today) || [];
        if (todayNudges.length >= this.config.maxNudgesPerDay) {
            return false;
        }

        // Check if we've sent this type recently
        const recentSameType = todayNudges.filter(n => 
            n.type === nudge.type && 
            (Date.now() - n.timestamp) < 2 * 60 * 60 * 1000 // 2 hours
        );

        if (recentSameType.length > 0) {
            return false;
        }

        // Random chance based on priority
        const chances = { high: 0.8, medium: 0.5, low: 0.3 };
        return Math.random() < chances[nudge.priority];
    }

    async sendNudge(nudge) {
        try {
            const message = `🤖 ${nudge.message}`;
            
            if (this.telegram) {
                await this.telegram.sendNotification(this.config.chatId, message);
            }

            // Track the nudge
            const today = new Date().toDateString();
            const todayNudges = this.nudgeHistory.get(today) || [];
            todayNudges.push({
                ...nudge,
                timestamp: Date.now()
            });
            this.nudgeHistory.set(today, todayNudges);

            console.log(`📤 Sent ${nudge.type} nudge`);

        } catch (error) {
            console.error('❌ Failed to send nudge:', error.message);
        }
    }

    async sendMorningNudge() {
        if (!this.isActiveHour()) return;

        const messages = [
            "🌅 Good morning! What's one thing you want to accomplish today?",
            "☀️ New day, new possibilities! What's on your agenda?",
            "🚀 Morning! Ready to tackle your goals today?",
            "🌱 Good morning! How are you feeling about today's challenges?"
        ];

        const nudge = {
            type: 'morning_motivation',
            message: messages[Math.floor(Math.random() * messages.length)],
            priority: 'medium'
        };

        if (await this.shouldSendNudge(nudge)) {
            await this.sendNudge(nudge);
        }
    }

    async sendAfternoonNudge() {
        if (!this.isActiveHour()) return;

        // Get today's note to see if there are any goals
        try {
            const todaysNote = await this.obsidian.getTodaysNote();
            
            let message = "🕐 Afternoon check-in! How's your day progressing?";
            
            if (todaysNote.content.includes('[ ]')) {
                message = "✅ Afternoon check-in! Any of those to-dos ready to be checked off?";
            }

            const nudge = {
                type: 'afternoon_checkin',
                message: message,
                priority: 'low'
            };

            if (await this.shouldSendNudge(nudge)) {
                await this.sendNudge(nudge);
            }

        } catch (error) {
            console.error('Error in afternoon nudge:', error);
        }
    }

    async sendEveningNudge() {
        if (!this.isActiveHour()) return;

        const messages = [
            "🌙 Evening reflection: What went well today?",
            "📝 End of day check-in - any thoughts to capture?",
            "🌅 What's one thing you learned today?",
            "💭 Time to wind down - anything on your mind?"
        ];

        const nudge = {
            type: 'evening_reflection',
            message: messages[Math.floor(Math.random() * messages.length)],
            priority: 'medium'
        };

        if (await this.shouldSendNudge(nudge)) {
            await this.sendNudge(nudge);
        }
    }

    isActiveHour() {
        const hour = new Date().getHours();
        return hour >= this.config.startHour && hour <= this.config.endHour;
    }

    async stop() {
        if (this.analysisJob) {
            this.analysisJob.stop();
            console.log('🛑 Nudging system stopped');
        }
    }

    async sendWeeklyReview() {
        if (!this.isActiveHour()) return;

        try {
            console.log('📊 Generating weekly review...');

            // Get all active projects and goals
            const projects = await this.getActiveProjectsAndGoals();

            if (projects.length === 0) {
                const nudge = {
                    type: 'weekly_review',
                    message: '📅 Weekly Review Time!\n\nHow did this week go? Any wins or learnings to capture?',
                    priority: 'high'
                };

                if (await this.shouldSendNudge(nudge)) {
                    await this.sendNudge(nudge);
                }
                return;
            }

            // Build review message with project/goal status
            let reviewMessage = '📅 **Weekly Review Time!**\n\nLet\'s reflect on your projects and goals:\n\n';

            for (const project of projects.slice(0, 5)) {
                const icon = project.type === 'project' ? '📋' : '🎯';
                const progress = project.progress || 0;
                const progressBar = this.generateProgressBar(progress);
                reviewMessage += `${icon} **${project.name}**\n${progressBar} ${progress}%\n\n`;
            }

            reviewMessage += '\n💭 Questions to reflect on:\n';
            reviewMessage += '• What progress did you make this week?\n';
            reviewMessage += '• What challenges did you face?\n';
            reviewMessage += '• What are your priorities for next week?\n';

            const nudge = {
                type: 'weekly_review',
                message: reviewMessage,
                priority: 'high'
            };

            if (await this.shouldSendNudge(nudge)) {
                await this.sendNudge(nudge);
            }

        } catch (error) {
            console.error('Error in weekly review:', error);
        }
    }

    async sendMidWeekCheck() {
        if (!this.isActiveHour()) return;

        try {
            const projects = await this.getActiveProjectsAndGoals();

            if (projects.length === 0) {
                return; // Skip if no projects
            }

            const projectsNeedingAttention = projects.filter(p => {
                const lastUpdated = new Date(p.lastUpdated || p.created);
                const daysSinceUpdate = (Date.now() - lastUpdated.getTime()) / (1000 * 60 * 60 * 24);
                return daysSinceUpdate > 7; // Not updated in a week
            });

            if (projectsNeedingAttention.length > 0) {
                let message = '📌 **Mid-Week Check-In**\n\nThese projects/goals could use some attention:\n\n';

                projectsNeedingAttention.slice(0, 3).forEach(p => {
                    const icon = p.type === 'project' ? '📋' : '🎯';
                    message += `${icon} ${p.name}\n`;
                });

                message += '\nMaybe spend some time on one of these today?';

                const nudge = {
                    type: 'midweek_check',
                    message: message,
                    priority: 'medium'
                };

                if (await this.shouldSendNudge(nudge)) {
                    await this.sendNudge(nudge);
                }
            } else {
                const message = '🎯 Mid-week check-in! You\'re staying on top of your projects. How\'s the week going so far?';

                const nudge = {
                    type: 'midweek_check',
                    message: message,
                    priority: 'medium'
                };

                if (await this.shouldSendNudge(nudge)) {
                    await this.sendNudge(nudge);
                }
            }

        } catch (error) {
            console.error('Error in mid-week check:', error);
        }
    }

    async getActiveProjectsAndGoals() {
        try {
            const fs = await import('fs/promises');
            const path = await import('path');
            const matter = (await import('gray-matter')).default;

            const projectsFolder = this.obsidian.projectsFolder;
            const files = await fs.readdir(projectsFolder);

            const projects = [];

            for (const file of files) {
                if (!file.endsWith('.md')) continue;

                const filePath = path.join(projectsFolder, file);
                const content = await fs.readFile(filePath, 'utf-8');
                const parsed = matter(content);

                if (parsed.data.status === 'active' || !parsed.data.status) {
                    projects.push({
                        name: file.replace('.md', '').replace(/-/g, ' '),
                        type: parsed.data.type || 'project',
                        progress: parsed.data.progress || 0,
                        priority: parsed.data.priority || 'medium',
                        created: parsed.data.created,
                        lastUpdated: parsed.data.last_updated,
                        deadline: parsed.data.deadline
                    });
                }
            }

            // Sort by priority (high > medium > low) and then by progress (lower first)
            projects.sort((a, b) => {
                const priorityOrder = { high: 3, medium: 2, low: 1 };
                if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
                    return priorityOrder[b.priority] - priorityOrder[a.priority];
                }
                return a.progress - b.progress;
            });

            return projects;

        } catch (error) {
            console.error('Error getting projects:', error);
            return [];
        }
    }

    generateProgressBar(percent, length = 10) {
        const filled = Math.round((percent / 100) * length);
        const empty = length - filled;
        return '█'.repeat(filled) + '░'.repeat(empty);
    }

    getStats() {
        const today = new Date().toDateString();
        const todayNudges = this.nudgeHistory.get(today) || [];

        return {
            enabled: this.config.enabled,
            nudgesToday: todayNudges.length,
            maxPerDay: this.config.maxNudgesPerDay,
            activeHours: `${this.config.startHour}:00 - ${this.config.endHour}:00`,
            isActiveNow: this.isActiveHour()
        };
    }
}