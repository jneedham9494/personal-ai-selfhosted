# Phase 2: Code Quality & Maintainability

> Refactoring and testing - Estimated: 3-4 weeks

---

## Work Item 2.1: Split ObsidianService

**Priority:** HIGH
**Effort:** Large (8-16 hours)
**Current Location:** [obsidian.js](src/services/obsidian.js) (930 lines)

### Problem
Single file handles vault management, conversation saving, project tracking, and file watching. Too large to maintain.

### Target Structure
```
src/services/obsidian/
├── index.js              # Re-exports
├── vault-manager.js      # Folder structure, file ops
├── conversation-service.js # Save, format, analyze
├── project-service.js    # Project/goal CRUD
└── content-analyzer.js   # Mood, category, action items
```

### Acceptance Criteria

- GIVEN split files
  WHEN imported via `import { ObsidianService } from './services/obsidian'`
  THEN existing API unchanged

- GIVEN any file in split structure
  WHEN measured
  THEN file is < 300 lines

- GIVEN all existing tests
  WHEN run after refactor
  THEN all tests pass

- GIVEN conversation save
  WHEN executed
  THEN behavior identical to before split

### Implementation Tasks

#### 2.1.1 Create VaultManager (Est: 2 hours)
- [ ] Create `src/services/obsidian/vault-manager.js`
- [ ] Move: `constructor`, `initialize`, `createFolderStructure`, `setupWatcher`, `close`
- [ ] Move template creation methods
- [ ] Export class

#### 2.1.2 Create ContentAnalyzer (Est: 2 hours)
- [ ] Create `src/services/obsidian/content-analyzer.js`
- [ ] Move: `extractActionItems`, `detectMood`, `categorizeConversation`, `determinePriority`
- [ ] Move: `generateConversationSummary`, `generateKeyInsights`, `getExcerpt`
- [ ] Export as functions or class

#### 2.1.3 Create ConversationService (Est: 3 hours)
- [ ] Create `src/services/obsidian/conversation-service.js`
- [ ] Move: `saveConversation`, `linkConversationToDailyNote`
- [ ] Move: `getTodaysNote`, `searchNotes`
- [ ] Import ContentAnalyzer for analysis methods

#### 2.1.4 Create ProjectService (Est: 3 hours)
- [ ] Create `src/services/obsidian/project-service.js`
- [ ] Move: `createProject`, `createGoal`, `getProjectOrGoal`
- [ ] Move: `linkConversationToProject`, `updateProjectProgress`
- [ ] Export class

#### 2.1.5 Create PromptHandler (Est: 2 hours)
- [ ] Create `src/services/obsidian/prompt-handler.js`
- [ ] Move: `setupPromptWatcher`, `processPromptFile`, `extractTopic`
- [ ] Export class

#### 2.1.6 Create Facade (Est: 2 hours)
- [ ] Create `src/services/obsidian/index.js`
- [ ] Create `ObsidianService` that composes all sub-services
- [ ] Maintain existing public API
- [ ] Re-export for backward compatibility

#### 2.1.7 Update Imports (Est: 1 hour)
- [ ] Update `index.js` import
- [ ] Update `telegram.js` import
- [ ] Update `nudging.js` import
- [ ] Verify all references

### Definition of Done
- [ ] No file > 300 lines
- [ ] Existing API unchanged
- [ ] All imports updated
- [ ] Tests pass
- [ ] No runtime errors

---

## Work Item 2.2: Split TelegramBotService

**Priority:** HIGH
**Effort:** Medium (6-10 hours)
**Current Location:** [telegram.js](src/bots/telegram.js) (559 lines)

### Problem
Single file handles commands, messages, conversation context, and notifications.

### Target Structure
```
src/bots/telegram/
├── index.js              # Main service & facade
├── command-handlers.js   # /start, /help, /project, etc.
├── message-handler.js    # Conversation handling
└── context-manager.js    # Active conversations
```

### Acceptance Criteria

- GIVEN split files
  WHEN `TelegramBotService` instantiated
  THEN all commands work as before

