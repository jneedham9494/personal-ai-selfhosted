# Security Design

**Version:** 1.0
**Date:** 2025-11-09
**Security Level:** HIGH

---

## Threat Model

### Assets to Protect

1. **Personal Data**
   - Obsidian vault (Q4 goals, daily notes, personal information)
   - Chat history and conversations
   - User credentials
   - API tokens

2. **System Resources**
   - LLM compute (prevent abuse)
   - Disk space
   - Network bandwidth
   - Home server uptime

3. **Code and IP**
   - Personal projects
   - Configuration files
   - Custom slash commands and agents

### Threat Actors

1. **External Attackers**
   - Random internet scanners
   - Targeted attacks (unlikely but prepare anyway)
   - Bot networks

2. **Internal Threats**
   - Compromised dependencies
   - Malicious LLM prompt injection
   - Accidental data exposure

3. **Physical Threats**
   - Laptop theft
   - Home server physical access
   - Network eavesdropping (local network)

---

## Security Principles

### 1. Defense in Depth

**Layer 1: Network**
- Tailscale/Wireguard VPN (encrypted tunnel)
- No public ports exposed
- Firewall rules (drop all except VPN)

**Layer 2: Application**
- TLS 1.3 (even within VPN for practice)
- Rate limiting (per-user, per-endpoint)
- Input sanitization
- CSRF protection

**Layer 3: Authentication**
- JWT tokens (short-lived)
- Bcrypt password hashing (cost factor 12)
- Session management
- Logout invalidates tokens

**Layer 4: Authorization**
- Single user (you) - simplifies model
- Future: Role-based access control

**Layer 5: Data**
- Encrypted backups
- Sensitive data never logged
- Secure deletion on logout

### 2. Least Privilege

**LLM Permissions:**
- Read-only access to Obsidian vault
- Sandboxed bash execution
- No sudo/root access
- Whitelisted commands only

**Application Permissions:**
- Non-root user (UID 1000)
- Read-only vault mount
- Write access only to database
- No network access from LLM container

### 3. Zero Trust

**Every Request:**
- Must have valid JWT
- Must pass rate limit check
- Must be within timeout
- Must match expected schema

**Every Tool Call:**
- Validated against whitelist
- Sandboxed execution
- Timeout enforced
- Result sanitized

---

## Security Implementation

### Authentication Flow

```
1. User visits https://ai.home.local
    ↓
2. Nginx serves login page (React app)
    ↓
3. User enters credentials
    ↓
4. POST /auth/login (HTTPS)
    ↓
5. Backend validates username/password
    ↓
6. Bcrypt.verify(password, hash)
    ↓
7. Generate JWT (expires in 1 hour)
    ↓
8. Return JWT + refresh token (7 days)
    ↓
9. Frontend stores in httpOnly cookie
    ↓
10. All subsequent requests include JWT in Authorization header
```

**JWT Payload:**
```json
{
  "sub": "user_id",
  "username": "jack",
  "iat": 1699564800,
  "exp": 1699568400,
  "jti": "unique_token_id"
}
```

**Security Features:**
- Short expiration (1 hour)
- Refresh token rotation
- Token revocation list (Redis/DB)
- HTTPS-only cookies
- SameSite=Strict

### Password Security

**Storage:**
```python
import bcrypt

# Registration
password_hash = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt(rounds=12)  # Cost factor 12 (256ms on modern CPU)
)

# Login
is_valid = bcrypt.checkpw(
    password.encode('utf-8'),
    stored_hash
)
```

**Requirements:**
- Minimum 12 characters
- Must include: uppercase, lowercase, number, symbol
- No common passwords (check against list)
- No password reuse (check last 3 hashes)

### Input Sanitization

**Text Inputs:**
```python
from bleach import clean
from html import escape

def sanitize_input(text: str, allow_markdown: bool = False) -> str:
    """Sanitize user input"""

    # Remove null bytes
    text = text.replace('\x00', '')

    # Limit length
    if len(text) > 10000:
        raise ValueError("Input too long")

    if allow_markdown:
        # Allow safe markdown, strip dangerous HTML
        allowed_tags = ['p', 'br', 'strong', 'em', 'code', 'pre']
        text = clean(text, tags=allowed_tags, strip=True)
    else:
        # Escape all HTML
        text = escape(text)

    return text
```

