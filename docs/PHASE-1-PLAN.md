# Phase 1: Mac Development Plan

**Version:** 1.0
**Duration:** 3 weeks
**Platform:** M4 MacBook Pro (localhost development)
**Goal:** Build fully functional local AI system with Claude Code feature parity

---

## Overview

Phase 1 focuses on rapid development and iteration on your local Mac. All services run on localhost, no networking complexity, maximum development speed. By the end of Phase 1, you'll have a working AI assistant that replicates your Claude Code workflow.

**Success Criteria:**
- ✅ Chat with local LLM via web interface
- ✅ Execute slash commands (e.g., `/vmodel`, `/review`)
- ✅ Hooks run automatically (e.g., lint-gherkin)
- ✅ Tools work (read files, bash, vault search)
- ✅ Agents can be spawned (explore, plan, review)
- ✅ TODO tracking with acceptance criteria
- ✅ Security foundations in place

---

## Week 1: Core Infrastructure

### Day 1-2: Project Setup

**Goal:** Get basic backend + frontend running

**Tasks:**
```gherkin
Given a new project directory
When setting up the development environment
Then the system should have:
- Python 3.11+ virtual environment
- FastAPI backend serving on localhost:8000
- React frontend serving on localhost:3000
- Ollama running with Llama 3 8B model
- PostgreSQL database (or SQLite for quick start)
```

**Implementation:**

```bash
# Backend setup
cd /Users/jackdev/development/personal-ai-selfhosted
mkdir -p backend frontend

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy anthropic ollama chromadb python-multipart

# Create basic FastAPI app
# backend/main.py
```

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Personal AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Personal AI Assistant API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

```bash
# Frontend setup
cd ../frontend
npm create vite@latest . -- --template react-ts
npm install
npm install @tanstack/react-query axios react-router-dom
```

**Verification:**
- Backend: `curl http://localhost:8000/health`
- Frontend: Visit `http://localhost:3000`
- Ollama: `curl http://localhost:11434/api/tags`

**Deliverables:**
- [ ] Backend responds on port 8000
- [ ] Frontend loads on port 3000
- [ ] Ollama installed with llama3:8b
- [ ] Database initialized

### Day 3-4: Basic Chat Interface

**Goal:** Send messages to LLM and get responses

**Tasks:**
```gherkin
Given a running backend and frontend
When a user types a message and clicks send
Then the system should:
- Send message to FastAPI backend
- Forward to Ollama LLM
- Stream response back to frontend
- Display in chat interface
```

**Backend Implementation:**

```python
# backend/services/llm_service.py
import ollama
from typing import AsyncGenerator

class LLMService:
    def __init__(self, model: str = "llama3:8b"):
        self.model = model
        self.system_prompt = """You are a personal AI assistant with access to the user's Obsidian vault and development tools. You can execute slash commands, run hooks, use tools, and spawn agents to help with tasks."""

    async def generate_response(
        self,
        messages: list[dict],
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate LLM response with streaming"""

        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *messages
        ]

        if stream:
            stream = ollama.chat(
                model=self.model,
                messages=full_messages,
                stream=True
            )

            for chunk in stream:
                yield chunk['message']['content']
        else:
            response = ollama.chat(
                model=self.model,
                messages=full_messages
            )
            yield response['message']['content']

# backend/routers/chat.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    stream: bool = True

@router.post("/message")
async def chat_message(request: ChatRequest):
    """Send message to LLM"""

    llm = LLMService()

    if request.stream:
        async def generate():
            async for chunk in llm.generate_response(
                [msg.dict() for msg in request.messages],
                stream=True
            ):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )
    else:
        response = ""
        async for chunk in llm.generate_response(
            [msg.dict() for msg in request.messages],
            stream=False
        ):
            response += chunk

        return {"response": response}
```

**Frontend Implementation:**

```typescript
// frontend/src/components/ChatInterface.tsx
import { useState } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat/message', {
        messages: [...messages, userMessage],
        stream: false
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
```

