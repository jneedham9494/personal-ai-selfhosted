"""
Claude API service for Anthropic integration.

Provides an alternative LLM backend to Ollama with rate limiting
and conversation pattern analysis capabilities.
"""

import os
import time
import logging
from typing import List, Dict, Any
from collections import deque

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Anthropic's Claude API."""

    def __init__(
        self,
        api_key: str = None,
        model: str = "claude-3-haiku-20240307",
        max_requests_per_minute: int = 50
    ):
        """
        Initialize Claude service.

        Args:
            api_key: Anthropic API key (defaults to env variable)
            model: Claude model to use
            max_requests_per_minute: Rate limit for API calls

        Raises:
            ValueError: If API key not provided and not in environment
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key provided - Claude service disabled")
            self.client = None
            self.enabled = False
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.enabled = True
        except ImportError:
            logger.error("anthropic package not installed")
            self.client = None
            self.enabled = False
            return

        self.model = model
        self.max_requests_per_minute = max_requests_per_minute
        self.request_timestamps: deque = deque()

        self.system_prompt = """You are a personal AI assistant focused on productivity,
self-improvement, and knowledge management.

You have access to the user's Obsidian vault with their personal notes, goals,
habit tracking, and journal entries.

Key capabilities:
- Personal task and todo management
- Goal tracking and progress monitoring
- Habit tracking and streak monitoring
- Self-reflection and journaling prompts
- Search personal knowledge base
- Proactive nudges and reminders

