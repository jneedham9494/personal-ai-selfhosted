import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileTools:
    """File operation tools with security protections"""

    def __init__(self, allowed_paths: List[str] = None):
        """
        Initialize file tools with allowed paths

        Args:
            allowed_paths: List of absolute paths that are allowed for file operations
        """
        self.allowed_paths = [Path(p).resolve() for p in (allowed_paths or [])]

    def _is_path_allowed(self, file_path: str) -> bool:
        """
        Check if file path is within allowed paths (path traversal protection)

        Args:
            file_path: Path to check

        Returns:
            True if path is allowed, False otherwise
        """
        try:
            resolved_path = Path(file_path).resolve()

            # Check if path is within any allowed path
            for allowed_path in self.allowed_paths:
                try:
                    resolved_path.relative_to(allowed_path)
                    return True
                except ValueError:
                    continue

            logger.warning(f"Path not allowed: {file_path}")
            return False

        except Exception as e:
            logger.error(f"Error checking path: {e}")
            return False

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file contents

        Args:
            file_path: Path to file to read

        Returns:
            {
                'success': bool,
                'content': str,
                'error': str
            }
        """
        if not self._is_path_allowed(file_path):
            return {
                'success': False,
                'content': None,
                'error': 'Path not allowed'
            }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'success': True,
                'content': content,
                'error': None
            }

        except FileNotFoundError:
            return {
                'success': False,
                'content': None,
                'error': f'File not found: {file_path}'
            }
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                'success': False,
                'content': None,
                'error': str(e)
            }

    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to file

        Args:
            file_path: Path to file to write
            content: Content to write

        Returns:
            {
                'success': bool,
                'error': str
            }
        """
        if not self._is_path_allowed(file_path):
            return {
                'success': False,
                'error': 'Path not allowed'
            }

        try:
            # Create parent directories if they don't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def list_files(self, directory: str, pattern: str = "*.md") -> Dict[str, Any]:
        """
        List files in directory matching pattern

        Args:
            directory: Directory to search
            pattern: Glob pattern (default: *.md)

        Returns:
            {
                'success': bool,
                'files': List[str],
                'error': str
            }
        """
        if not self._is_path_allowed(directory):
            return {
                'success': False,
                'files': [],
                'error': 'Path not allowed'
            }

        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {
                    'success': False,
                    'files': [],
                    'error': f'Directory not found: {directory}'
                }

            files = [str(f) for f in dir_path.glob(pattern)]

            return {
                'success': True,
                'files': files,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return {
                'success': False,
                'files': [],
                'error': str(e)
            }

    async def search_in_files(
        self,
        directory: str,
        query: str,
        pattern: str = "**/*.md"
    ) -> Dict[str, Any]:
        """
        Search for query in files

        Args:
            directory: Directory to search
            query: Search query
            pattern: Glob pattern (default: **/*.md for recursive search)

        Returns:
            {
                'success': bool,
                'results': List[Dict],  # Each result has 'file', 'line_number', 'line_content'
                'error': str
            }
        """
        if not self._is_path_allowed(directory):
            return {
                'success': False,
                'results': [],
                'error': 'Path not allowed'
            }

        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {
                    'success': False,
                    'results': [],
                    'error': f'Directory not found: {directory}'
                }

            results = []
            query_lower = query.lower()

            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if query_lower in line.lower():
                                    results.append({
                                        'file': str(file_path),
                                        'line_number': line_num,
                                        'line_content': line.strip()
                                    })
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue

            return {
                'success': True,
                'results': results,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error searching in {directory}: {e}")
            return {
                'success': False,
                'results': [],
                'error': str(e)
            }