**Deliverables:**
- [ ] Chat interface accepts user input
- [ ] Messages sent to Ollama via FastAPI
- [ ] Responses displayed in UI
- [ ] Conversation history maintained

### Day 5-7: Slash Command System

**Goal:** Parse and execute slash commands

**Tasks:**
```gherkin
Given a chat message starting with "/"
When the message is sent to the backend
Then the system should:
- Parse command name and arguments
- Load command definition from .ai/commands/
- Execute command with context
- Return formatted response
```

**Implementation:**

```python
# backend/services/command_service.py
import re
import yaml
from pathlib import Path
from typing import Optional, Dict

class CommandService:
    def __init__(self, commands_dir: Path):
        self.commands_dir = commands_dir
        self.commands = self._load_commands()

    def _load_commands(self) -> Dict[str, Dict]:
        """Load all command definitions from .ai/commands/"""
        commands = {}

        if not self.commands_dir.exists():
            return commands

        for cmd_file in self.commands_dir.glob("*.md"):
            with open(cmd_file, 'r') as f:
                content = f.read()

                # Parse frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        body = parts[2].strip()

                        commands[frontmatter['name']] = {
                            'definition': frontmatter,
                            'prompt': body
                        }

        return commands

    def parse_command(self, message: str) -> Optional[Dict]:
        """Parse slash command from message"""
        match = re.match(r'^/(\w+)(?:\s+(.*))?$', message.strip())

        if not match:
            return None

        cmd_name, cmd_args = match.groups()

        if cmd_name not in self.commands:
            return {
                'error': f"Unknown command: /{cmd_name}",
                'available': list(self.commands.keys())
            }

        return {
            'name': cmd_name,
            'args': cmd_args or '',
            'definition': self.commands[cmd_name]
        }

    def execute_command(self, command: Dict, context: Dict) -> str:
        """Execute a command by expanding its prompt template"""

        prompt = command['definition']['prompt']

        # Replace template variables
        prompt = prompt.replace('{{task_description}}', command['args'])
        prompt = prompt.replace('{{user_name}}', context.get('user_name', 'User'))

        return prompt
```

**Example Command Definition:**

```markdown
# .ai/commands/vmodel.md
---
name: vmodel
description: Execute full V-model development process
hooks:
  pre: pre-vmodel
  post: post-vmodel
---

# V-Model Development Workflow

You are executing the V-Model development process for the following task:

**Task:** {{task_description}}

## Step 1: Requirements Analysis
Analyze the requirements and break down into:
- Functional requirements
- Non-functional requirements
- Acceptance criteria (Gherkin format)

## Step 2: System Design
Create high-level design:
- Architecture decisions
- Component interactions
- Data flow

## Step 3: Implementation
Write code following best practices:
- Clean code principles
- Security considerations
- Error handling

## Step 4: Testing
Create comprehensive tests:
- Unit tests
- Integration tests
- End-to-end tests

## Step 5: Verification
Verify against acceptance criteria:
- All scenarios pass
- No regressions
- Code review completed

Please proceed with Step 1: Requirements Analysis.
```

**Deliverables:**
- [ ] Command parser recognizes `/` prefix
- [ ] Commands loaded from `.ai/commands/`
- [ ] Template variables replaced
- [ ] Command execution integrated with LLM

---

## Week 2: Tools and Hooks

### Day 8-10: Tool System

**Goal:** LLM can call tools (read files, execute bash, search vault)

**Tasks:**
```gherkin
Given a conversation with the LLM
When the LLM needs to perform an action
Then the system should:
- Detect tool call from LLM response
- Execute tool with sanitized parameters
- Return result to LLM
- Continue conversation flow
```

**Implementation:**

