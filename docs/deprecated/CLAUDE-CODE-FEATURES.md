# Claude Code Features Implementation

**Version:** 1.0
**Date:** 2025-11-09

---

## Overview

This document describes how to implement Claude Code's powerful features (slash commands, hooks, tools, agents) in the self-hosted LLM system.

**Goal:** Make the local LLM operate identically to Claude Code, but with complete privacy and control.

---

## Feature Parity Matrix

| Feature | Claude Code | Self-Hosted | Status |
|---------|-------------|-------------|--------|
| Slash Commands | ✅ | 🔄 | Phase 1 |
| Custom Hooks | ✅ | 🔄 | Phase 1 |
| File Tools | ✅ | 🔄 | Phase 1 |
| Bash Execution | ✅ | 🔄 | Phase 1 |
| Web Search | ✅ | 🔄 | Phase 2 |
| Multi-Agent | ✅ | 🔄 | Phase 2 |
| TODO Tracking | ✅ | 🔄 | Phase 1 |
| Git Integration | ✅ | 🔄 | Phase 1 |

---

## 1. Slash Commands System

### Architecture

```
User: "/vmodel Implement user authentication"
    ↓
1. Command Parser (regex match)
    ↓
2. Load Command Definition (.ai/commands/vmodel.md)
    ↓
3. Execute Pre-Command Hooks
    ↓
4. Expand Prompt Template
    ↓
5. Send to LLM with System Context
    ↓
6. Execute Post-Command Hooks
    ↓
7. Return Response
```

### Command Storage Structure

```
/Users/jackdev/development/personal-ai-selfhosted/.ai/
├── commands/
│   ├── vmodel.md
│   ├── review.md
│   ├── feature.md
│   ├── quickfix.md
│   ├── lint-gherkin.md
│   └── analyze.md
├── hooks/
│   ├── pre-vmodel.py
│   ├── post-todo.py
│   └── lint-gherkin.py
└── agents/
    ├── explore-agent.yaml
    ├── review-agent.yaml
    └── test-runner.yaml
```

### Command Definition Format

**File:** `.ai/commands/vmodel.md`

```markdown
---
name: vmodel
description: Execute full V-model development process
category: workflow
priority: high
requires_context: true
hooks:
  pre: pre-vmodel
  post: post-vmodel
agents:
  - explore
  - plan
---

# V-Model Development Workflow

You are executing the V-Model development process for:
**Task:** {{task_description}}

## Context
- Current directory: {{cwd}}
- Git branch: {{git_branch}}
- Modified files: {{git_status}}

## V-Model Phases

### Phase 1: Requirements Analysis
1. Understand the task requirements
2. Ask clarifying questions if needed
3. Document acceptance criteria in Gherkin format

**Acceptance Criteria Template:**
\```gherkin
Feature: {{feature_name}}
  Scenario: {{scenario_name}}
    Given {{precondition}}
    When {{action}}
    Then {{expected_result}}
\```

### Phase 2: Design
... (rest of v-model process)

## Hooks
- **Pre-execution:** Verify git status is clean
- **Post-execution:** Run lint-gherkin on acceptance criteria

## Tools Available
- Read/Write files
- Execute bash commands
- Search codebase
- Git operations
- Run tests

Execute this workflow systematically, asking for confirmation at each phase.
```

### Implementation

**Backend:** `src/backend/services/command_service.py`

