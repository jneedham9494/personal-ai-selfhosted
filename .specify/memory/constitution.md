# Project Constitution

**Project:** Personal AI Self-Hosted System
**Version:** 1.0.0
**Created:** 2025-11-18
**Status:** Phase 1 - Mac Development

---

## Project Identity

### Purpose
A secure, self-hosted personal AI assistant with local LLM and web interface. Privacy-first system that integrates with Obsidian knowledge base, runs on local hardware, and provides intelligent assistance without external service dependencies.

### Core Values
1. **Security First** - End-to-end encryption, local processing, no cloud dependencies
2. **Privacy** - All data stays on user's hardware
3. **Simplicity** - Clean, focused functionality over feature bloat
4. **Self-Contained** - Minimal external dependencies

---

## Architecture Standards

### Project Structure
```
personal-ai-selfhosted/
├── backend/                    # Python FastAPI server
│   ├── main.py                 # Application entry point
│   ├── routers/                # API endpoint routes
│   ├── services/               # Business logic layer
│   │   ├── commands/           # Slash command handling
│   │   └── tools/              # Utility tools
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React + TypeScript UI
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── App.tsx             # Main app component
│   │   └── main.tsx            # Entry point
│   ├── tests/                  # Playwright E2E tests
│   └── package.json            # npm dependencies
├── .ai/commands/               # Command definitions (JSON)
├── .specify/                   # SpecKit specifications
├── docs/                       # Project documentation
└── .env                        # Environment variables
```

### Backend Architecture
- **Framework:** FastAPI with async support
- **Pattern:** Service-oriented architecture
- **Routers:** Route handlers in `routers/` directory
- **Services:** Business logic in `services/` directory
- **Tools:** Utility functions in `services/tools/` directory

### Frontend Architecture
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite
- **Pattern:** Single-page application with component-based architecture
- **State:** React hooks (useState, useEffect)
- **API Client:** Axios

---

## Code Standards

### Python (Backend)

#### File Organization
- Maximum file length: 300 lines
- Maximum function length: 40 lines
- One router per domain (chat, vault)
- Services encapsulate business logic

#### Naming Conventions
- Files: `snake_case.py`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: `_leading_underscore`

#### Type Hints
All functions MUST have type hints:
```python
def process_message(content: str, stream: bool = False) -> str | StreamingResponse:
    pass
```

#### Imports Organization
```python
# Standard library
import os
from pathlib import Path

# Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Local
from services.llm_service import LLMService
```

#### Error Handling
- Use specific exception types
- Always provide context in error messages
- Log errors with appropriate level
- Return user-friendly messages via HTTPException

```python
try:
    result = operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    raise HTTPException(status_code=404, detail=f"File not found: {path}")
```

#### Pydantic Models
All request/response bodies use Pydantic models:
```python
class MessageRequest(BaseModel):
    messages: list[dict[str, str]]
    stream: bool = False
```

### TypeScript (Frontend)

#### File Organization
- Components in `src/components/`
- Component files: `PascalCase.tsx`
- One component per file (primarily)

#### Naming Conventions
- Variables/functions: `camelCase`
- Components: `PascalCase`
- Interfaces/Types: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

#### TypeScript Strict Mode
- Always enabled (`strict: true`)
- No `any` types - use `unknown` and narrow
- Explicit return types on functions

#### React Patterns
- Functional components only
- Hooks for state and side effects
- Props destructuring
- Conditional rendering with `&&` or ternary

```typescript
const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    // Side effects
  }, []);

  return (
    <div>
      {messages.length > 0 && <MessageList messages={messages} />}
    </div>
  );
};
```

---

## Security Standards

### Input Validation (MANDATORY)
- All external input validated at API boundaries
- Use Pydantic models for request validation
- Validate path inputs to prevent traversal attacks
- Sanitize content before processing

### Path Security
```python
def is_path_safe(path: Path, allowed_base: Path) -> bool:
    """Verify path doesn't escape allowed directory."""
    resolved = path.resolve()
    return resolved.is_relative_to(allowed_base.resolve())
```

