# Chapter 12 — Deployment and Migration

> **Projects:** `fca-server` (packaged library), `import-fca-server`, migration patterns

---

## 🎯 What This Chapter Covers

How to package a FastAPI app as a reusable Python library, compose multiple FastAPI apps together, prepare for production (gunicorn, Docker, environment config), migrate from Flask or Django, and a production-readiness checklist.

---

## 🧠 The Packaging Problem

As your codebase grows, you might want to:
- Share an authentication router across multiple services
- Publish an internal SDK that other teams import
- Compose several FastAPI "mini-apps" into one deployed app

FastAPI's `include_router()` is designed for this. You build the router, package it as a library, and consumers just import and mount it.

---

## 📦 Packaging a FastAPI Router as a Library

```
fca-server/
├── pyproject.toml          ← package metadata and build config
├── src/
│   └── fca_server/
│       ├── __init__.py
│       ├── router.py       ← the APIRouter that consumers mount
│       ├── models.py       ← Pydantic models (shared types)
│       └── dependencies.py ← shared dependencies
└── tests/
    └── test_router.py
```

```toml
# pyproject.toml
[project]
name = "fca-server"
version = "0.2.0"
description = "FastAPI router for FCA data services"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "pydantic>=2.0",
    "httpx>=0.27",     # for any outgoing HTTP calls
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.optional-dependencies]
dev = ["pytest", "httpx"]  # test dependencies
```

```python
# src/fca_server/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Export these types so consumers can use them in their own response models
class FCAStatus(BaseModel):
    service: str
    version: str
    healthy: bool

class FCADataItem(BaseModel):
    id: int
    name: str
    category: str
    value: float

# The router that consumers will mount
router = APIRouter(
    prefix="/fca",           # all endpoints: /fca/...
    tags=["FCA Service"],    # swagger grouping
)

@router.get("/status", response_model=FCAStatus)
def get_status():
    return FCAStatus(service="fca-server", version="0.2.0", healthy=True)

@router.get("/data/{item_id}", response_model=FCADataItem)
def get_item(item_id: int):
    # In production: fetch from actual FCA data source
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Item ID must be positive")
    return FCADataItem(id=item_id, name=f"Item {item_id}", category="standard", value=99.5)

@router.get("/data", response_model=list[FCADataItem])
def list_items(limit: int = 20, category: str | None = None):
    items = get_fca_items(limit=limit, category=category)
    return items

# src/fca_server/__init__.py
# Export the router at the package level for easy importing
from .router import router
from .models import FCAStatus, FCADataItem

__all__ = ["router", "FCAStatus", "FCADataItem"]
```

---

## 🔌 Consuming the Library — Composing Multiple Routers

```python
# Another service's main.py — importing fca-server as a dependency
from fastapi import FastAPI
from fca_server import router as fca_router        # from pypi or local install

# Your own routers
from auth.router import router as auth_router
from payments.router import router as payments_router
from users.router import router as users_router

app = FastAPI(
    title="My Unified API",
    description="Combines FCA data, auth, payments, and user management",
)

# Mount all routers — each brings its own prefix, tags, and endpoints
app.include_router(auth_router)       # /auth/...
app.include_router(payments_router)   # /payments/...
app.include_router(users_router)      # /users/...
app.include_router(fca_router)        # /fca/...  ← from the installed library

# The app now serves ALL endpoints from all routers
# /openapi.json reflects all of them automatically
```

---

## 🚀 Production Setup — Gunicorn + Uvicorn Workers

The development server (`uvicorn main:app --reload`) is single-process and not suited for production. In production you need multiple workers.

```
Gunicorn (process manager)
    ├── Worker 1 (Uvicorn ASGI)   ← handles requests
    ├── Worker 2 (Uvicorn ASGI)   ← handles requests
    ├── Worker 3 (Uvicorn ASGI)   ← handles requests
    └── Worker 4 (Uvicorn ASGI)   ← handles requests

Gunicorn manages the workers:
- Restarts crashed workers
- Rotates logs
- Graceful reload on SIGHUP
- Graceful shutdown on SIGTERM
```

```bash
# Production start command
gunicorn main:app \
  --workers 4 \                              # (2 × CPU cores) + 1 is the rule of thumb
  --worker-class uvicorn.workers.UvicornWorker \  # async-capable worker
  --bind 0.0.0.0:8000 \
  --timeout 120 \                            # kill workers that take >120s
  --keep-alive 5 \                           # keep-alive timeout in seconds
  --access-logfile - \                       # log to stdout (for Docker/k8s)
  --error-logfile - \
  --log-level info
```

```python
# gunicorn.conf.py — config file approach (cleaner than long CLI)
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Lifecycle hooks — useful for cleanup
def on_starting(server):
    print("Gunicorn starting")

def worker_exit(server, worker):
    print(f"Worker {worker.pid} exited")
```

---

