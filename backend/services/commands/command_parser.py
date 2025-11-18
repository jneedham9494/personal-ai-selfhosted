import re
import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CommandParser:
    """Parse and execute slash commands similar to Claude Code"""

    def __init__(self, commands_dir: str = ".ai/commands", obsidian_service=None):
        self.commands_dir = Path(commands_dir)
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.obsidian_service = obsidian_service
        self.load_commands()

    def load_commands(self):
        """Load command definitions from .ai/commands/ directory"""
        if not self.commands_dir.exists():
            logger.warning(f"Commands directory not found: {self.commands_dir}")
            return

        for command_file in self.commands_dir.glob("*.json"):
            try:
                with open(command_file, 'r') as f:
                    command_def = json.load(f)
                    command_name = command_def.get('name')
                    if command_name:
                        self.commands[command_name] = command_def
                        logger.info(f"Loaded command: {command_name}")
            except Exception as e:
                logger.error(f"Error loading command from {command_file}: {e}")

    def is_command(self, message: str) -> bool:
        """Check if message starts with a slash command"""
        return message.strip().startswith('/')

    def parse(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse a slash command from a message

        Returns:
            {
                'command': str,  # command name without /
                'args': str,     # arguments string
                'definition': dict  # command definition if found
            }
        """
        if not self.is_command(message):
            return None

        # Extract command and arguments
        # Format: /command [arguments]
        match = re.match(r'^/(\w+)(?:\s+(.*))?$', message.strip())
        if not match:
            return None

        command_name = match.group(1)
        args = match.group(2) or ""

        return {
            'command': command_name,
            'args': args.strip(),
            'definition': self.commands.get(command_name)
        }

    async def execute(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a parsed command

        Returns:
            {
                'success': bool,
                'message': str,
                'data': any
            }
        """
        command_name = parsed_command['command']
        definition = parsed_command['definition']

        if not definition:
            return {
                'success': False,
                'message': f"Unknown command: /{command_name}",
                'data': None
            }

        # Special handling for /help command
        if command_name == 'help':
            args = parsed_command['args']
            if args:
                # Show help for specific command
                target_cmd = self.commands.get(args)
                if target_cmd:
                    return {
                        'success': True,
                        'message': 'help_specific',
                        'data': {
                            'command': args,
                            'definition': target_cmd
                        }
                    }
                else:
                    return {
                        'success': False,
                        'message': f"Command not found: /{args}",
                        'data': None
                    }
            else:
                # Show all commands
                return {
                    'success': True,
                    'message': 'help_all',
                    'data': {
                        'commands': self.get_available_commands()
                    }
                }

        # Handle /search command
        if command_name == 'search' and self.obsidian_service:
            query = parsed_command['args']
            if not query:
                return {
                    'success': False,
                    'message': 'Search query is required',
                    'data': None
                }

            search_result = await self.obsidian_service.search_vault(query)

            if search_result['success']:
                return {
                    'success': True,
                    'message': 'search_results',
                    'data': search_result
                }
            else:
                return {
                    'success': False,
                    'message': search_result['error'],
                    'data': None
                }

        # For now, return command info
        # In future, this will actually execute the command handler
        return {
            'success': True,
            'message': f"Command /{command_name} recognized",
            'data': {
                'command': command_name,
                'description': definition.get('description'),
                'args': parsed_command['args']
            }
        }

    def get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available commands"""
        return [
            {
                'name': name,
                'description': definition.get('description'),
                'syntax': definition.get('syntax')
            }
            for name, definition in self.commands.items()
        ]
