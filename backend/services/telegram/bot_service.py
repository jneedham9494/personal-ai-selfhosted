"""
Telegram bot service for Personal AI Assistant.

Provides a mobile-first interface via Telegram with conversation
management, Obsidian integration, and proactive nudging support.
"""

import os
import logging
from typing import Set

from .conversation import ConversationManager, Conversation
from .handlers import TelegramHandlers

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Service for Telegram bot integration."""

    def __init__(
        self,
        token: str = None,
        chat_id: str = None,
        llm_service=None,
        obsidian_service=None,
        claude_service=None
    ):
        """
        Initialize Telegram bot service.

        Args:
            token: Telegram bot token (defaults to env variable)
            chat_id: Authorized chat ID (defaults to env variable)
            llm_service: LLMService instance for Ollama
            obsidian_service: ObsidianService instance
            claude_service: ClaudeService instance (optional)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        if not self.token:
            logger.warning("No Telegram bot token - bot service disabled")
            self.enabled = False
            self.application = None
            return

        self.enabled = True
        self.llm_service = llm_service
        self.obsidian_service = obsidian_service
        self.claude_service = claude_service

        # Conversation management
        self.conversation_manager = ConversationManager()

        # Authorized users
        self.authorized_users: Set[int] = set()
        if self.chat_id:
            try:
                self.authorized_users.add(int(self.chat_id))
            except ValueError:
                pass

        # Bot application (initialized on start)
        self.application = None
        self.handlers = TelegramHandlers(self)

        # Use Claude if available, otherwise Ollama
        self.use_claude = claude_service is not None and claude_service.enabled

        logger.info(f"TelegramBotService initialized (Claude: {self.use_claude})")

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized."""
        return user_id in self.authorized_users

    async def start(self):
        """Start the Telegram bot with polling."""
        if not self.enabled:
            logger.warning("Telegram bot not started - missing token")
            return

        try:
            from telegram.ext import (
                Application,
                CommandHandler,
                MessageHandler,
                filters
            )

            self.application = (
                Application.builder()
                .token(self.token)
                .build()
            )

            # Register command handlers
            commands = [
                ("start", self.handlers.cmd_start),
                ("help", self.handlers.cmd_help),
                ("search", self.handlers.cmd_search),
                ("today", self.handlers.cmd_today),
                ("project", self.handlers.cmd_project),
                ("goal", self.handlers.cmd_goal),
                ("new", self.handlers.cmd_new),
                ("context", self.handlers.cmd_context),
                ("progress", self.handlers.cmd_progress),
                ("clear", self.handlers.cmd_clear),
                ("status", self.handlers.cmd_status),
            ]

            for cmd_name, handler in commands:
                self.application.add_handler(CommandHandler(cmd_name, handler))

            # Message handler
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.handlers.handle_message
                )
            )

            logger.info("Starting Telegram bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()

        except ImportError:
            logger.error("python-telegram-bot not installed")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            self.enabled = False

    async def stop(self):
        """Stop the Telegram bot gracefully."""
        if self.application:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

    async def generate_response(self, conversation: Conversation) -> str:
        """Generate AI response for conversation."""
        if self.use_claude and self.claude_service:
            result = await self.claude_service.generate_response(conversation.messages)
            if result['success']:
                return result['content']
            return f"Error: {result['error']}"
        elif self.llm_service:
            response_parts = []
            async for chunk in self.llm_service.generate_response(
                conversation.messages,
                stream=False
            ):
                response_parts.append(chunk)
            return "".join(response_parts)
        else:
            return "No LLM service available. Please configure Ollama or Claude."

    async def save_conversation(self, user_id: int):
        """Save conversation to Obsidian vault."""
        conversation = self.conversation_manager.conversations.get(user_id)
        if not conversation or not conversation.messages:
            return

        # TODO: Implement save to Obsidian using enhanced ObsidianService
        self.conversation_manager.mark_saved(user_id)
        logger.info(f"Saved conversation for user {user_id}")

    async def send_message(self, chat_id: int, text: str, parse_mode: str = 'Markdown'):
        """
        Send a message to a specific chat.

        Used by NudgingService to send proactive messages.

        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: 'Markdown' or 'HTML'
        """
        if not self.application:
            logger.warning("Cannot send message - bot not running")
            return

        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
