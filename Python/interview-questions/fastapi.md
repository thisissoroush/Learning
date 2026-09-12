# ⚡ FastAPI — Interview Questions (Junior → Architect)

A comprehensive set of FastAPI-specific interview questions, organized from fundamentals to architecture-level design.

---

## 🟢 Junior Level

---

### 1. What is FastAPI and what makes it different from Flask and Django?

**A:** FastAPI is a modern, async-first Python web framework for building APIs, built on **Starlette** (ASGI) and **Pydantic** (validation).

| | FastAPI | Flask | Django |
|--|--------|-------|--------|
| Type | API framework | Micro framework | Full-stack |
| Async | Native | Via extensions | 3.1+ |
| Validation | Pydantic (built-in) | Manual | Forms/DRF |
| Docs | Auto OpenAPI/Swagger | Manual | Manual/DRF |
| Performance | Very high (Starlette) | Moderate | Moderate |
| ORM | Choose your own | Choose your own | Built-in |

FastAPI auto-generates OpenAPI documentation from your type hints — no separate doc writing needed.

---

### 2. What is the basic structure of a FastAPI application?

**A:**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def get_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/", status_code=201)
def create_item(item: Item):
    return item

# Run: uvicorn main:app --reload
```

---

### 3. How does FastAPI handle path parameters, query parameters, and request bodies?

**A:**

```python
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(..., title="The item ID", ge=1),   # path param
    q: str | None = Query(None, min_length=3, max_length=50),  # query param
    limit: int = Query(10, ge=1, le=100),   # query with validation
):
    return {"item_id": item_id, "q": q, "limit": limit}

@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    item: Item,                          # request body (Pydantic model)
    importance: int = Body(..., ge=1),   # extra body field
):
    return {"item_id": item_id, **item.dict(), "importance": importance}
```

FastAPI automatically:
- Validates types and constraints
- Returns 422 Unprocessable Entity on validation failure
- Documents all params in Swagger UI

---

### 4. What is Pydantic and how does it work with FastAPI?

**A:** Pydantic provides data validation, serialization, and schema generation using Python type hints:

```python
from pydantic import BaseModel, validator, Field, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100, example="Alice")
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("name")
    def name_must_not_be_empty(cls, v):
        return v.strip()

    class Config:
        schema_extra = {
            "example": {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}
        }

# FastAPI uses Pydantic models for:
# - Request body validation
# - Response serialization
# - Schema generation (OpenAPI docs)
user = User(id=1, name="Alice", email="alice@example.com", age=30)
user.dict()   # {"id": 1, "name": "Alice", ...}
user.json()   # JSON string
```

---

### 5. What is `response_model` and why do you use it?

**A:** `response_model` tells FastAPI what schema to use for the response — it filters out fields not in the model and validates output:

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str   # sensitive — should NOT be in response

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # no password field!

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    db_user = save_to_db(user)
    return db_user  # password is stripped by response_model

# response_model_exclude_unset — don't include fields that weren't set
@app.get("/items/{id}", response_model=Item, response_model_exclude_unset=True)
def get_item(id: int): ...
```

---

### 6. How does async work in FastAPI?

**A:**

```python
import asyncio
import httpx

# Async route — non-blocking; event loop handles other requests during await
@app.get("/users/{id}")
async def get_user(id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://user-service/{id}")
    return resp.json()

# Sync route — FastAPI runs it in a thread pool automatically (won't block event loop)
@app.get("/items/{id}")
def get_item(id: int):
    return db.query(Item).get(id)  # blocking DB call — OK in sync route
```

**Rule:** Use `async def` for I/O-bound async code. Use `def` (sync) for blocking code — FastAPI runs it in a thread pool so it doesn't block the event loop.

---

### 7. What is dependency injection in FastAPI?

**A:** FastAPI's `Depends()` system wires dependencies declaratively:

```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
```

Dependencies are:
- Reusable across routes
- Composable (dependencies can have their own dependencies)
- Automatically documented
- Cached per request by default

---

### 8. How do you return different HTTP status codes and errors?

**A:**

```python
from fastapi import HTTPException, status

@app.get("/users/{id}", status_code=status.HTTP_200_OK)
def get_user(id: int):
    user = db.get(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {id} not found"
        )
    return user

@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate): ...

@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int): ...

# Custom error with headers
raise HTTPException(
    status_code=401,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"}
)
```

