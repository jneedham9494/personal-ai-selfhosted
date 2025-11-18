# Next Steps

**Last Updated:** 2025-11-18

---

## Git Status: Ready

- [x] Repository initialized
- [x] .gitignore configured
- [x] .env.example for onboarding
- [x] Initial commit complete
- [x] Secrets protected (gitleaks passed)

### Push to Remote

```bash
# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/personal-ai-selfhosted.git
git push -u origin main
```

---

## Development Priorities

### Phase 1: Testing Foundation (Before adding features)

1. **Backend Test Setup** (1 day)
   ```bash
   mkdir -p backend/tests
   # Add pytest, pytest-cov to requirements.txt
   # Create conftest.py and first test
   ```

2. **Unit Tests for Services** (3-5 days)
   - FileTools (security critical)
   - LLMService
   - ObsidianService
   - CommandParser
   - Target: 70% coverage

### Phase 2: Security (Before deployment)

3. **JWT Authentication** (2-3 days)
   - Dependencies already installed
   - Protect /chat and /vault endpoints
   - Add /auth/login, /auth/refresh endpoints

4. **Rate Limiting** (1 day)
   - Add slowapi or similar
   - Protect against abuse

### Phase 3: Features (After foundation solid)

5. **Message Persistence** - Store chat history
6. **Streaming UI** - Show tokens as they arrive
7. **Dark Mode** - System preference detection
8. **Component Refactoring** - Split ChatInterface

---

## Quick Reference

### Run the App

```bash
# Terminal 1: Backend
cd backend
source ../venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Run Tests

```bash
# Frontend E2E (requires servers running)
cd frontend && npm test

# Backend (once tests exist)
cd backend && pytest
```

### Key Files

| Purpose | Location |
|---------|----------|
| Backend entry | [backend/main.py](backend/main.py) |
| Chat API | [backend/routers/chat.py](backend/routers/chat.py) |
| Vault API | [backend/routers/vault.py](backend/routers/vault.py) |
| Frontend UI | [frontend/src/components/ChatInterface.tsx](frontend/src/components/ChatInterface.tsx) |
| Project specs | [.specify/](.specify/) |
| Roadmap | [.specify/memory/plans/improvement-roadmap.md](.specify/memory/plans/improvement-roadmap.md) |

---

## Connected Systems

- **Ollama:** localhost:11434 (must be running)
- **Obsidian Vault:** Configured in .env (`OBSIDIAN_VAULT_PATH`)

---

**Full roadmap:** [.specify/memory/plans/improvement-roadmap.md](.specify/memory/plans/improvement-roadmap.md)
