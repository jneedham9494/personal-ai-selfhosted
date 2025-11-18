"""
Conversation saving for Obsidian vault.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import frontmatter

from .metadata import MetadataExtractor

logger = logging.getLogger(__name__)


class ConversationSaver:
    """Saves AI conversations to Obsidian vault."""

    def __init__(self, vault_path: str, claude_service=None):
        """
        Initialize conversation saver.

        Args:
            vault_path: Path to Obsidian vault
            claude_service: Optional ClaudeService for AI summaries
        """
        self.vault_path = Path(vault_path)
        self.claude_service = claude_service
        self.metadata_extractor = MetadataExtractor()

        # Ensure folders exist
        self.conversations_folder = self.vault_path / "AI-Conversations"
        self.daily_notes_folder = self.vault_path / "Daily-Notes"

        self.conversations_folder.mkdir(parents=True, exist_ok=True)
        self.daily_notes_folder.mkdir(parents=True, exist_ok=True)

    async def save_conversation(
        self,
        messages: List[Dict[str, str]],
        topic: str = "",
        context_type: Optional[str] = None,
        context_name: str = "",
        platform: str = "telegram"
    ) -> Dict[str, Any]:
        """
        Save a conversation to the vault.

        Args:
            messages: List of {'role': str, 'content': str}
            topic: Conversation topic (auto-detected if empty)
            context_type: 'project' or 'goal' or None
            context_name: Name of project/goal
            platform: Source platform (telegram, web)

        Returns:
            {'success': bool, 'path': str, 'error': str}
        """
        if not messages:
            return {
                'success': False,
                'path': '',
                'error': 'No messages to save'
            }

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            topic_slug = self._slugify(topic or self._extract_topic(messages))
            filename = f"{timestamp}-{topic_slug}.md"
            file_path = self.conversations_folder / filename

            # Extract metadata
            full_text = "\n".join([m['content'] for m in messages])
            metadata = self.metadata_extractor.extract_all(full_text)

            # Generate AI summary if available
            summary = await self._generate_summary(messages)
            key_insights = await self._generate_insights(messages)

            # Build frontmatter
            fm_data = {
                'type': 'ai-conversation',
                'date': datetime.now().isoformat(),
                'platform': platform,
                'topic': topic or topic_slug,
                'category': metadata['category'],
                'mood': metadata['mood'],
                'priority': metadata['priority'],
                'tags': metadata['tags'],
                'summary': summary,
                'action_items': metadata['action_items'],
                'key_insights': key_insights,
            }

            # Add project/goal context
            if context_type and context_name:
                fm_data['related_projects'] = [context_name]
                fm_data['context_type'] = context_type

            # Format conversation content
            content = self._format_conversation(messages)

            # Create post
            post = frontmatter.Post(content)
            post.metadata = fm_data

            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))

            # Link to daily note
            await self._link_to_daily_note(file_path.name, topic or topic_slug)

            logger.info(f"Saved conversation: {filename}")
            return {
                'success': True,
                'path': str(file_path.relative_to(self.vault_path)),
                'error': None
            }

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return {
                'success': False,
                'path': '',
                'error': str(e)
            }

    async def _generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """Generate AI summary of conversation."""
        if not self.claude_service or not self.claude_service.enabled:
            # Fallback: use first user message
            for msg in messages:
                if msg['role'] == 'user':
                    return msg['content'][:100] + "..."
            return ""

        return await self.claude_service.generate_summary(messages)

    async def _generate_insights(self, messages: List[Dict[str, str]]) -> List[str]:
        """Generate key insights from conversation."""
        if not self.claude_service or not self.claude_service.enabled:
            return []

        return await self.claude_service.extract_key_insights(messages)

    async def _link_to_daily_note(self, conversation_file: str, topic: str):
        """Add link to conversation in today's daily note."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_note_path = self.daily_notes_folder / f"{today}.md"

        link = f"- [[AI-Conversations/{conversation_file}|{topic}]]"

        try:
            if daily_note_path.exists():
                post = frontmatter.load(daily_note_path)

                # Add to AI Conversations section
                if '## AI Conversations' in post.content:
                    post.content = post.content.replace(
                        '## AI Conversations\n',
                        f'## AI Conversations\n{link}\n'
                    )
                else:
                    post.content += f"\n\n## AI Conversations\n{link}\n"

                with open(daily_note_path, 'w', encoding='utf-8') as f:
                    f.write(frontmatter.dumps(post))
            else:
                # Create daily note
                content = self._get_daily_note_template(today, link)
                with open(daily_note_path, 'w', encoding='utf-8') as f:
                    f.write(content)

        except Exception as e:
            logger.warning(f"Failed to link to daily note: {e}")

    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format messages as markdown conversation."""
        lines = ["## Conversation\n"]

        for msg in messages:
            role = msg['role'].title()
            content = msg['content']

            if role == 'User':
                lines.append(f"**{role}:** {content}\n")
            else:
                lines.append(f"**{role}:**\n{content}\n")

        return "\n".join(lines)

    def _extract_topic(self, messages: List[Dict[str, str]]) -> str:
        """Extract topic from first user message."""
        for msg in messages:
            if msg['role'] == 'user':
                # Take first 50 chars, clean up
                topic = msg['content'][:50].strip()
                topic = topic.split('\n')[0]  # First line only
                return topic if topic else "conversation"
        return "conversation"

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        # Lowercase and replace spaces
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = slug[:50]  # Limit length
        return slug.strip('-') or 'conversation'

    def _get_daily_note_template(self, date: str, initial_link: str) -> str:
        """Generate daily note template."""
        return f"""---
date: {date}
type: daily-note
tags: [daily]
---

# {date}

## Goals for Today

- [ ] Define daily goals

## Completed

-

## Reflections

## AI Conversations
{initial_link}

"""