```python
import re
from pathlib import Path
from typing import Dict, Optional
import frontmatter

class CommandService:
    def __init__(self, commands_dir: Path):
        self.commands_dir = commands_dir
        self.commands = self._load_commands()

    def _load_commands(self) -> Dict[str, Dict]:
        """Load all command definitions from .ai/commands/"""
        commands = {}
        for cmd_file in self.commands_dir.glob("*.md"):
            with open(cmd_file) as f:
                post = frontmatter.load(f)
                commands[post['name']] = {
                    'metadata': post.metadata,
                    'content': post.content
                }
        return commands

    def parse_command(self, message: str) -> Optional[Dict]:
        """Parse slash command from user message"""
        match = re.match(r'^/(\w+)(?:\s+(.*))?$', message.strip())
        if not match:
            return None

        cmd_name, cmd_args = match.groups()
        if cmd_name not in self.commands:
            return None

        return {
            'name': cmd_name,
            'args': cmd_args or '',
            'definition': self.commands[cmd_name]
        }

    async def execute_command(
        self,
        command: Dict,
        context: Dict
    ) -> str:
        """Execute a slash command with context"""

        # 1. Run pre-command hooks
        if 'hooks' in command['definition']['metadata']:
            if 'pre' in command['definition']['metadata']['hooks']:
                await self._run_hook(
                    command['definition']['metadata']['hooks']['pre'],
                    context
                )

        # 2. Expand prompt template
        prompt = self._expand_template(
            command['definition']['content'],
            {
                'task_description': command['args'],
                'cwd': context['cwd'],
                'git_branch': context['git_branch'],
                'git_status': context['git_status'],
                **context
            }
        )

        # 3. Send to LLM
        response = await self.llm_service.chat(
            messages=[
                {'role': 'system', 'content': self._get_system_prompt(context)},
                {'role': 'user', 'content': prompt}
            ]
        )

        # 4. Run post-command hooks
        if 'hooks' in command['definition']['metadata']:
            if 'post' in command['definition']['metadata']['hooks']:
                await self._run_hook(
                    command['definition']['metadata']['hooks']['post'],
                    context,
                    response
                )

        return response

    def _expand_template(self, template: str, vars: Dict) -> str:
        """Replace {{variable}} placeholders"""
        import re
        def replacer(match):
            var_name = match.group(1)
            return str(vars.get(var_name, f'{{{{var_name}}}}'))
        return re.sub(r'\{\{(\w+)\}\}', replacer, template)

    async def _run_hook(self, hook_name: str, context: Dict, response: str = None):
        """Execute a hook script"""
        hook_path = self.commands_dir.parent / 'hooks' / f'{hook_name}.py'
        if not hook_path.exists():
            return

        # Run hook in sandboxed environment
        import subprocess
        result = subprocess.run(
            ['python', str(hook_path)],
            input=json.dumps({'context': context, 'response': response}),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise Exception(f"Hook {hook_name} failed: {result.stderr}")
```

---

## 2. Hooks System

### Hook Types

**Pre-Command Hooks:**
- Validate preconditions
- Check git status
- Verify file permissions
- Lint acceptance criteria

**Post-Command Hooks:**
- Format output
- Run linters
- Update TODO lists
- Commit changes

### Hook Definition

**File:** `.ai/hooks/lint-gherkin.py`

