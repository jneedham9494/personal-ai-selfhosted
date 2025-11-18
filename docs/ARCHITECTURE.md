# System Architecture

**Version:** 1.0
**Date:** 2025-11-09
**Status:** Design Phase

---

## Executive Summary

A secure, self-hosted AI assistant system with local LLM processing, web-based interface, and deep integration with your Obsidian knowledge base. Built for privacy, security, and complete data ownership.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web UI     │  │   Mobile     │  │   Desktop    │     │
│  │   Browser    │  │   Browser    │  │   Browser    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTPS (TLS 1.3)
          ┌──────────────────▼──────────────────┐
          │   Nginx Reverse Proxy (Port 443)    │
          │   - TLS Termination                 │
          │   - Rate Limiting                   │
          │   - Security Headers                │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      FastAPI Backend Server         │
          │   ┌─────────────────────────────┐   │
          │   │  Authentication Middleware  │   │
          │   │  - JWT Validation           │   │
          │   │  - Rate Limiting            │   │
          │   │  - Request Sanitization     │   │
          │   └──────────┬──────────────────┘   │
          │              │                       │
          │   ┌──────────▼──────────────────┐   │
          │   │      API Endpoints          │   │
          │   │  /chat, /vault, /goals      │   │
          │   └──────────┬──────────────────┘   │
          └──────────────┼──────────────────────┘
                         │
          ┌──────────────┴──────────────────┐
          │                                 │
┌─────────▼─────────┐         ┌───────────▼──────────┐
│   LLM Service     │         │   Knowledge Service   │
│   (Ollama)        │         │   (Obsidian Vault)    │
│                   │         │                       │
│  - Model: Llama3  │         │  - File Reader        │
│  - Context: 8K    │         │  - Semantic Search    │
│  - Temperature    │         │  - RAG Pipeline       │
└─────────┬─────────┘         └───────────┬──────────┘
          │                               │
          │                               │
┌─────────▼───────────────────────────────▼──────────┐
│              Storage Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │  PostgreSQL  │  │   Obsidian   │  │ Chroma  │ │
│  │  - Users     │  │   Vault      │  │ Vector  │ │
│  │  - Sessions  │  │   (Markdown) │  │   DB    │ │
│  │  - Logs      │  │              │  │         │ │
│  └──────────────┘  └──────────────┘  └─────────┘ │
└────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Web Interface (Frontend)

**Technology:** React + TypeScript + Vite

**Features:**
- Chat interface with markdown support
- Dark mode (respects system preference)
- Mobile-responsive design
- Real-time streaming responses
- Goal tracking dashboard
- Vault search interface

**Security:**
- Content Security Policy (CSP)
- XSS protection via React
- CSRF tokens
- Input sanitization
- Secure cookie handling

**File Structure:**
```
src/frontend/
├── components/
│   ├── Chat/
│   ├── Dashboard/
│   ├── Auth/
│   └── VaultBrowser/
├── hooks/
├── services/
│   ├── api.ts
│   └── auth.ts
├── store/
│   └── userStore.ts
└── App.tsx
```

---

### 2. API Server (Backend)

**Technology:** Python 3.11 + FastAPI

**Features:**
- RESTful API design
- WebSocket support for streaming
- JWT authentication
- Rate limiting (per-user, per-endpoint)
- Request/response logging
- Async operations

**Key Endpoints:**

**Authentication:**
- `POST /auth/login` - User login (JWT)
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - Session invalidation

**Chat:**
- `POST /chat/message` - Send message to LLM
- `GET /chat/stream` - WebSocket for streaming responses
- `GET /chat/history` - Retrieve conversation history
- `DELETE /chat/session/{id}` - Clear chat session

**Vault:**
- `GET /vault/search` - Search Obsidian vault
- `GET /vault/file/{path}` - Read specific file
- `POST /vault/query` - Semantic search (RAG)
- `GET /vault/recent` - Recent notes

**Goals:**
- `GET /goals/progress` - Q4 goal progress
- `POST /goals/update` - Update goal metrics
- `GET /goals/dashboard` - Dashboard data

**System:**
- `GET /health` - Health check
- `GET /metrics` - System metrics (admin only)

**File Structure:**
```
src/backend/
├── api/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── vault.py
│   │   └── goals.py
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   ├── rate_limit.py
│   │   └── security.py
│   └── dependencies.py
├── services/
│   ├── llm_service.py
│   ├── vault_service.py
│   ├── rag_service.py
│   └── nudging_service.py
├── models/
│   ├── user.py
│   ├── chat.py
│   └── goal.py
├── database/
│   ├── connection.py
│   └── migrations/
├── config.py
└── main.py
```

