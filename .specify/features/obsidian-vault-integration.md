# Feature: Obsidian Vault Integration

## Status
**Retroactive specification** - Feature implemented and operational

## Overview
Read-only integration with Obsidian vault for file listing, content reading, and text search. Provides the knowledge base foundation for the AI assistant.

---

## Current Behavior

### Capabilities
1. List all markdown files in vault
2. Read specific file content by path
3. List recently modified files
4. Search vault content by text query

### Access Pattern
- Read-only access (no write operations)
- Path-safe operations with traversal protection
- Direct file system access to vault directory

---

## Technical Implementation

### Files
- [vault.py](backend/routers/vault.py) - Router with vault endpoints
- [obsidian_service.py](backend/services/obsidian_service.py) - Vault operations
- [file_tools.py](backend/services/tools/file_tools.py) - Path-safe file utilities

### API Endpoints

#### GET /vault/files
List all markdown files in vault

#### GET /vault/file?path={path}
Read specific file content

#### GET /vault/recent?limit={n}
List recently modified files

---

## Acceptance Criteria (Current State)

### List All Files
- GIVEN a configured Obsidian vault path
  WHEN GET /vault/files is called
  THEN returns list of all .md files
  AND each file includes path, name, and folder
  AND count of total files is included

### Read File Content
- GIVEN a valid file path in the vault
  WHEN GET /vault/file?path={path} is called
  THEN returns the file content as text
  AND status is 200

### Read File - Not Found
- GIVEN a path to a non-existent file
  WHEN GET /vault/file?path={path} is called
  THEN returns 404 Not Found
  AND error message indicates file not found

### Read File - Path Traversal Attempt
- GIVEN a path attempting directory traversal (e.g., "../../../etc/passwd")
  WHEN GET /vault/file?path={path} is called
  THEN returns 403 Forbidden
  AND access is denied

### Recent Files
- GIVEN vault with multiple files
  WHEN GET /vault/recent?limit=10 is called
  THEN returns up to 10 most recently modified files
  AND files are sorted by modification time descending

### Search Vault
- GIVEN a search query
  WHEN search is performed via /search command
  THEN searches all markdown files for matching text
  AND returns file paths, line numbers, and excerpts
  AND results are formatted for display

### Search - No Results
- GIVEN a query with no matches
  WHEN search is performed
  THEN returns empty results
  AND message indicates no matches found

---

## Response Schema

### List Files Response
```json
{
  "files": [
    {
      "path": "folder/note.md",
      "name": "note.md",
      "folder": "folder"
    }
  ],
  "count": 150
}
```

### File Content Response
```json
{
  "content": "# Note Title\n\nNote content here..."
}
```

### Search Results (via command)
```
Found 3 results for "query":

📄 folder/note1.md (line 15)
   ...excerpt with matched text...

📄 folder/note2.md (line 42)
   ...excerpt with matched text...
```

---

## Configuration

### Environment Variables
- `VAULT_PATH` - Absolute path to Obsidian vault directory

### Supported File Types
- `.md` (Markdown files only)

---

## Security Implementation

### Path Traversal Protection
```python
def is_path_safe(path: Path, allowed_base: Path) -> bool:
    resolved = path.resolve()
    return resolved.is_relative_to(allowed_base.resolve())
```

### Access Control
- All paths validated against vault base directory
- Symlinks resolved to prevent escape
- Read-only operations only

---

## Known Issues / Tech Debt

- [ ] No caching of file listings (hits filesystem on every request)
- [ ] Search is basic text grep (no fuzzy matching)
- [ ] No frontmatter parsing for metadata extraction
- [ ] No tag or link extraction
- [ ] Large vaults may have performance issues
- [ ] No pagination for file listings

---

## Future Improvements

- [ ] Implement file caching with invalidation on changes
- [ ] Parse YAML frontmatter for metadata
- [ ] Extract and index tags (#tag)
- [ ] Extract and resolve wiki links ([[link]])
- [ ] Add ChromaDB vector embeddings for semantic search
- [ ] Implement RAG pipeline for contextual retrieval
- [ ] Add file watcher for automatic re-indexing
- [ ] Pagination for large vaults
- [ ] Full-text search with ranking

---

## Testing Coverage

### Current Tests
- E2E tests for file browser UI (Playwright)
- No backend unit tests

### Required Tests
- [ ] Unit tests for ObsidianService methods
- [ ] Unit tests for FileTools path validation
- [ ] Integration tests for vault endpoints
- [ ] Test path traversal prevention
- [ ] Test with empty vault
- [ ] Test with deeply nested folders
- [ ] Performance tests with large vault

---

## Dependencies

### External
- Obsidian vault on accessible file system

### Internal
- FileTools for path-safe operations
- Environment config for vault path

---

## Performance Notes

- File listing: O(n) where n = number of files
- File reading: Single file I/O
- Search: Full scan of all files (no indexing)
- Consider caching for vaults with 1000+ files

---

## Edge Cases Handled

- Empty vault (returns empty list)
- Non-existent vault path (returns error)
- Files with special characters in names
- Deeply nested folder structures
- Binary files mixed with markdown (ignored)

---

**Specification Created:** 2025-11-18
**Last Updated:** 2025-11-18
