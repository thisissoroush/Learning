# Chapter 1 — Getting Started with FastAPI

> **Project:** `bookstore` + `fastapi_start`

---

## 🎯 What This Chapter Covers

FastAPI's core mechanics: how requests are routed, how URL parameters are parsed and validated, how Pydantic enforces input shapes, how `APIRouter` splits a large app into modules, and how to customize error responses globally.

---

## 🧠 The Mental Model First

Before writing any code, understand what FastAPI actually does when a request arrives:

```
HTTP Request
    ↓
FastAPI matches URL path → finds your function
    ↓
Extracts path params, query params, body → validates them using type hints
    ↓
Calls your function with the validated, converted values
    ↓
Serializes the return value → HTTP Response
```

The key insight: **your type annotations ARE your validation**. You write `book_id: int` and FastAPI automatically rejects `GET /books/banana` with a proper 422 error. You don't write any validation code yourself.

---

## 🚀 Your First App — What Each Line Does

```python
from fastapi import FastAPI

app = FastAPI()          # creates the ASGI application
                         # this is the object uvicorn serves

@app.get("/")            # registers a route: GET /
async def read_root():   # function name doesn't matter — just readable
    return {"Hello": "World"}   # dict → auto-serialized to JSON
```

Run it:
```bash
uvicorn main:app --reload
# main     = filename (main.py)
# app      = the FastAPI() instance
# --reload = restart on file change (dev only!)
```

Visit `http://localhost:8000/docs` — FastAPI generated a **full Swagger UI** from your code, with no extra configuration.

---

## 🗂️ Splitting Routes with APIRouter

As your app grows, putting everything in `main.py` becomes unmanageable. `APIRouter` lets you define routes in separate files and mount them into the main app.

**Without APIRouter (messy):**
```python
# main.py — everything piled in one file
app = FastAPI()

@app.get("/books/{id}") ...
@app.post("/books") ...
@app.get("/authors/{id}") ...
@app.post("/authors") ...
@app.get("/orders/{id}") ...
# ... 50 more routes
```

**With APIRouter (clean):**
```python
# books/router.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/books",          # all routes in this file start with /books
    tags=["books"],           # Swagger groups them under "books"
)

@router.get("/{book_id}")     # actual path: /books/{book_id}
async def get_book(book_id: int):
    return {"book_id": book_id}

@router.post("/")             # actual path: /books/
async def create_book():
    ...
```

```python
# main.py — stays clean
from fastapi import FastAPI
from books.router import router as books_router
from authors.router import router as authors_router

app = FastAPI()
app.include_router(books_router)     # mounts /books/* routes
app.include_router(authors_router)   # mounts /authors/* routes
```

The `prefix` and `tags` parameters do two jobs at once: they set the URL prefix AND organize the Swagger docs visually.

---

## 📦 Pydantic Models — Input Validation Done Right

Pydantic models are the contract between your API and its callers. When a POST request arrives, FastAPI passes the JSON body through the Pydantic model — if it doesn't match, the request is **rejected before your function even runs**.

```python
from pydantic import BaseModel, Field
from typing import Optional

class Book(BaseModel):
    title: str = Field(
        ...,                      # ... means REQUIRED — no default
        min_length=1,             # rejects empty strings
        max_length=100,
        description="The full title of the book",  # appears in Swagger
    )
    author: str = Field(..., min_length=1, max_length=50)
    year: int = Field(
        ...,
        gt=1900,                  # gt = greater than (exclusive)
        lt=2100,                  # lt = less than (exclusive)
    )
    isbn: Optional[str] = None    # optional field — can be omitted

# What happens with different inputs:
# POST /books {"title": "1984", "author": "Orwell", "year": 1949}  → ✅ passes
# POST /books {"title": "", "author": "Orwell", "year": 1949}      → ❌ 422: min_length
# POST /books {"author": "Orwell", "year": 1949}                   → ❌ 422: title required
# POST /books {"title": "1984", "author": "Orwell", "year": 1800}  → ❌ 422: year > 1900
```

**Important distinction:**
- `Field(...)` — required, will error if missing
- `Field(None)` or `Optional[str] = None` — optional, defaults to None
- `Field("default")` — optional, defaults to the given value

---

## 🛤️ Path Parameters vs Query Parameters

The location of a parameter in your function signature determines how FastAPI reads it from the request.

