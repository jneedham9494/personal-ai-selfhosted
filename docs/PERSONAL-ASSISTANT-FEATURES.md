# Personal Assistant Features

**Version:** 2.0
**Date:** 2025-11-12
**Purpose:** Personal productivity, self-improvement, and knowledge management

---

## Overview

This system is a **personal AI assistant** focused on:
- Personal productivity and task management
- Goal tracking and habit formation
- Self-reflection and journaling
- Knowledge base queries (Obsidian vault)
- Proactive nudges and reminders

**NOT** a development assistant. No code review, no bash execution, no git operations.

---

## Core Features

### 1. Personal Task Management

**Commands:**
- `/todo` - Manage personal todos
- `/today` - Today's tasks and priorities

**Features:**
- Create, update, and complete todos
- Todo storage in Obsidian vault
- Integration with daily notes
- Priority levels and due dates

### 2. Goal Tracking

**Commands:**
- `/goals` - View and update personal goals
- `/progress` - Check goal progress

**Features:**
- Track hours toward learning goals (XRPL, Japanese)
- Workout/fitness tracking
- Quit urge detection and intervention
- Progress visualization

### 3. Habit Tracking

**Commands:**
- `/habits` - Track daily habits
- `/streak` - View habit streaks

**Features:**
- Daily habit checkboxes
- Streak counting
- Habit analytics
- Reminder integration

### 4. Self-Reflection

**Commands:**
- `/reflect` - Guided self-reflection
- `/journal` - Journal entry prompts

**Features:**
- Daily reflection prompts
- Mood tracking
- Pattern recognition
- Goal alignment checks

### 5. Knowledge Base (Obsidian)

**Commands:**
- `/search <query>` - Search vault
- `/note <title>` - Find/create note
- `/recent` - Recent notes

**Features:**
- Full-text search across vault
- Tag-based filtering
- Daily note access
- Note summarization

### 6. Proactive Nudging

**Commands:**
- `/nudge` - Get contextual nudge
- `/remind <what> <when>` - Set reminder

**Features:**
- Time-based nudges (morning, afternoon, evening)
- Context-aware suggestions
- Quit urge interventions
- Goal-aligned reminders

---

## Command Definitions

### /todo

```json
{
  "name": "todo",
  "description": "Manage personal tasks and todos",
  "syntax": "/todo [action] [task]",
  "category": "productivity",
  "examples": [
    "/todo list",
    "/todo add Buy groceries",
    "/todo complete 1",
    "/todo today"
  ],
  "handler": "todo_handler"
}
```

### /goals

```json
{
  "name": "goals",
  "description": "Track personal goals and progress",
  "syntax": "/goals [goal_type] [action]",
  "category": "self-improvement",
  "examples": [
    "/goals",
    "/goals XRPL log 2.5 hours",
    "/goals workout today",
    "/goals progress"
  ],
  "handler": "goals_handler"
}
```

### /habits

```json
{
  "name": "habits",
  "description": "Track daily habits and streaks",
  "syntax": "/habits [action]",
  "category": "self-improvement",
  "examples": [
    "/habits list",
    "/habits check meditation",
    "/habits streak workout",
    "/habits today"
  ],
  "handler": "habits_handler"
}
```

### /reflect

```json
{
  "name": "reflect",
  "description": "Guided self-reflection and journaling",
  "syntax": "/reflect [topic]",
  "category": "self-awareness",
  "examples": [
    "/reflect",
    "/reflect goals",
    "/reflect mood",
    "/reflect progress"
  ],
  "handler": "reflect_handler"
}
```

### /search

```json
{
  "name": "search",
  "description": "Search Obsidian vault for notes",
  "syntax": "/search <query>",
  "category": "knowledge",
  "examples": [
    "/search trip planning",
    "/search workout routine",
    "/search meeting notes"
  ],
  "handler": "search_handler"
}
```

---

## Tool System (Safe Operations Only)

**Allowed Tools:**
- `read_vault_note(path)` - Read note from Obsidian
- `write_vault_note(path, content)` - Write/update note
- `search_vault(query)` - Search vault
- `list_recent_notes(days)` - Get recent notes
- `get_daily_note(date)` - Get specific daily note
- `parse_frontmatter(path)` - Read note metadata

**Blocked Tools:**
- ❌ `execute_bash()` - NO bash execution
- ❌ `git_*()` - NO git operations
- ❌ File operations outside vault
- ❌ Network requests
- ❌ System commands

---

## Integration with Existing Setup

### Obsidian Vault Structure