---

### 3. LLM Service (Ollama)

**Technology:** Ollama + Llama 3

**Model Selection:**
- **Phase 1 (Mac):** Llama 3 8B (fits M4 memory)
- **Phase 2 (Server):** Llama 3 70B or Mixtral 8x7B

**Features:**
- Local inference (no cloud)
- Context window: 8K tokens
- Streaming responses
- Temperature control per-request
- System prompt injection (personality, rules)

**Integration:**
```python
import ollama

response = ollama.chat(
    model='llama3',
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message}
    ],
    stream=True
)
```

**System Prompt:**
```
You are a personal AI assistant helping Jack achieve his Q4 2025 goals.

Your knowledge base:
- Obsidian vault with Q4 goals, daily notes, and anti-quit strategies
- Current date: {current_date}
- User's goals: Fitness (4x/week gym), Finance (expense tracking),
  Digital Wellness (reduce screen time), XRPL (learn blockchain)

Your personality:
- Direct and concise
- Accountability-focused
- Supportive but honest
- Security-conscious

When user asks about goals:
1. Check recent daily notes for progress
2. Highlight patterns (good or concerning)
3. Remind of anti-quit strategies if needed
4. Provide actionable next steps
```

---

### 4. Knowledge Service (Obsidian Vault Integration)

**Technology:** Python file reading + ChromaDB (vector store)

**Features:**
- Read-only access to Obsidian vault
- Markdown parsing (frontmatter + content)
- Tag extraction
- Link resolution
- Semantic search via embeddings

**RAG Pipeline:**

```
User Query
    ↓
1. Query Embedding (sentence-transformers)
    ↓
2. Vector Search (ChromaDB)
    ↓
3. Top-K Relevant Docs (k=5)
    ↓
4. Context Injection into LLM Prompt
    ↓
5. LLM Response with Citations
```

**Embedding Model:**
- `all-MiniLM-L6-v2` (fast, good quality)
- 384 dimensions
- Stored in ChromaDB

**File Structure:**
```
src/backend/services/vault_service.py
src/backend/services/rag_service.py
src/backend/services/embedding_service.py
```

---

### 5. Storage Layer

**Development (Phase 1):**
- **SQLite** - User data, sessions, chat logs
- **File System** - Obsidian vault (read-only)
- **ChromaDB** - Vector embeddings

**Production (Phase 2):**
- **PostgreSQL** - User data, sessions, chat logs
- **File System** - Obsidian vault (read-only via mount)
- **ChromaDB** - Vector embeddings (persistent volume)

**Database Schema:**

**Users Table:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Sessions Table:**
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT
);
```

**Chat Messages Table:**
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id UUID,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Goals Table:**
```sql
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    goal_type VARCHAR(50) NOT NULL, -- 'fitness', 'finance', etc.
    current_value INTEGER,
    target_value INTEGER,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Data Flow

### Chat Request Flow

```
1. User sends message via Web UI
   ↓
2. POST /chat/message with JWT token
   ↓
3. Nginx validates TLS, forwards to FastAPI
   ↓
4. Auth Middleware validates JWT
   ↓
5. Rate Limiter checks user quota
   ↓
6. RAG Service searches Obsidian vault for context
   ↓
7. LLM Service sends [system + context + user message] to Ollama
   ↓
8. Ollama streams response tokens
   ↓
9. FastAPI streams back to client via WebSocket
   ↓
10. Web UI displays streaming response
   ↓
11. Message saved to database (both user + assistant)
```

### Goal Update Flow

```
1. Daily note updated in Obsidian (manual)
   ↓
2. File watcher detects change (optional)
   ↓
3. Embedding service re-indexes changed file
   ↓
4. User opens dashboard
   ↓
5. GET /goals/dashboard
   ↓
6. Backend reads Obsidian vault for recent daily notes
   ↓
7. Extracts frontmatter (habits_completed, energy_level, etc.)
   ↓
8. Calculates progress metrics
   ↓
9. Returns JSON to frontend
   ↓
10. Dashboard renders progress bars and charts
```

---

## Security Architecture

See [SECURITY.md](./SECURITY.md) for detailed security design.

**Key Principles:**
1. **Defense in Depth** - Multiple security layers
2. **Least Privilege** - Minimal permissions
3. **Zero Trust** - Verify everything
4. **Encryption Everywhere** - TLS + encrypted storage
5. **Audit Everything** - Comprehensive logging

---

## Deployment Architecture

### Phase 1: Mac Development

