"""
Conversation state management for Telegram bot.
"""

from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, field


@dataclass
class Conversation:
    """Represents an active conversation state."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    topic: str = ""
    context_type: Optional[str] = None  # 'project' or 'goal'
    context_name: str = ""
    last_save_time: Optional[datetime] = None
    message_count_since_save: int = 0


class ConversationManager:
    """Manages conversation state for multiple users."""

    # Auto-save thresholds
    AUTO_SAVE_MESSAGE_COUNT = 4
    AUTO_SAVE_INTERVAL_MINUTES = 5

    def __init__(self):
        self.conversations: Dict[int, Conversation] = {}

    def get(self, user_id: int) -> Conversation:
        """Get or create conversation for user."""
        if user_id not in self.conversations:
            self.conversations[user_id] = Conversation()
        return self.conversations[user_id]

    def reset(self, user_id: int) -> None:
        """Reset conversation for user."""
        self.conversations[user_id] = Conversation()

    def should_auto_save(self, user_id: int) -> bool:
        """Check if conversation should be auto-saved."""
        conversation = self.conversations.get(user_id)
        if not conversation:
            return False

        # Check message count
        if conversation.message_count_since_save >= self.AUTO_SAVE_MESSAGE_COUNT:
            return True

        # Check time since last save
        if conversation.last_save_time:
            elapsed = datetime.now() - conversation.last_save_time
            if elapsed.total_seconds() / 60 >= self.AUTO_SAVE_INTERVAL_MINUTES:
                return True

        return False

    def mark_saved(self, user_id: int) -> None:
        """Mark conversation as saved."""
        conversation = self.conversations.get(user_id)
        if conversation:
            conversation.last_save_time = datetime.now()
            conversation.message_count_since_save = 0