```python
# backend/services/tool_service.py
from pathlib import Path
import subprocess
import shlex
from typing import Dict, Any

class ToolService:
    ALLOWED_COMMANDS = ['git', 'npm', 'python', 'pytest', 'ls', 'cat', 'grep']
    BLOCKED_PATTERNS = ['rm -rf /', 'dd ', '> /dev/', 'mkfs', 'chmod 777']

    def __init__(self, vault_path: Path, workspace_path: Path):
        self.vault_path = vault_path
        self.workspace_path = workspace_path

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """Execute a tool and return result"""

        if tool_name == "read_file":
            return self._read_file(parameters['path'])

        elif tool_name == "write_file":
            return self._write_file(parameters['path'], parameters['content'])

        elif tool_name == "execute_bash":
            return self._execute_bash(parameters['command'])

        elif tool_name == "search_vault":
            return self._search_vault(parameters['query'])

        elif tool_name == "list_files":
            return self._list_files(parameters.get('pattern', '*'))

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _read_file(self, path: str) -> Dict:
        """Read file contents with path traversal protection"""
        try:
            file_path = self._sanitize_path(path)
            content = file_path.read_text()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _write_file(self, path: str, content: str) -> Dict:
        """Write file contents"""
        try:
            file_path = self._sanitize_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return {"success": True, "message": f"Wrote {len(content)} bytes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_bash(self, command: str) -> Dict:
        """Execute bash command with safety checks"""
        try:
            # Check for dangerous patterns
            for pattern in self.BLOCKED_PATTERNS:
                if pattern in command.lower():
                    return {
                        "success": False,
                        "error": f"Blocked dangerous pattern: {pattern}"
                    }

            # Parse command
            tokens = shlex.split(command)
            if tokens[0] not in self.ALLOWED_COMMANDS:
                return {
                    "success": False,
                    "error": f"Command not allowed: {tokens[0]}"
                }

            # Execute with timeout
            result = subprocess.run(
                tokens,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.workspace_path
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_vault(self, query: str) -> Dict:
        """Search Obsidian vault"""
        try:
            results = []
            for md_file in self.vault_path.rglob("*.md"):
                content = md_file.read_text()
                if query.lower() in content.lower():
                    # Get surrounding context
                    lines = content.split('\n')
                    matches = [
                        (i, line) for i, line in enumerate(lines)
                        if query.lower() in line.lower()
                    ]

                    results.append({
                        "file": str(md_file.relative_to(self.vault_path)),
                        "matches": len(matches),
                        "preview": matches[0][1][:100] if matches else ""
                    })

            return {
                "success": True,
                "results": results,
                "total": len(results)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _sanitize_path(self, user_path: str) -> Path:
        """Prevent path traversal attacks"""
        # Try workspace first, then vault
        for base_dir in [self.workspace_path, self.vault_path]:
            requested = (base_dir / user_path).resolve()
            if requested.is_relative_to(base_dir):
                return requested

        raise ValueError(f"Path outside allowed directories: {user_path}")
```

**Tool Definitions for LLM:**

```python
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to file"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "execute_bash",
        "description": "Execute a bash command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "search_vault",
        "description": "Search the Obsidian vault for content",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    }
]
```

**Deliverables:**
- [ ] Tool service with 5+ tools
- [ ] Path traversal protection
- [ ] Bash command whitelisting
- [ ] Vault search functionality
- [ ] LLM can call tools and receive results

### Day 11-12: Hook System

**Goal:** Execute hooks before/after commands and tool calls

**Tasks:**
```gherkin
Given a command or tool execution
When hooks are configured for that action
Then the system should:
- Execute pre-hooks before action
- Block action if pre-hook fails
- Execute action if pre-hook passes
- Execute post-hooks after action
- Log all hook results
```

**Implementation:**