## 🐳 Docker — Containerized Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Create non-root user — security best practice
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies first (Docker layer caching — only re-run on requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check — Docker marks container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-"]
```

```yaml
# docker-compose.yml — for local dev with real services
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://api:secret@db:5432/myapp
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}     # from .env file
      - DEBUG=false
    depends_on:
      db:
        condition: service_healthy   # wait for DB to be ready
      redis:
        condition: service_started
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: api
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "api"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes   # enable persistence

volumes:
  postgres_data:
```

---

## ⚙️ Environment-Based Configuration

Never hardcode secrets in code. Use environment variables with Pydantic's `BaseSettings`:

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Settings are loaded from environment variables (or .env file in dev).
    Pydantic validates types and raises at startup if anything is missing.
    """
    # Database
    database_url: str                     # required — app won't start without it
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Security
    secret_key: str                       # required
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # Application
    debug: bool = False
    api_title: str = "My API"
    api_version: str = "1.0.0"
    allowed_hosts: list[str] = ["localhost"]

    # External services (optional — might not be used in all environments)
    redis_url: str | None = None
    sentry_dsn: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",         # load from .env in development
        env_file_encoding="utf-8",
        case_sensitive=False,    # DATABASE_URL and database_url both work
    )

@lru_cache   # parse settings once, reuse — don't re-read env vars on every call
def get_settings() -> Settings:
    return Settings()

# In main.py or as a dependency
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
)
```

```bash
# .env (development — never commit to git)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/myapp
SECRET_KEY=dev-secret-not-for-production
DEBUG=true
REDIS_URL=redis://localhost:6379/0

# Production environment variables set in cloud provider
# Never in files, never in code
```

---

## 🔄 Migrating from Flask — Pattern Comparison

```python
# ===== FLASK =====
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    return jsonify({"id": user.id, "name": user.name})

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    # Manual validation — no automatic checking
    if not data.get("name"):
        return jsonify({"error": "name required"}), 400
    user = User(name=data["name"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id}), 201

# ===== FASTAPI EQUIVALENT =====
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

app = FastAPI()

class UserCreate(BaseModel):
    name: str                    # validation is automatic

class UserResponse(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(name=user_data.name)  # name is already validated by Pydantic
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

**Migration checklist:**

| Flask | FastAPI equivalent |
|-------|-------------------|
| `@app.route("/path", methods=["GET"])` | `@app.get("/path")` |
| `request.get_json()` | Pydantic model as function param |
| `request.args.get("q")` | `q: str` function param |
| `jsonify(data)` | `return data` (auto-serialized) |
| `abort(404)` | `raise HTTPException(status_code=404)` |
| `flask_login` | `Depends(get_current_user)` |
| `flask_sqlalchemy` | SQLAlchemy 2.0 + `Depends(get_db)` |
| Manual `@validates` | Pydantic `@field_validator` |

---

## ✅ Production Readiness Checklist

```
Security:
  ✅ HTTPS via reverse proxy (nginx or cloud load balancer)
  ✅ SECRET_KEY is a 32+ byte random string (not "dev-key")
  ✅ DEBUG=False in production
  ✅ CORS allow_origins is explicit (not ["*"])
  ✅ TrustedHostMiddleware configured
  ✅ Rate limiting on public endpoints
  ✅ Passwords hashed with bcrypt (not MD5/SHA1)

Database:
  ✅ Alembic migrations (not create_all())
  ✅ Connection pooling configured
  ✅ DB credentials from environment variables
  ✅ Database backups configured

Performance:
  ✅ Gunicorn + UvicornWorker (multiple processes)
  ✅ Async endpoints for I/O-bound operations
  ✅ Redis caching for expensive reads
  ✅ N+1 query prevention (eager loading)

Observability:
  ✅ Structured logging (JSON) — search and filter in production
  ✅ GET /health endpoint (returns 200 when healthy, 503 if degraded)
  ✅ Request ID header (X-Request-ID) for tracing across services
  ✅ Error tracking (Sentry or equivalent)
  ✅ Metrics (Prometheus /metrics endpoint)

Reliability:
  ✅ Docker health checks (container restarts if /health fails)
  ✅ Graceful shutdown (lifespan closes DB connections, drains requests)
  ✅ Alembic upgrade head in deploy pipeline (before rolling out new code)
  ✅ Rollback plan (alembic downgrade -1 if something breaks)
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| Package routers with `pyproject.toml` | Versioned, installable, reusable across services |
| `app.include_router(imported_router)` | Compose multiple apps into one without code duplication |
| `(2 × CPU cores) + 1` workers | Standard formula for Gunicorn worker count |
| `BaseSettings` for config | Type-validated env vars — app refuses to start if SECRET_KEY is missing |
| `@lru_cache` on `get_settings()` | Environment is read once at startup, not on every request |
| HEALTHCHECK in Dockerfile | Kubernetes and Docker restart unhealthy containers automatically |
| Non-root user in Docker | Security principle: don't run app code as root |
| Alembic in deploy hook | DB schema migration runs before new app code is deployed — prevents version mismatch |