**File Paths:**
```python
from pathlib import Path

def sanitize_path(user_path: str, base_dir: Path) -> Path:
    """Prevent path traversal attacks"""

    # Resolve to absolute path
    requested = (base_dir / user_path).resolve()

    # Ensure it's within base_dir
    if not requested.is_relative_to(base_dir):
        raise ValueError("Path traversal detected")

    # Ensure it exists
    if not requested.exists():
        raise FileNotFoundError("File not found")

    return requested
```

**Bash Commands:**
```python
import shlex

ALLOWED_COMMANDS = ['git', 'npm', 'python', 'pytest', 'ls', 'cat']
BLOCKED_PATTERNS = ['rm -rf /', 'dd ', '> /dev/', 'mkfs', 'chmod 777']

def sanitize_bash(command: str) -> str:
    """Validate bash command safety"""

    # Check for dangerous patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern in command.lower():
            raise ValueError(f"Dangerous command blocked: {pattern}")

    # Parse command
    try:
        tokens = shlex.split(command)
    except ValueError:
        raise ValueError("Invalid command syntax")

    # Check first token (command name)
    if tokens[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {tokens[0]}")

    return command
```

### TLS Configuration

**Nginx (Production):**
```nginx
server {
    listen 443 ssl http2;
    server_name ai.home.local;

    # TLS 1.3 only
    ssl_protocols TLSv1.3;

    # Strong cipher suites
    ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
    ssl_prefer_server_ciphers off;

    # Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/ai.home.local/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.home.local/privkey.pem;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;

    # Rate limiting
    limit_req zone=api burst=20 nodelay;
    limit_req_status 429;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Rate Limiting

**Per-User Limits:**
```python
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat/message")
@limiter.limit("60/minute")  # 60 requests per minute
async def chat_message(request: Request):
    pass

@app.post("/vault/search")
@limiter.limit("20/minute")  # 20 searches per minute
async def vault_search(request: Request):
    pass
```

**Global Limits (Nginx):**
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
```

### Secure Logging

**What to Log:**
- ✅ Authentication attempts (success/failure)
- ✅ API endpoint hits (without sensitive data)
- ✅ Rate limit violations
- ✅ Security events (blocked commands, path traversal attempts)
- ✅ System errors

**What NOT to Log:**
- ❌ Passwords
- ❌ JWT tokens
- ❌ Personal data from vault
- ❌ Full chat messages (log metadata only)

**Log Format:**
```json
{
  "timestamp": "2025-11-09T18:30:00Z",
  "level": "INFO",
  "event": "chat_message",
  "user_id": "uuid",
  "ip": "192.168.1.100",
  "endpoint": "/chat/message",
  "status": 200,
  "duration_ms": 1234,
  "tokens_used": 500
}
```

**Log Rotation:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

---

## Network Security

### Phase 1: Development (Mac)

```
┌─────────────────────────┐
│  M4 MacBook (localhost)  │
│                         │
│  All services local:    │
│  - Frontend: 3000       │
│  - Backend: 8000        │
│  - Ollama: 11434        │
│                         │
│  No external access     │
└─────────────────────────┘
```

**Security:**
- Localhost only (127.0.0.1)
- macOS firewall enabled
- No inbound connections

### Phase 2: Production (Home Server)

```
┌──────────────────────────────┐
│         Internet             │
└─────────┬────────────────────┘
          │
  ┌───────▼──────────┐
  │  Tailscale VPN   │
  │  (Encrypted)     │
  └───────┬──────────┘
          │
┌─────────▼─────────────────────┐
│    Home Network (192.168.1.x) │
│                               │
│  ┌──────────────────────────┐ │
│  │  Home Server            │ │
│  │  192.168.1.100          │ │
│  │                         │ │
│  │  Firewall Rules:        │ │
│  │  - Drop all inbound     │ │
│  │  - Allow Tailscale VPN  │ │
│  │  - Allow outbound       │ │
│  └──────────────────────────┘ │
└───────────────────────────────┘
```