```python
# backend/services/hook_service.py
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List

class HookService:
    def __init__(self, hooks_dir: Path):
        self.hooks_dir = hooks_dir

    def execute_hook(
        self,
        hook_name: str,
        context: Dict,
        hook_type: str = "pre"
    ) -> Dict:
        """Execute a hook script"""

        hook_path = self.hooks_dir / f"{hook_name}.py"

        if not hook_path.exists():
            return {
                "success": True,
                "message": f"Hook {hook_name} not found, skipping"
            }

        try:
            # Execute hook with context as JSON
            result = subprocess.run(
                ["python3", str(hook_path)],
                input=json.dumps(context),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }

            # Parse hook response
            try:
                response = json.loads(result.stdout)
                return {
                    "success": response.get("valid", True),
                    "message": response.get("message", ""),
                    "errors": response.get("errors", [])
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_command_hooks(
        self,
        command_name: str,
        command_def: Dict,
        context: Dict
    ) -> tuple[bool, List[str]]:
        """Execute pre and post hooks for a command"""

        errors = []

        # Pre-hook
        if "hooks" in command_def.get("definition", {}) and "pre" in command_def["definition"]["hooks"]:
            pre_hook = command_def["definition"]["hooks"]["pre"]
            result = self.execute_hook(pre_hook, context, "pre")

            if not result["success"]:
                errors.append(f"Pre-hook failed: {result.get('error', 'Unknown error')}")
                return False, errors

        return True, errors
```

**Example Hook:**

```python
#!/usr/bin/env python3
# .ai/hooks/lint-gherkin.py

import sys
import json
import re

def lint_gherkin(text: str) -> dict:
    """Validate Gherkin acceptance criteria"""
    errors = []
    warnings = []

    # Check for required keywords
    if not re.search(r'^\s*(Given|When|Then)', text, re.MULTILINE | re.IGNORECASE):
        errors.append("Missing Given/When/Then structure")

    # Check for Feature keyword
    if 'Feature:' not in text and 'Scenario:' not in text:
        warnings.append("No Feature or Scenario keyword found")

    # Check for And abuse
    and_count = len(re.findall(r'^\s*And', text, re.MULTILINE))
    if and_count > 5:
        warnings.append(f"Too many 'And' clauses ({and_count}), consider breaking into multiple scenarios")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

if __name__ == "__main__":
    context = json.loads(sys.stdin.read())
    text = context.get("text", "")

    result = lint_gherkin(text)
    print(json.dumps(result))
```

**Deliverables:**
- [ ] Hook execution service
- [ ] Pre-hook blocking capability
- [ ] Post-hook execution
- [ ] Example lint-gherkin hook
- [ ] Hook results logged

### Day 13-14: TODO Tracking

**Goal:** Track tasks with Gherkin acceptance criteria

**Tasks:**
```gherkin
Given a conversation with multiple tasks
When the LLM creates a TODO item
Then the system should:
- Store TODO with Gherkin acceptance criteria
- Track status (pending, in_progress, completed)
- Display TODOs in UI
- Update status as work progresses
- Block completion if acceptance criteria not met
```

**Implementation:**

```python
# backend/services/todo_service.py
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class TodoStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Todo(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    active_form = Column(String, nullable=False)
    status = Column(Enum(TodoStatus), default=TodoStatus.PENDING)
    acceptance_criteria = Column(Text)  # Gherkin format
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class TodoService:
    def __init__(self, db_session):
        self.db = db_session

    def create_todo(self, content: str, active_form: str, acceptance_criteria: str) -> Todo:
        """Create a new TODO"""
        todo = Todo(
            id=self._generate_id(),
            content=content,
            active_form=active_form,
            acceptance_criteria=acceptance_criteria
        )
        self.db.add(todo)
        self.db.commit()
        return todo

    def update_status(self, todo_id: str, status: TodoStatus) -> bool:
        """Update TODO status"""
        todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            return False

        todo.status = status
        if status == TodoStatus.COMPLETED:
            todo.completed_at = datetime.utcnow()

        self.db.commit()
        return True

    def get_active_todos(self) -> list[Todo]:
        """Get all non-completed TODOs"""
        return self.db.query(Todo).filter(
            Todo.status != TodoStatus.COMPLETED
        ).all()
```

