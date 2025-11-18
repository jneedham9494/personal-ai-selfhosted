"""
Obsidian vault integration package.
"""

from .service import ObsidianService
from .projects import ProjectManager
from .conversations import ConversationSaver
from .metadata import MetadataExtractor, generate_tags_from_content

__all__ = [
    'ObsidianService',
    'ProjectManager',
    'ConversationSaver',
    'MetadataExtractor',
    'generate_tags_from_content',
]
