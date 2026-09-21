# FastAPI Cookbook — Key Takeaways

Quick reference for every chapter, based on the actual source code from the book's GitHub repo.

---

## Ch 1 — Getting Started
- `APIRouter` splits routes across files; `app.include_router()` merges them
- `Field(..., min_length=1, gt=0)` adds Pydantic constraints at validation + schema level
- `response_model` (or `-> Type`) filters output — strips fields not in the model
- Override `@app.exception_handler(ExcType)` to customize error responses globally
- FastAPI generates `/docs` + `/redoc` automatically — no extra work

## Ch 2 — Data Storage
- `Depends(get_db)` with `yield` + `finally` guarantees the DB session always closes
- `db.refresh(obj)` after `commit()` reloads DB-generated values (id, timestamps)
- `async def` + `await asyncio.sleep()` = non-blocking; never `time.sleep()` in `async def`
- `ObjectId.is_valid(id)` before converting prevents crashes on bad MongoDB IDs
- `model_dump(exclude_none=True)` — don't store null fields in MongoDB

## Ch 3 — Task Manager
- `model_dump(exclude_unset=True)` is essential for PATCH/PUT — only updates sent fields
- `OAuth2PasswordBearer(tokenUrl="token")` + `Depends()` makes endpoints require Bearer tokens
- `OAuth2PasswordRequestForm` expects `application/x-www-form-urlencoded`, not JSON
- Cache `app.openapi_schema` — don't regenerate on every request
- `TestClient` from `fastapi.testclient` tests as if calling a real HTTP server

## Ch 4 — Auth and Authorization
- Use `lifespan` for startup logic (`create_all`, DB init) — replaces deprecated `@app.on_event`
- Chain `Depends()` for layered auth: `get_admin` → `get_premium` → `get_current_user`
- `Annotated[Type, Depends()]` is the modern, type-safe dependency declaration
- GitHub OAuth: redirect → code → exchange for token → get user info — three steps
- `APIKeyHeader(name="X-API-Key")` + `Security()` for API key authentication

## Ch 5 — Testing and Profiling
- `dependency_overrides[real_dep] = test_dep` swaps dependencies in tests cleanly
- `scope="function"` fixture + `drop_all()` in teardown = isolated DB per test
- `@app.middleware("http")` + `call_next(request)` wraps every request
- Locust: `@task` defines user behavior; `--headless -u 10 -r 2` runs without UI
- Use in-memory SQLite (`sqlite:///:memory:`) for fast, isolated DB tests

## Ch 6 — Async SQLAlchemy + Alembic
- `create_async_engine` + `AsyncSession` + `async_sessionmaker` = fully non-blocking DB
- Use `select(Model).where(...)` not `session.query()` — ORM 2.0 style
- `await session.execute(...)` returns `Result`; `.scalar_one_or_none()` or `.scalars().all()`
- `expire_on_commit=False` in async sessions avoids lazy-load errors after commit
- **Never `create_all()` in production** — use Alembic migrations

## Ch 7 — Advanced Storage
- `ENCODERS_BY_TYPE[ObjectId] = str` — register globally, ObjectId auto-serializes to string
- `await gather(ping_mongo(), ping_elastic(), ping_redis())` — check all stores in parallel
- `query.explain()` reveals which MongoDB index was used — critical for optimization
- `{"$text": {"$search": artist}}` requires a text index — must create first
- `@cache(expire=60)` from `fastapi-cache` caches the full response in Redis

## Ch 8 — DI and Middleware
- Class-based dependencies group related params; chain them for layered validation
- `BackgroundTasks.add_task(fn, *args)` runs after response is sent — fire-and-forget
- SlowAPI rate limiting needs `request: Request` as an endpoint param to get caller's IP
- `Accept-Language` header is the standard locale detection mechanism
- Rate limit strings: `"5/minute"`, `"100/hour"`, combined with semicolons

## Ch 9 — WebSockets
- Always `await websocket.accept()` before any send/receive
- `WebSocketDisconnect` is raised when client closes — catch it and clean up
- `websocket.iter_text()` is cleaner than `while True: receive_text()`
- Auth via query param (`?token=...`) — browsers can't set custom WS headers
- `ConnectionManager` with `dict[room_id, list[WebSocket]]` is the standard broadcast pattern

## Ch 10 — AI Integrations
- `request.state` from `lifespan` yield = clean app-level resource sharing (vector DB, LLM client)
- RAG = embed query → vector search → inject context → LLM prompt
- `chain = prompt | llm | StrOutputParser()` — LangChain pipe composes processing steps
- Strawberry GraphQL: `@strawberry.type`, `@strawberry.field`, `GraphQLRouter` — mount in one line
- gRPC gateway: FastAPI handles HTTP, proxies to gRPC — REST clients + gRPC backends

## Ch 11 — Custom Middleware
- `BaseHTTPMiddleware`: override `dispatch(request, call_next)` — simplest middleware pattern
- Raw ASGI: `__call__(scope, receive, send)` — lower overhead, more control
- **Middleware order**: `add_middleware()` wraps in reverse — last added = outermost = runs first
- CORS must be outermost — add it last with `add_middleware()`
- `app.webhooks.post()` documents webhook events in OpenAPI without creating an actual endpoint

## Ch 12 — Deployment and Migration
- Package routers as pip libraries; `app.include_router(library_router)` composes them
- Production: Gunicorn + UvicornWorker; workers = `(2 × CPU cores) + 1`
- Flask migration: routes → routes, `jsonify()` → `return dict`, `request.args` → function params
- Environment variables for all secrets — never hardcode DATABASE_URL, SECRET_KEY
- Health check endpoint (`/health`) is non-negotiable for Kubernetes/load balancers
