import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChatInterface.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface VaultFile {
  path: string;
  name: string;
  folder: string;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [files, setFiles] = useState<VaultFile[]>([]);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [mdContent, setMdContent] = useState<string>(`# Welcome to Your Personal AI Assistant

## Quick Start

This is your markdown viewer. Content from your Obsidian vault will appear here.

### Available Commands

- \`/search <query>\` - Search your vault
- \`/help\` - Show available commands

### Features

- **Goal Tracking** - Track your personal goals
- **Habit Monitoring** - Build and maintain habits
- **Task Management** - Organize your todos
- **Knowledge Base** - Search and reference your notes

---

Try typing a message in the chat to get started!
`);

  // Fetch file list on mount
  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await axios.get('http://localhost:8000/vault/files');
      setFiles(response.data.files);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    }
  };

  const loadFile = async (filePath: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/vault/file?path=${encodeURIComponent(filePath)}`);
      setMdContent(response.data.content);
      setCurrentFile(filePath);
      setSidebarOpen(false);
    } catch (error) {
      console.error('Failed to load file:', error);
      setMdContent(`# Error\n\nFailed to load file: ${filePath}`);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat/message', {
        messages: [...messages, userMessage],
        stream: false
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      {/* MD Viewer Panel */}
      <div className="md-viewer-panel">
        <div className="md-viewer-header">
          <button
            className="hamburger-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle file browser"
          >
            ☰
          </button>
          <h2>Note Viewer</h2>
          {currentFile && (
            <div className="current-file-name">{currentFile}</div>
          )}
        </div>

        {/* File Browser Sidebar */}
        <div className={`file-sidebar ${sidebarOpen ? 'open' : ''}`}>
          <div className="file-sidebar-header">
            <h3>Your Vault</h3>
            <button
              className="close-sidebar-btn"
              onClick={() => setSidebarOpen(false)}
            >
              ×
            </button>
          </div>
          <div className="file-list">
            {files.length === 0 ? (
              <div className="no-files">No files found</div>
            ) : (
              files.map((file) => (
                <div
                  key={file.path}
                  className={`file-item ${currentFile === file.path ? 'active' : ''}`}
                  onClick={() => loadFile(file.path)}
                >
                  <div className="file-icon">📄</div>
                  <div className="file-info">
                    <div className="file-name">{file.name}</div>
                    {file.folder && (
                      <div className="file-folder">{file.folder}</div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Overlay */}
        {sidebarOpen && (
          <div
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <div className="md-viewer-content">
          {mdContent ? (
            <div className="md-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {mdContent}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="md-viewer-empty">
              <div className="md-viewer-empty-icon">📄</div>
              <div>No note selected</div>
              <div style={{ fontSize: '14px', marginTop: '8px', opacity: 0.7 }}>
                Search results will appear here
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Panel */}
      <div className="chat-panel">
        <div className="chat-header">
          <h1>Personal AI Assistant</h1>
          <p>Powered by Qwen 2.5 Coder (Local LLM)</p>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <div className="empty-state-text">Start a conversation</div>
              <div className="empty-state-hint">
                Try asking about your goals, todos, or search your vault
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`message ${
                msg.role === 'user' ? 'message-user' : 'message-assistant'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="message-avatar">🤖</div>
              )}
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
              </div>
              {msg.role === 'user' && (
                <div className="message-avatar">👤</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="loading-indicator">
              <span>Thinking</span>
              <div className="loading-dots">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            </div>
          )}
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type a message... (Press Enter to send)"
              disabled={loading}
              className="input-field"
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              className="send-button"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
