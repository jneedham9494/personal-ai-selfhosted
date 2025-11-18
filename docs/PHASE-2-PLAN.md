# Phase 2: Home Server Deployment Plan

**Version:** 1.0
**Duration:** 3 weeks
**Platform:** Home Server + Tailscale VPN
**Goal:** Production-ready self-hosted AI system accessible remotely

---

## Overview

Phase 2 transforms your working Mac development system into a production-ready home server deployment. Focus on security, reliability, and remote access via Tailscale VPN.

**Success Criteria:**
- ✅ System runs in Docker containers
- ✅ Accessible via Tailscale from any device
- ✅ PostgreSQL database in production
- ✅ Automated backups configured
- ✅ Monitoring and logging active
- ✅ System survives reboots
- ✅ All Phase 1 features work identically

---

## Prerequisites

### Home Server Specs

**Minimum:**
- CPU: 4 cores
- RAM: 16GB
- Storage: 500GB SSD
- OS: Ubuntu 22.04 LTS

**Recommended:**
- CPU: 8+ cores (for Llama 3 70B)
- RAM: 32GB+
- Storage: 1TB NVMe SSD
- GPU: NVIDIA (optional, for faster inference)

### Network Requirements

- Home network with router access
- Static local IP for server (192.168.1.100)
- Tailscale account (free tier OK)
- No port forwarding needed (Tailscale handles this)

---

## Week 1: Containerization

### Day 1-2: Docker Setup

**Goal:** All services running in Docker containers

**Tasks:**
```gherkin
Given a working Phase 1 application
When containerizing the application
Then the system should have:
- Backend in Python container
- Frontend in Nginx container
- PostgreSQL in database container
- Ollama in GPU-enabled container (if GPU available)
- All services connected via Docker network
```

**Backend Dockerfile:**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 aiuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=aiuser:aiuser . .

# Switch to non-root user
USER aiuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: ai-postgres
    environment:
      POSTGRES_DB: personal_ai
      POSTGRES_USER: aiuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - ai-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aiuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: ai-backend
    environment:
      DATABASE_URL: postgresql://aiuser:${DB_PASSWORD}@postgres:5432/personal_ai
      OLLAMA_HOST: http://ollama:11434
      VAULT_PATH: /vault
      JWT_SECRET: ${JWT_SECRET}
    volumes:
      - ${OBSIDIAN_VAULT_PATH}:/vault:ro
      - ./backend/.ai:/app/.ai:ro
      - ./logs:/app/logs
    networks:
      - ai-network
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_healthy
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: ai-ollama
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - ai-network
    restart: unless-stopped
    # Uncomment for GPU support
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: ai-frontend
    ports:
      - "80:80"
    networks:
      - ai-network
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: ai-nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - ai-network
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

networks:
  ai-network:
    driver: bridge

volumes:
  postgres_data:
  ollama_data:
```

**Deliverables:**
- [ ] All services containerized
- [ ] Docker Compose orchestration working
- [ ] Health checks passing
- [ ] Volumes persisting data
- [ ] Non-root users in containers

### Day 3-4: PostgreSQL Migration

**Goal:** Migrate from SQLite to PostgreSQL

**Tasks:**
```gherkin
Given a SQLite database with development data
When migrating to PostgreSQL
Then the system should:
- Export all data from SQLite
- Create PostgreSQL schema
- Import data to PostgreSQL
- Verify data integrity
- Update application connection strings
```

**Migration Script:**

```python
# scripts/migrate_to_postgres.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch

def migrate_sqlite_to_postgres(
    sqlite_path: str,
    postgres_conn_string: str
):
    """Migrate SQLite database to PostgreSQL"""

    # Connect to databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    postgres_conn = psycopg2.connect(postgres_conn_string)

    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()

    try:
        # Get all tables
        sqlite_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in sqlite_cursor.fetchall()]

        for table in tables:
            print(f"Migrating table: {table}")

            # Get table schema
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns = sqlite_cursor.fetchall()

            # Get data
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()

            if not rows:
                print(f"  No data in {table}")
                continue

            # Insert into PostgreSQL
            placeholders = ','.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table} VALUES ({placeholders})"

            execute_batch(postgres_cursor, insert_query, rows)
            print(f"  Migrated {len(rows)} rows")

        postgres_conn.commit()
        print("Migration complete!")

    except Exception as e:
        postgres_conn.rollback()
        print(f"Migration failed: {e}")
        raise

    finally:
        sqlite_cursor.close()
        postgres_cursor.close()
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    migrate_sqlite_to_postgres(
        "backend/data/dev.db",
        "postgresql://aiuser:password@localhost:5432/personal_ai"
    )
