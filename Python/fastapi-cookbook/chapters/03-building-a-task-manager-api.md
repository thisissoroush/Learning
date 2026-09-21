# Chapter 3 — Building a Task Manager API

> **Project:** `task_manager_app`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter03)

---

## 🎯 What This Chapter Covers

A full CRUD task management API with OAuth2 authentication, API versioning, custom OpenAPI schema, and testing with pytest.

---

## 📋 Pydantic Models

```python
from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    title: str
    description: str
    status: str

class TaskWithID(Task):
    id: int

class TaskV2WithID(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str        # new field in v2
    due_date: str | None = None
```

---

## 🔄 Full CRUD Endpoints

```python
from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI(
    title="Task Manager API",
    description="This is a task management API",
    version="0.1.0",
)

@app.get("/tasks", response_model=list[TaskWithID])
def get_tasks(status: Optional[str] = None, title: Optional[str] = None):
    tasks = read_all_tasks()
    if status:
        tasks = [t for t in tasks if t.status == status]
    if title:
        tasks = [t for t in tasks if t.title == title]
    return tasks

@app.get("/task/{task_id}")
def get_task(task_id: int):
    task = read_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task

@app.post("/task", response_model=TaskWithID)
def add_task(task: Task):
    return create_task(task)

class UpdateTask(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

@app.put("/task/{task_id}", response_model=TaskWithID)
def update_task(task_id: int, task_update: UpdateTask):
    # model_dump(exclude_unset=True) — only update provided fields
    modified = modify_task(task_id, task_update.model_dump(exclude_unset=True))
    if not modified:
        raise HTTPException(status_code=404, detail="task not found")
    return modified

@app.delete("/task/{task_id}", response_model=Task)
def delete_task(task_id: int):
    removed_task = remove_task(task_id)
    if not removed_task:
        raise HTTPException(status_code=404, detail="task not found")
    return removed_task

@app.get("/tasks/search", response_model=list[TaskWithID])
def search_tasks(keyword: str):
    tasks = read_all_tasks()
    return [
        task for task in tasks
        if keyword.lower() in (task.title + task.description).lower()
    ]
```

**`model_dump(exclude_unset=True)`** — crucial for PATCH/PUT: only updates fields the client actually sent, not all fields including defaults.

---

## 🔐 OAuth2 Password Flow

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

# Simulated user DB (in real app: actual DB with hashed passwords)
fake_users_db = {
    "johndoe": {"username": "johndoe", "hashed_password": "hashedsecret"},
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

def fakely_hash_password(password: str) -> str:
    return f"hashed{password}"

def fake_token_generator(user: UserInDB) -> str:
    return f"tokenized{user.username}"

def get_user_from_token(token: str = Depends(oauth2_scheme)) -> UserInDB:
    if token.startswith("tokenized"):
        username = token.removeprefix("tokenized")
        user = fake_users_db.get(username)
        if user:
            return UserInDB(**user)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    if fakely_hash_password(form_data.password) != user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": fake_token_generator(user), "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_user_from_token)):
    return current_user
```

---

## 🔢 API Versioning

```python
# v1 — original tasks
@app.get("/tasks", response_model=list[TaskWithID])
def get_tasks(): ...

# v2 — extended tasks with priority and due_date
@app.get("/v2/tasks", response_model=list[TaskV2WithID])
def get_tasks_v2():
    return read_all_tasks_v2()
```

Versioning strategies:
- **URL prefix** (`/v1/`, `/v2/`) — simplest, most visible ✅ used here
- **Header** (`API-Version: 2`) — cleaner URLs, harder to use in browser
- **Query param** (`?version=2`) — easy but pollutes query space

---

## 📄 Custom OpenAPI Schema

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Customized Title",
        version="2.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    # Remove internal endpoints from docs
    del openapi_schema["paths"]["/token"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi   # replace the default
```

---

## 🧪 Testing with pytest

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_task():
    response = client.post("/task", json={
        "title": "Test Task",
        "description": "A test task",
        "status": "pending",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

def test_get_nonexistent_task():
    response = client.get("/task/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"

def test_update_task():
    # Create first
    create_resp = client.post("/task", json={
        "title": "Old Title", "description": "Desc", "status": "pending"
    })
    task_id = create_resp.json()["id"]

    # Update only status
    update_resp = client.put(f"/task/{task_id}", json={"status": "done"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "done"
    assert update_resp.json()["title"] == "Old Title"  # untouched
```

---

## 🔑 Key Takeaways

- `model_dump(exclude_unset=True)` is essential for partial updates — only applies fields the client sent
- `OAuth2PasswordBearer(tokenUrl="token")` + `Depends()` makes any endpoint require Bearer token
- `OAuth2PasswordRequestForm` expects `application/x-www-form-urlencoded` (not JSON)
- Custom `app.openapi = my_func` replaces the default schema generator — use for hiding internal endpoints
- `TestClient` from `fastapi.testclient` wraps `requests` — test as if calling a real HTTP server
- Cache `app.openapi_schema` to avoid regenerating on every request