---

### 9. What is `APIRouter` and how do you organize a FastAPI project?

**A:**

```python
# routers/users.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
def list_users(): ...

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate): ...

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int): ...

# main.py
from routers import users, orders, products

app = FastAPI()
app.include_router(users.router)
app.include_router(orders.router, prefix="/v1")
app.include_router(products.router, dependencies=[Depends(get_current_user)])
```

**Project structure:**
```
app/
├── main.py
├── routers/
│   ├── users.py
│   └── orders.py
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├── crud/          # DB operations
└── dependencies/  # Shared Depends()
```

---

### 10. What is the `Request` object and how do you access raw request data?

**A:**

```python
from fastapi import Request

@app.get("/debug")
async def debug(request: Request):
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host,
        "query_params": dict(request.query_params),
        "path_params": request.path_params,
        "cookies": request.cookies,
    }

# Read raw body (e.g., for webhook signature verification)
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    verify_signature(body, request.headers.get("X-Signature"))
    data = await request.json()
    return {"received": True}
```

---

### 11. How do you set cookies and headers in a response?

**A:**

```python
from fastapi import Response
from fastapi.responses import JSONResponse

@app.post("/login")
def login(response: Response, credentials: LoginForm):
    token = create_token(credentials)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600
    )
    response.headers["X-Auth-Token"] = token
    return {"status": "logged in"}

# Return a custom response directly
@app.get("/redirect")
def redirect():
    return JSONResponse(
        content={"message": "moved"},
        status_code=301,
        headers={"Location": "/new-path"}
    )
```

---

### 12. What is `BackgroundTasks` in FastAPI?

**A:** Runs a task after returning the response — without blocking the client:

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Runs after response is sent
    email_client.send(email, message)

def write_log(data: dict):
    with open("log.txt", "a") as f:
        f.write(json.dumps(data) + "\n")

@app.post("/register")
def register(user: UserCreate, background_tasks: BackgroundTasks):
    new_user = create_user(user)
    background_tasks.add_task(send_email, user.email, "Welcome!")
    background_tasks.add_task(write_log, {"event": "user_registered", "id": new_user.id})
    return new_user  # response sent immediately; tasks run after
```

For heavy work, use Celery instead — `BackgroundTasks` runs in the same process and blocks the worker slot.

---

### 13. What is the difference between `BaseModel` and `BaseSettings` in Pydantic?

**A:**

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings  # pydantic v2

# BaseModel — for data validation (request/response)
class Item(BaseModel):
    name: str
    price: float

# BaseSettings — reads from environment variables and .env files
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    max_connections: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()  # reads from environment
print(settings.database_url)  # from DATABASE_URL env var
```

---

### 14. How does FastAPI auto-generate documentation?

**A:** FastAPI generates OpenAPI 3.0 schema from your code — automatically available at:
- `/docs` — Swagger UI (interactive)
- `/redoc` — ReDoc (readable)
- `/openapi.json` — raw schema

```python
app = FastAPI(
    title="Order Service",
    description="Manages customer orders",
    version="2.0.0",
    terms_of_service="https://example.com/terms",
    contact={"name": "Support", "email": "support@example.com"},
    license_info={"name": "MIT"},
)

@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Get a single order",
    description="Returns full order details including line items and shipping info.",
    tags=["orders"],
    responses={
        404: {"description": "Order not found"},
        403: {"description": "Access denied"},
    }
)
def get_order(order_id: int): ...
```

---

### 15. What are `tags` and how do you organize your API docs?

**A:**

```python
# Define tags at app level for ordering and descriptions
tags_metadata = [
    {"name": "users", "description": "User management operations"},
    {"name": "orders", "description": "Order processing"},
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/users/", tags=["users"])
def list_users(): ...

@app.post("/orders/", tags=["orders"])
def create_order(): ...

# Or on the router
router = APIRouter(prefix="/users", tags=["users"])
```

Tags group endpoints in Swagger UI — each tag becomes a section.

---

## 🟡 Mid Level

---

### 16. How do you implement JWT authentication in FastAPI?

**A:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).get(user_id)
    if not user:
        raise credentials_exception
    return user