```

**Database Schema Update:**

```sql
-- backend/migrations/001_initial_schema.sql

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    active_form VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed')),
    acceptance_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS command_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    command_name VARCHAR(100) NOT NULL,
    arguments TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT true,
    error_message TEXT
);

CREATE INDEX idx_chat_messages_user_created ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_todos_user_status ON todos(user_id, status);
CREATE INDEX idx_command_history_user ON command_history(user_id, executed_at DESC);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

**Deliverables:**
- [ ] PostgreSQL schema created
- [ ] Migration script tested
- [ ] All data migrated successfully
- [ ] Application uses PostgreSQL
- [ ] SQLite backup preserved

### Day 5-7: Ollama Model Setup

**Goal:** Install and configure Llama 3 models

**Tasks:**
```gherkin
Given Ollama running in container
When pulling models
Then the system should have:
- llama3:8b for fast responses
- llama3:70b for complex tasks (if resources allow)
- Model selection based on task complexity
- Automatic fallback to smaller model
```

**Model Setup Script:**

```bash
#!/bin/bash
# scripts/setup_ollama.sh

set -e

echo "🦙 Setting up Ollama models..."

# Pull Llama 3 8B (always)
echo "Pulling llama3:8b (required)..."
docker exec ai-ollama ollama pull llama3:8b

# Check available memory
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')

if [ "$TOTAL_RAM" -ge 32 ]; then
    echo "Sufficient RAM detected ($TOTAL_RAM GB)"
    echo "Pulling llama3:70b (optional)..."
    docker exec ai-ollama ollama pull llama3:70b
else
    echo "Insufficient RAM for llama3:70b ($TOTAL_RAM GB < 32 GB)"
    echo "Skipping 70B model..."
fi

# List installed models
echo ""
echo "Installed models:"
docker exec ai-ollama ollama list

echo ""
echo "✅ Ollama setup complete!"
```

**Model Selection Logic:**

```python
# backend/services/llm_service.py

class LLMService:
    def __init__(self):
        self.available_models = self._check_available_models()

    def _check_available_models(self) -> list[str]:
        """Check which models are available"""
        try:
            result = ollama.list()
            return [model['name'] for model in result['models']]
        except Exception:
            return ['llama3:8b']  # Default fallback

    def select_model(self, task_complexity: str = "medium") -> str:
        """Select appropriate model based on task complexity"""

        if task_complexity == "high" and "llama3:70b" in self.available_models:
            return "llama3:70b"
        else:
            return "llama3:8b"

    async def generate_response(
        self,
        messages: list[dict],
        complexity: str = "medium"
    ) -> AsyncGenerator[str, None]:
        """Generate response with appropriate model"""

        model = self.select_model(complexity)
        print(f"Using model: {model}")

        # ... rest of implementation
```

**Deliverables:**
- [ ] llama3:8b installed
- [ ] llama3:70b installed (if RAM >= 32GB)
- [ ] Model selection logic working
- [ ] Automatic fallback tested

---

## Week 2: Tailscale VPN and Security

### Day 8-9: Tailscale Setup

**Goal:** Secure remote access via Tailscale VPN

**Tasks:**
```gherkin
Given a home server with Tailscale installed
When accessing from remote device
Then the user should:
- Connect to Tailscale network
- Access AI system via Tailscale IP
- Have encrypted connection
- Experience normal performance
- Not need port forwarding
```

**Installation:**

