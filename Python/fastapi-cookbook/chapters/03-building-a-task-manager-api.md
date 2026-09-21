# Chapter 3 — Building a Task Manager API

> **Project:** `task_manager_app`

---

## 🎯 What This Chapter Covers

Building a production-shaped CRUD API: full create/read/update/delete with proper status codes, partial updates, OAuth2 authentication, API versioning, customizing the OpenAPI schema, and testing with `TestClient`.

---

## 🧠 Design Before Code

A Task Manager API needs to handle:
- **Two different request shapes**: creating a task (no id) vs returning a task (has id)
- **Partial updates**: a PATCH request should only update the fields provided — not reset everything
- **Authentication**: tasks should require a logged-in user
- **Versioning**: changing the task shape without breaking existing clients

These needs drive the model design.

---

## 📋 Data Models — Separation of Concerns

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    """Using an Enum constrains the status to known values.
    str inheritance means it serializes as a plain string in JSON."""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

# Request body for creating a task
class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending   # defaults to pending

# Full task as stored (has id)
class Task(TaskCreate):
    id: int
    # Inherits title, description, status from TaskCreate

# Version 2 of the full task — added fields without breaking v1
class TaskV2(Task):
    priority: str = "normal"   # new field — backward compatible (has default)
    tags: list[str] = []       # new field — backward compatible

# For partial updates (PATCH): all fields are optional
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    # model_dump(exclude_unset=True) returns only the fields
    # the caller actually sent — not the None defaults
    # e.g. PATCH {"status": "completed"} → only status is updated
```

---

## 🔄 CRUD Endpoints — Status Codes Matter

```python
from fastapi import FastAPI, HTTPException, status
from typing import Optional

app = FastAPI(title="Task Manager", version="1.0")

# In-memory store (replace with DB in production)
tasks_db: dict[int, dict] = {}
_next_id = 1

@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status_filter: Optional[TaskStatus] = None,  # query: ?status_filter=pending
    title_contains: Optional[str] = None,        # query: ?title_contains=meeting
):
    tasks = list(tasks_db.values())
    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]
    if title_contains:
        tasks = [t for t in tasks if title_contains.lower() in t["title"].lower()]
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks_db.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task

@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,  # 201 Created — not 200 OK
)
def create_task(task_data: TaskCreate):
    global _next_id
    task = {"id": _next_id, **task_data.model_dump()}
    tasks_db[_next_id] = task
    _next_id += 1
    return task

# PUT = full replacement — caller must send all fields
@app.put("/tasks/{task_id}", response_model=Task)
def replace_task(task_id: int, task_data: TaskCreate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    # Full replacement: overwrite everything
    task = {"id": task_id, **task_data.model_dump()}
    tasks_db[task_id] = task
    return task

# PATCH = partial update — caller sends only the fields to change
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, update_data: TaskUpdate):
    task = tasks_db.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # exclude_unset=True is the key: only includes fields the client sent
    # If client sends {} — nothing changes
    # If client sends {"status": "completed"} — only status changes
    changes = update_data.model_dump(exclude_unset=True)
    task.update(changes)
    tasks_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    # 204 No Content: return nothing — not even an empty dict
```

---

## 🔐 OAuth2 Password Authentication

OAuth2 with Password flow is a standard way to authenticate: client sends username/password, gets back a token, uses the token on future requests.

```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# This tells FastAPI: to authenticate, clients POST to /token
# Any route using oauth2_scheme as a dependency gets a 🔒 padlock in Swagger docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# User models
class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

# Simulated user store (production: hash with bcrypt, store in DB)
fake_users_db = {
    "alice": {"username": "alice", "hashed_password": "hashed_s3cret"},
    "bob":   {"username": "bob",   "hashed_password": "hashed_p4ssw0rd"},
}

def hash_password(password: str) -> str:
    """In production: use passlib.hash.bcrypt.hash(password)"""
    return f"hashed_{password}"

def verify_password(plain: str, hashed: str) -> bool:
    """In production: use passlib.hash.bcrypt.verify(plain, hashed)"""
    return hash_password(plain) == hashed

def create_token(username: str) -> str:
    """In production: use python-jose to create a signed JWT"""
    return f"token_for_{username}"

