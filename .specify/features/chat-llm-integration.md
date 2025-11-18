# Feature: Chat/LLM Integration

## Status
**Retroactive specification** - Feature implemented and operational

## Overview
Core chat functionality that sends user messages to the Ollama LLM and returns AI-generated responses. Supports both streaming and non-streaming modes with special handling for slash commands.

---

## Current Behavior

### Message Flow
1. User sends message via frontend
2. Backend receives POST request to `/chat/message`
3. Command parser checks for slash commands
4. If command: execute and return formatted result
5. If regular message: send to Ollama LLM
6. Return response (streaming or complete)

### Supported Modes
- **Non-streaming:** Returns complete response as JSON
- **Streaming:** Returns chunks via StreamingResponse (event-stream)

---

## Technical Implementation

### Files
- [chat.py](backend/routers/chat.py) - Router with endpoints
- [llm_service.py](backend/services/llm_service.py) - Ollama integration

### API Endpoints

#### POST /chat/message
Send message to LLM or execute command

#### GET /chat/health
Check LLM service availability

---

## Acceptance Criteria (Current State)

### Happy Path - Regular Message
- GIVEN a user with a valid message
  WHEN the message is sent to POST /chat/message
  THEN Ollama processes the message
  AND returns an AI-generated response
  AND response status is 200

### Happy Path - Streaming Mode
- GIVEN a user message with stream=true
  WHEN the message is sent to POST /chat/message
  THEN response is returned as StreamingResponse
  AND content-type is text/event-stream
  AND chunks are prefixed with "data: "

### Command Detection
- GIVEN a message starting with "/"
  WHEN the message is sent to POST /chat/message
  THEN command parser intercepts the message
  AND executes the appropriate command
  AND returns formatted command result

### Help Command
- GIVEN a message "/help"
  WHEN processed by the chat endpoint
  THEN returns formatted list of available commands

### Search Command
- GIVEN a message "/search <query>"
  WHEN processed by the chat endpoint
  THEN searches Obsidian vault for query
  AND returns formatted search results with file paths and excerpts

### Error Handling - LLM Unavailable
- GIVEN Ollama service is not running
  WHEN a message is sent
  THEN returns 503 Service Unavailable
  AND error message indicates LLM is unavailable

### Error Handling - Invalid Request
- GIVEN an empty messages array
  WHEN sent to POST /chat/message
  THEN returns 422 Validation Error
  AND specifies the validation issue

### Health Check
- GIVEN Ollama is running
  WHEN GET /chat/health is called
  THEN returns {"status": "healthy", "model": "llama3"}

---

## Request/Response Schema

### Request
```json
{
  "messages": [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well!"}
  ],
  "stream": false
}
```

### Response (Non-streaming)
```json
{
  "response": "AI generated response text..."
}
```

### Response (Streaming)
```
data: chunk1
data: chunk2
data: [DONE]
```

---

## Dependencies

### External
- Ollama server running on localhost:11434
- Model: llama3 (configurable)

### Internal
- CommandParser service for slash command detection
- ObsidianService for search command execution

---

## Configuration

### Environment Variables
- `OLLAMA_HOST` - Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Model to use (default: llama3)

---

## Known Issues / Tech Debt

- [ ] No message history persistence (messages only in frontend state)
- [ ] No conversation context management beyond current session
- [ ] ThreadPoolExecutor used for async - could use native async
- [ ] No rate limiting on chat endpoint
- [ ] No authentication required (single-user assumption)
- [ ] Streaming error handling could be improved

---

## Future Improvements

- [ ] Implement WebSocket for true bidirectional streaming
- [ ] Add conversation history persistence to database
- [ ] Implement RAG with ChromaDB for knowledge retrieval
- [ ] Add temperature and other model parameter controls
- [ ] Implement JWT authentication
- [ ] Add rate limiting
- [ ] Context window management for long conversations

---

## Testing Coverage

### Current Tests
- None (backend tests not implemented)

### Required Tests
- [ ] Unit tests for LLMService.generate_response
- [ ] Unit tests for command detection
- [ ] Integration tests for chat endpoint
- [ ] Test streaming response format
- [ ] Test error scenarios (Ollama down, invalid input)

---

## Security Considerations

### Implemented
- Input validation via Pydantic models
- CORS restricted to localhost

### Needed
- Authentication for chat endpoint
- Rate limiting to prevent abuse
- Input sanitization for potential prompt injection
- Audit logging of all chat interactions

---

## Performance Notes

- Current: ~1-2 second latency for first token (depends on model)
- Streaming provides better UX for long responses
- ThreadPoolExecutor limits concurrent requests

---

**Specification Created:** 2025-11-18
**Last Updated:** 2025-11-18