- GIVEN any file in split structure
  WHEN measured
  THEN file is < 200 lines

### Implementation Tasks

#### 2.2.1 Create ContextManager (Est: 2 hours)
- [ ] Create `src/bots/telegram/context-manager.js`
- [ ] Move: `activeConversations` Map management
- [ ] Add methods: `get`, `set`, `clear`, `has`
- [ ] Move `extractTopic` method

#### 2.2.2 Create CommandHandlers (Est: 3 hours)
- [ ] Create `src/bots/telegram/command-handlers.js`
- [ ] Move all `onText` handlers as separate functions
- [ ] Export as object with handler functions
- [ ] Handlers receive dependencies via closure

#### 2.2.3 Create MessageHandler (Est: 2 hours)
- [ ] Create `src/bots/telegram/message-handler.js`
- [ ] Move `handleConversationMessage`
- [ ] Move `saveConversationToObsidian`

#### 2.2.4 Create Facade (Est: 2 hours)
- [ ] Update `src/bots/telegram/index.js`
- [ ] Compose all handlers
- [ ] Maintain `sendNotification` and `stop` methods

### Definition of Done
- [ ] No file > 200 lines
- [ ] All commands functional
- [ ] Tests pass
- [ ] Context persists correctly

---

## Work Item 2.3: Split NudgingService

**Priority:** MEDIUM
**Effort:** Medium (4-8 hours)
**Current Location:** [nudging.js](src/services/nudging.js) (544 lines)

### Target Structure
```
src/services/nudging/
├── index.js              # Main service
├── scheduler.js          # Cron job management
├── analyzer.js           # Pattern analysis
└── generator.js          # Nudge message generation
```

### Implementation Tasks

- [ ] **2.3.1** Create `scheduler.js` - cron job setup and management
- [ ] **2.3.2** Create `analyzer.js` - `analyzeConversationPatterns`, `getRecentConversations`
- [ ] **2.3.3** Create `generator.js` - nudge message generation, `generateProgressBar`
- [ ] **2.3.4** Update main service as facade

---

## Work Item 2.4: Unit Test Foundation

**Priority:** HIGH
**Effort:** Large (12-20 hours)
**Target Coverage:** 80%

### Problem
No unit tests exist. Changes risk breaking existing functionality.

### Acceptance Criteria

- GIVEN any service method
  WHEN tested
  THEN happy path and error cases covered

- GIVEN test suite
  WHEN `npm test` run
  THEN all tests pass in < 30 seconds

- GIVEN coverage report
  WHEN generated
  THEN coverage >= 80%

### Implementation Tasks

#### 2.4.1 Test Infrastructure (Est: 2 hours)
- [ ] Configure Jest for ES Modules
- [ ] Create `tests/` directory structure
- [ ] Create mock utilities for external services
- [ ] Add coverage configuration

#### 2.4.2 ClaudeService Tests (Est: 3 hours)
- [ ] Test `generateResponse` happy path
- [ ] Test rate limiting
- [ ] Test error handling (401, 429, other)
- [ ] Test `analyzeConversationPatterns`
- [ ] Mock Anthropic client

#### 2.4.3 ObsidianService Tests (Est: 4 hours)
- [ ] Test `saveConversation`
- [ ] Test `createProject` / `createGoal`
- [ ] Test `searchNotes`
- [ ] Test `updateProjectProgress`
- [ ] Test content analysis methods
- [ ] Use temp directories for file tests

#### 2.4.4 TelegramBotService Tests (Est: 4 hours)
- [ ] Test command handlers
- [ ] Test message handling
- [ ] Test authorization
- [ ] Test conversation context
- [ ] Mock telegram-bot-api

#### 2.4.5 NudgingService Tests (Est: 3 hours)
- [ ] Test nudge generation
- [ ] Test rate limiting (shouldSendNudge)
- [ ] Test pattern analysis
- [ ] Test active hours check

#### 2.4.6 OnePasswordService Tests (Est: 2 hours)
- [ ] Test configuration loading
- [ ] Test secret retrieval
- [ ] Test error handling
- [ ] Mock exec calls

