# Feature: Chat Interface UI

## Status
**Retroactive specification** - Feature implemented and operational

## Overview
React-based web interface providing a split-panel layout with markdown viewer/file browser on the left and chat interface on the right. Primary user-facing component of the system.

---

## Current Behavior

### Layout
- **Left Panel:** Markdown viewer with collapsible file browser sidebar
- **Right Panel:** Chat messages and input field
- **Responsive:** Adapts to different screen sizes

### Capabilities
1. Send messages to backend
2. Display AI responses
3. Browse Obsidian vault files
4. View markdown content with GFM rendering
5. Load and display file content

---

## Technical Implementation

### Files
- [ChatInterface.tsx](frontend/src/components/ChatInterface.tsx) - Main component
- [App.tsx](frontend/src/App.tsx) - App wrapper
- [main.tsx](frontend/src/main.tsx) - Entry point
- [file-browser.spec.ts](frontend/tests/file-browser.spec.ts) - E2E tests

### Component Structure
```
ChatInterface (257 lines)
├── State: messages, input, loading, files, activeFile, sidebarOpen
├── useEffect: fetch files on mount
├── handlers: sendMessage, selectFile, toggleSidebar
└── Render:
    ├── MD Viewer Panel
    │   ├── Sidebar (file browser)
    │   └── Content (markdown)
    └── Chat Panel
        ├── Messages list
        └── Input field
```

---

## Acceptance Criteria (Current State)

### Initial Load
- GIVEN the application URL
  WHEN user navigates to the page
  THEN chat interface loads
  AND welcome message is displayed
  AND vault files are fetched automatically

### Send Message
- GIVEN text in the input field
  WHEN user presses Enter or clicks Send
  THEN message appears in chat history
  AND loading indicator shows
  AND AI response is received and displayed

### Send Message - Empty Input
- GIVEN empty input field
  WHEN user attempts to send
  THEN no message is sent
  AND no error occurs

### File Browser - Toggle
- GIVEN chat interface loaded
  WHEN user clicks sidebar toggle button
  THEN file browser sidebar opens/closes
  AND overlay appears when sidebar is open

### File Browser - List Files
- GIVEN sidebar is open
  WHEN vault files are loaded
  THEN files are displayed in list
  AND file names are visible

### File Browser - Select File
- GIVEN file list displayed
  WHEN user clicks on a file
  THEN file content is fetched
  AND content displays in markdown viewer
  AND file is highlighted as active

### Markdown Rendering
- GIVEN file content loaded
  WHEN content contains markdown
  THEN renders with GitHub Flavored Markdown
  AND headings, lists, code blocks display correctly

### Close Sidebar via Overlay
- GIVEN sidebar is open
  WHEN user clicks the overlay
  THEN sidebar closes

### Loading State
- GIVEN a message was sent
  WHEN waiting for response
  THEN loading indicator is displayed
  AND input may be disabled

### Error Display
- GIVEN an API error occurs
  WHEN response is received
  THEN error message is displayed to user

---

## UI Components

### Header
- Application title
- Navigation (if any)

### Left Panel (MD Viewer)
```
┌────────────────────────┐
│ [Toggle] File Title    │
├────────────────────────┤
│                        │
│  Rendered Markdown     │
│  Content               │
│                        │
└────────────────────────┘

Sidebar (overlay):
┌──────────┐
│ Files    │
├──────────┤
│ file1.md │
│ file2.md │
│ ...      │
└──────────┘
```

### Right Panel (Chat)
```
┌────────────────────────┐
│ Messages               │
├────────────────────────┤
│ User: Hello            │
│ AI: Hi there!          │
│ ...                    │
├────────────────────────┤
│ [Input field    ][Send]│
└────────────────────────┘
```

---

## State Management

### Component State
```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [input, setInput] = useState('');
const [loading, setLoading] = useState(false);
const [files, setFiles] = useState<VaultFile[]>([]);
const [activeFile, setActiveFile] = useState<string | null>(null);
const [fileContent, setFileContent] = useState<string>('');
const [sidebarOpen, setSidebarOpen] = useState(false);
```

### Message Type
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
}
```

### VaultFile Type
```typescript
interface VaultFile {
  path: string;
  name: string;
  folder: string;
}
```

---

## API Integration

### Endpoints Used
- `POST /chat/message` - Send chat message
- `GET /vault/files` - List vault files
- `GET /vault/file?path={path}` - Get file content

### Configuration
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## Testing Coverage

### Current E2E Tests (Playwright)
10 tests covering:
- [x] Main interface loads
- [x] Welcome content displays
- [x] File browser opens/closes
- [x] Vault files display
- [x] File content loads
- [x] Active file highlighting
- [x] Markdown rendering with GFM
- [x] Sequential file loading
- [x] Sidebar overlay closes sidebar
- [x] Chat interface displays

### Running Tests
```bash
npm test              # Run all tests
npm run test:ui       # Interactive UI
npm run test:headed   # See browser
```

---

## Known Issues / Tech Debt

- [ ] All state in single component (no state management library)
- [ ] Messages not persisted (lost on refresh)
- [ ] No conversation history across sessions
- [ ] No message editing or deletion
- [ ] No streaming response rendering
- [ ] Limited mobile responsiveness
- [ ] No dark mode support
- [ ] No keyboard shortcuts
- [ ] No accessibility (a11y) implementation
- [ ] File browser doesn't show folder structure
- [ ] No search in file browser

---

## Future Improvements

### Short-term
- [ ] Add message persistence to localStorage
- [ ] Implement streaming response display
- [ ] Add dark mode toggle
- [ ] Improve mobile layout
- [ ] Add keyboard shortcuts (Ctrl+Enter to send)

### Medium-term
- [ ] Extract to smaller components
- [ ] Add state management (Zustand or similar)
- [ ] Folder tree view in file browser
- [ ] Search files in sidebar
- [ ] Message markdown rendering

### Long-term
- [ ] Full accessibility (WCAG 2.1 AA)
- [ ] Conversation history with sessions
- [ ] Message editing/deletion
- [ ] Code syntax highlighting
- [ ] Export conversation
- [ ] Goal tracking dashboard panel

---

## Dependencies

### Runtime
- react >= 19.2.0
- react-dom >= 19.2.0
- axios >= 1.13.2
- react-markdown >= 10.1.0
- remark-gfm >= 4.0.1

### Development
- typescript >= 5.9.3
- vite >= 7.2.2
- @playwright/test >= 1.56.1

---

## Accessibility Status

### Current
- Basic HTML semantics
- No specific a11y implementation

### Needed
- [ ] ARIA labels for interactive elements
- [ ] Keyboard navigation support
- [ ] Screen reader testing
- [ ] Color contrast validation
- [ ] Focus management

---

## Performance Notes

- Initial bundle: ~200KB (production)
- Files loaded on mount (may cause delay for large vaults)
- Messages stored in memory (no virtualization)
- Consider virtualized list for many messages

---

## Browser Support

### Tested
- Chrome/Chromium (Playwright tests)

### Expected to Work
- Firefox
- Safari
- Edge

### Not Supported
- Internet Explorer

---

**Specification Created:** 2025-11-18
**Last Updated:** 2025-11-18