@app.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
```

---

### 17. How do you handle database sessions with SQLAlchemy in FastAPI?

**A:**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

DATABASE_URL = "postgresql://user:pass@localhost/db"
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency — yields session, closes after request
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async version (with asyncpg)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/{id}")
async def get_user(id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()
```

---

### 18. How do you implement middleware in FastAPI?

**A:**

```python
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestLoggingMiddleware)

# Built-in middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(CORSMiddleware,
    allow_origins=["https://myfrontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

### 19. How do you implement global exception handling in FastAPI?

**A:**

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class NotFoundException(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id

@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": f"{exc.resource} {exc.id} not found"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "body": exc.body,
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.status_code), "message": exc.detail}
    )
```

---

### 20. How do you implement rate limiting in FastAPI?

**A:**

```python
# Using slowapi (limits library)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("100/minute")
async def get_data(request: Request):
    return {"data": "..."}

# Per-user limit
@app.get("/api/sensitive")
@limiter.limit("10/hour", key_func=lambda req: req.state.user.id)
async def sensitive_endpoint(request: Request, user=Depends(get_current_user)):
    return {"data": "..."}
```

---

### 21. How do you implement pagination in FastAPI?

**A:**

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

@app.get("/users/", response_model=Page[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size
    total = db.query(User).count()
    users = db.query(User).offset(offset).limit(size).all()
    return Page(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size)
    )

# Or use fastapi-pagination library
from fastapi_pagination import Page, add_pagination, paginate
add_pagination(app)

@app.get("/users/", response_model=Page[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return paginate(db.query(User))
```

---

### 22. How do you use `lifespan` for startup and shutdown events?

**A:**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    app.state.db_pool = await create_db_pool()
    app.state.redis = await aioredis.create_redis_pool("redis://localhost")

    yield  # Application runs here

    # Shutdown
    print("Shutting down...")
    app.state.db_pool.close()
    await app.state.db_pool.wait_closed()
    app.state.redis.close()

app = FastAPI(lifespan=lifespan)

# Old way (deprecated but still works)
@app.on_event("startup")
async def startup(): ...

@app.on_event("shutdown")
async def shutdown(): ...
```

`lifespan` is preferred over `on_event` (deprecated in newer FastAPI).

---

### 23. How do you handle file uploads in FastAPI?

**A:**

```python
from fastapi import UploadFile, File, Form
import shutil, uuid, aiofiles

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(None),  # combine File + Form
):
    # Validate
    allowed_types = {"image/jpeg", "image/png", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "File type not allowed")

    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(400, "File too large")

    # Save
    filename = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    path = UPLOAD_DIR / filename

    async with aiofiles.open(path, "wb") as out:
        await out.write(content)

    return {"filename": filename, "size": len(content)}

# Multiple files
@app.post("/upload-multiple/")
async def upload_multiple(files: list[UploadFile] = File(...)):
    return [{"filename": f.filename} for f in files]
```

---

### 24. How do you implement WebSockets in FastAPI?

**A:**

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, client_id: str):
        await ws.accept()
        self.active[client_id] = ws

    def disconnect(self, client_id: str):
        self.active.pop(client_id, None)

    async def broadcast(self, message: str, exclude: str = None):
        for cid, ws in self.active.items():
            if cid != exclude:
                await ws.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{client_id}: {data}", exclude=client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"{client_id} left")
```

---

### 25. How do you implement background task queues with Celery in FastAPI?

**A:**

```python
# celery_app.py
from celery import Celery

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery.task(bind=True, max_retries=3)
def send_email_task(self, email: str, subject: str, body: str):
    try:
        email_client.send(email, subject, body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# FastAPI route
from celery.result import AsyncResult

@app.post("/send-email", status_code=202)
def send_email(data: EmailRequest):
    task = send_email_task.delay(data.email, data.subject, data.body)
    return {"task_id": task.id}

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

---

### 26. How does FastAPI's `Depends` caching work?

**A:** By default, a dependency is computed once per request and cached — the same instance is reused:

```python
call_count = 0

def get_settings():
    global call_count
    call_count += 1
    return Settings()

@app.get("/test")
def test(
    s1: Settings = Depends(get_settings),
    s2: Settings = Depends(get_settings),  # same instance as s1!
):
    return {"same_object": s1 is s2, "calls": call_count}
# call_count = 1, same_object = True

# Disable caching
@app.get("/no-cache")
def no_cache(s: Settings = Depends(get_settings, use_cache=False)):
    ...
```

---

### 27. How do you test FastAPI applications?

**A:**

```python
from fastapi.testclient import TestClient
import pytest

app = FastAPI()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_client(client):
    # Login and get token
    resp = client.post("/auth/token", data={"username": "user", "password": "pass"})
    token = resp.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_create_user(client):
    resp = client.post("/users/", json={"name": "Alice", "email": "alice@test.com"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "Alice"

def test_get_user_not_found(client):
    resp = client.get("/users/99999")
    assert resp.status_code == 404

# Async tests
import pytest_asyncio
from httpx import AsyncClient

@pytest.mark.anyio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/async-endpoint")
    assert resp.status_code == 200

# Override dependency in tests
def override_get_db():
    yield test_db_session

app.dependency_overrides[get_db] = override_get_db
```

---

### 28. What is `response_model_exclude` and `response_model_include`?

**A:**

```python
class User(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str
    internal_notes: str

# Exclude specific fields
@app.get("/users/{id}", response_model=User,
         response_model_exclude={"password_hash", "internal_notes"})
def get_user(id: int): ...

# Include only specific fields
@app.get("/users/{id}/summary", response_model=User,
         response_model_include={"id", "name"})
def get_user_summary(id: int): ...

# Better practice: define separate response schemas
class UserPublic(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{id}", response_model=UserPublic)
def get_user(id: int): ...
```

Separate schemas are clearer than runtime exclude/include — easier to document and test.

---

### 29. How does FastAPI handle CORS?

**A:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myfrontend.com",
        "https://admin.myfrontend.com",
    ],
    allow_origin_regex=r"https://.*\.myfrontend\.com",  # regex match
    allow_credentials=True,   # allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Total-Count"],
    max_age=600,  # preflight cache seconds
)

# Development — allow all
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

---

### 30. What are `path operation decorators` vs `APIRouter` dependencies?

**A:**

```python
# Route-level dependency (single endpoint)
@app.get("/admin/data", dependencies=[Depends(require_admin)])
def admin_data(): ...

# Router-level dependency (all routes in router)
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)]  # applied to ALL admin routes
)

@admin_router.get("/users")
def list_users(): ...  # require_admin applied automatically

@admin_router.get("/stats")
def get_stats(): ...   # require_admin applied automatically

# App-level dependency (entire app)
app = FastAPI(dependencies=[Depends(rate_limit)])
```

---

## 🔴 Senior Level

---

### 31. How do you implement event-driven patterns with FastAPI and Kafka?

**A:**

```python
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json

# Producer setup
async def get_producer():
    producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

@app.post("/orders/", status_code=201)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_async_db),
    producer: AIOKafkaProducer = Depends(get_producer),
):
    db_order = Order(**order.dict())
    db.add(db_order)
    await db.commit()

    event = {"event": "order_created", "order_id": db_order.id}
    await producer.send_and_wait("orders", json.dumps(event).encode())
    return db_order

# Consumer (run as background service alongside FastAPI)
async def consume_events():
    consumer = AIOKafkaConsumer("inventory-events", bootstrap_servers="kafka:9092",
                                group_id="order-service")
    await consumer.start()
    async for msg in consumer:
        event = json.loads(msg.value)
        await handle_inventory_event(event)
```

---

### 32. How do you implement hexagonal architecture (ports & adapters) with FastAPI?

**A:**

```python
# Domain layer — pure Python, no framework dependency
class OrderRepository(Protocol):
    async def save(self, order: Order) -> Order: ...
    async def find_by_id(self, id: UUID) -> Order | None: ...

class OrderService:
    def __init__(self, repo: OrderRepository, events: EventPublisher):
        self._repo = repo
        self._events = events

    async def create_order(self, cmd: CreateOrderCommand) -> Order:
        order = Order.create(cmd.customer_id, cmd.items)
        await self._repo.save(order)
        await self._events.publish(OrderCreated(order.id))
        return order

# Infrastructure layer — implements the ports
class SQLAlchemyOrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, order: Order) -> Order:
        self.db.add(order)
        await self.db.commit()
        return order

# FastAPI adapter — thin HTTP layer
@router.post("/orders/", response_model=OrderResponse, status_code=201)
async def create_order(
    cmd: CreateOrderCommand,
    service: OrderService = Depends(get_order_service),
):
    order = await service.create_order(cmd)
    return OrderResponse.from_domain(order)
```

---

### 33. How do you implement OpenTelemetry tracing in FastAPI?

**A:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Setup
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317")))
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)   # auto-traces all routes
SQLAlchemyInstrumentor().instrument()      # auto-traces DB queries
HTTPXClientInstrumentor().instrument()     # auto-traces HTTP client calls

