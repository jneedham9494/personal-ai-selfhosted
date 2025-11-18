import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from .tools.file_tools import FileTools

logger = logging.getLogger(__name__)

class ObsidianService:
    """Service for interacting with Obsidian vault"""

    def __init__(self, vault_path: str = None):
        """
        Initialize Obsidian service

        Args:
            vault_path: Path to Obsidian vault (defaults to env variable)
        """
        # Use local vault for now (iCloud has permissions issues)
        default_path = '/Users/jackdev/obsidian-vault-local'

        self.vault_path = vault_path or os.getenv(
            'OBSIDIAN_VAULT_PATH',
            default_path
        )

        # Initialize file tools with vault path as allowed path
        self.file_tools = FileTools(allowed_paths=[self.vault_path])

        logger.info(f"ObsidianService initialized with vault: {self.vault_path}")

    async def search_vault(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search for notes in the vault

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            {
                'success': bool,
                'results': List[Dict],  # Each with 'file', 'excerpt', 'line_number'
                'count': int,
                'error': str
            }
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

        # Format results and apply limit
        results = []
        for result in search_result['results'][:limit]:
            # Extract relative path from vault root
            file_path = Path(result['file'])
            try:
                relative_path = file_path.relative_to(self.vault_path)
            except ValueError:
                relative_path = file_path.name

            results.append({
                'file': str(relative_path),
                'excerpt': result['line_content'][:200],  # Limit excerpt length
                'line_number': result['line_number']
            })

        return {
            'success': True,
            'results': results,
            'count': len(results),
            'error': None
        }

    async def read_note(self, note_path: str) -> Dict[str, Any]:
        """
        Read a specific note from the vault

        Args:
            note_path: Relative path to note within vault

        Returns:
            {
                'success': bool,
                'content': str,
                'error': str
            }
        """
        full_path = os.path.join(self.vault_path, note_path)
        return await self.file_tools.read_file(full_path)

    async def list_all_notes(self) -> Dict[str, Any]:
        """
        Get list of all markdown notes in the vault

        Returns:
            {
                'success': bool,
                'notes': List[Dict],  # Each with 'path', 'name', 'folder'
                'error': str
            }
        """
        try:
            vault_path = Path(self.vault_path)
            if not vault_path.exists():
                return {
                    'success': False,
                    'notes': [],
                    'error': f'Vault not found: {self.vault_path}'
                }

            # Get all markdown files
            md_files = list(vault_path.glob("**/*.md"))

            # Sort alphabetically
            md_files.sort(key=lambda f: str(f))

            # Build structured list
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
        Get list of recently modified notes

        Args:
            limit: Maximum number of notes to return

        Returns:
            {
                'success': bool,
                'notes': List[str],
                'error': str
            }
        """
        try:
            vault_path = Path(self.vault_path)
            if not vault_path.exists():
                return {
                    'success': False,
                    'notes': [],
                    'error': f'Vault not found: {self.vault_path}'
                }

            # Get all markdown files
            md_files = list(vault_path.glob("**/*.md"))

            # Sort by modification time (most recent first)
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Get relative paths
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