### Test File Structure
```
tests/
├── unit/
│   ├── services/
│   │   ├── claude.test.js
│   │   ├── obsidian.test.js
│   │   ├── nudging.test.js
│   │   └── onepassword.test.js
│   └── bots/
│       └── telegram.test.js
├── integration/
│   └── conversation-flow.test.js
├── mocks/
│   ├── anthropic.js
│   ├── telegram-bot-api.js
│   └── fs.js
└── fixtures/
    └── sample-conversations.json
```

### Definition of Done
- [ ] Jest configured for ES Modules
- [ ] All services have unit tests
- [ ] Coverage >= 80%
- [ ] Tests run in < 30 seconds
- [ ] CI-ready configuration

---

## Work Item 2.5: Custom Error Types

**Priority:** MEDIUM
**Effort:** Medium (3-5 hours)

### Problem
Generic errors make debugging difficult. No distinction between error types.

### Target Structure
```
src/errors/
├── index.js
├── api-error.js
├── validation-error.js
├── storage-error.js
└── auth-error.js
```

### Implementation Tasks

- [ ] **2.5.1** Create base error classes
  ```javascript
  export class AppError extends Error {
    constructor(message, code, details = {}) {
      super(message);
      this.code = code;
      this.details = details;
    }
  }

  export class ApiError extends AppError { ... }
  export class ValidationError extends AppError { ... }
  export class StorageError extends AppError { ... }
  export class AuthError extends AppError { ... }
  ```

- [ ] **2.5.2** Update ClaudeService to throw `ApiError`

- [ ] **2.5.3** Update ObsidianService to throw `StorageError`

- [ ] **2.5.4** Update TelegramBot to throw `ValidationError`, `AuthError`

- [ ] **2.5.5** Add error codes enum
  ```javascript
  export const ErrorCodes = {
    RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
    INVALID_API_KEY: 'INVALID_API_KEY',
    STORAGE_WRITE_FAILED: 'STORAGE_WRITE_FAILED',
    // ...
  };
  ```

### Definition of Done
- [ ] All errors use custom types
- [ ] Error codes defined
- [ ] Stack traces preserved
- [ ] Error handling updated throughout

---

## Work Item 2.6: Structured Logging

**Priority:** LOW
**Effort:** Small (2-4 hours)

### Problem
Console.log everywhere makes filtering and analysis difficult.

### Implementation Tasks

- [ ] **2.6.1** Create logger utility
  ```javascript
  // src/utils/logger.js
  export const logger = {
    info: (message, meta = {}) => console.log(JSON.stringify({ level: 'info', message, ...meta, timestamp: new Date().toISOString() })),
    error: (message, meta = {}) => console.error(JSON.stringify({ level: 'error', message, ...meta, timestamp: new Date().toISOString() })),
    warn: (message, meta = {}) => console.warn(JSON.stringify({ level: 'warn', message, ...meta, timestamp: new Date().toISOString() })),
    debug: (message, meta = {}) => { if (process.env.DEBUG) console.log(JSON.stringify({ level: 'debug', message, ...meta, timestamp: new Date().toISOString() })); }
  };
  ```

- [ ] **2.6.2** Replace console.log calls with logger
- [ ] **2.6.3** Add context (userId, requestId) to logs
- [ ] **2.6.4** Add log level configuration

---

## Summary

| Work Item | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| 2.1 Split ObsidianService | HIGH | Large | None |
| 2.2 Split TelegramBotService | HIGH | Medium | None |
| 2.3 Split NudgingService | MEDIUM | Medium | None |
| 2.4 Unit Test Foundation | HIGH | Large | 2.1, 2.2 (preferred) |
| 2.5 Custom Error Types | MEDIUM | Medium | None |
| 2.6 Structured Logging | LOW | Small | None |

**Recommended Order:** 2.5 → 2.1 → 2.2 → 2.3 → 2.6 → 2.4

---

*Created: 2025-11-18*
