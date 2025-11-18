"""
Metadata extraction for Obsidian conversations.

Extracts mood, category, priority, and action items from text.
"""

import re
from typing import List, Dict, Any


class MetadataExtractor:
    """Extracts metadata from conversation text."""

    # Mood detection patterns
    MOOD_PATTERNS = {
        'stressed': [
            'stress', 'worried', 'anxious', 'overwhelm', 'pressure',
            'difficult', 'struggle', 'frustrated', 'tired', 'exhausted'
        ],
        'excited': [
            'excited', 'amazing', 'great', 'awesome', 'love',
            'fantastic', 'excellent', 'happy', 'thrilled', 'pumped'
        ],
        'focused': [
            'plan', 'goal', 'organize', 'structure', 'focus',
            'work on', 'complete', 'finish', 'progress', 'productive'
        ],
        'confused': [
            'confused', 'not sure', 'unclear', "don't understand",
            'lost', 'help', 'stuck', "can't figure", 'uncertain'
        ],
        'reflective': [
            'think', 'realize', 'understand', 'learn', 'reflect',
            'consider', 'wondering', 'looking back', 'appreciate'
        ]
    }

    # Category detection patterns
    CATEGORY_PATTERNS = {
        'work': [
            'work', 'project', 'meeting', 'deadline', 'task',
            'client', 'business', 'job', 'office', 'team'
        ],
        'personal': [
            'personal', 'family', 'friend', 'relationship', 'life',
            'home', 'kids', 'spouse', 'partner'
        ],
        'learning': [
            'learn', 'study', 'course', 'tutorial', 'practice',
            'skill', 'knowledge', 'education', 'class', 'book'
        ],
        'health': [
            'health', 'fitness', 'exercise', 'workout', 'diet',
            'sleep', 'mental', 'meditation', 'wellness', 'gym'
        ],
        'finance': [
            'money', 'budget', 'finance', 'invest', 'expense',
            'income', 'cost', 'save', 'bank', 'crypto'
        ],
        'creative': [
            'creative', 'write', 'design', 'art', 'music',
            'create', 'build', 'make', 'draw', 'compose'
        ]
    }

    # Priority indicators
    PRIORITY_KEYWORDS = {
        'high': [
            'urgent', 'asap', 'immediately', 'critical', 'important',
            'must', 'deadline', 'today', 'now', 'emergency'
        ],
        'medium': [
            'soon', 'should', 'need to', 'this week', 'plan to'
        ],
        'low': [
            'eventually', 'someday', 'maybe', 'would be nice', 'when possible'
        ]
    }

    # Action item patterns
    ACTION_PATTERNS = [
        r'I need to (.+?)(?:\.|$)',
        r'I should (.+?)(?:\.|$)',
        r'I will (.+?)(?:\.|$)',
        r'I have to (.+?)(?:\.|$)',
        r'I must (.+?)(?:\.|$)',
        r'- \[ \] (.+?)(?:\n|$)',
        r'TODO:?\s*(.+?)(?:\n|$)',
        r'remind me to (.+?)(?:\.|$)',
        r"don't forget to (.+?)(?:\.|$)",
    ]

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all metadata from text.

        Args:
            text: Text to analyze

        Returns:
            {
                'mood': str,
                'category': str,
                'priority': str,
                'action_items': List[str],
                'tags': List[str]
            }
        """
        text_lower = text.lower()

        mood = self._detect_mood(text_lower)
        category = self._detect_category(text_lower)
        priority = self._detect_priority(text_lower)
        action_items = self._extract_action_items(text)

        # Build tags
        tags = ['ai', 'conversation']
        if mood != 'neutral':
            tags.append(mood)
        if category:
            tags.append(category)

        return {
            'mood': mood,
            'category': category or 'general',
            'priority': priority,
            'action_items': action_items,
            'tags': tags
        }

    def _detect_mood(self, text: str) -> str:
        """Detect mood from text patterns."""
        scores = {mood: 0 for mood in self.MOOD_PATTERNS}

        for mood, patterns in self.MOOD_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    scores[mood] += 1

        # Return mood with highest score, or 'neutral'
        best_mood = max(scores, key=scores.get)
        return best_mood if scores[best_mood] > 0 else 'neutral'

    def _detect_category(self, text: str) -> str:
        """Detect category from text patterns."""
        scores = {cat: 0 for cat in self.CATEGORY_PATTERNS}

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    scores[category] += 1

        # Return category with highest score
        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else ''

    def _detect_priority(self, text: str) -> str:
        """Detect priority from text patterns."""
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return priority
        return 'medium'

    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from text."""
        items = []

        for pattern in self.ACTION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                item = match.strip()
                if item and len(item) > 3 and item not in items:
                    items.append(item)

        return items[:10]  # Limit to 10 items


def generate_tags_from_content(content: str) -> List[str]:
    """
    Generate tags from conversation content.

    Args:
        content: Full conversation text

    Returns:
        List of tags
    """
    extractor = MetadataExtractor()
    metadata = extractor.extract_all(content)
    return metadata['tags']