```bash
#!/bin/bash
# scripts/setup_tailscale.sh

set -e

echo "🔒 Installing Tailscale..."

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale
sudo tailscale up --ssh

# Get Tailscale IP
TAILSCALE_IP=$(tailscale ip -4)

echo ""
echo "✅ Tailscale installed!"
echo "Server IP: $TAILSCALE_IP"
echo ""
echo "Access your AI system at: https://$TAILSCALE_IP"
echo ""
echo "Install Tailscale on other devices:"
echo "  - Mac: brew install tailscale"
echo "  - iPhone: App Store → Tailscale"
echo "  - Android: Play Store → Tailscale"
```

**Nginx Configuration for Tailscale:**

```nginx
# nginx/nginx.conf

server {
    listen 443 ssl http2;
    server_name ai.home.local;

    # TLS 1.3 only
    ssl_protocols TLSv1.3;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Auth endpoints (stricter rate limit)
    location /api/auth/ {
        limit_req zone=login burst=3 nodelay;

        proxy_pass http://backend:8000/auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Deliverables:**
- [ ] Tailscale installed on server
- [ ] Tailscale installed on Mac/iPhone
- [ ] Can access system via Tailscale IP
- [ ] HTTPS working with self-signed cert
- [ ] All features work remotely

### Day 10-11: Firewall Configuration

**Goal:** Lock down server, only allow Tailscale

**Tasks:**
```gherkin
Given a home server with services running
When configuring the firewall
Then the server should:
- Drop all incoming connections by default
- Allow Tailscale interface (tailscale0)
- Allow outbound connections
- Block all public ports
- Log blocked connection attempts
```

**UFW Setup:**

```bash
#!/bin/bash
# scripts/setup_firewall.sh

set -e

echo "🔥 Configuring firewall..."

# Reset UFW to default
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow Tailscale interface
sudo ufw allow in on tailscale0

# Allow SSH only from local network (backup access)
sudo ufw allow from 192.168.1.0/24 to any port 22

# Enable UFW
sudo ufw --force enable

# Show status
sudo ufw status verbose

echo ""
echo "✅ Firewall configured!"
echo ""
echo "⚠️  IMPORTANT: SSH is only accessible from local network"
echo "    Use Tailscale SSH for remote access: tailscale ssh"
```

**Intrusion Detection (Optional):**

```bash
# Install fail2ban for additional protection
sudo apt install fail2ban

# Configure jail
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Deliverables:**
- [ ] UFW firewall active
- [ ] Only Tailscale connections allowed
- [ ] SSH restricted to local network
- [ ] Fail2ban monitoring SSH
- [ ] Connection logs reviewed

### Day 12-14: Backup and Monitoring

**Goal:** Automated backups and system monitoring

**Tasks:**
```gherkin
Given a production system with data
When backup system is configured
Then the system should:
- Backup database daily
- Backup configuration files
- Encrypt backups with GPG
- Retain 7 daily + 4 weekly backups
- Alert on backup failure
```

**Backup Script:**

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y-%m-%d-%H%M%S)
BACKUP_NAME="ai-backup-$DATE"

echo "🗄️  Starting backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup PostgreSQL
echo "Backing up database..."
docker exec ai-postgres pg_dump -U aiuser personal_ai > "$BACKUP_DIR/$BACKUP_NAME/database.sql"

# Backup configuration
echo "Backing up configuration..."
cp -r .ai "$BACKUP_DIR/$BACKUP_NAME/"
cp docker-compose.yml "$BACKUP_DIR/$BACKUP_NAME/"
cp .env "$BACKUP_DIR/$BACKUP_NAME/"

# Create tarball
echo "Creating archive..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"

