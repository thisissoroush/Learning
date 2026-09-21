# Chapter 2 — Data Storage and Retrieval

> **Projects:** `sql_example`, `nosql_example`, `async_example`, `uploads_and_downloads`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter02)

---

## 🎯 What This Chapter Covers

Four data patterns: SQL with SQLAlchemy (sync), MongoDB with PyMongo, async vs sync endpoint comparison, and file uploads/downloads.

---

## 🗄️ SQL with SQLAlchemy (Sync)

### Database Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Dependency Injection for DB Session

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db          # yields session to the endpoint
    finally:
        db.close()        # always closes, even on exception

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/user")
def add_new_user(user: UserBody, db: Session = Depends(get_db)):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)   # refresh to get generated id
    return new_user

@app.delete("/user")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}
```

---

## 🍃 MongoDB with PyMongo (Sync)

```python
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, EmailStr, field_validator

client = MongoClient("mongodb://localhost:27017/")
db = client["mydb"]
user_collection = db["users"]

class Tweet(BaseModel):
    content: str
    hashtags: list[str]

class User(BaseModel):
    name: str
    email: EmailStr
    age: int
    tweets: list[Tweet] | None = None

    @field_validator("age")
    def validate_age(cls, value):
        if value < 18 or value > 100:
            raise ValueError("Age must be between 18 and 100")
        return value

@app.post("/user")
def create_user(user: User):
    result = user_collection.insert_one(user.model_dump(exclude_none=True))
    return {"id": str(result.inserted_id), **user.model_dump()}

@app.get("/user")
def get_user(user_id: str):
    db_user = user_collection.find_one(
        {"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
    )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user["id"] = str(db_user["_id"])
    return db_user
```

**Key MongoDB patterns:**
- `ObjectId.is_valid(user_id)` before converting — avoids exceptions on bad input
- `model_dump(exclude_none=True)` — don't store null fields in MongoDB
- `str(result.inserted_id)` — convert `ObjectId` to string for JSON response

---

## ⚡ Async vs Sync Endpoints

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

# SYNC — blocks the thread during sleep (no other requests handled)
@app.get("/sync")
def read_sync():
    time.sleep(2)                    # blocks uvicorn worker thread
    return {"message": "Synchronous blocking endpoint"}

# ASYNC — yields to event loop during await (other requests handled)
@app.get("/async")
async def read_async():
    await asyncio.sleep(2)           # non-blocking: event loop handles other requests
    return {"message": "Asynchronous non-blocking endpoint"}
```

**When to use which:**
| Situation | Use |
|-----------|-----|
| I/O-bound: HTTP calls, DB queries, file reads | `async def` + `await` |
| CPU-bound: image processing, heavy computation | `def` (runs in thread pool) |
| Sync DB library (e.g. psycopg2, pymongo sync) | `def` |
| Async DB library (e.g. asyncpg, motor) | `async def` |

> ⚠️ Never call blocking I/O inside `async def` without `await` — it blocks the entire event loop.

---

## 📁 File Uploads and Downloads

```python
from fastapi import UploadFile
from fastapi.responses import FileResponse
import shutil

UPLOAD_DIR = "uploads"

@app.post("/upload")
async def upload_file(file: UploadFile):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "content_type": file.content_type}

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"{UPLOAD_DIR}/{filename}"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )

# Multiple file upload
@app.post("/upload-many")
async def upload_multiple(files: list[UploadFile]):
    results = []
    for file in files:
        file_path = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        results.append({"filename": file.filename})
    return results
```

---

## 🔑 Key Takeaways

- `Depends(get_db)` with `yield` ensures the DB session is always closed — even on exceptions
- `db.refresh(obj)` after `commit()` reloads the object with DB-generated values (id, timestamps)
- `ObjectId.is_valid()` before converting prevents crashes on bad MongoDB IDs
- `async def` + `await` = non-blocking; `def` = runs in thread pool (still concurrent in FastAPI)
- Never `time.sleep()` in `async def` — use `await asyncio.sleep()` instead
- `UploadFile` gives you `file.filename`, `file.content_type`, and `file.file` (file-like object)
