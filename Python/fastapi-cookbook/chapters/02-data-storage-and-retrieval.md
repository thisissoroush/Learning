# Chapter 2 — Data Storage and Retrieval

> **Projects:** `sql_example`, `nosql_example`, `async_example`, `uploads_and_downloads`

---

## 🎯 What This Chapter Covers

How to connect FastAPI to real databases — SQL via SQLAlchemy (sync), MongoDB via PyMongo, plus how `async def` vs `def` endpoints actually behave differently under load, and how to handle file uploads/downloads.

---

## 🧠 The Core Problem: Database Sessions and Lifetimes

The most important thing to understand about databases in FastAPI is **session lifecycle**. A database session/connection must be:
1. Opened before the request is processed
2. Closed after — even if an exception is raised
3. Never shared between requests

FastAPI's `Depends()` with a generator function solves this cleanly. Here's the pattern explained step by step:

```
Request arrives
    → FastAPI calls get_db()
    → get_db() opens a session, yields it
    → FastAPI passes session to your endpoint via Depends()
    → Your endpoint runs (success or exception)
    → FastAPI runs the finally block in get_db() → session.close()
    → Response sent
```

---

## 🗄️ SQL with SQLAlchemy — Full Walkthrough

### Step 1: Define the Database Engine and Base

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite for development — swap for PostgreSQL in production:
# "postgresql+psycopg2://user:password@localhost:5432/mydb"
DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    # SQLite-specific: allow multiple threads (not needed for PostgreSQL)
    connect_args={"check_same_thread": False},
)

# All ORM models inherit from Base
class Base(DeclarativeBase):
    pass

# Session factory — creates new sessions on request
SessionLocal = sessionmaker(
    autocommit=False,  # we control commits explicitly
    autoflush=False,   # don't flush until commit
    bind=engine,
)
```

### Step 2: Define ORM Models

```python
# models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from database import Base

class User(Base):
    __tablename__ = "users"         # SQL table name

    # Mapped[type] = mapped_column(...) — SQLAlchemy 2.0 style
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    def __repr__(self):
        return f"<User id={self.id} name={self.name}>"
