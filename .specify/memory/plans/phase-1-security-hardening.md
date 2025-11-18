# Phase 1: Security Hardening

> Critical security fixes - Estimated: 2 weeks

---

## Work Item 1.1: Shell Injection Protection

**Priority:** CRITICAL
**Effort:** Small (2-4 hours)
**Location:** [onepassword.js:53-64](src/services/onepassword.js#L53-L64)

### Problem
The `getSecret()`, `createItem()`, and `updateCredential()` methods use string interpolation directly in shell commands, allowing potential command injection.

### Acceptance Criteria

- GIVEN a secret reference containing shell metacharacters (e.g., `; rm -rf /`)
  WHEN `getSecret()` is called
  THEN the metacharacters are escaped and treated as literal text

- GIVEN an item title with quotes or backticks
  WHEN `createItem()` is called
  THEN the characters are properly escaped in the command

- GIVEN a field value with newlines or special characters
  WHEN `updateCredential()` is called
  THEN the value is safely passed without executing injected commands

- GIVEN any 1Password operation
  WHEN executed
  THEN no shell expansion occurs on user-provided values

### Implementation Tasks

- [ ] **1.1.1** Create `sanitizeShellArg()` utility function
  ```javascript
  function sanitizeShellArg(arg) {
    // Escape single quotes and wrap in single quotes
    return `'${arg.replace(/'/g, "'\\''")}'`;
  }
  ```

- [ ] **1.1.2** Update `getSecret()` to use sanitized reference
  ```javascript
  const { stdout } = await execAsync(`op read ${sanitizeShellArg(reference)}`);
  ```

- [ ] **1.1.3** Update `createItem()` to escape JSON properly
  - Use `JSON.stringify()` for the template
  - Pipe through stdin instead of echo

- [ ] **1.1.4** Update `updateCredential()` to escape field and value

- [ ] **1.1.5** Add unit tests for injection attempts

### Definition of Done
- [ ] All exec calls use sanitized inputs
- [ ] Unit tests cover injection vectors
- [ ] No shell metacharacters can escape
- [ ] Existing functionality unchanged

---

## Work Item 1.2: Persistent User Authorization

**Priority:** HIGH
**Effort:** Medium (4-8 hours)
**Location:** [telegram.js:11](src/bots/telegram.js#L11)

### Problem
`authorizedUsers` is an in-memory Set that loses all users on restart. Users must `/start` again after every restart.

### Acceptance Criteria

- GIVEN a user who previously ran `/start`
  WHEN the service restarts
  THEN the user remains authorized without re-running `/start`

- GIVEN a new user
  WHEN they run `/start`
  THEN they are added to persistent storage

- GIVEN an authorized user
  WHEN checking authorization
  THEN lookup completes in < 10ms

- GIVEN the storage file is corrupted
  WHEN service starts
  THEN service continues with empty auth list and logs error

### Implementation Tasks

- [ ] **1.2.1** Create `src/utils/storage.js` for JSON file persistence
  ```javascript
  export class JsonStorage {
    constructor(filePath) { ... }
    async load() { ... }
    async save(data) { ... }
  }
  ```

- [ ] **1.2.2** Create `data/` directory for persistent storage

- [ ] **1.2.3** Update `TelegramBotService` constructor
  - Initialize storage with `data/authorized-users.json`
  - Load existing users on startup

- [ ] **1.2.4** Update `/start` handler to persist new users
  ```javascript
  this.authorizedUsers.add(userId);
  await this.storage.save([...this.authorizedUsers]);
  ```

- [ ] **1.2.5** Add graceful handling for storage errors

- [ ] **1.2.6** Add unit tests for persistence

### Definition of Done
- [ ] Users persist across restarts
- [ ] Storage errors handled gracefully
- [ ] Lookup performance < 10ms
- [ ] Unit tests pass
- [ ] No breaking changes to existing auth flow

---

## Work Item 1.3: Input Validation

**Priority:** MEDIUM
**Effort:** Small (2-4 hours)
**Locations:**
- [telegram.js:159-201](src/bots/telegram.js#L159-L201)
- [obsidian.js:188](src/services/obsidian.js#L188)

### Problem
Project/goal names are not validated, which could cause file system issues or create malformed filenames.

### Acceptance Criteria

- GIVEN a project name with path traversal (`../../etc/passwd`)
  WHEN `/project` command executed
  THEN name is rejected with error message

- GIVEN a project name with only special characters
  WHEN sanitized for filename
  THEN a fallback name is used

- GIVEN a project name > 100 characters
  WHEN `/project` command executed
  THEN name is truncated or rejected

- GIVEN a valid project name with mixed characters
  WHEN sanitized
  THEN safe filename is generated preserving readability

### Implementation Tasks

- [ ] **1.3.1** Create `src/utils/validation.js`
  ```javascript
  export function validateProjectName(name) {
    if (!name || name.length < 1) return { valid: false, error: 'Name required' };
    if (name.length > 100) return { valid: false, error: 'Name too long' };
    if (name.includes('..') || name.includes('/')) return { valid: false, error: 'Invalid characters' };
    return { valid: true };
  }

  export function sanitizeFilename(name) {
    let safe = name.replace(/[^a-zA-Z0-9\s-]/g, '').trim();
    if (!safe) safe = 'untitled';
    return safe.replace(/\s+/g, '-').substring(0, 50);
  }
  ```

- [ ] **1.3.2** Update `/project` handler to validate input

- [ ] **1.3.3** Update `/goal` handler to validate input

- [ ] **1.3.4** Update `ObsidianService.createProject()` to use sanitizer

- [ ] **1.3.5** Update `ObsidianService.createGoal()` to use sanitizer

- [ ] **1.3.6** Add unit tests for edge cases

### Definition of Done
- [ ] All user inputs validated before use
- [ ] Clear error messages for invalid input
- [ ] Path traversal attacks prevented
- [ ] Unit tests cover edge cases

---

## Work Item 1.4: Per-User Rate Limiting

**Priority:** MEDIUM
**Effort:** Small (2-4 hours)
**Location:** [telegram.js:430](src/bots/telegram.js#L430)

### Problem
No per-user rate limiting allows a single user to exhaust the Claude API rate limit for everyone.

### Acceptance Criteria

- GIVEN a user sending > 10 messages per minute
  WHEN they send another message
  THEN they receive "Please slow down" error

- GIVEN rate limit exceeded
  WHEN user waits 1 minute
  THEN they can send messages again

- GIVEN multiple users
  WHEN one user hits rate limit
  THEN other users are not affected

### Implementation Tasks

- [ ] **1.4.1** Create `src/utils/rate-limiter.js`
  ```javascript
  export class UserRateLimiter {
    constructor(maxPerMinute = 10) { ... }
    check(userId) { ... } // returns { allowed: boolean, retryAfter?: number }
    track(userId) { ... }
  }
  ```

- [ ] **1.4.2** Add rate limiter to `TelegramBotService`

- [ ] **1.4.3** Check rate limit before processing message
  ```javascript
  const rateCheck = this.rateLimiter.check(userId);
  if (!rateCheck.allowed) {
    this.bot.sendMessage(chatId, `⏳ Please slow down. Try again in ${rateCheck.retryAfter}s`);
    return;
  }
  ```

- [ ] **1.4.4** Add unit tests

### Definition of Done
- [ ] Per-user rate limiting enforced
- [ ] User-friendly error messages
- [ ] No impact on other users
- [ ] Unit tests pass

---

## Work Item 1.5: API Retry Logic

**Priority:** MEDIUM
**Effort:** Small (2-4 hours)
**Location:** [claude.js:33-63](src/services/claude.js#L33-L63)

### Problem
Single API failures cause errors. Transient issues should be retried.

### Acceptance Criteria

- GIVEN a transient API error (500, network timeout)
  WHEN `generateResponse()` called
  THEN request retried up to 3 times with exponential backoff

- GIVEN persistent API error
  WHEN all retries exhausted
  THEN appropriate error thrown

- GIVEN 429 rate limit error
  WHEN error received
  THEN wait for Retry-After header before retrying

- GIVEN successful retry
  WHEN response received
  THEN normal response returned to caller

### Implementation Tasks

- [ ] **1.5.1** Create `src/utils/retry.js`
  ```javascript
  export async function withRetry(fn, options = {}) {
    const { maxRetries = 3, baseDelay = 1000 } = options;
    for (let i = 0; i <= maxRetries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (i === maxRetries || !isRetryable(error)) throw error;
        await delay(baseDelay * Math.pow(2, i));
      }
    }
  }
  ```

- [ ] **1.5.2** Update `generateResponse()` to use retry wrapper

- [ ] **1.5.3** Handle Retry-After header for 429 errors

- [ ] **1.5.4** Add logging for retry attempts

- [ ] **1.5.5** Add unit tests with mocked failures

### Definition of Done
- [ ] Transient errors retried automatically
- [ ] Exponential backoff implemented
- [ ] 429 errors respect Retry-After
- [ ] Unit tests cover retry scenarios

---

## Work Item 1.6: Request Timeout

**Priority:** MEDIUM
**Effort:** Small (1-2 hours)
**Location:** [claude.js:37-43](src/services/claude.js#L37-L43)

### Problem
No timeout on Claude API requests could cause indefinite hangs.

### Acceptance Criteria

- GIVEN API request taking > 30 seconds
  WHEN timeout reached
  THEN request cancelled and error thrown

- GIVEN timeout error
  WHEN caught
  THEN user-friendly message returned

### Implementation Tasks

- [ ] **1.6.1** Add timeout option to Anthropic client
  ```javascript
  this.client = new Anthropic({
    apiKey: apiKey,
    timeout: 30000, // 30 seconds
  });
  ```

- [ ] **1.6.2** Handle timeout errors in catch block

- [ ] **1.6.3** Make timeout configurable via options

### Definition of Done
- [ ] Requests timeout after 30 seconds
- [ ] Timeout errors handled gracefully
- [ ] User receives friendly error message

---

## Summary

| Work Item | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| 1.1 Shell Injection | CRITICAL | Small | None |
| 1.2 Persistent Auth | HIGH | Medium | None |
| 1.3 Input Validation | MEDIUM | Small | None |
| 1.4 Per-User Rate Limit | MEDIUM | Small | None |
| 1.5 API Retry Logic | MEDIUM | Small | None |
| 1.6 Request Timeout | MEDIUM | Small | None |

**Recommended Order:** 1.1 → 1.6 → 1.5 → 1.3 → 1.4 → 1.2

---

*Created: 2025-11-18*
