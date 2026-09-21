# Chapter 11 — Custom Middleware

> **Project:** `middleware_project`

---

## 🎯 What This Chapter Covers

What middleware actually is, how to write it three different ways (class-based ASGI, function-based ASGI, `BaseHTTPMiddleware`), how middleware layers stack and in what order they execute, CORS and trusted host security, and implementing a webhook sender that fires after every response.

---

## 🧠 What Middleware Is — The Mental Model

Middleware wraps every request and response. Think of it as a stack of interceptors:

```
Incoming request
    ↓
[TrustedHostMiddleware]     ← outermost, runs first on requests
    ↓
[CORSMiddleware]
    ↓
[RateLimiterMiddleware]
    ↓
[AuthMiddleware]
    ↓
[LoggingMiddleware]         ← innermost, runs last before handler
    ↓
[Your endpoint handler]
    ↓
[LoggingMiddleware]         ← innermost, runs first on responses
    ↓
[AuthMiddleware]
    ↓
[RateLimiterMiddleware]
    ↓
[CORSMiddleware]
    ↓
[TrustedHostMiddleware]     ← outermost, runs last on responses
    ↓
Response sent to client
```

The key rule: **`add_middleware()` calls stack in reverse order** — the last `add_middleware()` call becomes the outermost layer (runs first on requests).

---

## 🔧 Method 1: `BaseHTTPMiddleware` — The Simplest Way

`BaseHTTPMiddleware` gives you a `dispatch(request, call_next)` method. Call `call_next` to pass the request down the stack and get the response back.

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import time
import uuid

class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Add X-Process-Time header to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        # Code here runs BEFORE the request reaches your endpoint
        request_id = str(uuid.uuid4())[:8]

        response = await call_next(request)    # ← passes to next middleware/endpoint

        # Code here runs AFTER your endpoint returns a response
        elapsed = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
        response.headers["X-Request-ID"] = request_id

        return response


class RequestBodyHashMiddleware(BaseHTTPMiddleware):
    """
    For certain paths, compute a hash of the request body.
    Useful for detecting duplicate requests or verifying integrity.
    """
    def __init__(self, app, allowed_paths: list[str] = None):
        super().__init__(app)
        self.allowed_paths = set(allowed_paths or [])

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.allowed_paths:
            # Read the body — this consumes the stream
            body = await request.body()
            import hashlib
            body_hash = hashlib.sha256(body).hexdigest()
            # Store in request.state so endpoints can read it
            request.state.body_hash = body_hash

        return await call_next(request)


