# Chapter 11 — Custom Middleware

> **Project:** `middleware_project`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter11)

---

## 🎯 What This Chapter Covers

Building custom ASGI middleware (class-based and functional), request/response middleware, CORS, TrustedHost, webhook sender middleware, and understanding middleware execution order.

---

## 🏗️ App with Full Middleware Stack

```python
from contextlib import asynccontextmanager
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware import Middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield {"webhook_urls": set()}   # shared state for webhook middleware

app = FastAPI(
    title="Middleware Application",
    lifespan=lifespan,
    middleware=[
        # Declared at construction time — applied before add_middleware()
        Middleware(ASGIMiddleware, parameter="example_parameter"),
        Middleware(asgi_middleware, parameter="example_parameter"),
    ],
)
```

---

## 🔧 Class-Based ASGI Middleware

```python
from starlette.types import ASGIApp, Receive, Scope, Send

class ASGIMiddleware:
    """Lowest level: raw ASGI interface."""
    def __init__(self, app: ASGIApp, parameter: str = ""):
        self.app = app
        self.parameter = parameter

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            # Intercept HTTP requests
            scope["state"]["custom_param"] = self.parameter
        await self.app(scope, receive, send)   # pass to next middleware/handler
```

---

## 🔧 Functional ASGI Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

# Functional style using decorator
def asgi_middleware(app: ASGIApp, parameter: str = ""):
    async def middleware(scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            scope["state"]["func_param"] = parameter
        await app(scope, receive, send)
    return middleware
```

---

## 📦 Request Middleware (Hash Body Content)

```python
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib

class HashBodyContentMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app, allowed_paths: list[str] = None):
        super().__init__(app)
        self.allowed_paths = allowed_paths or []

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.allowed_paths:
            body = await request.body()
            content_hash = hashlib.sha256(body).hexdigest()
            request.state.content_hash = content_hash

        response = await call_next(request)
        return response

app.add_middleware(
    HashBodyContentMiddleWare,
    allowed_paths=["/send"],
)
```

---

## 📤 Response Middleware (Extra Headers)

```python
from starlette.middleware.base import BaseHTTPMiddleware

class ExtraHeadersResponseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, headers: tuple[tuple[str, str], ...] = ()):
        super().__init__(app)
        self.headers = headers

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add headers to every response
        for header_name, header_value in self.headers:
            response.headers[header_name] = header_value
        return response

app.add_middleware(
    ExtraHeadersResponseMiddleware,
    headers=(
        ("new-header", "fastapi-cookbook"),
        ("another-header", "fastapi-cookbook"),
    ),
)
```

---

## 🌐 CORS and TrustedHost

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myfrontend.com"],   # or ["*"] for dev
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "myapp.com"],   # reject requests from other hosts
)
```

---

## 🪝 Webhook Sender Middleware

```python
import httpx
from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    host: str
    path: str
    timestamp: str
    body: str | None = None

class WebhookSenderMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        response = await call_next(request)

        # After response — fire webhooks to registered URLs
        webhook_urls = request.state.webhook_urls
        if webhook_urls:
            event = Event(
                host=request.headers.get("host", ""),
                path=request.url.path,
                timestamp=datetime.now().isoformat(),
                body=body.decode() if body else None,
            )
            async with httpx.AsyncClient() as client:
                for url in webhook_urls:
                    try:
                        await client.post(url, json=event.model_dump())
                    except Exception as e:
                        logger.error(f"Webhook failed to {url}: {e}")

        return response

# Register webhook endpoints via API
@app.post("/register-webhook-url")
async def add_webhook_url(request: Request, url: str = Body()):
    if not url.startswith("http"):
        url = f"http://{url}"
    request.state.webhook_urls.add(url)
    return {"url added": url}

# Document webhook in OpenAPI
@app.webhooks.post("/fastapi-webhook")
def fastapi_webhook(event: Event):
    """Receives POST when any request is processed."""
```

---

## ⚠️ Middleware Execution Order

```
Request flow (outermost → innermost):
  TrustedHostMiddleware        ← added last = outermost
  CORSMiddleware
  ExtraHeadersResponseMiddleware
  HashBodyContentMiddleWare
  WebhookSenderMiddleWare
  ASGIMiddleware               ← in Middleware[] = innermost
  → Route Handler

Response flow (innermost → outermost):
  Route Handler
  ASGIMiddleware
  HashBodyContentMiddleWare
  ExtraHeadersResponseMiddleware
  ...
  TrustedHostMiddleware        ← sends to client
```

**Rule:** `add_middleware()` wraps in reverse order — the last `add_middleware()` call is the outermost layer. Middleware in the `middleware=[]` constructor param runs inside `add_middleware()` layers.

---

## 🔑 Key Takeaways

- `BaseHTTPMiddleware` is the easiest way to write middleware — override `dispatch(request, call_next)`
- Raw ASGI middleware (`__call__(scope, receive, send)`) has lower overhead but more complexity
- `await call_next(request)` passes to the next middleware/handler and returns the response
- Middleware added last with `add_middleware()` = outermost = runs first on request, last on response
- CORS middleware must be added **after** other middleware so it's the outermost layer
- `request.state` is request-scoped shared state; `app.state` (from lifespan) is app-scoped
- `app.webhooks.post()` documents webhook events in OpenAPI schema without creating an actual endpoint
