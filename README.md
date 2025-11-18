# Personal AI System - Self-Hosted

A secure, self-hosted personal AI assistant with local LLM and web interface.

## Project Overview

**Goal:** Build a privacy-first, self-hosted AI system that integrates with your Obsidian knowledge base, runs on local hardware, and provides intelligent assistance without relying on external services.

**Key Features:**
- 🔒 **Security First** - End-to-end encryption, local processing, no cloud dependencies
- 🏠 **Self-Hosted** - Runs on your hardware (Mac dev, home server production)
- 🧠 **Local LLM** - Ollama-based AI with multiple model support
- 🌐 **Web Interface** - Clean, responsive web portal for chat and management
- 📚 **Knowledge Integration** - Direct access to Obsidian vault
- 📊 **Goal Tracking** - Built-in Q4 goal monitoring and accountability
- 🔔 **Proactive Nudging** - Context-aware reminders and check-ins

## Project Phases

### Phase 1: Mac Development (Weeks 1-3)
- Local development environment on M4 MacBook Pro
- Core LLM integration (Ollama)
- Basic web interface
- Obsidian vault integration
- Security foundations

### Phase 2: Home Server Deployment (Weeks 4-6)
- Docker containerization
- Secure remote access (Tailscale/Wireguard)
- Production hardening
- Monitoring and logging
- Backup systems

## Quick Start

```bash
# Clone the repository
cd /Users/jackdev/development/personal-ai-selfhosted

# Read the design docs
open docs/ARCHITECTURE.md
open docs/SECURITY.md
open docs/PHASE-1-PLAN.md

# Follow the implementation guide
open docs/IMPLEMENTATION-GUIDE.md
```

## Documentation

- [Personal Assistant Features](docs/PERSONAL-ASSISTANT-FEATURES.md) - Core features and commands
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [Security Design](docs/SECURITY.md) - Security model and threat analysis
- [Phase 1 Plan](docs/PHASE-1-PLAN.md) - Mac development roadmap
- [Phase 2 Plan](docs/PHASE-2-PLAN.md) - Home server deployment
- [Implementation Guide](docs/IMPLEMENTATION-GUIDE.md) - Step-by-step setup
- [Technology Stack](docs/TECH-STACK.md) - Technologies and rationale

## Tech Stack (Planned)

**Backend:**
- Python 3.11+ (FastAPI)
- Ollama (Local LLM)
- SQLite → PostgreSQL (dev → prod)

**Frontend:**
- React + TypeScript
- Tailwind CSS
- Vite

**Infrastructure:**
- Docker + Docker Compose
- Nginx (reverse proxy)
- Tailscale/Wireguard (secure access)

**Security:**
- Let's Encrypt (TLS)
- JWT authentication
- Rate limiting
- Input sanitization
- Encrypted storage

## Current Status

**Status:** Design Phase
**Last Updated:** 2025-11-09

- [x] Project structure created
- [ ] Architecture design (in progress)
- [ ] Security design (in progress)
- [ ] Phase 1 planning (in progress)
- [ ] Implementation guide (pending)

## Related Projects

- [Personal AI Assistant (Telegram)](../personal-ai-assistant) - Current Telegram bot system
- [Obsidian Vault](../../Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi) - Knowledge base

## License

Private project - All rights reserved

## Author

Jack (2025)
