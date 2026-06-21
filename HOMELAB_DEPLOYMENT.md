# Deploying to Homelab

This guide explains how to deploy the Personal AI System to the homelab production environment.

## Homelab Overview

The homelab is the **production environment** - services deployed here should be stable and run continuously. Development and testing happens in this project directory.

**Homelab location:** `/home/devbox2/Projects/homelab` (or `/mnt/fast/home/Projects/homelab`)

### Deployment Structure

The homelab uses a phased deployment model:

```
homelab/
├── podman-compose/
│   ├── core/          # Caddy, Homepage, AdGuard, Vaultwarden
│   ├── security/      # Authelia, CrowdSec
│   ├── ai/            # Ollama, Open WebUI, Whisper, SD, AnythingLLM, ChromaDB
│   ├── intelligence/  # n8n automation
│   ├── knowledge/     # Memos, Paperless, Immich
│   ├── capture/       # Miniflux, ArchiveBox, TubeArchivist
│   ├── privacy/       # SearXNG, Invidious
│   ├── dev/           # Gitea, Code-server
│   ├── voice/         # Piper, OpenWakeWord
│   └── extras/        # Jellyfin, Grafana, Actual
├── config/            # Configuration files
├── data/              # Persistent data
└── .env               # Environment variables
```

---

## Integration Points

Your Personal AI System can leverage existing homelab services:

| Service | Internal URL | Purpose |
|---------|--------------|---------|
| **Ollama** | `http://ollama:11434` | LLM inference (Llama 3, etc.) |
| **ChromaDB** | `http://chromadb:8000` | Vector embeddings for RAG |
| **PostgreSQL** | Deploy your own or share existing | User data, sessions |
| **Authelia** | SSO via Caddy `import authelia` | Optional: Use homelab SSO |

### Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      homelab network                         │
│  Caddy ←→ All services that need external/internet access   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      isolated network                        │
│  Internal service-to-service communication only             │
│  Ollama, ChromaDB, PostgreSQL, your backend                 │
└─────────────────────────────────────────────────────────────┘
```

- **homelab network**: Services that need internet access (model downloads, external APIs)
- **isolated network**: Internal service communication (LLM calls, database)

---

## Deployment Steps

### 1. Prepare Your Service

Before deployment, ensure:

- [ ] Docker/Podman image builds successfully
- [ ] App works with environment variables (not hardcoded config)
- [ ] No secrets in code (use `.env`)
- [ ] Health check endpoint exists (`/health`)
- [ ] Tested locally with Ollama connection

### 2. Create Compose File

Create `homelab/podman-compose/intelligence/personal-ai.yml` or add to existing compose:

```yaml
# Personal AI System
# Add to intelligence/ or create new phase

networks:
  homelab:
    external: true
  isolated:
    external: true

services:
  # ===========================================
  # Personal AI - Backend API
  # ===========================================
  personal-ai-backend:
    build:
      context: /home/devbox2/Projects/development/personal-ai-selfhosted/backend
      dockerfile: Dockerfile
    # Or use pre-built image:
    # image: personal-ai-backend:latest
    container_name: personal-ai-backend
    restart: unless-stopped
    volumes:
      - ${DATA_DIR}/personal-ai/data:/app/data
      # Read-only access to Obsidian vault
      - ${DATA_DIR}/obsidian:/app/vault:ro
    networks:
      - isolated
    environment:
      - TZ=${TZ:-America/New_York}
      - DATABASE_URL=sqlite:///app/data/personal-ai.db
      # Or PostgreSQL:
      # - DATABASE_URL=postgresql://personal_ai:${PERSONAL_AI_DB_PASSWORD}@personal-ai-db:5432/personal_ai
      - OLLAMA_BASE_URL=http://ollama:11434
      - CHROMA_HOST=http://chromadb:8000
      - VAULT_PATH=/app/vault
      - JWT_SECRET=${PERSONAL_AI_JWT_SECRET}
      - LOG_LEVEL=INFO
    depends_on:
      - personal-ai-frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ===========================================
  # Personal AI - Frontend
  # ===========================================
  personal-ai-frontend:
    build:
      context: /home/devbox2/Projects/development/personal-ai-selfhosted/frontend
      dockerfile: Dockerfile
    container_name: personal-ai-frontend
    restart: unless-stopped
    networks:
      - isolated
    environment:
      - VITE_API_URL=/api
    # Static files served by Caddy, or:
    # ports:
    #   - "127.0.0.1:3001:80"

  # ===========================================
  # Personal AI - Database (Optional)
  # ===========================================
  # personal-ai-db:
  #   image: docker.io/postgres:16-alpine
  #   container_name: personal-ai-db
  #   restart: unless-stopped
  #   volumes:
  #     - ${DATA_DIR}/personal-ai/postgres:/var/lib/postgresql/data
  #   networks:
  #     - isolated
  #   environment:
  #     - POSTGRES_DB=personal_ai
  #     - POSTGRES_USER=personal_ai
  #     - POSTGRES_PASSWORD=${PERSONAL_AI_DB_PASSWORD}
  #   healthcheck:
  #     test: ["CMD-SHELL", "pg_isready -U personal_ai"]
  #     interval: 10s
  #     timeout: 5s
  #     retries: 5
