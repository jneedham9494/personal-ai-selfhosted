"""
Telegram bot command and message handlers.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramHandlers:
    """Command and message handlers for Telegram bot."""

    def __init__(self, bot_service):
        """
        Initialize handlers with reference to bot service.

        Args:
            bot_service: TelegramBotService instance
        """
        self.bot = bot_service

    async def cmd_start(self, update, context):
        """Handle /start command - authorize user and show welcome."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "there"

        self.bot.authorized_users.add(user_id)

        welcome = f"""Welcome, {username}!

I'm your personal AI assistant with access to your Obsidian vault.

**Getting Started:**
- Just send me a message to start chatting
- Use /help to see all commands
- Use /search <query> to search your vault
- Use /project or /goal to set conversation context

I'll help you stay productive and aligned with your goals!"""

        await update.message.reply_text(welcome, parse_mode='Markdown')
        logger.info(f"User {user_id} authorized via /start")

    async def cmd_help(self, update, context):
        """Handle /help command - show available commands."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        help_text = """**Available Commands:**

**Conversation:**
/new - Start a fresh conversation
/context - Show current conversation state
/clear - Clear conversation context

**Knowledge Base:**
/search <query> - Search your Obsidian vault
/today - View today's daily note

**Projects & Goals:**
/project <name> - Create or switch to a project
/goal <name> - Create or switch to a goal
/progress <0-100> - Update progress percentage

**System:**
/status - Show system status
/help - Show this message

Just send a regular message to chat with AI!"""

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def cmd_search(self, update, context):
        """Handle /search command - search Obsidian vault."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        if not context.args:
            await update.message.reply_text("Usage: /search <query>")
            return

        if not self.bot.obsidian_service:
            await update.message.reply_text("Obsidian service not available.")
            return

        query = " ".join(context.args)
        result = await self.bot.obsidian_service.search_vault(query, limit=5)

        if not result['success']:
            await update.message.reply_text(f"Search error: {result['error']}")
            return

        if not result['results']:
            await update.message.reply_text(f"No results found for: {query}")
            return

        response = f"**Search results for '{query}':**\n\n"
        for i, item in enumerate(result['results'], 1):
            excerpt = item['excerpt'][:100] + "..." if len(item['excerpt']) > 100 else item['excerpt']
            response += f"{i}. **{item['file']}**\n   {excerpt}\n\n"

        await update.message.reply_text(response, parse_mode='Markdown')

    async def cmd_today(self, update, context):
        """Handle /today command - show today's daily note."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        if not self.bot.obsidian_service:
            await update.message.reply_text("Obsidian service not available.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        note_path = f"Daily-Notes/{today}.md"
        result = await self.bot.obsidian_service.read_note(note_path)

        if not result['success']:
            await update.message.reply_text(
                f"No daily note for today yet.\nCreate one at: `{note_path}`",
                parse_mode='Markdown'
            )
            return

        content = result['content']
        if len(content) > 3000:
            content = content[:3000] + "\n\n...(truncated)"

        await update.message.reply_text(
            f"**Daily Note - {today}**\n\n{content}",
            parse_mode='Markdown'
        )

    async def cmd_project(self, update, context):
        """Handle /project command - create or switch to project context."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /project <name>\n\nExample: /project Website Redesign"
            )
            return

        project_name = " ".join(context.args)
        conversation = self.bot.conversation_manager.get(update.effective_user.id)
        conversation.context_type = "project"
        conversation.context_name = project_name

        await update.message.reply_text(
            f"Project context set to: **{project_name}**\n\n"
            f"All messages will be linked to this project.",
            parse_mode='Markdown'
        )

    async def cmd_goal(self, update, context):
        """Handle /goal command - create or switch to goal context."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /goal <name>\n\nExample: /goal Learn Japanese N3"
            )
            return

        goal_name = " ".join(context.args)
        conversation = self.bot.conversation_manager.get(update.effective_user.id)
        conversation.context_type = "goal"
        conversation.context_name = goal_name

        await update.message.reply_text(
            f"Goal context set to: **{goal_name}**\n\n"
            f"All messages will be linked to this goal.",
            parse_mode='Markdown'
        )

    async def cmd_new(self, update, context):
        """Handle /new command - start fresh conversation."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        user_id = update.effective_user.id
        self.bot.conversation_manager.reset(user_id)

        await update.message.reply_text(
            "Started a new conversation.\n\nPrevious conversation saved to Obsidian."
        )

    async def cmd_context(self, update, context):
        """Handle /context command - show current conversation state."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        conversation = self.bot.conversation_manager.get(update.effective_user.id)
        duration = datetime.now() - conversation.start_time
        minutes = int(duration.total_seconds() / 60)

        context_info = f"""**Current Conversation Context:**

