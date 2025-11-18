# Improvement Roadmap

**Created:** 2025-11-18
**Last Updated:** 2025-11-18
**Phase:** 1 - Mac Development

---

## Priority Framework

| Priority | Description | Timeline |
|----------|-------------|----------|
| P0 - Critical | Security/blocking issues | This week |
| P1 - High | Core functionality gaps | Next 2 weeks |
| P2 - Medium | Quality & UX improvements | Phase 1 |
| P3 - Low | Nice-to-have features | Phase 2+ |

---

## P0 - Critical Fixes

### Security Gaps
- [ ] **Implement JWT Authentication**
  - Files: New `backend/routers/auth.py`, `backend/services/auth_service.py`
  - Use prepared dependencies (python-jose, passlib)
  - Protect all endpoints except /health and /auth/*
  - Acceptance: Only authenticated users can access /chat and /vault

### Testing Foundation
- [ ] **Add Backend Unit Test Infrastructure**
  - Create `backend/tests/` directory structure
  - Configure pytest with coverage
  - Add CI pipeline for test runs
  - Acceptance: pytest runs with at least conftest.py and one passing test

---

## P1 - High Priority

### Testing Coverage
- [ ] **Unit Tests for LLM Service**
  - Test generate_response with mocked Ollama
  - Test streaming mode
  - Test error handling when Ollama down
  - Coverage target: 80%

- [ ] **Unit Tests for Obsidian Service**
  - Test list_files with mock filesystem
  - Test read_file with valid/invalid paths
  - Test search_vault with mock results
  - Coverage target: 80%

- [ ] **Unit Tests for Command Parser**
  - Test parse() for all command types
  - Test help handler
  - Test search handler
  - Test unknown command
  - Coverage target: 80%

- [ ] **Unit Tests for File Tools**
  - Test path validation
  - Test path traversal prevention
  - Test various path edge cases
  - Coverage target: 90% (security critical)

### Data Persistence
- [ ] **Message History Persistence**
  - Store messages in database (SQLite for Phase 1)
  - Load history on page load
  - Clear history endpoint
  - Acceptance: Messages survive page refresh

### Error Handling
- [ ] **Improve LLM Error Recovery**
  - Retry logic for transient failures
  - User-friendly error messages
  - Graceful degradation when Ollama unavailable
  - Acceptance: System doesn't crash when LLM fails

---

## P2 - Medium Priority

### User Experience
- [ ] **Streaming Response UI**
  - Display tokens as they arrive
  - Smooth animation for text appearance
  - Cancel button for long responses
  - Acceptance: User sees text appear progressively

- [ ] **Dark Mode Support**
  - Detect system preference
  - Toggle switch in UI
  - Persist preference
  - Acceptance: All components render correctly in both modes

- [ ] **Keyboard Shortcuts**
  - Ctrl/Cmd+Enter to send message
  - Escape to clear input
  - / to focus input
  - Acceptance: Shortcuts documented and working

### Code Quality
- [ ] **Refactor ChatInterface Component**
  - Extract MessageList component
  - Extract FileViewer component
  - Extract ChatInput component
  - Keep ChatInterface under 100 lines
  - Acceptance: No component > 150 lines

- [ ] **Add State Management**
  - Evaluate Zustand or Jotai
  - Centralize application state
  - Improve data flow
  - Acceptance: State logic separated from components

### API Improvements
- [ ] **Rate Limiting**
  - Add rate limiter middleware
  - Per-endpoint limits
  - Return 429 with retry-after
  - Acceptance: Abuse prevention tested

- [ ] **Audit Logging**
  - Log all API requests
  - Include user, timestamp, endpoint
  - Structured logging (JSON)
  - Acceptance: All actions traceable

### Features
- [ ] **Folder Tree in File Browser**
  - Show nested folder structure
  - Expand/collapse folders
  - Sort alphabetically
  - Acceptance: Easy navigation for large vaults

- [ ] **Search in File Browser**
  - Filter files by name
  - Quick search box
  - Acceptance: Find files without scrolling

---

## P3 - Low Priority (Phase 2)

### Advanced Features
- [ ] **ChromaDB Vector Embeddings**
  - Index vault on startup
  - Semantic search capability
  - RAG pipeline for context
  - Acceptance: Search finds semantically related notes

- [ ] **Goal Tracking Dashboard**
  - Parse daily notes for frontmatter
  - Calculate progress metrics
  - Visual charts/graphs
  - Acceptance: Q4 goals visible at a glance

- [ ] **Proactive Nudging System**
  - Schedule-based reminders
  - Context-aware suggestions
  - Pattern detection
  - Acceptance: System prompts user proactively

### Polish
- [ ] **Full Accessibility (a11y)**
  - ARIA labels everywhere
  - Keyboard navigation
  - Screen reader testing
  - WCAG 2.1 AA compliance
  - Acceptance: Pass accessibility audit

- [ ] **Mobile Optimization**
  - Responsive design refinement
  - Touch-friendly interactions
  - Bottom navigation for mobile
  - Acceptance: Usable on phone/tablet

- [ ] **Export/Import Conversations**
  - Export to markdown
  - Export to JSON
  - Import from backup
  - Acceptance: Data portability

### Infrastructure
- [ ] **Docker Containerization**
  - Dockerfile for backend
  - Dockerfile for frontend
  - Docker Compose for full stack
  - Acceptance: `docker-compose up` runs everything

- [ ] **Nginx Reverse Proxy**
  - TLS termination
  - Security headers
  - Rate limiting
  - Acceptance: Production-ready deployment

---

## Phase 1 Completion Checklist

Before moving to Phase 2 (Home Server Deployment):

### Must Have
- [ ] Authentication implemented and tested
- [ ] Backend test coverage ≥ 70%
- [ ] Message persistence working
- [ ] All P0 and P1 items completed
- [ ] Security review passed

### Should Have
- [ ] Streaming UI implemented
- [ ] Dark mode available
- [ ] Major refactoring completed
- [ ] All P2 items completed

### Nice to Have
- [ ] Rate limiting in place
- [ ] Basic audit logging
- [ ] Some P3 items started

---

## Effort Estimates

| Priority | Items | Total Effort |
|----------|-------|--------------|
| P0 | 2 | 3-4 days |
| P1 | 5 | 5-7 days |
| P2 | 9 | 7-10 days |
| P3 | 8 | 10-15 days |

**Phase 1 Total:** ~15-20 days for P0-P2

---

## Dependencies

### Blocked By
- ChromaDB features blocked by basic search completion
- Dashboard blocked by database implementation
- Docker blocked by all features working locally

### Enables
- Authentication enables all production features
- Database enables persistence and analytics
- Testing enables confident refactoring

---

## Success Metrics

### End of Phase 1
- Test coverage: ≥70%
- Security: Auth implemented
- Performance: <2s LLM response
- Quality: No component >150 lines

### End of Phase 2
- Uptime: 99%
- Security: TLS + auth + rate limiting
- Performance: Production-optimized
- Features: RAG + goals + nudging

---

## Review Schedule

- **Weekly:** Review progress, adjust priorities
- **End of Phase 1:** Full retrospective
- **Before Phase 2:** Security audit

---

**Next Review:** After P0 items completed