def get_user_from_token(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency: extracts and validates the Bearer token.
    Used by any endpoint that requires authentication."""
    # In production: jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if not token.startswith("token_for_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},  # required by OAuth2 spec
        )
    username = token.removeprefix("token_for_")
    if username not in fake_users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return User(username=username)

# Login endpoint — OAuth2PasswordRequestForm expects form data, not JSON
# Content-Type must be: application/x-www-form-urlencoded
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

# Protected endpoint — requires valid token
@app.get("/users/me", response_model=User)
def get_current_user(current_user: User = Depends(get_user_from_token)):
    return current_user

# Protected task creation — attaches task to logged-in user
@app.post("/my-tasks", response_model=Task, status_code=201)
def create_my_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_user_from_token),
):
    global _next_id
    task = {"id": _next_id, "owner": current_user.username, **task_data.model_dump()}
    tasks_db[_next_id] = task
    _next_id += 1
    return task
```

---

## 🔢 API Versioning — Changing Without Breaking

When you need to change your API's response shape, versioning lets old clients keep working while new clients use the improved version.

```python
# V1 route: original task shape
@app.get("/v1/tasks", response_model=list[Task])
def get_tasks_v1():
    return list(tasks_db.values())

# V2 route: extended task with new fields
@app.get("/v2/tasks", response_model=list[TaskV2])
def get_tasks_v2():
    tasks = list(tasks_db.values())
    # Add V2-only fields with defaults for existing tasks
    return [
        {**task, "priority": task.get("priority", "normal"), "tags": task.get("tags", [])}
        for task in tasks
    ]

# Better approach for bigger apps: use APIRouter with version prefix
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1", tags=["v1"])
v2_router = APIRouter(prefix="/v2", tags=["v2"])

@v1_router.get("/tasks", response_model=list[Task])
def v1_tasks(): ...

@v2_router.get("/tasks", response_model=list[TaskV2])
def v2_tasks(): ...

app.include_router(v1_router)
app.include_router(v2_router)
```

---

## 📄 Customizing the OpenAPI Schema

Sometimes you want to hide internal endpoints (like `/token`) from the public docs, or add custom descriptions.

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    # Cache the schema — don't regenerate on every /openapi.json call
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Task Manager API",
        version="2.0.0",
        description="""
## Task Manager API

Manage your tasks with full CRUD operations.

### Authentication
Use the `/token` endpoint to get a Bearer token, then include it in
the `Authorization: Bearer <token>` header on protected endpoints.
        """,
        routes=app.routes,
    )

    # Hide the /token endpoint from the public docs
    # (it still works — just not visible in Swagger UI)
    if "/token" in openapi_schema.get("paths", {}):
        del openapi_schema["paths"]["/token"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## 🧪 Testing with TestClient

`TestClient` wraps your app in a test harness. No server needed — tests run in-process.

```python
# test_tasks.py
import pytest
from fastapi.testclient import TestClient
from main import app

# TestClient uses requests under the hood — same API
client = TestClient(app)

def test_create_task():
    response = client.post("/tasks", json={
        "title": "Write tests",
        "description": "Cover all endpoints",
        "status": "pending",
    })
    assert response.status_code == 201      # 201 Created
    data = response.json()
    assert data["title"] == "Write tests"
    assert "id" in data                     # id was assigned

def test_get_task_not_found():
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_partial_update():
    # Create a task first
    create_resp = client.post("/tasks", json={
        "title": "Original", "description": "Original desc", "status": "pending"
    })
    task_id = create_resp.json()["id"]

    # Patch only the status
    patch_resp = client.patch(f"/tasks/{task_id}", json={"status": "completed"})
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["status"] == "completed"
    assert data["title"] == "Original"      # unchanged

def test_invalid_status_rejected():
    response = client.post("/tasks", json={
        "title": "Test", "description": "Desc", "status": "not_a_real_status"
    })
    assert response.status_code == 422      # Pydantic validation error

def test_authenticated_endpoint():
    # First: login to get token
    login_resp = client.post("/token", data={   # note: data= not json= (form)
        "username": "alice",
        "password": "s3cret",
    })
    token = login_resp.json()["access_token"]

    # Then: use token on protected endpoint
    me_resp = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "alice"
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `TaskCreate` vs `Task` | Request and response have different shapes — model them separately |
| `model_dump(exclude_unset=True)` | PATCH needs to know which fields the client actually sent |
| `status_code=201` on POST | Semantically correct — 201 means "resource was created" |
| `204 No Content` on DELETE | Correct status for operations that return nothing |
| `OAuth2PasswordRequestForm` | Expects form-encoded body, not JSON — `data=` not `json=` in tests |
| `headers={"WWW-Authenticate": "Bearer"}` | OAuth2 spec requires this on 401 responses |
| Custom `app.openapi` | Cache the schema and modify it before returning — runs once per app lifetime |
