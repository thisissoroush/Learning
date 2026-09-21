# Chapter 8 — Dependency Injection and Middleware

> **Project:** `trip_platform`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter08)

---

## 🎯 What This Chapter Covers

Advanced dependency injection patterns, background tasks, rate limiting with SlowAPI, internationalization (i18n), application profiling, and a custom client info middleware.

---

## 🔗 Advanced Dependency Injection

### Simple Dependencies

```python
from fastapi import Depends
from datetime import date

def time_range(start: date, end: date | None = None):
    return start, end

@app.get("/v1/trips")
def get_trips(time_range: Annotated[time_range, Depends()]):
    start, end = time_range
    message = f"Request trips from {start}"
    if end:
        return f"{message} to {end}"
    return message
```

### Chainable Dependencies

```python
def select_category(category: str):
    allowed = ["beach", "mountain", "city", "countryside"]
    if category not in allowed:
        raise HTTPException(status_code=400, detail=f"Category must be one of {allowed}")
    return category

def check_coupon_validity(coupon_code: str | None = None):
    valid_coupons = {"SUMMER20", "WINTER10"}
    return coupon_code in valid_coupons

@app.get("/v2/trips/{category}")
def get_trips_by_category(
    background_tasks: BackgroundTasks,
    category: Annotated[str, Depends(select_category)],
    discount_applicable: Annotated[bool, Depends(check_coupon_validity)],
):
    message = f"You requested {category.replace('-', ' ').title()} trips."
    if discount_applicable:
        message += "\n. The coupon code is valid! You will get a discount!"

    background_tasks.add_task(store_query_to_external_db, message)
    logger.info("Query sent to background task, end of request.")
    return message
```

### Class-Based Dependencies (CommonQueryParams)

```python
class CommonQueryParams:
    """Groups multiple query params into one injectable object."""
    def __init__(
        self,
        start: date,
        end: date | None = None,
        category: str = Depends(select_category),
        applicable_discount: bool = Depends(check_coupon_validity),
    ):
        self.start = start
        self.end = end
        self.category = category
        self.applicable_discount = applicable_discount

@app.get("/v3/trips/{category}")
def get_trips_by_category_v3(
    common_params: Annotated[CommonQueryParams, Depends()],
):
    start = common_params.start
    category = common_params.category.replace("-", " ").title()
    message = f"You requested {category} trips from {start}"
    if common_params.end:
        message += f" to {common_params.end}"
    if common_params.applicable_discount:
        message += "\n. Discount applied!"
    return message
```

---

## ⏳ Background Tasks

```python
from fastapi import BackgroundTasks

async def store_query_to_external_db(message: str):
    """Runs AFTER the response is sent to the client."""
    await asyncio.sleep(1)   # simulate slow external write
    logger.info(f"Stored to external DB: {message}")

@app.get("/v2/trips/{category}")
def get_trips_by_category(
    background_tasks: BackgroundTasks,
    category: str,
):
    # This returns immediately; store_query_to_external_db runs after response
    background_tasks.add_task(store_query_to_external_db, f"Trips to {category}")
    return {"message": f"Trips to {category} requested"}
```

**When to use `BackgroundTasks`:**
- Sending emails after registration
- Writing audit logs
- Updating caches
- Webhooks/notifications
- NOT for heavy CPU work — use Celery/worker queues for that

---

## 🚦 Rate Limiting with SlowAPI

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.get("/v1/trips")
@limiter.limit("5/minute")     # 5 requests per minute per IP
def get_trips(request: Request):   # Request param required for SlowAPI
    return {"trips": [...]}

@app.get("/search")
@limiter.limit("10/minute;100/hour")   # multiple limits
def search(request: Request, q: str):
    return {"results": [...]}
```

---

## 🌍 Internationalization (i18n)

```python
from fastapi import APIRouter, Header

router = APIRouter()

TRANSLATIONS = {
    "en": {"welcome": "Welcome!", "error": "An error occurred"},
    "fr": {"welcome": "Bienvenue!", "error": "Une erreur s'est produite"},
    "es": {"welcome": "¡Bienvenido!", "error": "Ocurrió un error"},
}

@router.get("/welcome")
def welcome(accept_language: str | None = Header(default="en")):
    lang = accept_language.split(",")[0].split("-")[0].lower()
    messages = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return {"message": messages["welcome"]}
```

---

## 📊 Profiling with Custom Router

```python
from fastapi import APIRouter
import cProfile
import pstats
import io

router = APIRouter(prefix="/profiler")

@router.get("/profile/{n}")
def profile_endpoint(n: int):
    profiler = cProfile.Profile()
    profiler.enable()

    # Run the code to profile
    result = [i**2 for i in range(n)]

    profiler.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(10)
    return {"profile": stream.getvalue(), "result_len": len(result)}
```

---

## 🔑 Key Takeaways

- `Depends()` on class `__init__` params creates class-based dependencies — group related params together
- Chain dependencies: `CommonQueryParams` depends on `select_category` which depends on nothing — composes cleanly
- `BackgroundTasks.add_task(fn, *args)` runs after response is sent — no blocking the client
- SlowAPI needs `request: Request` as an endpoint parameter to identify the caller's IP
- Rate limit strings: `"5/minute"`, `"100/hour"`, `"1000/day"` — multiple with semicolon
- `Accept-Language` header is the standard way to detect client locale
- Profiling router: mount it only in dev/staging, not production