```python
#!/usr/bin/env python3
"""
Lint Gherkin acceptance criteria for quality
"""
import sys
import json
import re

def lint_gherkin(text: str) -> dict:
    """Validate Gherkin format"""
    errors = []
    warnings = []

    # Check for Feature keyword
    if not re.search(r'^Feature:', text, re.MULTILINE):
        errors.append("Missing 'Feature:' keyword")

    # Check for Scenario
    if not re.search(r'^\s+Scenario:', text, re.MULTILINE):
        errors.append("Missing 'Scenario:' keyword")

    # Check for Given/When/Then
    if not re.search(r'^\s+Given', text, re.MULTILINE):
        warnings.append("Missing 'Given' statement")
    if not re.search(r'^\s+When', text, re.MULTILINE):
        warnings.append("Missing 'When' statement")
    if not re.search(r'^\s+Then', text, re.MULTILINE):
        warnings.append("Missing 'Then' statement")

    # Check for verification step
    if not re.search(r'Verification:', text, re.MULTILINE):
        warnings.append("Missing 'Verification:' section")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def main():
    # Read input from stdin
    input_data = json.loads(sys.stdin.read())
    response_text = input_data.get('response', '')

    # Extract Gherkin blocks
    gherkin_blocks = re.findall(
        r'```gherkin\n(.*?)\n```',
        response_text,
        re.DOTALL
    )

    if not gherkin_blocks:
        print(json.dumps({
            'status': 'error',
            'message': 'No Gherkin acceptance criteria found'
        }))
        sys.exit(1)

    # Lint each block
    all_valid = True
    results = []

    for block in gherkin_blocks:
        result = lint_gherkin(block)
        results.append(result)
        if not result['valid']:
            all_valid = False

    if all_valid:
        print(json.dumps({
            'status': 'success',
            'message': '✓ TASK COMPLEXITY: STANDARD - Using Micro V-Model',
            'results': results
        }))
        sys.exit(0)
    else:
        print(json.dumps({
            'status': 'error',
            'message': 'Gherkin validation failed',
            'results': results
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### Hook Integration

**In Backend:**

```python
class HookService:
    def __init__(self, hooks_dir: Path):
        self.hooks_dir = hooks_dir

    async def run_hook(
        self,
        hook_name: str,
        hook_type: str,  # 'pre' or 'post'
        context: Dict,
        response: str = None
    ) -> Dict:
        """Execute a hook and return result"""

        hook_file = self.hooks_dir / f"{hook_name}.py"
        if not hook_file.exists():
            return {'status': 'skipped', 'message': 'Hook not found'}

        # Prepare hook input
        hook_input = {
            'type': hook_type,
            'context': context,
            'response': response
        }

        # Execute hook with timeout
        import subprocess
        import asyncio

        try:
            result = await asyncio.create_subprocess_exec(
                'python', str(hook_file),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                result.communicate(input=json.dumps(hook_input).encode()),
                timeout=30.0
            )

            return json.loads(stdout.decode())

        except asyncio.TimeoutError:
            return {'status': 'error', 'message': 'Hook timeout'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
```

---

## 3. Tools System (Function Calling)

### Available Tools

**File Operations:**
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write file
- `edit_file(path, old, new)` - Replace text
- `glob_files(pattern)` - Find files by pattern
- `grep_files(pattern, path)` - Search file contents

**Bash Commands:**
- `execute_bash(command, timeout)` - Run shell command
- `git_status()` - Get git status
- `git_diff()` - Get uncommitted changes

**Vault Operations:**
- `search_vault(query)` - Semantic search in Obsidian
- `read_daily_note(date)` - Get specific daily note
- `get_recent_notes(days)` - Get recent notes

**Goal Tracking:**
- `get_goal_progress(goal_type)` - Get hours/progress
- `update_goal(goal_type, hours)` - Update progress
- `check_quit_urge()` - Analyze for quit patterns

### Tool Implementation

**Backend:** `src/backend/services/tool_service.py`

```python
from typing import List, Dict, Callable
import subprocess
from pathlib import Path

class ToolService:
    def __init__(self, workspace_root: Path, vault_path: Path):
        self.workspace_root = workspace_root
        self.vault_path = vault_path
        self.tools = self._register_tools()

    def _register_tools(self) -> Dict[str, Callable]:
        """Register all available tools"""
        return {
            'read_file': self.read_file,
            'write_file': self.write_file,
            'edit_file': self.edit_file,
            'glob_files': self.glob_files,
            'grep_files': self.grep_files,
            'execute_bash': self.execute_bash,
            'git_status': self.git_status,
            'search_vault': self.search_vault,
            'read_daily_note': self.read_daily_note,
            'get_goal_progress': self.get_goal_progress,
        }

    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for LLM function calling"""
        return [
            {
                'name': 'read_file',
                'description': 'Read contents of a file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path': {
                            'type': 'string',
                            'description': 'Absolute or relative file path'
                        }
                    },
                    'required': ['path']
                }
            },
            {
                'name': 'execute_bash',
                'description': 'Execute a bash command',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'command': {
                            'type': 'string',
                            'description': 'Bash command to execute'
                        },
                        'timeout': {
                            'type': 'number',
                            'description': 'Timeout in seconds (max 600)',
                            'default': 120
                        }
                    },
                    'required': ['command']
                }
            },
            {
                'name': 'search_vault',
                'description': 'Search Obsidian vault using semantic search',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Search query'
                        },
                        'limit': {
                            'type': 'number',
                            'description': 'Max results to return',
                            'default': 5
                        }
                    },
                    'required': ['query']
                }
            },
            # ... more tools
        ]

    async def read_file(self, path: str) -> str:
        """Read file contents"""
        file_path = self._resolve_path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return file_path.read_text()

    async def execute_bash(self, command: str, timeout: int = 120) -> Dict:
        """Execute bash command safely"""
        # Validate command (no dangerous operations)
        dangerous_patterns = ['rm -rf /', 'dd ', '> /dev/', 'mkfs']
        if any(pattern in command for pattern in dangerous_patterns):
            raise ValueError("Dangerous command blocked")

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.workspace_root
        )

        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }

    async def search_vault(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Obsidian vault"""
        # Use RAG service for semantic search
        from .rag_service import RAGService
        rag = RAGService(self.vault_path)

        results = await rag.search(query, k=limit)
        return results

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace"""
        p = Path(path)
        if p.is_absolute():
            return p
        return (self.workspace_root / p).resolve()
```

### LLM Function Calling Integration

**Using Llama 3 with Function Calling:**

```python
async def chat_with_tools(
    self,
    messages: List[Dict],
    tools: List[Dict]
) -> str:
    """Chat with LLM that can call tools"""

    # Initial LLM call with tools
    response = await ollama.chat(
        model='llama3',
        messages=messages,
        tools=tools
    )

    # Check if LLM wants to call a tool
    while response.get('tool_calls'):
        for tool_call in response['tool_calls']:
            tool_name = tool_call['function']['name']
            tool_args = json.loads(tool_call['function']['arguments'])

            # Execute tool
            tool_result = await self.tool_service.execute_tool(
                tool_name,
                tool_args
            )

            # Add tool result to conversation
            messages.append({
                'role': 'assistant',
                'content': '',
                'tool_calls': [tool_call]
            })
            messages.append({
                'role': 'tool',
                'content': json.dumps(tool_result)
            })

        # Continue conversation with tool results
        response = await ollama.chat(
            model='llama3',
            messages=messages,
            tools=tools
        )

    return response['message']['content']
```

---

## 4. Multi-Agent System

### Agent Types

**Explore Agent:**
- Fast codebase exploration
- File pattern matching
- Keyword search
- Answers "where is X?" questions

**Plan Agent:**
- Task breakdown
- Implementation planning
- Complexity estimation

**Review Agent:**
- Code review
- Acceptance criteria verification
- Testing recommendations

**Test Runner Agent:**
- Execute tests
- Report results
- Suggest fixes

### Agent Definition

**File:** `.ai/agents/explore-agent.yaml`

```yaml
name: explore
description: Fast agent specialized for exploring codebases
model: llama3:8b  # Use smaller, faster model
tools:
  - glob_files
  - grep_files
  - read_file
  - search_vault
system_prompt: |
  You are a fast exploration agent specialized in finding code and information.

  Your capabilities:
  - Find files by pattern (glob_files)
  - Search code for keywords (grep_files)
  - Read specific files (read_file)
  - Search Obsidian vault (search_vault)

  Be concise and direct. Return file paths and line numbers.
  Don't read entire files unless specifically asked.

  Example queries you handle:
  - "Where is the authentication code?"
  - "Find all files that import FastAPI"
  - "Search vault for Q4 goals"
  - "What files were modified recently?"
thoroughness_levels:
  quick:
    max_files: 5
    timeout: 10
  medium:
    max_files: 20
    timeout: 30
  very_thorough:
    max_files: 100
    timeout: 120
```

### Agent Spawning

**Backend:** `src/backend/services/agent_service.py`

```python
class AgentService:
    def __init__(self, agents_dir: Path, tool_service: ToolService):
        self.agents_dir = agents_dir
        self.tool_service = tool_service
        self.agents = self._load_agents()

    def _load_agents(self) -> Dict:
        """Load agent definitions"""
        import yaml
        agents = {}
        for agent_file in self.agents_dir.glob("*.yaml"):
            with open(agent_file) as f:
                agent = yaml.safe_load(f)
                agents[agent['name']] = agent
        return agents

    async def spawn_agent(
        self,
        agent_name: str,
        task: str,
        thoroughness: str = 'medium'
    ) -> str:
        """Spawn an agent to handle a task"""

        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent = self.agents[agent_name]

        # Get agent configuration
        config = agent.get('thoroughness_levels', {}).get(thoroughness, {})

        # Build agent system prompt
        system_prompt = agent['system_prompt']

        # Get available tools for this agent
        available_tools = [
            self.tool_service.get_tool_definition(tool_name)
            for tool_name in agent.get('tools', [])
        ]

        # Execute agent task
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': task}
        ]

        # Use lighter model for faster agents
        model = agent.get('model', 'llama3')

        response = await self.llm_service.chat_with_tools(
            model=model,
            messages=messages,
            tools=available_tools,
            timeout=config.get('timeout', 60)
        )

        return response
```

### Agent Usage in Commands

**Example:** V-Model command spawns Explore agent

```markdown
## Phase 1: Requirements Analysis

First, spawn the Explore agent to understand the codebase:

\```python
explore_result = await spawn_agent(
    'explore',
    f'Find all files related to: {task_description}',
    thoroughness='medium'
)
\```

Then analyze the results and ask clarifying questions...
```

---

## 5. TODO Tracking System

### TODO Format

```markdown
- [x] Install Dataview plugin
  Status: completed
  Completed: 2025-11-09

- [ ] Create Q4 Dashboard
  Status: in_progress
  Started: 2025-11-09
  Acceptance Criteria:
    Given I have Dataview installed
    When I open Q4-Goals-Dashboard.md
    Then I see tables with my daily note data
  Verification: Tables show 3 sample daily notes

- [ ] Set up home server
  Status: pending
  Phase: 2
```

### TODO Service

**Backend:** `src/backend/services/todo_service.py`

```python
class TodoService:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    async def parse_todos(self, file_path: Path) -> List[Dict]:
        """Parse TODOs from markdown file"""
        import re

        content = file_path.read_text()
        todos = []

        # Find checkbox items
        pattern = r'^- \[([ x])\] (.+)$'
        for match in re.finditer(pattern, content, re.MULTILINE):
            status = 'completed' if match.group(1) == 'x' else 'pending'
            title = match.group(2)

            todos.append({
                'title': title,
                'status': status,
                'file': str(file_path)
            })

        return todos

    async def update_todo(
        self,
        file_path: Path,
        todo_title: str,
        new_status: str
    ):
        """Update TODO status"""
        content = file_path.read_text()

        # Find and replace
        old_checkbox = '[ ]' if new_status == 'completed' else '[x]'
        new_checkbox = '[x]' if new_status == 'completed' else '[ ]'

        pattern = rf'- \{old_checkbox}\] {re.escape(todo_title)}'
        replacement = f'- {new_checkbox}] {todo_title}'

        updated = re.sub(pattern, replacement, content)
        file_path.write_text(updated)
```

---

## 6. Integration with Existing Setup

### Obsidian Vault Integration

**Access Patterns:**

```python
# Read Q4 goals
goals = await vault_service.read_file('Quarterly-Goals-2025-Q4.md')

# Search for workout patterns
workout_days = await vault_service.search(
    query='workout completed',
    filter_tags=['daily-note', 'workout']
)

# Get recent daily notes
recent = await vault_service.get_recent_notes(days=7)

# Analyze for quit patterns
analysis = await vault_service.analyze_quit_patterns(
    goal_type='XRPL',
    days=14
)
```

### Telegram Bot Compatibility

**Share infrastructure:**

```python
# Same LLM service
llm_service = LLMService(ollama_host='localhost:11434')

# Same vault service
vault_service = VaultService(vault_path='/path/to/obsidian')

# Different interfaces
telegram_bot = TelegramBotService(llm_service, vault_service)
web_api = FastAPIServer(llm_service, vault_service)
```

---

## 7. Configuration

### User Config File

**File:** `.ai/config.yaml`

```yaml
# Personal AI Configuration
version: "1.0"

# LLM Settings
llm:
  provider: ollama
  host: localhost:11434
  model: llama3
  temperature: 0.7
  context_window: 8192

# Workspace
workspace:
  root: /Users/jackdev/development/personal-ai-selfhosted
  obsidian_vault: /Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi

# Security
security:
  enable_sandbox: true
  allowed_bash_commands:
    - git
    - npm
    - python
    - pytest
  blocked_bash_patterns:
    - "rm -rf /"
    - "dd "
    - "> /dev/"

# Features
features:
  slash_commands: true
  hooks: true
  tools: true
  agents: true
  todo_tracking: true

# Hooks
hooks:
  pre_command:
    - lint-gherkin
  post_command:
    - update-todos

# Agents
agents:
  explore:
    enabled: true
    default_thoroughness: medium
  review:
    enabled: true
  test_runner:
    enabled: false  # Phase 2

# Logging
logging:
  level: INFO
  file: .ai/logs/ai.log
  max_size: 10MB
  retention_days: 30
```

---

## 8. Web UI Integration

### Slash Command Input

```typescript
// Frontend: src/frontend/components/Chat/ChatInput.tsx

const ChatInput: React.FC = () => {
  const [message, setMessage] = useState('');
  const [isCommand, setIsCommand] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessage(value);

    // Detect slash command
    setIsCommand(value.startsWith('/'));
  };

  const handleSend = async () => {
    if (isCommand) {
      // Execute slash command
      const response = await api.executeCommand(message);
      // Handle response
    } else {
      // Normal chat
      const response = await api.sendMessage(message);
      // Handle response
    }
  };

  return (
    <div className="chat-input">
      <textarea
        value={message}
        onChange={handleInputChange}
        placeholder={isCommand ? "Executing command..." : "Type a message or /command"}
        className={isCommand ? "command-mode" : ""}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};
```

### Command Autocomplete

```typescript
// Command suggestions
const COMMANDS = [
  { name: '/vmodel', description: 'V-Model development workflow' },
  { name: '/review', description: 'Review code against acceptance criteria' },
  { name: '/feature', description: 'Full feature development workflow' },
  { name: '/quickfix', description: 'Fast bug fix workflow' },
  { name: '/analyze', description: 'Analyze code with tools' },
];

// Show autocomplete when typing /
if (message.startsWith('/') && message.length > 1) {
  const suggestions = COMMANDS.filter(cmd =>
    cmd.name.startsWith(message.toLowerCase())
  );
  // Show suggestion dropdown
}
```

---

## Next Steps

1. **Implement Command Parser** (Week 1)
2. **Build Tool Service** (Week 1)
3. **Create Hook System** (Week 2)
4. **Test with Existing Commands** (Week 2)
5. **Add Agent Support** (Week 3)

---

**Last Updated:** 2025-11-09
**Next Review:** After Phase 1 Week 1
