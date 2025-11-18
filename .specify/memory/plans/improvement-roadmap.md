# Improvement Roadmap

> Prioritized improvements identified from SpecKit retrofit

## Overview

This roadmap organizes improvements into phases based on priority and impact. Each item links back to the feature specification where it was identified.

---

## Phase 1: Critical Fixes (Security & Stability)

### Security Issues
- [ ] **Shell injection protection** - Sanitize inputs in 1Password service exec calls
  - Source: [onepassword-integration.md](../features/onepassword-integration.md)
  - Risk: HIGH - Could allow arbitrary command execution
  - Effort: Small

- [ ] **Persistent user authorization** - Move from memory to database
  - Source: [telegram-bot.md](../features/telegram-bot.md)
  - Risk: HIGH - Users lose access on restart
  - Effort: Medium

- [ ] **Input validation** - Sanitize project/goal names properly
  - Source: [telegram-bot.md](../features/telegram-bot.md), [obsidian-integration.md](../features/obsidian-integration.md)
  - Risk: MEDIUM - Could cause file system issues
  - Effort: Small

### Stability Issues
- [ ] **Rate limiting per user** - Prevent single user from exhausting limits
  - Source: [telegram-bot.md](../features/telegram-bot.md)
  - Risk: MEDIUM - Service could be unavailable
  - Effort: Small

- [ ] **Retry logic for API calls** - Handle transient failures
  - Source: [claude-ai-service.md](../features/claude-ai-service.md)
  - Risk: MEDIUM - Single failures cause errors
  - Effort: Small

- [ ] **Request timeout** - Prevent hanging requests
  - Source: [claude-ai-service.md](../features/claude-ai-service.md)
  - Risk: MEDIUM - Could hang indefinitely
  - Effort: Small

---

## Phase 2: Code Quality & Maintainability

### File Refactoring
Large files identified that should be split:

- [ ] **obsidian.js (930 lines)** → Split into:
  - `VaultManager` - folder structure, file operations
  - `ConversationService` - saving, formatting, analysis
  - `ProjectService` - project/goal CRUD, progress tracking
  - Source: [obsidian-integration.md](../features/obsidian-integration.md)
  - Effort: Large

- [ ] **telegram.js (559 lines)** → Split into:
  - `CommandHandlers` - command processing
  - `MessageHandlers` - conversation handling
  - `BotCore` - lifecycle, notifications
  - Source: [telegram-bot.md](../features/telegram-bot.md)
  - Effort: Medium

- [ ] **nudging.js (544 lines)** → Split into:
  - `NudgeScheduler` - cron management
  - `PatternAnalyzer` - conversation analysis
  - `NudgeGenerator` - message generation
  - Source: [nudging-system.md](../features/nudging-system.md)
  - Effort: Medium

### Testing
- [ ] **Unit test suite** - Test all service methods
  - Target: 80% coverage
  - Effort: Large

- [ ] **Integration tests** - Test Telegram command flows
  - Effort: Medium

- [ ] **Mock external services** - Claude API, 1Password CLI
  - Effort: Medium

### Error Handling
- [ ] **Custom error types** - Replace generic errors with specific types
  - Effort: Medium

- [ ] **Error logging context** - Add request IDs, user IDs to logs
  - Effort: Small

---

## Phase 3: Feature Enhancements

### Performance
- [ ] **Credential caching** - Cache 1Password values with TTL
  - Source: [onepassword-integration.md](../features/onepassword-integration.md)
  - Effort: Small

- [ ] **Full-text search indexing** - Replace simple string matching
  - Source: [obsidian-integration.md](../features/obsidian-integration.md)
  - Effort: Medium

- [ ] **Webhook-based bot** - Replace polling with webhooks
  - Source: [telegram-bot.md](../features/telegram-bot.md)
  - Effort: Medium

### User Experience
- [ ] **Inline keyboards** - Interactive buttons in Telegram
  - Effort: Medium

- [ ] **Voice message transcription** - Process audio messages
  - Source: [telegram-bot.md](../features/telegram-bot.md)
  - Effort: Medium

- [ ] **Response streaming** - Stream Claude responses
  - Source: [claude-ai-service.md](../features/claude-ai-service.md)
  - Effort: Medium

### Intelligence
- [ ] **Claude-powered analysis** - Replace keyword matching
  - Source: [nudging-system.md](../features/nudging-system.md)
  - Effort: Medium

- [ ] **Better topic extraction** - Use Claude instead of first 5 words
  - Source: [telegram-bot.md](../features/telegram-bot.md)
  - Effort: Small

- [ ] **User preference learning** - Adapt nudges to feedback
  - Source: [nudging-system.md](../features/nudging-system.md)
  - Effort: Large

---

## Phase 4: Infrastructure

### TypeScript Migration
- [ ] **Convert to TypeScript** - Type safety, better IDE support
  - Effort: Large
  - Benefits: Catch errors at compile time, better refactoring

### Database Integration
- [ ] **Add SQLite/PostgreSQL** - For users, sessions, analytics
  - Effort: Large
  - Benefits: Scalability, complex queries, persistence

### Observability
- [ ] **Structured logging** - Replace console.log with proper logger
  - Effort: Small

- [ ] **Metrics collection** - Track API usage, response times
  - Effort: Medium

- [ ] **Health checks** - Endpoint for monitoring
  - Effort: Small

### DevOps
- [ ] **Docker containerization** - Easy deployment
  - Effort: Small

- [ ] **CI/CD pipeline** - Automated testing and deployment
  - Effort: Medium

- [ ] **Environment management** - Separate dev/staging/prod
  - Effort: Small

---

## Phase 5: Future Features

### New Integrations
- [ ] **Calendar integration** - Sync with Google/Apple Calendar
- [ ] **Multiple AI providers** - Support OpenAI, local models
- [ ] **Email integration** - Process emails as conversations
- [ ] **Discord bot** - Additional chat platform

### Advanced Features
- [ ] **Web dashboard** - View conversations, manage projects
- [ ] **Export functionality** - Export conversations as PDF/JSON
- [ ] **Multi-language support** - i18n for messages
- [ ] **Collaborative features** - Share projects with others

---

## Implementation Priority Matrix

| Urgency ↓ / Impact → | Low Impact | Medium Impact | High Impact |
|----------------------|------------|---------------|-------------|
| **Urgent** | - | Rate limiting, Input validation | Shell injection, Persistent auth |
| **Soon** | - | Request timeout, Retry logic | File refactoring, Unit tests |
| **Later** | Voice transcription | TypeScript migration | Database integration |

---

## Suggested Sprint Plan

### Sprint 1: Security Hardening (Week 1-2)
1. Shell injection protection
2. Input validation
3. Persistent user authorization

### Sprint 2: Stability & Testing (Week 3-4)
1. Rate limiting per user
2. Retry logic with backoff
3. Unit test foundation

### Sprint 3: Code Quality (Week 5-6)
1. Split obsidian.js
2. Split telegram.js
3. Custom error types

### Sprint 4: Performance (Week 7-8)
1. Credential caching
2. Full-text search
3. Webhook migration

---

## Metrics to Track

### Code Health
- Test coverage %
- Lines per file (target: <300)
- Error rate

### Performance
- API response time
- Conversation save time
- Search latency

### User Experience
- Messages per day
- Nudge engagement rate
- Error message frequency

---

*Last updated: 2025-11-18*
*Generated by SpecKit Retrofit*