### API Security
- CORS restricted to localhost origins only
- Rate limiting on sensitive endpoints (prepared)
- JWT authentication for protected routes (prepared)
- No secrets in code - use environment variables

### Data Protection
- Read-only access to Obsidian vault
- No sensitive data in logs
- Secure session management (planned)

---

## Testing Standards

### E2E Tests (Frontend)
- Framework: Playwright
- Location: `frontend/tests/`
- Naming: `feature-name.spec.ts`

#### Test Structure
```typescript
test.describe('Feature Name', () => {
  test('should do something specific', async ({ page }) => {
    // Arrange
    await page.goto('/');

    // Act
    await page.click('#button');

    // Assert
    await expect(page.locator('#result')).toBeVisible();
  });
});
```

### Unit Tests (Backend) - TO BE IMPLEMENTED
- Framework: pytest
- Location: `backend/tests/`
- Coverage target: 80%
- Test naming: `test_<function>_<scenario>_<expected>`

---

## API Design Standards

### RESTful Conventions
- GET for retrieval
- POST for creation/actions
- PUT for updates
- DELETE for removal

### Route Organization
- Group by domain: `/chat`, `/vault`, `/goals`
- Consistent naming: plural nouns for collections
- Query params for filtering: `?limit=10`

### Response Format
```python
# Success
{"data": {...}, "count": 10}

# Error
{"detail": "Error message"}
```

### Streaming Responses
- Use `StreamingResponse` for LLM output
- Event-stream format with `data:` prefix

---

## Documentation Standards

### Code Documentation
- Docstrings for all public functions
- Comments explain "why" not "what"
- Type hints serve as documentation

#### Python Docstring Format
```python
def function_name(param: str) -> str:
    """
    Brief description of function.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        HTTPException: When something goes wrong
    """
```

### Project Documentation
- Architecture: `docs/ARCHITECTURE.md`
- Security: `docs/SECURITY.md`
- Phases: `docs/PHASE-X-PLAN.md`
- Features: `docs/PERSONAL-ASSISTANT-FEATURES.md`

---

## Development Workflow

### Local Development
1. Backend: `uvicorn main:app --reload` (port 8000)
2. Frontend: `npm run dev` (port 5173)
3. Ollama: Running on port 11434

### Testing
```bash
# Frontend E2E
cd frontend && npm test

# Run specific test
npm test -- --grep "test name"

# Headed mode
npm run test:headed
```

### Environment Variables
Required in `.env`:
- `VAULT_PATH` - Path to Obsidian vault
- `OLLAMA_HOST` - Ollama server URL (default: localhost:11434)

---

## Dependencies

### Backend (Critical)
- fastapi >= 0.104.1
- uvicorn >= 0.24.0
- pydantic >= 2.5.0
- ollama >= 0.1.6
- python-dotenv >= 1.0.0

### Frontend (Critical)
- react >= 19.2.0
- typescript >= 5.9.3
- vite >= 7.2.2
- axios >= 1.13.2
- @playwright/test >= 1.56.1

---

## Quality Gates

### Before Commit
- [ ] All tests pass
- [ ] No type errors (mypy/tsc)
- [ ] No lint errors
- [ ] Input validation complete
- [ ] Error handling implemented
- [ ] No TODO comments in new code

### Before Merge
- [ ] Code reviewed
- [ ] Security considerations addressed
- [ ] Documentation updated
- [ ] Acceptance criteria met

---

## Future Considerations

### Planned Features (Not Yet Implemented)
- JWT authentication system
- PostgreSQL database integration
- ChromaDB vector embeddings (RAG)
- WebSocket streaming
- Rate limiting
- Goal tracking dashboard

### Phase 2 Deployment
- Docker containerization
- Nginx reverse proxy
- Tailscale/Wireguard secure access
- Let's Encrypt TLS

---

## Amendment Process

To update this constitution:
1. Propose change with rationale
2. Review impact on existing code
3. Update relevant documentation
4. Apply change consistently across codebase

**Last Updated:** 2025-11-18
**Next Review:** After Phase 1 completion