class ClientInfoMiddleware(BaseHTTPMiddleware):
    """Extract and store client information for use in endpoints."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Store client info in request.state — accessible from endpoints via request.state.client_ip
        request.state.client_ip = request.client.host if request.client else "unknown"
        request.state.user_agent = request.headers.get("user-agent", "unknown")

        response = await call_next(request)
        return response

# Register middleware
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(RequestBodyHashMiddleware, allowed_paths=["/payments", "/webhooks"])
app.add_middleware(ClientInfoMiddleware)
```

---

## 🔧 Method 2: Raw ASGI Middleware — Maximum Control

ASGI is the underlying protocol. Raw ASGI middleware gives you lower-level access — you see the raw scope/receive/send objects. More control, more complexity.

```python
from starlette.types import ASGIApp, Receive, Scope, Send

class ASGILoggingMiddleware:
    """
    Raw ASGI middleware — intercepts at the ASGI protocol level.
    More efficient than BaseHTTPMiddleware for simple cases.
    """
    def __init__(self, app: ASGIApp, log_headers: bool = False):
        self.app = app
        self.log_headers = log_headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            # scope contains: method, path, headers, query_string, client, etc.
            method = scope.get("method", "")
            path = scope.get("path", "")
            client = scope.get("client", ("unknown", 0))

            if self.log_headers:
                headers = dict(scope.get("headers", []))
                print(f"Headers: {headers}")

            print(f"→ {method} {path} from {client[0]}")

            # Wrap send to intercept the response
            async def send_with_logging(message):
                if message["type"] == "http.response.start":
                    status = message.get("status", 0)
                    print(f"← {status} {path}")
                await send(message)

            await self.app(scope, receive, send_with_logging)

        elif scope["type"] == "websocket":
            # Handle WebSocket connections too
            path = scope.get("path", "")
            print(f"WebSocket connection: {path}")
            await self.app(scope, receive, send)

        else:
            # lifespan events (startup/shutdown) — just pass through
            await self.app(scope, receive, send)
```

```python
# Function-based ASGI middleware — lighter syntax, same capability
def response_size_middleware(app: ASGIApp, max_size_kb: int = 1024) -> ASGIApp:
    """Factory function that creates an ASGI middleware."""
    max_bytes = max_size_kb * 1024

    async def middleware(scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        response_size = 0

        async def counting_send(message):
            nonlocal response_size
            if message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_size += len(body)
                if response_size > max_bytes:
                    print(f"⚠️ Large response: {response_size / 1024:.1f}KB for {scope['path']}")
            await send(message)

        await app(scope, receive, counting_send)

    return middleware

# Attach at construction time (runs INSIDE add_middleware() layers)
from starlette.middleware import Middleware

app = FastAPI(
    middleware=[
        Middleware(ASGILoggingMiddleware, log_headers=False),
        Middleware(response_size_middleware, max_size_kb=512),
    ]
)
```

---

## 🌐 CORS and TrustedHost — Security Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# CORS: controls which browser origins can make requests to your API
# Without this, browsers block cross-origin requests (CORS policy error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.mycompany.com",      # production frontend
        "https://staging.mycompany.com",  # staging
        # "http://localhost:3000",        # dev frontend (add for local dev)
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    allow_credentials=True,   # needed for cookies/auth
    max_age=600,              # browser caches preflight for 600 seconds
)

# TrustedHost: rejects requests with invalid Host headers
# Prevents host header injection attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "api.mycompany.com",
        "localhost",
        "127.0.0.1",
    ],
)

# ⚠️ CORS must be the OUTERMOST layer — add it LAST
# It needs to wrap everything to add CORS headers to all responses
# Including error responses from other middleware
```

---

## 🪝 Webhook Sender Middleware

This middleware fires an outgoing HTTP POST to registered URLs after every request. It's a post-request side effect that doesn't block the response.

```python
# middleware/webhook.py
import httpx
from datetime import datetime
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

class WebhookEvent(BaseModel):
    timestamp: str
    method: str
    path: str
    status_code: int
    body_preview: str | None = None

class WebhookSenderMiddleware(BaseHTTPMiddleware):
    """
    After each request, notify all registered webhook URLs about it.
    The webhook URLs are stored in app.state (set at startup or via an endpoint).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Capture request body (if needed for the webhook payload)
        body = await request.body()
        body_preview = body[:200].decode("utf-8", errors="replace") if body else None

        # Process the actual request
        response = await call_next(request)

        # After response is ready, fire webhooks asynchronously
        webhook_urls = getattr(request.state, "webhook_urls", set())
        if webhook_urls:
            event = WebhookEvent(
                timestamp=datetime.utcnow().isoformat(),
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                body_preview=body_preview,
            )
            # Fire all webhooks concurrently, don't wait for them
            import asyncio
            asyncio.create_task(
                self._fire_webhooks(webhook_urls, event)
            )

        return response

    async def _fire_webhooks(self, urls: set[str], event: WebhookEvent):
        """Send the event to all registered webhook URLs."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = [
                client.post(url, json=event.model_dump())
                for url in urls
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    print(f"Webhook failed for {url}: {result}")
```

```python
# Endpoint to register webhook URLs
@app.post("/webhooks/register")
async def register_webhook(request: Request, url: str = Body(...)):
    """Register a URL to receive webhook notifications."""
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    request.state.webhook_urls.add(url)
    return {"registered": url, "total": len(request.state.webhook_urls)}

# FastAPI's built-in webhook documentation
@app.webhooks.post("/event-notification")
def webhook_docs(event: WebhookEvent):
    """
    This doesn't create an actual endpoint.
    It documents the shape of events YOUR app sends to registered URLs.
    Appears in /openapi.json under "webhooks".
    """
```

---

## ⚠️ Middleware Execution Order — Visualized

```python
# The order you add middleware determines execution order
# Later add_middleware() calls = OUTER layer = runs FIRST on requests

app.add_middleware(LoggingMiddleware)          # added 1st → INNER → runs last on requests
app.add_middleware(AuthMiddleware)             # added 2nd
app.add_middleware(RateLimiterMiddleware)      # added 3rd
app.add_middleware(CORSMiddleware, ...)        # added last → OUTER → runs first on requests

# Request flow:
# CORSMiddleware → RateLimiterMiddleware → AuthMiddleware → LoggingMiddleware → Endpoint

# Response flow (reverse):
# Endpoint → LoggingMiddleware → AuthMiddleware → RateLimiterMiddleware → CORSMiddleware

# Consequence: CORS headers are added by the outermost layer, so they appear
# on ALL responses — including 401s from AuthMiddleware and 429s from RateLimiter
# This is correct behavior: CORS errors should also have CORS headers
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `BaseHTTPMiddleware` | Simplest — override `dispatch(request, call_next)`, return response |
| Raw ASGI `__call__(scope, receive, send)` | Lower overhead, needed for WebSocket middleware or fine control |
| `await call_next(request)` returns the response | Everything before = request processing; everything after = response processing |
| Last `add_middleware()` = outermost | Reverse of declaration order — add CORS last so it wraps everything |
| `request.state` for request-scoped data | Pass data from middleware to endpoints without polluting function signatures |
| `asyncio.create_task()` for webhooks | Fires webhook after response without blocking — the client doesn't wait |
| `@app.webhooks.post()` | Documents outgoing webhooks in OpenAPI — no actual endpoint created |
