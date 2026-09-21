# Chapter 12 — Deployment and Migration

> **Projects:** `fca-server` (packaged library), `import-fca-server` (consumer), `live_application`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter12)

---

## 🎯 What This Chapter Covers

Packaging a FastAPI application as a reusable Python library, importing and composing multiple FastAPI apps, migrating existing applications to FastAPI, and production deployment patterns.

---

## 📦 Packaging FastAPI as a Library (fca-server)

```
fca-server/
├── pyproject.toml
├── src/
│   └── fca_server/
│       ├── __init__.py
│       └── router.py       ← exposes an APIRouter
└── tests/
```

```toml
# pyproject.toml
[project]
name = "fca-server"
version = "0.1.0"
dependencies = ["fastapi>=0.100.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```python
# src/fca_server/router.py
from fastapi import APIRouter

router = APIRouter(prefix="/fca", tags=["FCA Server"])

@router.get("/status")
def get_status():
    return {"status": "ok", "service": "fca-server"}

@router.get("/data/{item_id}")
def get_data(item_id: int):
    return {"item_id": item_id, "data": "..."}
```

---

## 🔌 Importing and Composing the Library

```python
# import-fca-server/main.py
from fastapi import FastAPI
from fca_server import router   # imported from the installed package

app = FastAPI(title="Import FCA Server Application")
app.include_router(router)     # mount the library's router

# Can combine multiple libraries:
# from fca_server import router as fca_router
# from payment_service import router as payment_router
# app.include_router(fca_router)
# app.include_router(payment_router)
```

**This pattern enables:**
- Shared internal APIs as versioned packages
- Microservice composition — multiple services as one mounted app
- Plugin-style extension points

---

## 🚀 Production Deployment

### Uvicorn + Gunicorn

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production — Gunicorn manages Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

# workers formula: (2 * CPU_count) + 1
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db/mydb
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_USER: user
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 🔄 Migrating to FastAPI from Flask/Django

### From Flask

```python
# Flask (before)
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"id": user.id, "name": user.name})

# FastAPI (after)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

### Migration Checklist

```
Flask → FastAPI:
  ✅ Replace @app.route with @app.get/post/put/delete
  ✅ Replace request.args/json with function parameters (auto-parsed)
  ✅ Replace jsonify() with return dict (FastAPI serializes automatically)
  ✅ Replace flask-sqlalchemy with SQLAlchemy 2.0 + async
  ✅ Replace manual validation with Pydantic models
  ✅ Replace flask-login with OAuth2/JWT dependencies

Django REST Framework → FastAPI:
  ✅ Replace Serializer with Pydantic BaseModel
  ✅ Replace ViewSet with APIRouter + route functions
  ✅ Replace permissions with Depends() chains
  ✅ Replace Django ORM with SQLAlchemy or Tortoise-ORM
  ✅ Keep: Alembic replaces Django migrations
```

---

## 📊 Production Checklist

```
Security:
  ✅ HTTPS via reverse proxy (nginx/caddy)
  ✅ TrustedHostMiddleware configured
  ✅ CORS origins locked down (not ["*"])
  ✅ API keys/secrets in environment variables, not code
  ✅ Rate limiting on public endpoints

Performance:
  ✅ Gunicorn + UvicornWorker (multiple processes)
  ✅ Async endpoints for I/O-bound operations
  ✅ DB connection pooling configured
  ✅ Redis caching for expensive reads
  ✅ Alembic migrations (not create_all())

Observability:
  ✅ Structured logging (JSON format)
  ✅ Health check endpoint (/health)
  ✅ Metrics (Prometheus /metrics)
  ✅ Request ID middleware for tracing

Reliability:
  ✅ Graceful shutdown (lifespan handles cleanup)
  ✅ Docker health checks
  ✅ Database connection retry on startup
  ✅ Background task queue (Celery) for heavy work
```

---

## 🔑 Key Takeaways

- Package your FastAPI routers as pip-installable libraries — `app.include_router(library_router)` composes them
- `pyproject.toml` + `hatchling` is the modern Python packaging standard
- Production: **Gunicorn + UvicornWorker** manages processes; Uvicorn handles async within each process
- Workers = `(2 × CPU cores) + 1` is the standard formula
- Migration from Flask: mostly mechanical — routes → routes, jsonify → return dict, decorators → Depends
- Always use environment variables for secrets; never hardcode DATABASE_URL, SECRET_KEY, etc.
- Health check endpoint is non-negotiable in production — Kubernetes, load balancers need it
