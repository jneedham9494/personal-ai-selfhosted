"""
Proactive nudging service for Personal AI Assistant.

Sends scheduled reminders, check-ins, and progress updates
via Telegram based on user activity and goals.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class NudgingService:
    """Service for proactive nudging and reminders."""

    # Nudge type priorities
    PRIORITY_HIGH = 3
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 1

    def __init__(
        self,
        telegram_bot=None,
        obsidian_service=None,
        chat_id: str = None,
        enabled: bool = True,
        start_hour: int = 8,
        end_hour: int = 22,
        max_nudges_per_day: int = 5
    ):
        """
        Initialize nudging service.

        Args:
            telegram_bot: TelegramBotService for sending messages
            obsidian_service: ObsidianService for project data
            chat_id: Target Telegram chat ID
            enabled: Whether nudging is enabled
            start_hour: Start of active hours (0-23)
            end_hour: End of active hours (0-23)
            max_nudges_per_day: Maximum nudges per day
        """
        self.telegram_bot = telegram_bot
        self.obsidian_service = obsidian_service
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = enabled and bool(self.chat_id)

        self.start_hour = start_hour
        self.end_hour = end_hour
        self.max_nudges_per_day = max_nudges_per_day

        # Track nudges sent today
        self.nudge_history: Dict[str, List[datetime]] = defaultdict(list)
        self.nudges_sent_today = 0
        self.last_reset_date = datetime.now().date()

        # Scheduler (initialized on start)
        self.scheduler = None

        if self.enabled:
            logger.info(f"NudgingService initialized (active {start_hour}:00-{end_hour}:00)")
        else:
            logger.warning("NudgingService disabled (missing chat_id or explicitly disabled)")

    async def start(self):
        """Start the nudging scheduler."""
        if not self.enabled:
            return

        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger

            self.scheduler = AsyncIOScheduler()

            # Morning motivation - 9 AM daily
            self.scheduler.add_job(
                self._morning_motivation,
                CronTrigger(hour=9, minute=0),
                id='morning_motivation'
            )

            # Afternoon check-in - 2 PM daily
            self.scheduler.add_job(
                self._afternoon_checkin,
                CronTrigger(hour=14, minute=0),
                id='afternoon_checkin'
            )

            # Evening reflection - 7 PM daily
            self.scheduler.add_job(
                self._evening_reflection,
                CronTrigger(hour=19, minute=0),
                id='evening_reflection'
            )

            # Weekly review - Sunday 6 PM
            self.scheduler.add_job(
                self._weekly_review,
                CronTrigger(day_of_week='sun', hour=18, minute=0),
                id='weekly_review'
            )

            # Mid-week stalled check - Wednesday 10 AM
            self.scheduler.add_job(
                self._midweek_stalled_check,
                CronTrigger(day_of_week='wed', hour=10, minute=0),
                id='midweek_stalled'
            )

            self.scheduler.start()
            logger.info("Nudging scheduler started with 5 scheduled jobs")

        except ImportError:
            logger.error("APScheduler not installed - nudging disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to start nudging scheduler: {e}")
            self.enabled = False

    async def stop(self):
        """Stop the nudging scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Nudging scheduler stopped")

    def _is_within_active_hours(self) -> bool:
        """Check if current time is within active hours."""
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour < self.end_hour

    def _can_send_nudge(self, nudge_type: str) -> bool:
        """Check if we can send a nudge of this type."""
        # Reset daily counter if needed
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.nudges_sent_today = 0
            self.nudge_history.clear()
            self.last_reset_date = today

        # Check daily limit
        if self.nudges_sent_today >= self.max_nudges_per_day:
            return False

        # Check active hours
        if not self._is_within_active_hours():
            return False

        # Check same-type throttle (2 hours)
        if nudge_type in self.nudge_history:
            last_time = self.nudge_history[nudge_type][-1] if self.nudge_history[nudge_type] else None
            if last_time and (datetime.now() - last_time) < timedelta(hours=2):
                return False

        return True

    async def _send_nudge(self, message: str, nudge_type: str):
        """Send a nudge message via Telegram."""
        if not self._can_send_nudge(nudge_type):
            logger.debug(f"Skipping nudge {nudge_type} (throttled or limit reached)")
            return

        if not self.telegram_bot or not self.chat_id:
            logger.warning("Cannot send nudge - no telegram bot or chat_id")
            return

        try:
            await self.telegram_bot.send_message(
                int(self.chat_id),
                message,
                parse_mode='Markdown'
            )

            # Record nudge
            self.nudge_history[nudge_type].append(datetime.now())
            self.nudges_sent_today += 1
            logger.info(f"Sent nudge: {nudge_type}")

        except Exception as e:
            logger.error(f"Failed to send nudge: {e}")

    # ===== Scheduled Nudge Handlers =====

    async def _morning_motivation(self):
        """Send morning motivation nudge."""
        messages = [
            "Good morning! What's the ONE thing that would make today a win?",
            "Rise and shine! Ready to make progress on your goals today?",
            "New day, new opportunities. What are you focusing on today?",
        ]

        import random
        message = f"🌅 {random.choice(messages)}"
        await self._send_nudge(message, 'morning')

    async def _afternoon_checkin(self):
        """Send afternoon check-in nudge."""
        messages = [
            "Afternoon check-in: How's your day going so far?",
            "Quick check: Making progress on today's priorities?",
            "Mid-day pulse check. Need to adjust any plans?",
        ]

        import random
        message = f"☀️ {random.choice(messages)}"
        await self._send_nudge(message, 'afternoon')

    async def _evening_reflection(self):
        """Send evening reflection nudge."""
        messages = [
            "Day's wrapping up. What did you accomplish today?",
            "Evening reflection: What went well today? What could be better?",
            "Time to wind down. What are you grateful for today?",
        ]

        import random
        message = f"🌙 {random.choice(messages)}"
        await self._send_nudge(message, 'evening')

    async def _weekly_review(self):
        """Send weekly review with project progress."""
        if not self.obsidian_service:
            return

        try:
            projects = await self.obsidian_service.get_active_projects()

            if not projects:
                message = "📅 **Weekly Review**\n\nNo active projects. Time to set some goals?"
            else:
                message = "📅 **Weekly Review**\n\n"

                # Group by type
                goals = [p for p in projects if p['type'] == 'goal']
                project_list = [p for p in projects if p['type'] == 'project']

                if goals:
                    message += "**Goals:**\n"
                    for g in goals[:5]:
                        progress_bar = self._progress_bar(g['progress'])
                        message += f"• {g['name']}: {progress_bar} {g['progress']}%\n"
                    message += "\n"

                if project_list:
                    message += "**Projects:**\n"
                    for p in project_list[:5]:
                        progress_bar = self._progress_bar(p['progress'])
                        message += f"• {p['name']}: {progress_bar} {p['progress']}%\n"

                message += "\nHow did this week go? What's the focus for next week?"

            await self._send_nudge(message, 'weekly')

        except Exception as e:
            logger.error(f"Weekly review failed: {e}")

    async def _midweek_stalled_check(self):
        """Check for stalled projects mid-week."""
        if not self.obsidian_service:
            return

        try:
            stalled = await self.obsidian_service.get_stalled_projects(days_threshold=7)

            if not stalled:
                return  # No nudge needed

            message = "⚠️ **Stalled Projects Alert**\n\n"
            message += "These haven't been updated in 7+ days:\n\n"

            for p in stalled[:5]:
                message += f"• {p['name']} ({p['progress']}%)\n"

            message += "\nNeed to reprioritize or make some progress?"

            await self._send_nudge(message, 'stalled')

        except Exception as e:
            logger.error(f"Stalled check failed: {e}")

    def _progress_bar(self, progress: int, width: int = 10) -> str:
        """Generate a visual progress bar."""
        filled = int(progress / 100 * width)
        empty = width - filled
        return '█' * filled + '░' * empty

    # ===== Public Methods =====

    def get_status(self) -> Dict[str, Any]:
        """Get current nudging status."""
        return {
            'enabled': self.enabled,
            'nudges_sent_today': self.nudges_sent_today,
            'max_per_day': self.max_nudges_per_day,
            'active_hours': f"{self.start_hour}:00-{self.end_hour}:00",
            'within_active_hours': self._is_within_active_hours(),
            'scheduler_running': self.scheduler is not None and self.scheduler.running if self.scheduler else False
        }

    async def send_custom_nudge(self, message: str):
        """Send a custom nudge message."""
        await self._send_nudge(message, 'custom')