Messages: {len(conversation.messages)}
Duration: {minutes} minutes
Topic: {conversation.topic or '(auto-detected)'}
"""

        if conversation.context_type:
            context_info += f"\n{conversation.context_type.title()}: {conversation.context_name}"
        else:
            context_info += "\nNo project/goal context set."

        await update.message.reply_text(context_info, parse_mode='Markdown')

    async def cmd_progress(self, update, context):
        """Handle /progress command - update project/goal progress."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        conversation = self.bot.conversation_manager.get(update.effective_user.id)

        if not conversation.context_type:
            await update.message.reply_text(
                "No project or goal context set.\nUse /project or /goal first."
            )
            return

        if not context.args:
            await update.message.reply_text("Usage: /progress <0-100>")
            return

        try:
            progress = int(context.args[0])
            if not 0 <= progress <= 100:
                raise ValueError("Out of range")
        except ValueError:
            await update.message.reply_text("Progress must be a number from 0 to 100.")
            return

        await update.message.reply_text(
            f"Updated {conversation.context_type} "
            f"'{conversation.context_name}' to {progress}% complete."
        )

    async def cmd_clear(self, update, context):
        """Handle /clear command - clear conversation context."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        conversation = self.bot.conversation_manager.get(update.effective_user.id)
        conversation.context_type = None
        conversation.context_name = ""
        conversation.topic = ""

        await update.message.reply_text("Conversation context cleared.")

    async def cmd_status(self, update, context):
        """Handle /status command - show system status."""
        if not self.bot.is_authorized(update.effective_user.id):
            await update.message.reply_text("Please /start first.")
            return

        status_parts = ["**System Status:**\n"]
        status_parts.append("Telegram Bot: Online")

        if self.bot.llm_service:
            healthy = self.bot.llm_service.check_health()
            status_parts.append(f"Ollama: {'Online' if healthy else 'Offline'}")
        else:
            status_parts.append("Ollama: Not configured")

        if self.bot.claude_service and self.bot.claude_service.enabled:
            rate_status = self.bot.claude_service.get_rate_limit_status()
            status_parts.append(
                f"Claude: Online ({rate_status['requests_remaining']} req remaining)"
            )
        else:
            status_parts.append("Claude: Not configured")

        if self.bot.obsidian_service:
            status_parts.append(f"Obsidian: {self.bot.obsidian_service.vault_path}")
        else:
            status_parts.append("Obsidian: Not configured")

        mode = "Claude" if self.bot.use_claude else "Ollama"
        status_parts.append(f"\nActive LLM: {mode}")

        await update.message.reply_text("\n".join(status_parts), parse_mode='Markdown')

    async def handle_message(self, update, context):
        """Handle regular text messages - AI conversation."""
        user_id = update.effective_user.id

        if not self.bot.is_authorized(user_id):
            await update.message.reply_text("Please /start first.")
            return

        user_message = update.message.text
        conversation = self.bot.conversation_manager.get(user_id)

        conversation.messages.append({'role': 'user', 'content': user_message})
        conversation.message_count_since_save += 1

        try:
            response = await self.bot.generate_response(conversation)

            conversation.messages.append({'role': 'assistant', 'content': response})
            conversation.message_count_since_save += 1

            await update.message.reply_text(response)

            if self.bot.conversation_manager.should_auto_save(user_id):
                await self.bot.save_conversation(user_id)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            await update.message.reply_text(f"Error generating response: {str(e)}")
