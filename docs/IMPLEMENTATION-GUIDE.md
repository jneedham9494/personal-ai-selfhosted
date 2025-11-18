# Implementation Guide

**Version:** 1.0
**Target:** Phase 1 (Mac Development)
**Time Estimate:** 2-4 hours for basic setup

---

## Prerequisites

Before starting, ensure you have:

### Required Software

**System Requirements:**
- macOS (M1/M2/M3/M4 Mac)
- 16GB+ RAM
- 50GB+ free disk space

**Development Tools:**
```bash
# Check versions
python3 --version  # Should be 3.11+
node --version     # Should be 18+
npm --version      # Should be 9+
git --version      # Should be 2.0+

# Install missing tools
# Python 3.11+
brew install python@3.11

# Node.js 18+
brew install node

# Git
brew install git
```

**Ollama (Local LLM):**
```bash
# Install Ollama
brew install ollama

# Start Ollama service
brew services start ollama

# Pull Llama 3 model (this will take 10-15 minutes, ~4.7GB download)
ollama pull llama3:8b

# Verify installation
ollama list
```

### Obsidian Vault Access

The system needs read access to your Obsidian vault:

```bash
# Your vault path
export OBSIDIAN_VAULT_PATH="/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi"

# Verify access
ls "$OBSIDIAN_VAULT_PATH"
```

---

## Quick Start (30 Minutes)

### Step 1: Clone and Setup Project

```bash
# Navigate to development directory
cd /Users/jackdev/development

# The project structure already exists
cd personal-ai-selfhosted

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Create requirements file
cat > backend/requirements.txt <<EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
python-dotenv==1.0.0
ollama==0.1.6
chromadb==0.4.18
EOF

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Step 2: Create Project Structure

```bash
# Create directory structure
mkdir -p backend/{services,routers,models,middleware,auth}
mkdir -p backend/.ai/{commands,hooks,agents}
mkdir -p backend/data
mkdir -p backend/logs
mkdir -p frontend/src/{components,pages,services}
mkdir -p nginx
mkdir -p scripts

# Create .env file
cat > .env <<EOF
# Application
APP_NAME="Personal AI Assistant"
DEBUG=true
PORT=8000

# Database
DATABASE_URL="sqlite:///./data/dev.db"

# Obsidian
OBSIDIAN_VAULT_PATH="/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi"

# LLM
OLLAMA_HOST="http://localhost:11434"
DEFAULT_MODEL="llama3:8b"

# Security (generate new secrets for production)
JWT_SECRET="dev-secret-change-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION=3600

# Features
ENABLE_COMMANDS=true
ENABLE_HOOKS=true
ENABLE_AGENTS=true
ENABLE_TOOLS=true
EOF

echo "✅ Project structure created"
```

### Step 3: Create Basic Backend

```bash
# Create main.py
cat > backend/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Personal AI Assistant",
    description="Self-hosted AI assistant with Claude Code feature parity",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Personal AI Assistant API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ollama": "connected",  # TODO: Actually check Ollama
        "database": "connected"  # TODO: Actually check DB
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
EOF

echo "✅ Basic backend created"
```

### Step 4: Test Backend

```bash
# Start backend (in one terminal)
cd backend
source ../venv/bin/activate
python main.py

# In another terminal, test the API
curl http://localhost:8000/
curl http://localhost:8000/health

# Should see:
# {"status":"ok","message":"Personal AI Assistant API","version":"1.0.0"}
# {"status":"healthy","ollama":"connected","database":"connected"}
```

### Step 5: Create Basic Frontend

```bash
# Create React app with TypeScript
cd frontend
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Install additional packages
npm install axios @tanstack/react-query react-router-dom