**Deliverables:**
- [ ] TODO database model
- [ ] CRUD operations for TODOs
- [ ] Gherkin validation on creation
- [ ] UI displays TODO list
- [ ] Status updates working

---

## Week 3: Agents and Polish

### Day 15-17: Multi-Agent System

**Goal:** Spawn specialized agents for specific tasks

**Tasks:**
```gherkin
Given a complex task requiring exploration
When the user or LLM requests agent assistance
Then the system should:
- Load agent definition from .ai/agents/
- Create isolated agent context
- Execute agent with specialized tools
- Return agent results to main conversation
- Log agent execution for debugging
```

**Implementation:**

```python
# backend/services/agent_service.py
import yaml
from pathlib import Path
from typing import Dict, List

class AgentService:
    def __init__(self, agents_dir: Path, llm_service, tool_service):
        self.agents_dir = agents_dir
        self.llm_service = llm_service
        self.tool_service = tool_service
        self.agents = self._load_agents()

    def _load_agents(self) -> Dict:
        """Load agent definitions"""
        agents = {}

        for agent_file in self.agents_dir.glob("*.yaml"):
            with open(agent_file, 'r') as f:
                agent_def = yaml.safe_load(f)
                agents[agent_def['name']] = agent_def

        return agents

    async def execute_agent(
        self,
        agent_name: str,
        task: str,
        context: Dict
    ) -> Dict:
        """Execute an agent with a specific task"""

        if agent_name not in self.agents:
            return {"error": f"Unknown agent: {agent_name}"}

        agent_def = self.agents[agent_name]

        # Build agent context
        agent_messages = [
            {
                "role": "system",
                "content": agent_def['system_prompt']
            },
            {
                "role": "user",
                "content": f"Task: {task}\n\nContext: {context}"
            }
        ]

        # Execute agent with specialized tools
        response_parts = []
        async for chunk in self.llm_service.generate_response(
            agent_messages,
            stream=True
        ):
            response_parts.append(chunk)

        full_response = "".join(response_parts)

        return {
            "success": True,
            "agent": agent_name,
            "response": full_response
        }
```

**Example Agent Definition:**

```yaml
# .ai/agents/explore-agent.yaml
name: explore
description: Fast exploration agent for finding code and files
model: llama3:8b
tools:
  - glob_files
  - grep_files
  - read_file
  - search_vault
system_prompt: |
  You are a fast exploration agent specialized in finding code, files, and patterns in the codebase.

  Your goal is to quickly locate relevant files and provide concise summaries.

  Available tools:
  - glob_files: Find files matching a pattern (e.g., "**/*.py")
  - grep_files: Search file contents for text or regex
  - read_file: Read file contents
  - search_vault: Search Obsidian vault

  Be concise and direct. Return file paths and line numbers.
  If you find what you're looking for, report immediately.

  Format your response as:
  - **Found:** [file paths]
  - **Summary:** [brief explanation]
  - **Next steps:** [recommendations if applicable]
```

**Deliverables:**
- [ ] Agent loading from YAML definitions
- [ ] Agent execution with isolated context
- [ ] Tool access limited per agent
- [ ] Example explore, plan, and review agents
- [ ] Agent results integrated in chat

### Day 18-19: Security Hardening

**Goal:** Implement core security measures

**Tasks:**
```gherkin
Given a working application
When implementing security measures
Then the system should have:
- JWT authentication for API
- Password hashing with bcrypt
- Rate limiting on endpoints
- Input sanitization for all user inputs
- HTTPS with self-signed certificate (dev)
- Security headers on all responses
```

**Implementation:**

```python
# backend/auth/jwt_service.py
from datetime import datetime, timedelta
import jwt
import bcrypt

SECRET_KEY = "your-secret-key-here"  # Load from env in production

class AuthService:
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    def create_token(self, user_id: str, username: str) -> str:
        """Create JWT token"""
        payload = {
            "sub": user_id,
            "username": username,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
```