```
PersonalAi/
├── Daily-Notes/
│   ├── 2025-11-12.md
│   └── ...
├── Goals/
│   ├── 2025-Q4-Goals.md
│   ├── XRPL-Learning.md
│   └── Fitness-Tracker.md
├── Habits/
│   └── Habit-Tracker-2025.md
├── Projects/
│   ├── Asia-Trip-2025.md
│   └── ...
└── Archive/
```

### Daily Note Format

```markdown
---
date: 2025-11-12
tags: [daily-note]
mood: energetic
---

# 2025-11-12 Tuesday

## 🎯 Today's Focus
- [ ] XRPL learning (2 hours)
- [ ] Workout
- [ ] Trip planning

## 📊 Goal Progress
- XRPL: 2.5 hours logged
- Workout: ✅ Completed
- Japanese: Skipped (catch up tomorrow)

## 🧘 Habits
- [x] Meditation
- [x] Journaling
- [ ] Reading

## 💭 Reflections
Felt motivated today. Made good progress on XRPL concepts.
Need to schedule Japan learning better.

## 🔥 Quit Urge Check
No urges to quit today. Feeling committed.
```

### Goal Tracking Integration

**Read Goals:**
```python
goals = await vault_service.read_note('Goals/2025-Q4-Goals.md')
```

**Update Progress:**
```python
await vault_service.update_goal_progress(
    goal='XRPL',
    hours=2.5,
    date='2025-11-12'
)
```

**Check Quit Patterns:**
```python
analysis = await vault_service.analyze_quit_patterns(
    goal_type='XRPL',
    days=14
)
```

---

## Nudging System

### Nudge Schedule

**Morning (9:00 AM):**
- Daily focus reminder
- Goal alignment check
- Habit prompt

**Afternoon (2:00 PM):**
- Progress check-in
- Midday motivation
- Quit urge detection

**Evening (7:00 PM):**
- Reflection prompt
- Tomorrow planning
- Gratitude journal

### Nudge Examples

```
🌅 Good morning! Ready to tackle XRPL learning today?
   Goal: 2 hours | Your avg: 2.3 hours/day

   Today's focus:
   - Review smart contract basics
   - Complete module 3 exercises
```

```
⚡ Afternoon check-in!
   You've logged 1.5 hours on XRPL so far.
   30 more minutes to hit your daily goal!

   Quick break suggestion: 10-min walk or meditation?
```

```
🌙 Evening reflection time
   How did today go?
   - Goals achieved?
   - What went well?
   - What to improve tomorrow?
```

---

## Telegram Bot Compatibility

**Same Core Services:**
- LLM Service (Qwen 2.5 Coder)
- Obsidian Service
- Goal Tracking
- Habit Tracking

**Different Interfaces:**
```python
# Web interface (new)
web_api = FastAPIServer(llm_service, vault_service)

# Telegram bot (existing)
telegram_bot = TelegramBotService(llm_service, vault_service)
```

**Shared Commands:**
- `/search` works in both
- `/goals` works in both
- `/todo` works in both
- `/reflect` works in both

---

## Configuration

### .ai/config.yaml

```yaml
# Personal AI Assistant Configuration
version: "2.0"

# LLM Settings
llm:
  provider: ollama
  host: localhost:11434
  model: qwen2.5-coder:7b
  temperature: 0.7

# Vault
vault:
  path: /Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi
  daily_notes_folder: Daily-Notes
  goals_folder: Goals
  habits_folder: Habits

# Nudging
nudging:
  enabled: true
  schedule:
    morning: "09:00"
    afternoon: "14:00"
    evening: "19:00"
  daily_limit: 5
  cooldown_minutes: 120

# Features (NO development features)
features:
  slash_commands: true
  todo_tracking: true
  goal_tracking: true
  habit_tracking: true
  reflections: true
  vault_search: true
  nudging: true
  # DISABLED:
  bash_execution: false
  git_integration: false
  code_tools: false
  agents: false

# Security
security:
  vault_only: true  # Only access vault directory
  no_bash: true     # Never execute bash commands
  no_network: true  # No external network access
```

---

## Next Steps

### Phase 1 (Weeks 1-2):
1. ✅ Basic chat infrastructure
2. ✅ Slash command system
3. ✅ Obsidian search integration
4. ⏳ Remove development commands
5. ⏳ Implement /todo command
6. ⏳ Implement /goals command
7. ⏳ Implement /habits command
8. ⏳ Implement /reflect command

### Phase 2 (Weeks 3-4):
1. Nudging system integration
2. Habit streak calculation
3. Goal progress visualization
4. Quit urge detection
5. Pattern analysis

### Phase 3 (Month 2):
1. Home server deployment
2. Tailscale VPN setup
3. Mobile access
4. Cross-device sync

---

**Last Updated:** 2025-11-12
**Focus:** Personal productivity and self-improvement ONLY
