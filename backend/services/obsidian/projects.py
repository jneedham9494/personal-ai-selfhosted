"""
Project and goal management for Obsidian vault.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import frontmatter

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages projects and goals in Obsidian vault."""

    def __init__(self, vault_path: str):
        """
        Initialize project manager.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.projects_folder = self.vault_path / "Projects"

        # Ensure folders exist
        self.projects_folder.mkdir(parents=True, exist_ok=True)

    async def create_project(
        self,
        name: str,
        description: str = "",
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Create a new project file.

        Args:
            name: Project name
            description: Project description
            priority: Priority level (high/medium/low)

        Returns:
            {'success': bool, 'path': str, 'error': str}
        """
        filename = self._sanitize_filename(name)
        file_path = self.projects_folder / f"{filename}.md"

        if file_path.exists():
            return {
                'success': False,
                'path': str(file_path),
                'error': f'Project "{name}" already exists'
            }

        try:
            content = self._get_project_template(name, description, priority)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Created project: {name}")
            return {
                'success': True,
                'path': str(file_path.relative_to(self.vault_path)),
                'error': None
            }

        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            return {
                'success': False,
                'path': '',
                'error': str(e)
            }

    async def create_goal(
        self,
        name: str,
        description: str = "",
        target_date: Optional[str] = None,
        habit_tracking: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new goal file.

        Args:
            name: Goal name
            description: Goal description
            target_date: Target completion date (YYYY-MM-DD)
            habit_tracking: Enable daily habit tracking

        Returns:
            {'success': bool, 'path': str, 'error': str}
        """
        filename = self._sanitize_filename(name)
        file_path = self.projects_folder / f"Goal-{filename}.md"

        if file_path.exists():
            return {
                'success': False,
                'path': str(file_path),
                'error': f'Goal "{name}" already exists'
            }

        try:
            content = self._get_goal_template(
                name, description, target_date, habit_tracking
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Created goal: {name}")
            return {
                'success': True,
                'path': str(file_path.relative_to(self.vault_path)),
                'error': None
            }

        except Exception as e:
            logger.error(f"Failed to create goal {name}: {e}")
            return {
                'success': False,
                'path': '',
                'error': str(e)
            }

    async def update_progress(
        self,
        name: str,
        progress: int,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Update progress for a project or goal.

        Args:
            name: Project/goal name
            progress: Progress percentage (0-100)
            notes: Optional progress notes

        Returns:
            {'success': bool, 'error': str}
        """
        # Find the file
        file_path = self._find_project_file(name)
        if not file_path:
            return {
                'success': False,
                'error': f'Project/goal "{name}" not found'
            }

        try:
            # Load with frontmatter
            post = frontmatter.load(file_path)

            # Update frontmatter
            post['progress'] = progress
            post['last_updated'] = datetime.now().isoformat()

            # Add progress note if provided
            if notes:
                progress_section = f"\n## Progress Log\n\n"
                progress_entry = f"- **{datetime.now().strftime('%Y-%m-%d')}** ({progress}%): {notes}\n"

                if '## Progress Log' in post.content:
                    # Append to existing log
                    post.content = post.content.replace(
                        '## Progress Log\n\n',
                        f'## Progress Log\n\n{progress_entry}'
                    )
                else:
                    # Create new log section
                    post.content += progress_section + progress_entry

            # Save
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))

            logger.info(f"Updated {name} to {progress}%")
            return {'success': True, 'error': None}

        except Exception as e:
            logger.error(f"Failed to update progress for {name}: {e}")
            return {'success': False, 'error': str(e)}

    async def get_active_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of active projects (progress < 100).

        Returns:
            List of project metadata dicts
        """
        projects = []

        for file_path in self.projects_folder.glob("*.md"):
            if file_path.name.startswith('.'):
                continue

            try:
                post = frontmatter.load(file_path)
                progress = post.get('progress', 0)

                if progress < 100:
                    projects.append({
                        'name': post.get('title', file_path.stem),
                        'type': 'goal' if file_path.name.startswith('Goal-') else 'project',
                        'progress': progress,
                        'priority': post.get('priority', 'medium'),
                        'last_updated': post.get('last_updated', ''),
                        'path': str(file_path.relative_to(self.vault_path))
                    })

            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                continue

        # Sort by priority then progress
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        projects.sort(key=lambda p: (
            priority_order.get(p['priority'], 1),
            p['progress']
        ))

        return projects

    async def get_stalled_projects(self, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """
        Get projects not updated recently.

        Args:
            days_threshold: Days without update to consider stalled

        Returns:
            List of stalled project metadata
        """
        from datetime import timedelta

        stalled = []
        cutoff = datetime.now() - timedelta(days=days_threshold)

        for project in await self.get_active_projects():
            last_updated = project.get('last_updated', '')
            if not last_updated:
                stalled.append(project)
                continue

            try:
                update_date = datetime.fromisoformat(last_updated)
                if update_date < cutoff:
                    stalled.append(project)
            except ValueError:
                stalled.append(project)

        return stalled

    async def link_conversation(
        self,
        project_name: str,
        conversation_path: str
    ) -> Dict[str, Any]:
        """
        Link a conversation to a project/goal.

        Args:
            project_name: Project or goal name
            conversation_path: Relative path to conversation file

        Returns:
            {'success': bool, 'error': str}
        """
        file_path = self._find_project_file(project_name)
        if not file_path:
            return {
                'success': False,
                'error': f'Project/goal "{project_name}" not found'
            }

        try:
            post = frontmatter.load(file_path)

            # Add to related conversations
            conversations = post.get('related_conversations', [])
            if conversation_path not in conversations:
                conversations.append(conversation_path)
                post['related_conversations'] = conversations

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))

            return {'success': True, 'error': None}

        except Exception as e:
            logger.error(f"Failed to link conversation: {e}")
            return {'success': False, 'error': str(e)}

    def _find_project_file(self, name: str) -> Optional[Path]:
        """Find project or goal file by name."""
        filename = self._sanitize_filename(name)

        # Try project
        project_path = self.projects_folder / f"{filename}.md"
        if project_path.exists():
            return project_path

        # Try goal
        goal_path = self.projects_folder / f"Goal-{filename}.md"
        if goal_path.exists():
            return goal_path

        return None

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        # Replace spaces with hyphens, remove special chars
        import re
        safe = re.sub(r'[^\w\s-]', '', name)
        safe = re.sub(r'[\s]+', '-', safe)
        return safe.strip('-')

    def _get_project_template(
        self,
        name: str,
        description: str,
        priority: str
    ) -> str:
        """Generate project markdown template."""
        now = datetime.now().isoformat()
        return f"""---
title: {name}
type: project
created: {now}
last_updated: {now}
progress: 0
priority: {priority}
status: active
tags: [project, {priority}]
related_conversations: []
---

# {name}

{description or 'Project description here.'}

## Goals

- [ ] Define project goals

## Tasks

- [ ] Initial task

## Progress Log

- **{datetime.now().strftime('%Y-%m-%d')}** (0%): Project created

## Notes

"""

    def _get_goal_template(
        self,
        name: str,
        description: str,
        target_date: Optional[str],
        habit_tracking: bool
    ) -> str:
        """Generate goal markdown template."""
        now = datetime.now().isoformat()
        target = target_date or "TBD"

        habit_section = """
## Daily Habit Tracker

| Date | Done | Notes |
|------|------|-------|
| | | |
""" if habit_tracking else ""

        return f"""---
title: {name}
type: goal
created: {now}
last_updated: {now}
target_date: {target}
progress: 0
priority: high
status: active
tags: [goal]
related_conversations: []
---

# {name}

{description or 'Goal description here.'}

## Success Criteria

- [ ] Define success criteria

## Milestones

- [ ] First milestone
{habit_section}
## Progress Log

- **{datetime.now().strftime('%Y-%m-%d')}** (0%): Goal created

## Notes

"""
