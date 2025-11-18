"""
Core Obsidian service for vault operations.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any

from ..tools.file_tools import FileTools
from .projects import ProjectManager
from .conversations import ConversationSaver

logger = logging.getLogger(__name__)


class ObsidianService:
    """Service for interacting with Obsidian vault."""

    def __init__(self, vault_path: str = None, claude_service=None):
        """
        Initialize Obsidian service.

        Args:
            vault_path: Path to Obsidian vault (defaults to env variable)
            claude_service: Optional ClaudeService for AI features
        """
        default_path = '/Users/jackdev/obsidian-vault-local'

        self.vault_path = vault_path or os.getenv(
            'OBSIDIAN_VAULT_PATH',
            default_path
        )

        # Initialize components
        self.file_tools = FileTools(allowed_paths=[self.vault_path])
        self.project_manager = ProjectManager(self.vault_path)
        self.conversation_saver = ConversationSaver(
            self.vault_path,
            claude_service
        )

        logger.info(f"ObsidianService initialized with vault: {self.vault_path}")

    # ===== Search Operations =====

    async def search_vault(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search for notes in the vault.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            {'success': bool, 'results': List[Dict], 'count': int, 'error': str}
        """
        search_result = await self.file_tools.search_in_files(
            directory=self.vault_path,
            query=query,
            pattern="**/*.md"
        )

        if not search_result['success']:
            return {
                'success': False,
                'results': [],
                'count': 0,
                'error': search_result['error']
            }

        results = []
        for result in search_result['results'][:limit]:
            file_path = Path(result['file'])
            try:
                relative_path = file_path.relative_to(self.vault_path)
            except ValueError:
                relative_path = file_path.name

            results.append({
                'file': str(relative_path),
                'excerpt': result['line_content'][:200],
                'line_number': result['line_number']
            })

        return {
            'success': True,
            'results': results,
            'count': len(results),
            'error': None
        }

    # ===== File Operations =====

    async def read_note(self, note_path: str) -> Dict[str, Any]:
        """
        Read a specific note from the vault.

        Args:
            note_path: Relative path to note within vault

        Returns:
            {'success': bool, 'content': str, 'error': str}
        """
        full_path = os.path.join(self.vault_path, note_path)
        return await self.file_tools.read_file(full_path)

    async def list_all_notes(self) -> Dict[str, Any]:
        """
        Get list of all markdown notes in the vault.

        Returns:
            {'success': bool, 'notes': List[Dict], 'error': str}
        """
        try:
            vault_path = Path(self.vault_path)
            if not vault_path.exists():
                return {
                    'success': False,
                    'notes': [],
                    'error': f'Vault not found: {self.vault_path}'
                }

            md_files = list(vault_path.glob("**/*.md"))
            md_files.sort(key=lambda f: str(f))

            notes = []
            for file_path in md_files:
                try:
                    relative_path = file_path.relative_to(vault_path)
                    notes.append({
                        'path': str(relative_path),
                        'name': file_path.name,
                        'folder': str(relative_path.parent) if relative_path.parent != Path('.') else ''
                    })
                except ValueError:
                    continue

            return {
                'success': True,
                'notes': notes,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error listing all notes: {e}")
            return {
                'success': False,
                'notes': [],
                'error': str(e)
            }

    async def list_recent_notes(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get list of recently modified notes.

        Args:
            limit: Maximum number of notes to return

        Returns:
            {'success': bool, 'notes': List[str], 'error': str}
        """
        try:
            vault_path = Path(self.vault_path)
            if not vault_path.exists():
                return {
                    'success': False,
                    'notes': [],
                    'error': f'Vault not found: {self.vault_path}'
                }

            md_files = list(vault_path.glob("**/*.md"))
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            recent_notes = []
            for file_path in md_files[:limit]:
                try:
                    relative_path = file_path.relative_to(vault_path)
                    recent_notes.append(str(relative_path))
                except ValueError:
                    continue

            return {
                'success': True,
                'notes': recent_notes,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error listing recent notes: {e}")
            return {
                'success': False,
                'notes': [],
                'error': str(e)
            }

    # ===== Project/Goal Operations (delegated) =====

    async def create_project(self, name: str, description: str = "", priority: str = "medium"):
        """Create a new project."""
        return await self.project_manager.create_project(name, description, priority)

    async def create_goal(self, name: str, description: str = "", target_date: str = None, habit_tracking: bool = False):
        """Create a new goal."""
        return await self.project_manager.create_goal(name, description, target_date, habit_tracking)

    async def update_progress(self, name: str, progress: int, notes: str = ""):
        """Update progress for project/goal."""
        return await self.project_manager.update_progress(name, progress, notes)

    async def get_active_projects(self):
        """Get list of active projects and goals."""
        return await self.project_manager.get_active_projects()

    async def get_stalled_projects(self, days_threshold: int = 7):
        """Get projects not updated recently."""
        return await self.project_manager.get_stalled_projects(days_threshold)

    async def link_conversation_to_project(self, project_name: str, conversation_path: str):
        """Link conversation to project/goal."""
        return await self.project_manager.link_conversation(project_name, conversation_path)

    # ===== Conversation Operations (delegated) =====

    async def save_conversation(
        self,
        messages: List[Dict[str, str]],
        topic: str = "",
        context_type: str = None,
        context_name: str = "",
        platform: str = "telegram"
    ):
        """Save conversation to vault."""
        return await self.conversation_saver.save_conversation(
            messages, topic, context_type, context_name, platform
        )