# Custom spans
tracer = trace.get_tracer(__name__)

@app.post("/orders/")
async def create_order(order: OrderCreate):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.customer_id", order.customer_id)
        span.set_attribute("order.items_count", len(order.items))
        result = await order_service.create(order)
        span.set_attribute("order.id", str(result.id))
        return result
```

---

### 34. How do you structure a large FastAPI project for maintainability?

**A:**

```
src/
├── main.py                    # app creation, middleware, router inclusion
├── config.py                  # BaseSettings
├── dependencies.py            # shared Depends() functions
│
├── auth/                      # bounded context
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── dependencies.py
│
├── orders/
│   ├── router.py
│   ├── schemas.py             # Pydantic input/output models
│   ├── models.py              # SQLAlchemy ORM models
│   ├── service.py             # business logic
│   ├── repository.py          # DB queries
│   └── dependencies.py        # order-specific Depends()
│
├── shared/
│   ├── database.py            # engine, session factory
│   ├── exceptions.py          # custom exceptions + handlers
│   ├── pagination.py          # Page[T] schema + helpers
│   └── logging.py
│
└── tests/
    ├── conftest.py            # fixtures, app override
    ├── test_orders.py
    └── test_auth.py
```

Key principles: each bounded context owns its router, schemas, models, and service. Shared infra lives in `shared/`. Domain logic never imports from FastAPI.

---

### 35. How do you implement caching with Redis in FastAPI?

**A:**

```python
import json
import hashlib
from functools import wraps
import aioredis

