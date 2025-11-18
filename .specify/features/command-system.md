# Feature: Command System

## Status
**Retroactive specification** - Feature implemented and operational

## Overview
Slash command system that intercepts messages starting with "/" and executes special operations instead of sending to the LLM. Commands are defined in JSON configuration files.

---

## Current Behavior

### Available Commands
1. `/help [command]` - List all commands or get help for specific command
2. `/search <query>` - Search Obsidian vault for text

### Processing Flow
1. User sends message starting with "/"
2. CommandParser.parse() extracts command and arguments
3. Command handler executes appropriate action
4. Formatted result returned to user

---

## Technical Implementation

### Files
- [command_parser.py](backend/services/commands/command_parser.py) - Parser and execution
- [help.json](.ai/commands/help.json) - Help command definition
- [search.json](.ai/commands/search.json) - Search command definition

### Command Definition Format
```json
{
  "name": "command-name",
  "description": "What the command does",
  "usage": "/command [args]",
  "examples": [
    "/command example1",
    "/command example2"
  ]
}
```

---

## Acceptance Criteria (Current State)

### Command Detection
- GIVEN a message starting with "/"
  WHEN processed by CommandParser.parse()
  THEN returns (command_name, arguments)
  AND command is extracted without leading "/"

### Help - All Commands
- GIVEN message "/help"
  WHEN processed
  THEN returns formatted list of all available commands
  AND each command shows name, description, and usage

### Help - Specific Command
- GIVEN message "/help search"
  WHEN processed
  THEN returns detailed help for search command
  AND includes description, usage, and examples

### Help - Unknown Command
- GIVEN message "/help unknown"
  WHEN processed
  THEN returns error message indicating command not found

### Search - With Results
- GIVEN message "/search my query"
  WHEN processed
  THEN searches vault for "my query"
  AND returns formatted results with file paths and excerpts

### Search - No Results
- GIVEN message "/search nonexistent12345"
  WHEN processed
  THEN returns message indicating no results found

### Search - Empty Query
- GIVEN message "/search" (no query)
  WHEN processed
  THEN returns error message about missing query

### Unknown Command
- GIVEN message "/unknown"
  WHEN processed
  THEN returns error message
  AND suggests using /help

---

## Command Response Format

### Help All Commands
```
📚 Available Commands:

/help [command]
  Get help for commands

/search <query>
  Search your knowledge base

Type /help <command> for detailed usage.
```

### Help Specific Command
```
📖 Command: /search

Search your Obsidian vault for text content.

Usage: /search <query>

Examples:
  /search project ideas
  /search meeting notes
```

### Search Results
```
🔍 Search Results for "query"

📄 folder/note1.md (line 15)
   ...context around the matched text...

📄 folder/note2.md (line 42)
   ...context around the matched text...

Found 2 results in 150 files.
```

---

## Configuration

### Command Definition Location
- `.ai/commands/*.json`

### Adding New Commands
1. Create JSON file in `.ai/commands/`
2. Add handler in `command_parser.py`
3. Update help command to include new command

---

## Known Issues / Tech Debt

- [ ] Command definitions hardcoded in parser
- [ ] No dynamic command loading from JSON files
- [ ] Limited argument parsing (basic split)
- [ ] No command aliases
- [ ] No command history tracking
- [ ] No command autocomplete support

---

## Future Improvements

- [ ] Dynamic command loading from JSON definitions
- [ ] Command argument validation schema
- [ ] Command aliases (e.g., /s for /search)
- [ ] Command history for user
- [ ] Autocomplete suggestions
- [ ] Custom user-defined commands
- [ ] Command chaining (multiple commands)
- [ ] Rich formatting (markdown in responses)

### Planned Commands
- [ ] `/goals` - View Q4 goal progress
- [ ] `/daily` - Create or view daily note
- [ ] `/remind` - Set reminder
- [ ] `/context` - Load specific context for conversation
- [ ] `/clear` - Clear conversation history

---

## Testing Coverage

### Current Tests
- None (backend tests not implemented)

### Required Tests
- [ ] Unit tests for CommandParser.parse()
- [ ] Unit tests for each command handler
- [ ] Test unknown command handling
- [ ] Test malformed command input
- [ ] Test command with special characters
- [ ] Integration tests for command execution

---

## Dependencies

### Internal
- ObsidianService for /search command
- FileTools for path-safe operations

### External
- None (commands are self-contained)

---

## Security Considerations

### Implemented
- Search limited to vault directory
- No write operations via commands

### Needed
- Input sanitization for command arguments
- Rate limiting on search operations
- Audit logging of command usage

---

## Extensibility Design

### Current: Hardcoded
```python
if command == "help":
    return self._handle_help(args)
elif command == "search":
    return self._handle_search(args)
```

### Desired: Plugin Architecture
```python
class Command:
    name: str
    handler: Callable

command_registry.register(SearchCommand())
command_registry.execute(command_name, args)
```

---

**Specification Created:** 2025-11-18
**Last Updated:** 2025-11-18
