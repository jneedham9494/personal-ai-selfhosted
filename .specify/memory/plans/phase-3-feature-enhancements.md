# Phase 3: Feature Enhancements

> Performance and UX improvements - Estimated: 3-4 weeks

---

## Work Item 3.1: Credential Caching

**Priority:** HIGH
**Effort:** Small (2-4 hours)
**Location:** [onepassword.js:156-199](src/services/onepassword.js#L156-L199)

### Problem
Every config load reads from 1Password CLI, adding latency and unnecessary calls.

### Acceptance Criteria

- GIVEN credentials loaded previously
  WHEN `loadConfiguration()` called again within TTL
  THEN cached values returned without CLI call

- GIVEN cache TTL expired (default 5 minutes)
  WHEN `loadConfiguration()` called
  THEN fresh values fetched from 1Password

- GIVEN `--no-cache` flag
  WHEN loading configuration
  THEN cache bypassed

- GIVEN cache in use
  WHEN checking performance
  THEN subsequent loads complete in < 10ms

### Implementation Tasks

- [ ] **3.1.1** Add cache structure to service
  ```javascript
  constructor() {
    this.cache = {
      data: null,
      timestamp: 0,
      ttl: 5 * 60 * 1000 // 5 minutes
    };
  }
  ```

- [ ] **3.1.2** Check cache before loading
  ```javascript
  async loadConfiguration(options = {}) {
    const now = Date.now();
    if (!options.noCache && this.cache.data && (now - this.cache.timestamp) < this.cache.ttl) {
      console.log('✅ Using cached configuration');
      return this.cache.data;
    }
    // ... fetch from 1Password
    this.cache.data = config;
    this.cache.timestamp = now;
    return config;
  }
  ```

- [ ] **3.1.3** Add cache invalidation method

- [ ] **3.1.4** Add unit tests

### Definition of Done
- [ ] Cached loads < 10ms
- [ ] TTL respected
- [ ] Cache bypass option works
- [ ] Unit tests pass

---

## Work Item 3.2: Full-Text Search with Indexing

**Priority:** HIGH
**Effort:** Medium (6-10 hours)
**Location:** [obsidian.js:612-645](src/services/obsidian.js#L612-L645)

### Problem
Current search scans all files on every query. Slow for large vaults, no relevance scoring.

### Acceptance Criteria

- GIVEN search query
  WHEN executed
  THEN results returned in < 100ms for 1000+ files

- GIVEN search results
  WHEN returned
  THEN results sorted by relevance score

- GIVEN file added/changed
  WHEN watcher detects change
  THEN index updated incrementally

- GIVEN fuzzy search query with typo
  WHEN searched
  THEN relevant results still returned

### Implementation Tasks

- [ ] **3.2.1** Add search index library
  ```bash
  npm install minisearch
  ```

- [ ] **3.2.2** Create search index service
  ```javascript
  // src/services/search-index.js
  import MiniSearch from 'minisearch';

  export class SearchIndex {
    constructor() {
      this.index = new MiniSearch({
        fields: ['title', 'content', 'tags'],
        storeFields: ['title', 'path'],
        searchOptions: {
          fuzzy: 0.2,
          prefix: true
        }
      });
    }

    async build(conversationsFolder) { ... }
    add(document) { ... }
    remove(id) { ... }
    search(query) { ... }
  }
  ```

- [ ] **3.2.3** Build index on startup
- [ ] **3.2.4** Update index on file changes via watcher
- [ ] **3.2.5** Update `searchNotes()` to use index
- [ ] **3.2.6** Add relevance scoring to results

### Definition of Done
- [ ] Search < 100ms on 1000+ files
- [ ] Results ranked by relevance
- [ ] Index updated incrementally
- [ ] Fuzzy matching works

---

## Work Item 3.3: Webhook-Based Telegram Bot

**Priority:** MEDIUM
**Effort:** Medium (6-10 hours)
**Location:** [telegram.js:6](src/bots/telegram.js#L6)

### Problem
Polling-based bot constantly checks for updates. Webhooks are more efficient and responsive.

### Acceptance Criteria

- GIVEN webhook configured
  WHEN message sent to bot
  THEN response received within 1 second

- GIVEN webhook URL
  WHEN Telegram sends update
  THEN Express server receives POST request

- GIVEN webhook failure
  WHEN Telegram retries
  THEN update processed successfully

- GIVEN development environment
  WHEN started
  THEN uses polling (no public URL needed)

### Implementation Tasks

- [ ] **3.3.1** Create Express webhook endpoint
  ```javascript
  // src/bots/telegram/webhook.js
  import express from 'express';

  export function createWebhookServer(bot, options = {}) {
    const app = express();
    app.use(express.json());

    app.post(`/webhook/${options.token}`, (req, res) => {
      bot.processUpdate(req.body);
      res.sendStatus(200);
    });

    return app;
  }
  ```

- [ ] **3.3.2** Add webhook configuration
  ```javascript
  // .env
  TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook
  USE_WEBHOOK=true
  ```

- [ ] **3.3.3** Update TelegramBotService to support both modes
  ```javascript
  if (config.USE_WEBHOOK && config.TELEGRAM_WEBHOOK_URL) {
    this.bot = new TelegramBot(token);
    await this.bot.setWebHook(`${config.TELEGRAM_WEBHOOK_URL}/${token}`);
  } else {
    this.bot = new TelegramBot(token, { polling: true });
  }
  ```

- [ ] **3.3.4** Add webhook health check endpoint
- [ ] **3.3.5** Add webhook setup instructions to README

### Definition of Done
- [ ] Webhook mode works in production
- [ ] Polling mode works in development
- [ ] Response time < 1 second
- [ ] Health check endpoint available

---

## Work Item 3.4: Claude-Powered Analysis

**Priority:** MEDIUM
**Effort:** Medium (4-8 hours)
**Location:** [nudging.js:147-198](src/services/nudging.js#L147-L198)

### Problem
Simple keyword matching misses nuance. Claude can provide better pattern analysis.

### Acceptance Criteria

- GIVEN conversation history
  WHEN analyzed by Claude
  THEN mood, goals, and challenges accurately identified

- GIVEN Claude API unavailable
  WHEN analysis requested
  THEN fallback to keyword-based analysis

- GIVEN analysis request
  WHEN executed
  THEN uses low-cost model (Haiku) with concise prompts

### Implementation Tasks

- [ ] **3.4.1** Create analysis prompts
  ```javascript
  const ANALYSIS_PROMPTS = {
    mood: `Analyze this conversation and return JSON: { "mood": "stressed|energetic|focused|neutral", "confidence": 0-1, "indicators": ["..."] }`,
    goals: `Extract goals from this conversation. Return JSON: { "goals": [{"text": "...", "urgency": "high|medium|low"}] }`,
    patterns: `Identify patterns in topics and timing. Return JSON: { "recurring_topics": [], "time_patterns": [] }`
  };
  ```

- [ ] **3.4.2** Update `analyzeConversationPatterns()` in NudgingService
- [ ] **3.4.3** Parse JSON response with error handling
- [ ] **3.4.4** Add fallback to keyword analysis on failure
- [ ] **3.4.5** Cache analysis results (5 minute TTL)

### Definition of Done
- [ ] Claude analysis more accurate than keywords
- [ ] Fallback works when API unavailable
- [ ] Analysis cached to reduce API calls
- [ ] JSON responses parsed safely

---

## Work Item 3.5: Better Topic Extraction

**Priority:** LOW
**Effort:** Small (2-4 hours)
**Location:** [telegram.js:533-538](src/bots/telegram.js#L533-L538)

### Problem
Topic is just first 5 words. Misses actual subject of conversation.

### Acceptance Criteria

- GIVEN conversation about trip planning
  WHEN topic extracted
  THEN topic is "Trip Planning" not "Can you help me"

- GIVEN conversation
  WHEN topic extracted by Claude
  THEN uses < 50 tokens for efficiency

### Implementation Tasks

- [ ] **3.5.1** Add topic extraction method to ClaudeService
  ```javascript
  async extractTopic(messages) {
    const firstExchange = messages.slice(0, 2).map(m => m.content).join('\n');
    const response = await this.generateResponse([{
      role: 'user',
      content: `Extract a 2-5 word topic from this conversation:\n\n${firstExchange}\n\nRespond with just the topic, nothing else.`
    }], { maxTokens: 20, temperature: 0.3 });
    return response.trim();
  }
  ```

- [ ] **3.5.2** Update `extractTopic()` in TelegramBotService to use Claude
- [ ] **3.5.3** Add fallback to current method if Claude unavailable

### Definition of Done
- [ ] Topics accurately reflect conversation subject
- [ ] Extraction uses minimal tokens
- [ ] Fallback works without Claude

---

## Work Item 3.6: Inline Keyboards

**Priority:** LOW
**Effort:** Medium (4-6 hours)

### Problem
Text-only interface. Buttons would improve UX for common actions.

### Acceptance Criteria

- GIVEN nudge message
  WHEN displayed
  THEN includes action buttons (Snooze, Done, Dismiss)

- GIVEN button press
  WHEN callback received
  THEN action executed and message updated

### Implementation Tasks

- [ ] **3.6.1** Add inline keyboard to nudge messages
  ```javascript
  const keyboard = {
    inline_keyboard: [[
      { text: '✅ Done', callback_data: 'nudge_done' },
      { text: '⏰ Snooze', callback_data: 'nudge_snooze' },
      { text: '❌ Dismiss', callback_data: 'nudge_dismiss' }
    ]]
  };
  ```

- [ ] **3.6.2** Add callback query handler
- [ ] **3.6.3** Update message on button press
- [ ] **3.6.4** Track nudge responses for analytics

### Definition of Done
- [ ] Buttons display correctly
- [ ] Callbacks handled
- [ ] Messages update on action

---

## Work Item 3.7: Response Streaming

**Priority:** LOW
**Effort:** Medium (4-6 hours)
**Location:** [claude.js:33-63](src/services/claude.js#L33-L63)

### Problem
User waits for full response. Streaming provides immediate feedback.

### Acceptance Criteria

- GIVEN long response
  WHEN streaming enabled
  THEN user sees text appearing in real-time

- GIVEN Telegram rate limits
  WHEN streaming
  THEN edits batched to avoid hitting limits

### Implementation Tasks

- [ ] **3.7.1** Update ClaudeService for streaming
  ```javascript
  async *generateResponseStream(messages, options = {}) {
    const stream = await this.client.messages.create({
      ...options,
      stream: true
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta') {
        yield event.delta.text;
      }
    }
  }
  ```

- [ ] **3.7.2** Update TelegramBotService to edit message
- [ ] **3.7.3** Batch edits (every 500ms or 50 chars)
- [ ] **3.7.4** Handle streaming errors

### Definition of Done
- [ ] Text appears progressively
- [ ] Edit rate limits respected
- [ ] Errors handled gracefully

---

## Summary

| Work Item | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| 3.1 Credential Caching | HIGH | Small | None |
| 3.2 Full-Text Search | HIGH | Medium | Phase 2 (preferred) |
| 3.3 Webhook Bot | MEDIUM | Medium | None |
| 3.4 Claude Analysis | MEDIUM | Medium | None |
| 3.5 Topic Extraction | LOW | Small | None |
| 3.6 Inline Keyboards | LOW | Medium | None |
| 3.7 Response Streaming | LOW | Medium | None |

**Recommended Order:** 3.1 → 3.2 → 3.4 → 3.3 → 3.5 → 3.6 → 3.7

---

*Created: 2025-11-18*