Be supportive, encouraging, and help the user stay aligned with their personal
goals and self-improvement journey. Keep responses concise but helpful."""

        logger.info(f"ClaudeService initialized with model: {self.model}")

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        window_start = now - 60  # 1 minute window

        # Remove timestamps older than 1 minute
        while self.request_timestamps and self.request_timestamps[0] < window_start:
            self.request_timestamps.popleft()

        # Check if we're at the limit
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            return False

        # Record this request
        self.request_timestamps.append(now)
        return True

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response from Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            {
                'success': bool,
                'content': str,
                'usage': Dict,
                'error': str
            }
        """
        if not self.enabled:
            return {
                'success': False,
                'content': '',
                'usage': {},
                'error': 'Claude service not enabled (missing API key)'
            }

        if not self._check_rate_limit():
            return {
                'success': False,
                'content': '',
                'usage': {},
                'error': 'Rate limit exceeded (50 requests/minute)'
            }

        try:
            # Convert messages to Claude format
            claude_messages = self._format_messages(messages)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=claude_messages,
                temperature=temperature
            )

            content = response.content[0].text if response.content else ""

            return {
                'success': True,
                'content': content,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                },
                'error': None
            }

        except Exception as e:
            error_msg = self._handle_error(e)
            logger.error(f"Claude API error: {error_msg}")
            return {
                'success': False,
                'content': '',
                'usage': {},
                'error': error_msg
            }

    async def analyze_conversation_patterns(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Analyze conversation for mood, goals, and challenges.

        Uses lower temperature for more consistent analysis.

        Args:
            messages: Conversation messages to analyze

        Returns:
            {
                'success': bool,
                'analysis': {
                    'mood': str,
                    'energy': str,
                    'topics': List[str],
                    'goals': List[str],
                    'challenges': List[str]
                },
                'error': str
            }
        """
        if not self.enabled:
            return {
                'success': False,
                'analysis': {},
                'error': 'Claude service not enabled'
            }

        analysis_prompt = """Analyze this conversation and extract:
1. Mood (stressed, excited, neutral, focused, confused, reflective)
2. Energy level (high, medium, low)
3. Main topics discussed (list 2-3)
4. Goals mentioned (list any)
5. Challenges or blockers mentioned (list any)

Respond in this exact JSON format:
{
    "mood": "neutral",
    "energy": "medium",
    "topics": ["topic1", "topic2"],
    "goals": ["goal1"],
    "challenges": ["challenge1"]
}"""

        # Format conversation for analysis
        conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in messages[-10:]  # Last 10 messages
        ])

        try:
            response = await self.generate_response(
                messages=[{
                    'role': 'user',
                    'content': f"{analysis_prompt}\n\nConversation:\n{conversation_text}"
                }],
                max_tokens=500,
                temperature=0.3  # Lower for consistency
            )

            if not response['success']:
                return {
                    'success': False,
                    'analysis': {},
                    'error': response['error']
                }

            # Parse JSON response
            import json
            try:
                analysis = json.loads(response['content'])
            except json.JSONDecodeError:
                # Fallback to defaults if parsing fails
                analysis = {
                    'mood': 'neutral',
                    'energy': 'medium',
                    'topics': [],
                    'goals': [],
                    'challenges': []
                }

            return {
                'success': True,
                'analysis': analysis,
                'error': None
            }

        except Exception as e:
            logger.error(f"Conversation analysis error: {e}")
            return {
                'success': False,
                'analysis': {},
                'error': str(e)
            }

    async def generate_summary(self, conversation: List[Dict[str, str]]) -> str:
        """
        Generate a one-sentence summary of a conversation.

        Args:
            conversation: List of messages

        Returns:
            Summary string or empty string on failure
        """
        if not self.enabled or not conversation:
            return ""

        prompt = """Summarize this conversation in ONE concise sentence
(max 100 characters). Focus on the main topic or outcome.

Conversation:
"""
        conversation_text = "\n".join([
            f"{m['role']}: {m['content'][:200]}"
            for m in conversation[-6:]  # Last 6 messages
        ])

        response = await self.generate_response(
            messages=[{'role': 'user', 'content': prompt + conversation_text}],
            max_tokens=100,
            temperature=0.5
        )

        return response['content'][:150] if response['success'] else ""

    async def extract_key_insights(self, conversation: List[Dict[str, str]]) -> List[str]:
        """
        Extract key insights from a conversation.

        Args:
            conversation: List of messages

        Returns:
            List of insight strings
        """
        if not self.enabled or not conversation:
            return []

        prompt = """Extract 2-3 key insights or takeaways from this conversation.
Return as a simple bulleted list (- item).

Conversation:
"""
        conversation_text = "\n".join([
            f"{m['role']}: {m['content'][:300]}"
            for m in conversation[-8:]
        ])

        response = await self.generate_response(
            messages=[{'role': 'user', 'content': prompt + conversation_text}],
            max_tokens=300,
            temperature=0.5
        )

        if not response['success']:
            return []

        # Parse bullet points
        insights = []
        for line in response['content'].split('\n'):
            line = line.strip()
            if line.startswith('- '):
                insights.append(line[2:])
            elif line.startswith('* '):
                insights.append(line[2:])

        return insights[:3]  # Max 3 insights

    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Convert messages to Claude API format.

        Args:
            messages: List of {'role': str, 'content': str}

        Returns:
            Formatted messages for Claude API
        """
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            # Claude uses 'user' and 'assistant' roles
            if role not in ('user', 'assistant'):
                role = 'user'
            formatted.append({
                'role': role,
                'content': msg.get('content', '')
            })
        return formatted

    def _handle_error(self, error: Exception) -> str:
        """
        Convert exceptions to user-friendly error messages.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message
        """
        error_str = str(error)

        if '401' in error_str:
            return 'Invalid API key. Please check your ANTHROPIC_API_KEY.'
        elif '429' in error_str:
            return 'Rate limit exceeded. Please wait a moment and try again.'
        elif '500' in error_str or '503' in error_str:
            return 'Claude service temporarily unavailable. Please try again later.'
        else:
            return f'Claude API error: {error_str}'

    def check_health(self) -> bool:
        """
        Check if Claude service is accessible.

        Returns:
            True if service is healthy
        """
        if not self.enabled:
            return False

        try:
            # Simple test request
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{'role': 'user', 'content': 'test'}]
            )
            return True
        except Exception as e:
            logger.error(f"Claude health check failed: {e}")
            return False

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            {
                'requests_used': int,
                'requests_remaining': int,
                'window_reset_seconds': int
            }
        """
        now = time.time()
        window_start = now - 60

        # Clean old timestamps
        while self.request_timestamps and self.request_timestamps[0] < window_start:
            self.request_timestamps.popleft()

        used = len(self.request_timestamps)
        remaining = self.max_requests_per_minute - used

        # Calculate reset time
        if self.request_timestamps:
            oldest = self.request_timestamps[0]
            reset_seconds = int(60 - (now - oldest))
        else:
            reset_seconds = 0

        return {
            'requests_used': used,
            'requests_remaining': remaining,
            'window_reset_seconds': max(0, reset_seconds)
        }