```
┌─────────────────────────────────────┐
│        M4 MacBook Pro (Local)       │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Web Browser (localhost:3000) │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │  Vite Dev Server (Port 3000) │  │
│  └──────────────┬───────────────┘  │
│                 │ API Proxy         │
│  ┌──────────────▼───────────────┐  │
│  │  FastAPI (Port 8000)         │  │
│  │  - Dev mode (hot reload)     │  │
│  │  - SQLite database           │  │
│  │  - Local Obsidian vault      │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │  Ollama (Port 11434)         │  │
│  │  - Llama 3 8B                │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Phase 2: Home Server Production

```
┌─────────────────────────────────────────────────────────┐
│                   Internet                              │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │  Tailscale/Wireguard│ (Secure VPN)
          │  - Encrypted tunnel  │
          └──────────┬───────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Home Server (Docker Host)                   │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Docker Compose Stack                    │  │
│  │                                                   │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │  Nginx Container (Port 443)              │   │  │
│  │  │  - TLS Termination (Let's Encrypt)       │   │  │
│  │  │  - Rate Limiting                         │   │  │
│  │  │  - Security Headers                      │   │  │
│  │  └────────────┬─────────────────────────────┘   │  │
│  │               │                                  │  │
│  │  ┌────────────▼─────────────────────────────┐   │  │
│  │  │  FastAPI Container                       │   │  │
│  │  │  - Production mode (gunicorn workers)    │   │  │
│  │  │  - PostgreSQL connection                 │   │  │
│  │  │  - Mounted Obsidian vault (read-only)    │   │  │
│  │  └────────────┬─────────────────────────────┘   │  │
│  │               │                                  │  │
│  │  ┌────────────▼─────────────────────────────┐   │  │
│  │  │  Ollama Container                        │   │  │
│  │  │  - Llama 3 70B (with GPU support)        │   │  │
│  │  │  - Model volume mount                    │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │  PostgreSQL Container                    │   │  │
│  │  │  - Persistent volume                     │   │  │
│  │  │  - Automated backups                     │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │  ChromaDB Container                      │   │  │
│  │  │  - Vector embeddings                     │   │  │
│  │  │  - Persistent volume                     │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  External Volumes                                 │  │
│  │  - /data/obsidian (read-only mount)              │  │
│  │  - /data/postgres (PostgreSQL data)               │  │
│  │  - /data/chroma (vector DB)                       │  │
│  │  - /data/backups (automated backups)              │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Scalability Considerations

**Current Design:** Single-user system

**Future Scaling (If Needed):**
1. Add Redis for session management
2. Add message queue (RabbitMQ) for async tasks
3. Horizontal scaling with load balancer
4. Separate read replicas for database
5. CDN for static assets

**For Now:** Keep it simple, single server is sufficient

---

## Technology Decisions

### Why FastAPI?
- Async/await support (perfect for streaming)
- Automatic API documentation (Swagger UI)
- Type safety with Pydantic
- Built-in security features
- Great performance

### Why Ollama?
- Dead simple local LLM setup
- Multiple model support
- Active development
- Good M4 optimization
- No Python dependencies needed

### Why React?
- Component reusability
- Strong TypeScript support
- Large ecosystem
- Good for real-time updates (chat)
- Familiar to most developers

### Why PostgreSQL (Production)?
- ACID compliance
- Strong security features
- Good for relational data
- Excellent backup tools
- Industry standard

### Why ChromaDB?
- Built for RAG use cases
- Easy Python integration
- Good performance
- Persistent storage
- Open source

---

## Non-Functional Requirements

**Performance:**
- LLM response latency: <2 seconds for first token
- Vault search: <500ms for results
- Dashboard load: <1 second
- Concurrent users: 1 (you)

**Reliability:**
- Uptime target: 99% (home server limitations)
- Auto-restart on failure
- Graceful degradation if LLM unavailable
- Data backup daily

**Security:**
- TLS 1.3 only
- No external dependencies once deployed
- Encrypted backups
- Audit logs for all actions
- Rate limiting to prevent abuse

**Maintainability:**
- Clear code structure
- Type hints everywhere
- Comprehensive logging
- Easy updates via Docker
- Rollback capability

---

## Next Steps

1. **Read Security Design:** [SECURITY.md](./SECURITY.md)
2. **Review Phase 1 Plan:** [PHASE-1-PLAN.md](./PHASE-1-PLAN.md)
3. **Start Implementation:** [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md)

---

**Last Updated:** 2025-11-09
**Approved By:** Jack
**Next Review:** After Phase 1 completion
