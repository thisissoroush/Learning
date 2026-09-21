# Chapter 1 — Getting Started with FastAPI

> **Project:** `bookstore` + `fastapi_start`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter01)

---

## 🎯 What This Chapter Covers

Core FastAPI building blocks: routing, path/query parameters, Pydantic validation, APIRouter, response models, and custom exception handlers. Built around a Bookstore API.

---

## 🚀 First App + APIRouter

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()

@router.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

app.include_router(router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}
```

**Key point:** `APIRouter` lets you split routes across files. `app.include_router(router)` merges them. This is how real apps are organized — one router per domain (books, authors, users).

---

## 📦 Pydantic Models for Validation

```python
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., gt=1900, lt=2100)
```

- `...` = required (no default)
- `Field()` adds constraints: `min_length`, `max_length`, `gt`, `lt`, `ge`, `le`, `regex`
- FastAPI auto-validates on every request and returns `422 Unprocessable Entity` with details on failure

---

## 🛤️ Path and Query Parameters

```python
# Path parameter — part of the URL
@app.get("/books/{book_id}")
async def read_book(book_id: int):           # type annotation = auto-validation
    return {"book_id": book_id}

# Query parameter — after ?
@app.get("/books")
async def read_books(year: int = None):      # optional query param
    if year:
        return {"year": year, "books": [...]}
    return {"books": ["All Books"]}

# Combination
@app.get("/authors/{author_id}/books")
async def author_books(author_id: int, published: bool = True):
    ...
```

---

## 📤 Response Models

```python
from pydantic import BaseModel

class BookResponse(BaseModel):
    title: str
    author: str
    # NOTE: no 'id' field — intentionally excluded from response

@app.get("/allbooks")
async def read_all_books() -> list[BookResponse]:
    return [
        {"id": 1, "title": "1984", "author": "George Orwell"},      # id filtered out
        {"id": 2, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    ]
```

**Why use `response_model`?**
- Strips fields not in the model (e.g. passwords, internal IDs)
- Powers OpenAPI schema documentation
- Enables serialization validation

---

## ⚠️ Custom Exception Handlers

```python
import json
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.responses import JSONResponse

app = FastAPI()

# Override the default HTTPException handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": "Oops! Something went wrong"},
    )

# Override validation error handler — return plain text with details
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return PlainTextResponse(
        f"Validation error:\n{json.dumps(exc.errors(), indent=2)}",
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.get("/error_endpoint")
async def raise_exception():
    raise HTTPException(status_code=400)
```

---

## 🔑 Key Takeaways

- `@app.get/post/put/delete/patch` decorators define routes; type annotations do the validation
- `APIRouter` = modular routing; use `prefix` and `tags` to organize
- `Field(...)` constrains Pydantic fields at both validation and schema-doc level
- `response_model` (or `-> ReturnType`) filters output and powers OpenAPI
- Override `@app.exception_handler(ExcType)` to customize error responses globally
- FastAPI generates `/docs` (Swagger) and `/redoc` automatically — no extra work