# Create simple chat component
cat > src/components/ChatInterface.tsx <<'EOF'
import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // TODO: Send to backend
    const assistantMessage: Message = {
      role: 'assistant',
      content: 'Backend integration coming soon...'
    };
    setTimeout(() => {
      setMessages(prev => [...prev, assistantMessage]);
    }, 500);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Personal AI Assistant</h1>

      <div style={{
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        height: '400px',
        overflowY: 'auto'
      }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            marginBottom: '10px',
            padding: '10px',
            backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
            borderRadius: '4px'
          }}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
          style={{
            flex: 1,
            padding: '10px',
            fontSize: '16px',
            borderRadius: '4px',
            border: '1px solid #ccc'
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: '#1976d2',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
EOF

# Update App.tsx
cat > src/App.tsx <<'EOF'
import { ChatInterface } from './components/ChatInterface'
import './App.css'

function App() {
  return <ChatInterface />
}

export default App
EOF

# Start frontend
npm run dev

# Visit http://localhost:5173
```

**At this point you have:**
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ Basic chat interface
- ⏳ Now we'll add LLM integration

---

## Full Implementation

### Step 6: Add LLM Service

```bash
# Create LLM service
cat > backend/services/llm_service.py <<'EOF'
import ollama
from typing import AsyncGenerator, List, Dict
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, model: str = "llama3:8b"):
        self.model = model
        self.system_prompt = """You are a personal AI assistant with access to the user's Obsidian vault and development tools.

You can execute slash commands, run hooks, use tools, and spawn agents to help with tasks.

Key capabilities:
- Answer questions about the user's notes and goals
- Execute development tasks
- Search the knowledge base
- Track TODOs with acceptance criteria
- Run specialized agents for complex tasks

Be helpful, concise, and proactive."""

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate LLM response with streaming"""

        # Prepare messages
        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *messages
        ]

        try:
            if stream:
                # Stream response
                response_stream = ollama.chat(
                    model=self.model,
                    messages=full_messages,
                    stream=True
                )

                for chunk in response_stream:
                    content = chunk['message']['content']
                    yield content
            else:
                # Non-streaming response
                response = ollama.chat(
                    model=self.model,
                    messages=full_messages
                )
                yield response['message']['content']

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            yield f"Error: {str(e)}"

    def check_health(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            ollama.list()
            return True
        except Exception:
            return False
EOF
```

### Step 7: Add Chat Router

```bash
# Create chat router
cat > backend/routers/chat.py <<'EOF'
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import sys
sys.path.append('..')
from services.llm_service import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = True

@router.post("/message")
async def chat_message(request: ChatRequest):
    """Send message to LLM"""

    llm = LLMService()

    # Convert messages to dict format
    messages_dict = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    if request.stream:
        async def generate():
            async for chunk in llm.generate_response(messages_dict, stream=True):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )
    else:
        # Non-streaming response
        response_parts = []
        async for chunk in llm.generate_response(messages_dict, stream=False):
            response_parts.append(chunk)

        return {"response": "".join(response_parts)}

@router.get("/health")
async def chat_health():
    """Check if LLM is accessible"""
    llm = LLMService()
    healthy = llm.check_health()

    if not healthy:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    return {"status": "healthy", "model": "llama3:8b"}
EOF

# Update main.py to include router
cat > backend/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat
import uvicorn

app = FastAPI(
    title="Personal AI Assistant",
    description="Self-hosted AI assistant with Claude Code feature parity",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Personal AI Assistant API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ollama": "connected",
        "database": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
EOF
```

### Step 8: Connect Frontend to Backend

```bash
# Update ChatInterface.tsx with real backend integration
cat > frontend/src/components/ChatInterface.tsx <<'EOF'
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
    if (!input.trim() || loading) return;

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
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Personal AI Assistant</h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Powered by Llama 3 (Local LLM)
      </p>

      <div style={{
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        height: '500px',
        overflowY: 'auto',
        backgroundColor: '#fafafa'
      }}>
        {messages.length === 0 && (
          <div style={{ color: '#999', textAlign: 'center', marginTop: '100px' }}>
            Start a conversation...
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            marginBottom: '15px',
            padding: '12px',
            backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#fff',
            borderRadius: '8px',
            border: msg.role === 'assistant' ? '1px solid #e0e0e0' : 'none'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '5px', color: '#555' }}>
              {msg.role === 'user' ? '👤 You' : '🤖 Assistant'}
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{ color: '#999', fontStyle: 'italic' }}>
            Thinking...
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder="Type a message... (Press Enter to send)"
          disabled={loading}
          style={{
            flex: 1,
            padding: '12px',
            fontSize: '16px',
            borderRadius: '8px',
            border: '1px solid #ccc',
            outline: 'none',
            opacity: loading ? 0.6 : 1
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: loading ? '#ccc' : '#1976d2',
            color: 'white',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>

      <div style={{ marginTop: '20px', fontSize: '12px', color: '#999' }}>
        <strong>Try these commands:</strong>
        <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
          <li>/vmodel [task] - Execute V-Model development workflow</li>
          <li>/review - Review completed work against criteria</li>
          <li>Search my vault for [query] - Search Obsidian vault</li>
        </ul>
      </div>
    </div>
  );
}
EOF
```

---

## Testing Your Setup

### Test 1: Basic Chat

```bash
# Ensure backend is running
cd backend
source ../venv/bin/activate
python main.py

# In another terminal, ensure frontend is running
cd frontend
npm run dev

# Visit http://localhost:5173
# Type: "Hello! Can you help me?"
# You should get a response from Llama 3
```

### Test 2: Test with Vault Query

```
User: "What are my Q4 2025 goals?"
Assistant: [Should search vault and return info about your goals]
```

### Test 3: Health Check

```bash
# Test API health
curl http://localhost:8000/health

# Test chat health
curl http://localhost:8000/chat/health
```

---

## Creating Your First Slash Command

Let's create the `/vmodel` command:

```bash
# Create command definition
cat > backend/.ai/commands/vmodel.md <<'EOF'
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

### Functional Requirements
- What features are needed?
- What should the system do?

### Non-Functional Requirements
- Performance requirements
- Security requirements
- Usability requirements

### Acceptance Criteria (Gherkin Format)
```gherkin
Given [context]
When [action]
Then [expected result]
```

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
- Testing as you go

## Step 4: Testing

Create comprehensive tests:
- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for user flows

## Step 5: Verification

Verify against acceptance criteria:
- All scenarios pass
- No regressions introduced
- Code review completed
- Documentation updated

---

**Now, let's begin with Step 1: Requirements Analysis for your task.**
EOF

echo "✅ Created /vmodel command"
```

---

## Next Steps

You now have a working AI assistant! Here's what to do next:

### Immediate Next Steps (Today)

1. **Test the chat interface** - Have a conversation, see how it works
2. **Review the Phase 1 plan** - Understand what features to build next
3. **Create a TODO** - Track your next task

### This Week

1. **Implement slash command parser** - Make `/vmodel` actually work
2. **Add tool service** - Enable file reading, vault search
3. **Create hook system** - Run lint-gherkin on TODOs

### This Month

1. **Complete Phase 1** - All features working on Mac
2. **Start using it daily** - Replace Claude Code for some tasks
3. **Gather feedback** - What works? What doesn't?

### Next 3 Months

1. **Deploy Phase 2** - Move to home server
2. **Enable remote access** - Use from iPhone via Tailscale
3. **Full feature parity** - Replicate all Claude Code workflows

---

## Troubleshooting

### Issue: Ollama not responding

```bash
# Check if Ollama is running
brew services list | grep ollama

# Restart Ollama
brew services restart ollama

# Check models
ollama list

# Pull model again if missing
ollama pull llama3:8b
```

### Issue: Backend import errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: Frontend won't connect to backend

```bash
# Check CORS configuration in main.py
# Ensure your frontend URL is in allow_origins

# Check if backend is running
curl http://localhost:8000/health
```

### Issue: Vault search not working

```bash
# Verify vault path
echo $OBSIDIAN_VAULT_PATH

# Test access
ls "$OBSIDIAN_VAULT_PATH"

# Check permissions
ls -la "$OBSIDIAN_VAULT_PATH"
```

---

## Useful Commands

```bash
# Start backend
cd backend && source ../venv/bin/activate && python main.py

# Start frontend
cd frontend && npm run dev

# View logs
tail -f backend/logs/app.log

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"stream":false}'

# Check Ollama models
ollama list

# Pull new model
ollama pull llama3:70b
```

---

## Getting Help

**Documentation:**
- [README.md](../README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [PHASE-1-PLAN.md](PHASE-1-PLAN.md) - Development roadmap
- [SECURITY.md](SECURITY.md) - Security design

**Common Issues:**
- Ollama not responding → Restart service
- Backend errors → Check logs in `backend/logs/`
- Frontend errors → Check browser console
- Database errors → Check `backend/data/dev.db`

---

**Last Updated:** 2025-11-09
**Next Review:** After completing basic setup