```

### 3. Add Environment Variables

Add to `homelab/.env`:

```bash
# ===========================================
# Personal AI System
# ===========================================
PERSONAL_AI_JWT_SECRET=  # Generate: openssl rand -hex 32
PERSONAL_AI_DB_PASSWORD= # Generate: openssl rand -base64 24
```

### 4. Configure Caddy

Add to `homelab/config/caddy/Caddyfile`:

```caddyfile
# Personal AI System
assistant.homelab.local {
    import authelia  # Require SSO login

    # API routes to backend
    handle /api/* {
        reverse_proxy personal-ai-backend:8000
    }

    # WebSocket for streaming
    handle /ws/* {
        reverse_proxy personal-ai-backend:8000
    }

    # Frontend static files
    handle {
        reverse_proxy personal-ai-frontend:80
    }
}
```

**Alternative:** If using JWT auth instead of Authelia:

```caddyfile
# Personal AI System (own auth)
assistant.homelab.local {
    reverse_proxy personal-ai-backend:8000
}
```

### 5. Add to Homepage Dashboard

Add to `homelab/config/homepage/services.yaml` under the AI section:

```yaml
- AI:
    # ... existing services ...
    - Personal AI:
        href: https://assistant.homelab.local
        icon: mdi-robot
        description: Personal AI Assistant
        server: my-docker
        container: personal-ai-backend
```

Update `homelab/config/homepage/settings.yaml` if needed to adjust column layout.

### 6. Create Data Directories

```bash
mkdir -p /mnt/fast/home/Projects/homelab/data/personal-ai/{data,postgres}

# If using Obsidian integration, create symlink or mount
ln -s /path/to/your/obsidian/vault /mnt/fast/home/Projects/homelab/data/obsidian
```

### 7. Deploy

```bash
cd /mnt/fast/home/Projects/homelab/podman-compose/intelligence
podman-compose up -d

# Or if added to a new phase:
# ./scripts/start-all.sh
```

### 8. Verify

```bash
# Check container status
podman ps | grep personal-ai

# Check logs
podman logs -f personal-ai-backend

# Test endpoint
curl https://assistant.homelab.local/health
```

---

## Dockerfile Examples

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile (Nginx)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

## Connecting to Ollama

Your backend should connect to Ollama at `http://ollama:11434`:

```python
# backend/services/llm_service.py
import httpx

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

async def chat(messages: list, model: str = "llama3"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=120.0
        )
        return response.json()
```

Models available in homelab (check with `podman exec ollama ollama list`):
- `llama3` - General purpose
- `nomic-embed-text` - Embeddings for RAG
- Others as installed

---

## Connecting to ChromaDB

ChromaDB is available at `http://chromadb:8000`:

```python
# backend/services/rag_service.py
import chromadb

CHROMA_HOST = os.getenv("CHROMA_HOST", "http://chromadb:8000")

client = chromadb.HttpClient(host="chromadb", port=8000)

# Create collection for your app
collection = client.get_or_create_collection(
    name="personal_ai_vault",
    metadata={"hnsw:space": "cosine"}
)
```

---

## Pre-Deployment Checklist

- [ ] Backend builds and runs locally
- [ ] Frontend builds and serves correctly
- [ ] Environment variables documented in `.env.example`
- [ ] Ollama connection tested (can reach `http://localhost:11434` locally)
- [ ] Database migrations work
- [ ] Health endpoint returns 200 OK
- [ ] No hardcoded secrets or paths
- [ ] Dockerfile tested with `podman build`

---

## Rollback

If deployment fails:

```bash
# Stop the service
podman-compose down

# Check logs for issues
podman logs personal-ai-backend

# Revert changes to Caddyfile if needed
podman restart caddy
```

---

## Development Workflow

1. **Develop** in this project (`personal-ai-selfhosted/`)
2. **Test** with local Ollama and SQLite
3. **Build** Docker image when ready
4. **Deploy** to homelab using steps above
5. **Monitor** via Grafana dashboards

The homelab should be treated as production - changes should be tested before deployment.