```

### Step 3: The Dependency — Session Per Request

```python
# dependencies.py
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session and guarantee it's closed afterward.

    This is a generator function — FastAPI recognizes the yield and:
    - Runs code before yield when request starts
    - Runs code after yield (finally) when request finishes
    """
    db = SessionLocal()
    try:
        yield db          # ← FastAPI injects this into your endpoint
    finally:
        db.close()        # ← always runs, even if endpoint raised an exception
```

### Step 4: CRUD Endpoints

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import User
from dependencies import get_db

app = FastAPI()

# Pydantic schemas for request/response
class UserCreate(BaseModel):
    name: str
    email: EmailStr          # EmailStr validates the format automatically

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}  # allow ORM object → Pydantic

# GET all users — list with pagination
@app.get("/users", response_model=list[UserResponse])
def get_users(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),     # FastAPI opens and closes the session
):
    return db.query(User).offset(offset).limit(limit).all()

# GET single user — raises 404 if not found
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user

# POST create user
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(name=user_data.name, email=user_data.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # ← IMPORTANT: re-reads from DB to get the generated id
    return new_user

# PUT update user
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_data.name
    user.email = user_data.email
    db.commit()
    db.refresh(user)
    return user

# DELETE user
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    # 204 No Content — don't return anything
```

**Why `db.refresh(new_user)` after commit?** After `db.commit()`, SQLAlchemy expires all attributes on the object (marks them as stale). If you return the object immediately, it will trigger a lazy load — but if the session is already closed, that fails. `refresh()` forces a re-read while the session is still open.

---

## 🍃 MongoDB with PyMongo — Document Store Patterns

MongoDB stores documents (JSON-like) instead of rows. The connection model is different: you create a client once at startup and reuse it.

```python
# nosql/database.py
from pymongo import MongoClient
from pymongo.collection import Collection

# Single client instance — thread-safe, reuse across requests
client = MongoClient("mongodb://localhost:27017/")
database = client["myapp"]

def get_users_collection() -> Collection:
    """Return the users collection — used as a Dependency."""
    return database["users"]
```

```python
# nosql/main.py
from fastapi import FastAPI, HTTPException, Depends
from pymongo.collection import Collection
from bson import ObjectId
from pydantic import BaseModel, EmailStr, field_validator

app = FastAPI()

# Pydantic model with a custom validator
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

    @field_validator("age")
    @classmethod
    def age_must_be_adult(cls, v):
        # field_validator runs BEFORE the value is stored
        # raise ValueError to trigger a 422 Unprocessable Entity
        if v < 18:
            raise ValueError("Must be 18 or older")
        if v > 120:
            raise ValueError("Age seems unrealistic")
        return v

class UserResponse(UserCreate):
    id: str    # MongoDB ObjectId as string

def get_users_collection() -> Collection:
    return database["users"]

@app.post("/users", status_code=201)
def create_user(
    user: UserCreate,
    collection: Collection = Depends(get_users_collection),
):
    # model_dump() converts Pydantic model to dict
    # exclude_none=True skips None fields — MongoDB doesn't need null fields
    doc = user.model_dump(exclude_none=True)
    result = collection.insert_one(doc)

    # MongoDB auto-generates _id (ObjectId) on insert
    # result.inserted_id is an ObjectId object — convert to string for JSON
    return {"id": str(result.inserted_id), **doc}

@app.get("/users/{user_id}")
def get_user(
    user_id: str,
    collection: Collection = Depends(get_users_collection),
):
    # ALWAYS validate before converting — ObjectId("not-valid") raises an exception
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    doc = collection.find_one({"_id": ObjectId(user_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert ObjectId → string before returning
    doc["id"] = str(doc.pop("_id"))
    return doc

@app.get("/users")
def list_users(
    collection: Collection = Depends(get_users_collection),
    limit: int = 20,
):
    # find() returns a cursor — convert to list
    # Never call find() without a limit on large collections!
    docs = list(collection.find().limit(limit))
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
    return docs
```

---

## ⚡ Async vs Sync — What Actually Happens

This is one of the most misunderstood parts of FastAPI. Here's what actually happens under the hood:

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

# SYNC endpoint — FastAPI runs this in a thread pool (not the event loop)
# ✅ Safe to call blocking code (time.sleep, psycopg2, pymongo)
# ❌ But thread pool has a limit — 40 concurrent threads by default
@app.get("/sync-example")
def sync_endpoint():
    time.sleep(2)     # blocks the thread — but NOT the event loop
                      # other async requests still proceed normally
    return {"msg": "done"}

# ASYNC endpoint — FastAPI runs this in the event loop directly
# ✅ Perfect for async I/O (httpx, asyncpg, motor, aioredis)
# ❌ NEVER call blocking code here — it freezes ALL requests!
@app.get("/async-example")
async def async_endpoint():
    await asyncio.sleep(2)   # suspends this coroutine, event loop handles others
    return {"msg": "done"}

# THE MISTAKE: blocking I/O inside async def
@app.get("/broken")
async def broken_endpoint():
    time.sleep(2)    # 🚨 BLOCKS THE ENTIRE EVENT LOOP
                     # ALL other requests are frozen for 2 seconds!
    return {"msg": "never do this"}
```

**Decision table:**

| Your situation | Use |
|----------------|-----|
| Using async library (asyncpg, motor, httpx) | `async def` + `await` |
| Using sync library (psycopg2, pymongo, requests) | `def` (thread pool) |
| CPU-heavy computation | `def` (thread pool) — or `run_in_executor` for async |
| Simple logic, no I/O | Either works |

---

## 📁 File Uploads and Downloads — Handling Binary Data

Files are a special case because they can't be sent as JSON. Use `multipart/form-data` for uploads.

```python
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import shutil
import uuid

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)    # create directory if it doesn't exist

@app.post("/upload")
async def upload_file(file: UploadFile):
    # UploadFile gives you:
    # - file.filename  → original filename (can be None for unnamed files)
    # - file.content_type → MIME type ("image/jpeg", "application/pdf", etc.)
    # - file.file      → a file-like object (SpooledTemporaryFile)
    # - await file.read() → full contents as bytes

    # Security: never trust the original filename — use a UUID instead
    extension = Path(file.filename).suffix if file.filename else ""
    safe_name = f"{uuid.uuid4()}{extension}"
    dest_path = UPLOAD_DIR / safe_name

    # Copy from upload buffer to disk
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "stored_as": safe_name,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size_bytes": dest_path.stat().st_size,
    }

# File validation before saving
@app.post("/upload/image")
async def upload_image(file: UploadFile):
    # Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image. Got: {file.content_type}",
        )

    # Validate file size (read into memory to check)
    contents = await file.read()
    max_size = 5 * 1024 * 1024    # 5 MB
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail="File exceeds 5MB limit")

    # Save to disk
    safe_name = f"{uuid.uuid4()}.jpg"
    (UPLOAD_DIR / safe_name).write_bytes(contents)
    return {"filename": safe_name}

# Download a file
@app.get("/download/{filename}")
async def download_file(filename: str):
    # Security: prevent path traversal attacks (../../etc/passwd)
    # Path().name extracts just the filename, stripping any directory components
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,             # sent as Content-Disposition header
        media_type="application/octet-stream",  # triggers browser download
    )
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `Depends(get_db)` with `yield` | Session always closes — even when exceptions occur |
| `db.refresh(obj)` after commit | SQLAlchemy expires attributes on commit — refresh re-reads from DB |
| `ObjectId.is_valid()` before converting | `ObjectId("bad")` raises `bson.errors.InvalidId` — validate first |
| `model_dump(exclude_none=True)` for MongoDB | Don't store null fields — wastes space and complicates queries |
| `def` for sync libraries | FastAPI runs sync functions in a thread pool — safe for blocking code |
| `async def` + `await` for async libraries | Runs in the event loop — never call blocking code here |
| `Path(filename).name` before saving | Strips directory traversal from user input (`../../etc/passwd` → `passwd`) |