redis: aioredis.Redis = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    redis = await aioredis.from_url("redis://localhost:6379", decode_responses=True)
    yield
    await redis.close()

# Cache decorator for async functions
def cache(ttl: int = 300, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name + args
            raw_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(raw_key.encode()).hexdigest()

            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/products/{id}")
@cache(ttl=300, key_prefix="product")
async def get_product(id: int, db: AsyncSession = Depends(get_async_db)):
    return await product_repo.get(db, id)
```

---

## 🏛️ Architect Level

---

### 36. How do you design a FastAPI service for high availability and zero-downtime?

**A:**

**Application:**
```python
# Readiness check — only ready when DB/Redis are available
@app.get("/readyz")
async def readyz(db: AsyncSession = Depends(get_async_db)):
    try:
        await db.execute(text("SELECT 1"))
        await redis.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# Liveness check — always available unless process is hung
@app.get("/healthz")
async def healthz():
    return {"status": "alive"}
```

**Graceful shutdown:**
```python
import signal

async def shutdown(app: FastAPI):
    # Stop accepting new connections, let in-flight requests complete
    ...

@asynccontextmanager
async def lifespan(app):
    yield
    # Cleanup: close DB pool, flush producer, drain queues
    await db_pool.dispose()
    await kafka_producer.flush()
```

**Kubernetes:** Same patterns as any service — readiness gate + preStop sleep + `RollingUpdate` with `maxUnavailable: 0`.

---

### 37. How do you design API versioning in FastAPI?

**A:**

```python
from fastapi import FastAPI
from fastapi.routing import APIRouter

# Version 1
v1 = APIRouter(prefix="/v1", tags=["v1"])

@v1.get("/users/{id}", response_model=UserV1Response)
async def get_user_v1(id: int): ...

# Version 2 — new response schema, different behavior
v2 = APIRouter(prefix="/v2", tags=["v2"])

@v2.get("/users/{id}", response_model=UserV2Response)
async def get_user_v2(id: int): ...

app = FastAPI()
app.include_router(v1)
app.include_router(v2)

# Deprecation header middleware
@app.middleware("http")
async def add_deprecation_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/v1"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "Sat, 01 Jan 2026 00:00:00 GMT"
    return response
```

---

### 38. How do you implement multi-tenancy in FastAPI?

**A:**

```python
from contextvars import ContextVar

current_tenant: ContextVar[str] = ContextVar("current_tenant", default=None)

async def resolve_tenant(request: Request) -> str:
    # Strategy 1: subdomain
    host = request.headers.get("host", "")
    tenant = host.split(".")[0]

    # Strategy 2: header
    tenant = request.headers.get("X-Tenant-ID")

    # Strategy 3: JWT claim
    token = decode_jwt(request.headers.get("Authorization"))
    tenant = token.get("tenant_id")

    if not tenant:
        raise HTTPException(400, "Tenant not identified")
    return tenant

# Inject tenant into every route
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    try:
        tenant = await resolve_tenant(request)
        token = current_tenant.set(tenant)
        response = await call_next(request)
        return response
    finally:
        current_tenant.reset(token)

# DB session with tenant-scoped schema
async def get_tenant_db():
    tenant = current_tenant.get()
    async with AsyncSessionLocal() as session:
        await session.execute(text(f"SET search_path = {tenant}"))
        yield session
```

---

### 39. How do you implement a CQRS pattern with FastAPI?

**A:**

```python
from pydantic import BaseModel
from typing import Protocol

# Commands — change state
class CreateOrderCommand(BaseModel):
    customer_id: UUID
    items: list[OrderItemCreate]

class CommandHandler(Protocol):
    async def handle(self, command: BaseModel) -> BaseModel: ...

# Queries — read state (no side effects)
class GetOrderQuery(BaseModel):
    order_id: UUID

class QueryHandler(Protocol):
    async def handle(self, query: BaseModel) -> BaseModel: ...

# Command bus
class CommandBus:
    def __init__(self):
        self._handlers: dict[type, CommandHandler] = {}

    def register(self, command_type: type, handler: CommandHandler):
        self._handlers[command_type] = handler

    async def dispatch(self, command: BaseModel) -> BaseModel:
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for {type(command)}")
        return await handler.handle(command)

# FastAPI endpoints — thin adapters
@router.post("/orders/", status_code=201)
async def create_order(
    command: CreateOrderCommand,
    bus: CommandBus = Depends(get_command_bus),
):
    return await bus.dispatch(command)

@router.get("/orders/{id}")
async def get_order(
    id: UUID,
    bus: QueryBus = Depends(get_query_bus),
):
    return await bus.dispatch(GetOrderQuery(order_id=id))
```

---

### 40. How do you benchmark and optimize FastAPI performance?

**A:**

**Benchmarking:**
```bash
# wrk — HTTP load testing
wrk -t4 -c100 -d30s http://localhost:8000/api/endpoint

# locust — Python-based load testing with ramp-up
locust -f locustfile.py --host=http://localhost:8000

# vegeta — HTTP load test with rate control
echo "GET http://localhost:8000/api/data" | vegeta attack -rate=1000 -duration=30s | vegeta report
```

**FastAPI-specific optimizations:**

```python
# 1. Use async everywhere that does I/O
async def get_item(id: int, db: AsyncSession = Depends(get_async_db)):
    return await db.get(Item, id)

# 2. Response model — use include/exclude to minimize serialization work
@app.get("/items/", response_model=list[ItemSummary])  # not full Item
def list_items(): ...

# 3. orjson for faster JSON serialization
from fastapi.responses import ORJSONResponse

@app.get("/data/", response_class=ORJSONResponse)
def get_data(): return {"large": "payload"}

app = FastAPI(default_response_class=ORJSONResponse)

# 4. Streaming responses for large payloads
from fastapi.responses import StreamingResponse

@app.get("/export/")
async def export_data():
    async def generate():
        async for chunk in get_large_dataset():
            yield json.dumps(chunk) + "\n"
    return StreamingResponse(generate(), media_type="application/x-ndjson")

# 5. Connection pool tuning
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=40)
```

**Profile:** `py-spy top --pid $(pgrep uvicorn)` for CPU hotspots.