```python
# backend/middleware/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    async def check_rate_limit(
        self,
        request: Request,
        max_requests: int = 60,
        window_seconds: int = 60
    ):
        """Check if request exceeds rate limit"""
        client_ip = request.client.host
        now = datetime.utcnow()

        # Clean old requests
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        # Add current request
        self.requests[client_ip].append(now)
```

**Deliverables:**
- [ ] JWT authentication working
- [ ] Password hashing implemented
- [ ] Rate limiting on chat endpoint
- [ ] Input sanitization on all inputs
- [ ] Self-signed cert for HTTPS

### Day 20-21: Testing and Documentation

**Goal:** Comprehensive testing and user documentation

**Tasks:**
```gherkin
Given a completed Phase 1 system
When running the test suite
Then all tests should pass:
- Unit tests for services (80%+ coverage)
- Integration tests for API endpoints
- End-to-end tests for critical flows
- Security tests for auth and sanitization
```

**Testing Implementation:**

```python
# backend/tests/test_command_service.py
import pytest
from services.command_service import CommandService
from pathlib import Path

def test_parse_command():
    service = CommandService(Path(".ai/commands"))

    # Test valid command
    result = service.parse_command("/vmodel Implement user auth")
    assert result is not None
    assert result['name'] == 'vmodel'
    assert result['args'] == 'Implement user auth'

    # Test invalid command
    result = service.parse_command("not a command")
    assert result is None

def test_command_execution():
    service = CommandService(Path(".ai/commands"))
    command = service.parse_command("/vmodel Test task")

    result = service.execute_command(command, {"user_name": "Jack"})
    assert "Test task" in result
    assert "Requirements Analysis" in result
```

**Deliverables:**
- [ ] 50+ unit tests
- [ ] 20+ integration tests
- [ ] 5+ end-to-end tests
- [ ] Test coverage report
- [ ] User documentation (README)

---

## Phase 1 Completion Checklist

### Core Features
- [ ] Web chat interface working
- [ ] Slash commands parsing and execution
- [ ] Tools (read, write, bash, search) working
- [ ] Hooks (pre/post) executing
- [ ] Agents (explore, plan, review) spawning
- [ ] TODO tracking with Gherkin

### Security
- [ ] JWT authentication
- [ ] Bcrypt password hashing
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] Path traversal protection
- [ ] Bash command whitelisting

### Quality
- [ ] 80%+ test coverage
- [ ] No critical security vulnerabilities
- [ ] Documentation complete
- [ ] All examples working

### Performance
- [ ] Chat responses < 2 seconds
- [ ] Vault search < 1 second
- [ ] Agent execution < 10 seconds
- [ ] No memory leaks

---

## Success Metrics

**Technical:**
- All tests passing
- No security vulnerabilities
- Chat interface responsive
- Slash commands working
- Tools executing safely

**User Experience:**
- Can chat naturally with AI
- Slash commands feel native
- TODOs help track progress
- Agents provide value
- System feels like Claude Code

**Readiness for Phase 2:**
- Codebase clean and documented
- Security foundations solid
- Easy to containerize
- Database ready for PostgreSQL migration

---

## Next Steps After Phase 1

Once Phase 1 is complete:

1. **Review and Refine**
   - Test all features end-to-end
   - Fix any bugs discovered
   - Optimize performance bottlenecks

2. **Prepare for Phase 2**
   - Create Dockerfiles
   - Plan PostgreSQL migration
   - Design Tailscale VPN setup

3. **User Acceptance**
   - Use the system daily for 1 week
   - Collect feedback
   - Adjust based on real usage

4. **Begin Phase 2**
   - Follow PHASE-2-PLAN.md
   - Deploy to home server
   - Enable remote access

---

**Last Updated:** 2025-11-09
**Status:** Ready for Implementation
**Estimated Effort:** 60-80 hours over 3 weeks