**Why Tailscale:**
- WireGuard-based (modern, fast)
- Zero-config NAT traversal
- Encrypted by default
- No open ports needed
- Easy multi-device access (laptop, phone)

**Firewall Rules (UFW):**
```bash
# Default deny
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow Tailscale
sudo ufw allow in on tailscale0

# Enable
sudo ufw enable
```

---

## Data Security

### Encryption at Rest

**Database (PostgreSQL):**
```bash
# Enable encryption
# postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

**Backups:**
```bash
# Encrypted backup script
#!/bin/bash

# Dump database
pg_dump personal_ai > backup.sql

# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 backup.sql

# Upload to encrypted cloud storage (optional)
rclone copy backup.sql.gpg remote:backups/

# Clean up
rm backup.sql backup.sql.gpg
```

### Encryption in Transit

**All Communications:**
- TLS 1.3 for HTTPS
- WireGuard for VPN
- Encrypted WebSocket (WSS)

---

## Dependency Security

### Scanning

**Python Dependencies:**
```bash
# Check for known vulnerabilities
pip-audit

# Safety check
safety check

# Automated in CI/CD
```

**Docker Images:**
```bash
# Scan base images
docker scan python:3.11-slim

# Use minimal base images
FROM python:3.11-slim  # Not python:latest
```

### Update Policy

**Critical Updates:**
- Apply within 24 hours
- Test in dev first
- Rollback plan ready

**Regular Updates:**
- Weekly dependency check
- Monthly full update
- Changelog review

---

## Incident Response

### Detection

**Monitoring:**
- Failed login attempts (>5 in 1 hour)
- Rate limit violations (>100/hour)
- Suspicious commands (blocked patterns)
- Disk space alerts (<10% free)
- CPU/Memory spikes

**Alerts:**
```python
async def alert_admin(event: str, details: dict):
    """Send security alert"""

    # Log to file
    logger.critical(f"SECURITY EVENT: {event}", extra=details)

    # Send notification (email/Telegram)
    await notify(
        f"🚨 Security Alert: {event}\n"
        f"Details: {json.dumps(details, indent=2)}"
    )
```

### Response Plan

**1. Detect**
- Automated monitoring flags suspicious activity
- Alert sent to admin

**2. Assess**
- Review logs
- Determine severity
- Identify affected systems

**3. Contain**
- Revoke compromised tokens
- Block IP if external attack
- Isolate affected containers

**4. Eradicate**
- Patch vulnerability
- Remove malicious content
- Reset credentials

**5. Recover**
- Restore from backup if needed
- Verify system integrity
- Resume operations

**6. Learn**
- Document incident
- Update security measures
- Improve monitoring

---

## Compliance

**Data Protection:**
- No third-party data sharing
- No telemetry or analytics
- Local processing only
- User owns all data

**Best Practices:**
- OWASP Top 10 mitigation
- CIS Benchmarks (where applicable)
- Regular security audits

---

## Security Checklist

### Development (Phase 1)

- [ ] Use HTTPS in dev (self-signed cert OK)
- [ ] Implement JWT authentication
- [ ] Add input sanitization
- [ ] Sandbox bash execution
- [ ] Rate limit endpoints
- [ ] Secure logging (no secrets)
- [ ] Password hashing (bcrypt)
- [ ] CSRF protection

### Production (Phase 2)

- [ ] Tailscale VPN configured
- [ ] Let's Encrypt TLS cert
- [ ] Firewall rules active
- [ ] Database encryption enabled
- [ ] Automated backups configured
- [ ] Intrusion detection setup
- [ ] Log monitoring active
- [ ] Incident response plan tested

---

**Last Updated:** 2025-11-09
**Next Review:** After Phase 1 completion
**Security Contact:** jack@localhost