# Encrypt backup
echo "Encrypting backup..."
gpg --symmetric --cipher-algo AES256 "$BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Clean up unencrypted files
rm -rf "$BACKUP_DIR/$BACKUP_NAME"
rm "$BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Rotate old backups (keep 7 daily)
echo "Rotating old backups..."
ls -t "$BACKUP_DIR"/*.tar.gz.gpg | tail -n +8 | xargs -r rm

echo "✅ Backup complete: $BACKUP_NAME.tar.gz.gpg"
```

**Cron Setup:**

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/aiuser/personal-ai-selfhosted/scripts/backup.sh >> /var/log/ai-backup.log 2>&1

# Weekly backup on Sunday at 3 AM (keep forever)
0 3 * * 0 /home/aiuser/personal-ai-selfhosted/scripts/backup.sh weekly >> /var/log/ai-backup.log 2>&1
```

**Monitoring Script:**

```bash
#!/bin/bash
# scripts/healthcheck.sh

set -e

echo "🏥 Health Check $(date)"

# Check Docker containers
echo "Checking containers..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep ai-

# Check disk space
echo ""
echo "Disk usage:"
df -h / /backups

# Check memory
echo ""
echo "Memory usage:"
free -h

# Check Ollama
echo ""
echo "Ollama status:"
curl -s http://localhost:11434/api/tags | jq '.models | length' || echo "ERROR"

# Check database
echo ""
echo "Database status:"
docker exec ai-postgres pg_isready -U aiuser || echo "ERROR"

# Check API
echo ""
echo "API status:"
curl -s http://localhost:8000/health | jq '.status' || echo "ERROR"

echo ""
echo "✅ Health check complete"
```

**Systemd Service for Auto-Start:**

```ini
# /etc/systemd/system/personal-ai.service

[Unit]
Description=Personal AI Assistant
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/aiuser/personal-ai-selfhosted
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=aiuser
Group=aiuser

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl enable personal-ai.service
sudo systemctl start personal-ai.service
```

**Deliverables:**
- [ ] Daily automated backups
- [ ] Backup encryption working
- [ ] Backup rotation configured
- [ ] Health check script running
- [ ] System auto-starts on reboot
- [ ] Monitoring logs reviewed

---

## Week 3: Testing and Optimization

### Day 15-17: End-to-End Testing

**Goal:** Verify all features work in production environment

**Test Scenarios:**

```gherkin
Scenario: Remote chat access via Tailscale
  Given I am connected to Tailscale on my iPhone
  When I visit https://<tailscale-ip>
  Then I should see the chat interface
  And I can send messages
  And I receive responses from Llama 3

Scenario: Slash command execution
  Given I am chatting with the AI
  When I send "/vmodel Implement user settings page"
  Then the command should execute
  And I should see V-Model workflow steps
  And TODOs should be created

Scenario: Tool usage (vault search)
  Given I request "Search my vault for Q4 goals"
  When the AI uses the search_vault tool
  Then I should see results from my Obsidian vault
  And the results should be accurate

Scenario: Hook execution
  Given I create a TODO with acceptance criteria
  When the TODO is saved
  Then the lint-gherkin hook should run
  And invalid Gherkin should be rejected

Scenario: Agent spawning
  Given I request "Find all Python files with 'auth' in the name"
  When the AI spawns an explore agent
  Then the agent should find the files
  And return a concise list

Scenario: System recovery after reboot
  Given the server is rebooted
  When the system starts up
  Then all Docker containers should start automatically
  And the system should be accessible
  And all data should be preserved

Scenario: Backup and restore
  Given a backup file exists
  When I restore from backup
  Then all data should be recovered
  And the system should function normally
```

**Testing Checklist:**
- [ ] Web interface loads
- [ ] Can send/receive messages
- [ ] Slash commands work
- [ ] Tools execute correctly
- [ ] Hooks block/allow as expected
- [ ] Agents spawn and complete tasks
- [ ] TODOs track properly
- [ ] Vault search works
- [ ] System survives reboot
- [ ] Backups can be restored
- [ ] Performance acceptable (<2s response)
- [ ] No memory leaks (run 24h test)

### Day 18-19: Performance Optimization

**Goal:** Optimize for production performance

**Optimization Areas:**

1. **Database Query Optimization:**
   ```sql
   -- Add missing indexes
   CREATE INDEX idx_chat_messages_content_search ON chat_messages USING gin(to_tsvector('english', content));
   CREATE INDEX idx_todos_acceptance_criteria ON todos USING gin(to_tsvector('english', acceptance_criteria));
   ```

2. **Caching Layer:**
   ```python
   # Add Redis for caching
   from redis import Redis

   cache = Redis(host='redis', port=6379, decode_responses=True)

   @cache_result(ttl=3600)
   def search_vault(query: str):
       # Cache search results for 1 hour
       pass
   ```

3. **Connection Pooling:**
   ```python
   # PostgreSQL connection pool
   from sqlalchemy import create_engine
   from sqlalchemy.pool import QueuePool

   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True
   )
   ```

4. **Response Streaming:**
   ```python
   # Stream LLM responses for faster perceived performance
   @router.post("/chat/message")
   async def chat_stream(request: ChatRequest):
       return StreamingResponse(
           llm_service.generate_stream(request.messages),
           media_type="text/event-stream"
       )
   ```

**Deliverables:**
- [ ] Database queries optimized
- [ ] Response times < 2 seconds
- [ ] Streaming responses working
- [ ] No memory leaks after 24h
- [ ] CPU usage reasonable (<50%)

### Day 20-21: Documentation and Handoff

**Goal:** Complete production documentation

**Documentation to Create:**

1. **Production Operations Guide:**
   - How to start/stop services
   - How to check logs
   - How to run backups manually
   - How to restore from backup
   - How to update the system
   - How to add new slash commands
   - How to add new agents

2. **Troubleshooting Guide:**
   - Container won't start → Check logs
   - Can't connect via Tailscale → Check firewall
   - Slow responses → Check Ollama model
   - Database errors → Check disk space
   - Common error messages and fixes

3. **Security Checklist:**
   - [ ] Firewall configured
   - [ ] Tailscale VPN only access
   - [ ] Strong passwords set
   - [ ] JWT secret rotated
   - [ ] Database encrypted
   - [ ] Backups encrypted
   - [ ] Logs not containing secrets
   - [ ] Security headers set
   - [ ] Rate limiting active

**Deliverables:**
- [ ] Operations guide complete
- [ ] Troubleshooting guide complete
- [ ] Security checklist verified
- [ ] All credentials documented (securely)
- [ ] Disaster recovery plan documented

---

## Phase 2 Completion Checklist

### Infrastructure
- [ ] All services in Docker
- [ ] Docker Compose orchestration
- [ ] PostgreSQL production database
- [ ] Ollama with Llama 3 models
- [ ] Nginx reverse proxy with TLS

### Security
- [ ] Tailscale VPN configured
- [ ] Firewall locked down
- [ ] TLS certificates installed
- [ ] Rate limiting active
- [ ] Security headers set
- [ ] Fail2ban monitoring

### Reliability
- [ ] Automated backups daily
- [ ] Backup encryption working
- [ ] System auto-starts on reboot
- [ ] Health monitoring active
- [ ] Logs rotated automatically

### Performance
- [ ] Response times < 2 seconds
- [ ] No memory leaks
- [ ] Database optimized
- [ ] Caching implemented

### Accessibility
- [ ] Accessible from Mac
- [ ] Accessible from iPhone
- [ ] Works over Tailscale
- [ ] HTTPS enabled
- [ ] WebSocket support

---

## Success Metrics

**Technical:**
- 99.9% uptime (< 9 hours downtime/year)
- All backups successful
- No security incidents
- Response time < 2 seconds

**User Experience:**
- Indistinguishable from Phase 1
- Accessible from anywhere
- Fast enough for natural conversation
- Reliable and trustworthy

---

## Maintenance Plan

### Daily
- Automated backup (2 AM)
- Health check (via cron)
- Log monitoring (automatic)

### Weekly
- Review logs for errors
- Check disk space
- Test backup restore
- Update system packages

### Monthly
- Security updates
- Performance review
- Dependency updates
- User feedback review

---

## Disaster Recovery

### Scenario 1: Database Corruption
1. Stop all services
2. Restore from latest backup
3. Verify data integrity
4. Restart services
5. Monitor for issues

### Scenario 2: Server Hardware Failure
1. Acquire new hardware
2. Install Ubuntu 22.04
3. Install Docker and Tailscale
4. Restore from backup
5. Update Tailscale IP in configs

### Scenario 3: Accidental Data Deletion
1. Don't panic
2. Stop services immediately
3. Restore from most recent backup before deletion
4. Verify restoration
5. Resume operations

---

**Last Updated:** 2025-11-09
**Status:** Ready for Implementation
**Estimated Effort:** 60-80 hours over 3 weeks
**Prerequisites:** Completed Phase 1
