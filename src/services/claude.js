import Anthropic from '@anthropic-ai/sdk';

export class ClaudeService {
    constructor(apiKey) {
        if (!apiKey || apiKey === 'your_claude_api_key_here') {
            console.log('⚠️ Claude API key not configured - bot will work without AI responses');
            this.client = null;
            return;
        }

        this.client = new Anthropic({
            apiKey: apiKey,
        });
        
        this.rateLimiter = {
            requests: [],
            maxPerMinute: 50 // Conservative rate limit
        };

        console.log('✅ Claude API service initialized');
    }

    async generateResponse(messages, options = {}) {
        if (!this.client) {
            throw new Error('Claude API not configured');
        }

        // Check rate limit
        if (!this.checkRateLimit()) {
            throw new Error('Rate limit exceeded - please wait a moment');
        }

        try {
            // Convert messages to Claude format
            const claudeMessages = this.formatMessagesForClaude(messages);
            
            const response = await this.client.messages.create({
                model: options.model || 'claude-3-haiku-20240307', // Using Haiku for speed/cost
                max_tokens: options.maxTokens || 1000,
                temperature: options.temperature || 0.7,
                system: options.systemPrompt || this.getDefaultSystemPrompt(),
                messages: claudeMessages
            });

            const responseText = response.content[0].text;
            
            // Track request for rate limiting
            this.trackRequest();
            
            console.log(`🤖 Claude response generated (${responseText.length} chars)`);
            return responseText;

        } catch (error) {
            console.error('Claude API error:', error);
            
            if (error.status === 429) {
                throw new Error('Rate limit exceeded - please try again in a moment');
            } else if (error.status === 401) {
                throw new Error('Invalid API key - please check your Claude API configuration');
            } else {
                throw new Error('Claude API temporarily unavailable');
            }
        }
    }

    formatMessagesForClaude(messages) {
        // Convert our message format to Claude's expected format
        return messages
            .filter(msg => msg.role === 'user' || msg.role === 'assistant')
            .map(msg => ({
                role: msg.role,
                content: msg.content
            }));
    }

    getDefaultSystemPrompt() {
        return `You are a helpful personal AI assistant integrated with the user's Obsidian knowledge base. 

Key behaviors:
- Be concise but helpful in your responses
- All conversations are automatically saved to the user's Obsidian vault
- You can reference that conversations are being saved for future reference
- Be proactive in suggesting ways to organize or connect information
- Use a friendly, personal tone since this is a private assistant
- When appropriate, suggest creating notes, reminders, or action items

Remember: This is a personal assistant for private use, so be more casual and helpful than a general AI.`;
    }

    checkRateLimit() {
        const now = Date.now();
        const oneMinuteAgo = now - 60000;
        
        // Remove old requests
        this.rateLimiter.requests = this.rateLimiter.requests.filter(time => time > oneMinuteAgo);
        
        return this.rateLimiter.requests.length < this.rateLimiter.maxPerMinute;
    }

    trackRequest() {
        this.rateLimiter.requests.push(Date.now());
    }

    // Method for analyzing conversations for patterns (for nudging system)
    async analyzeConversationPatterns(conversationHistory, analysisType = 'mood') {
        if (!this.client) {
            return null;
        }

        try {
            const analysisPrompt = this.getAnalysisPrompt(analysisType);
            
            const response = await this.client.messages.create({
                model: 'claude-3-haiku-20240307',
                max_tokens: 300,
                temperature: 0.3,
                system: analysisPrompt,
                messages: [
                    {
                        role: 'user',
                        content: `Analyze this conversation history:\n\n${conversationHistory}`
                    }
                ]
            });

            return response.content[0].text;

        } catch (error) {
            console.error('Analysis error:', error);
            return null;
        }
    }

    getAnalysisPrompt(type) {
        const prompts = {
            mood: 'Analyze the mood and energy level in this conversation. Return a brief assessment of whether the person seems stressed, energetic, focused, or needs support.',
            goals: 'Identify any goals, commitments, or action items mentioned in this conversation. Return a list of things the person wants to accomplish.',
            patterns: 'Look for patterns in topics, time of day, or recurring themes in this conversation. Identify anything that might be useful for personalized suggestions.'
        };

        return prompts[type] || prompts.mood;
    }

    getUsageStats() {
        return {
            configured: !!this.client,
            recentRequests: this.rateLimiter.requests.length,
            rateLimitRemaining: this.rateLimiter.maxPerMinute - this.rateLimiter.requests.length
        };
    }
}