```python
# Path parameter: embedded in the URL path with {braces}
# FastAPI extracts it and converts to the annotated type
@app.get("/books/{book_id}")
async def get_book(book_id: int):      # int → FastAPI parses from URL
    # GET /books/42    → book_id = 42
    # GET /books/abc   → 422 Unprocessable Entity (can't convert "abc" to int)
    return {"book_id": book_id}


# Query parameter: appears after ? in the URL
# Declared as a regular function parameter (no {braces} in path)
@app.get("/books")
async def list_books(
    year: int | None = None,       # optional — GET /books or GET /books?year=1949
    limit: int = 10,               # default value — GET /books?limit=5
    offset: int = 0,               # default value — GET /books?offset=20
):
    # GET /books                   → year=None, limit=10, offset=0
    # GET /books?year=1949         → year=1949, limit=10, offset=0
    # GET /books?limit=5&offset=20 → year=None, limit=5, offset=20
    return {"year": year, "limit": limit, "offset": offset}


# Mix of both: path param + query params
@app.get("/authors/{author_id}/books")
async def author_books(
    author_id: int,          # path parameter (required, from URL)
    published: bool = True,  # query parameter (optional, default True)
    genre: str | None = None # query parameter (optional, default None)
):
    # GET /authors/5/books              → author_id=5, published=True, genre=None
    # GET /authors/5/books?published=false&genre=fiction
    #                                   → author_id=5, published=False, genre="fiction"
    ...
```

**The rule:** if the name appears in the path `{braces}` → path param. If not → query param. Body params are declared as Pydantic models.

---

## 📤 Response Models — Controlling Output Shape

Your endpoint might work with objects that contain fields you don't want to expose (passwords, internal IDs, audit timestamps). The response model is a filter.

```python
from pydantic import BaseModel

# Internal model — what lives in your database
class UserDB(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str      # NEVER expose this
    created_at: datetime
    is_admin: bool            # NEVER expose this either

# External model — what the API returns
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    # hashed_password excluded — not in this model
    # is_admin excluded — not in this model

# The response_model parameter acts as the filter
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = get_user_from_db(user_id)  # returns a UserDB with password etc.
    return user   # FastAPI filters it through UserResponse before sending

# You can also declare it with a return type annotation
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> UserResponse:
    user = get_user_from_db(user_id)
    return user
```

Response models also power the Swagger docs: the schema shown for the response shape comes from this model.

---

## ⚠️ Custom Exception Handlers — Consistent Error Responses

By default, FastAPI returns different error formats for different error types. In production you want a **uniform error envelope** so clients always know what to expect.

```python
import json
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

# This is your standard error shape — all errors return this
class ErrorResponse(BaseModel):
    error: str
    detail: str | list | None = None
    request_id: str | None = None  # for tracing

# Override HTTPException (raised by your code: raise HTTPException(...))
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,            # e.g. "Book not found"
            "status_code": exc.status_code,
        },
    )

# Override validation errors (raised by Pydantic: wrong body shape, bad types)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.errors() gives you a list of every field that failed and why
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "detail": exc.errors(),          # list of {loc, msg, type}
        },
    )

# Catch-all for unexpected errors — never expose Python tracebacks in prod
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# Using HTTPException in endpoints
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    book = db.get(book_id)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with id={book_id} not found",  # included in "error" field
        )
    return book
```

**The flow:** your endpoint raises `HTTPException` → FastAPI catches it → calls your handler → sends JSON. No try/except in endpoint code needed.

---

## ✅ Putting It All Together — A Real Bookstore API

```python
from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

# --- Models ---
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., gt=1000, lt=2100)
    isbn: Optional[str] = None

class BookResponse(BookCreate):
    id: int    # added by DB on creation

# --- In-memory "database" for demo ---
books_db: dict[int, dict] = {}
next_id = 1

# --- Router ---
router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=list[BookResponse])
async def list_books(limit: int = 20, offset: int = 0):
    all_books = list(books_db.values())
    return all_books[offset : offset + limit]

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db[next_id] = new_book
    next_id += 1
    return new_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    del books_db[book_id]

# --- App ---
app = FastAPI(title="Bookstore API", version="1.0")
app.include_router(router)
```

---

## 🔑 Key Takeaways

| Concept | How it works | Why it matters |
|---------|-------------|----------------|
| Type annotations | FastAPI reads them to validate and convert | Zero boilerplate validation code |
| Path param | `{name}` in path + `name: type` in function | Auto-parsed and converted |
| Query param | `name: type = default` in function (no braces) | Optional/required by whether there's a default |
| Body param | Pydantic `BaseModel` as function param | Validated against schema, 422 on failure |
| `response_model` | Pydantic model that filters output | Security: never leak internal fields |
| `APIRouter` | Groups routes by domain with shared prefix/tags | Keeps `main.py` clean as app grows |
| Exception handler | `@app.exception_handler(ExcType)` | Uniform error shape across all endpoints |
