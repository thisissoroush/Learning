# Chapter 8 — Dependency Injection and Middleware

> **Project:** `trip_platform`

---

## 🎯 What This Chapter Covers

How FastAPI's dependency injection system really works, how to compose dependencies into chains and classes, background tasks for fire-and-forget work, rate limiting, internationalization, and application profiling.

---

## 🧠 Dependency Injection — The Mental Model

`Depends()` is FastAPI's answer to one question: **how do endpoints get the things they need?**

Without DI, every endpoint would manually open DB connections, validate tokens, check permissions, parse common parameters — lots of duplicate code. With DI, you declare what you need and FastAPI assembles it:

```
Endpoint declares:
    db: Session = Depends(get_db)
    user: User = Depends(get_current_user)
    category: str = Depends(validate_category)

FastAPI before calling your endpoint:
    1. calls get_db() → passes session to get_current_user AND your endpoint
    2. calls get_current_user(token, db) → passes User to your endpoint
    3. calls validate_category(category_str) → passes validated str
    4. calls YOUR endpoint with all three resolved values
```

Dependencies are **cached within a request** — if two things depend on `get_db`, it's called once and the same session is shared.

---

## 🔗 Simple Dependencies — Parsing and Validating Common Parameters

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from datetime import date
from typing import Annotated

app = FastAPI()

# A dependency is just a function — FastAPI reads its signature like an endpoint
def parse_date_range(
    start: date,                  # required query param
    end: date | None = None,      # optional query param
) -> tuple[date, date | None]:
    """Parse and validate a date range from query parameters."""
    if end and end < start:
        raise HTTPException(
            status_code=400,
            detail=f"end date ({end}) cannot be before start date ({start})",
        )
    return start, end

# Type alias makes the endpoint signature readable
DateRange = Annotated[tuple[date, date | None], Depends(parse_date_range)]

@app.get("/trips")
def get_trips(date_range: DateRange):
    start, end = date_range
    # GET /trips?start=2024-01-01&end=2024-03-01
    # GET /trips?start=2024-01-01                  (end is optional)
    return {"from": start, "to": end}
```

---

## ⛓️ Chained Dependencies — Validation Layers

Dependencies can depend on other dependencies. FastAPI resolves the whole chain automatically.

```python
ALLOWED_CATEGORIES = {"beach", "mountain", "city", "countryside", "adventure"}

def validate_category(category: str) -> str:
    """Level 1: validate the category string."""
    normalized = category.lower().replace("-", " ")
    if normalized not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown category '{category}'. Choose from: {sorted(ALLOWED_CATEGORIES)}",
        )
    return normalized

def check_coupon(coupon_code: str | None = None) -> bool:
    """Level 1: check if a coupon is valid. Returns True/False, never raises."""
    if not coupon_code:
        return False
    # In production: look up coupon in DB, check expiry, check usage count
    valid_coupons = {"SUMMER20", "WINTER10", "WELCOME50"}
    return coupon_code.upper() in valid_coupons

@app.get("/trips/{category}")
def get_trips_by_category(
    # FastAPI calls validate_category(category) first, passes result here
    category: Annotated[str, Depends(validate_category)],
    # FastAPI calls check_coupon(coupon_code) — coupon_code comes from query param
    has_discount: Annotated[bool, Depends(check_coupon)],
    background_tasks: BackgroundTasks,
):
    message = f"Showing {category} trips"
    if has_discount:
        message += " — 20% discount applied!"

    # Log the search in the background (after response is sent)
    background_tasks.add_task(log_search, category, has_discount)
    return {"message": message}
```

---

## 🏗️ Class-Based Dependencies — Grouping Related Parameters

When an endpoint needs many related parameters, a class keeps things organized and makes them testable.

```python
from fastapi import Depends, Query
from datetime import date
from typing import Annotated

class TripSearchParams:
    """
    Encapsulates all trip search parameters.
    FastAPI reads the __init__ signature exactly like an endpoint signature:
    each parameter becomes a query/path/header param.
    """
    def __init__(
        self,
        start: date,
        end: date | None = None,
        category: str = Depends(validate_category),    # nested dependency!
        has_discount: bool = Depends(check_coupon),    # nested dependency!
        min_price: float | None = Query(None, ge=0),
        max_price: float | None = Query(None, ge=0),
    ):
        self.start = start
        self.end = end
        self.category = category
        self.has_discount = has_discount
        self.min_price = min_price
        self.max_price = max_price

    @property
    def price_range(self) -> tuple[float | None, float | None]:
        return self.min_price, self.max_price


# Clean endpoint signature — all complexity hidden in the class
@app.get("/trips/search/{category}")
def search_trips(
    params: Annotated[TripSearchParams, Depends()],
):
    # GET /trips/search/beach?start=2024-06-01&end=2024-06-15&coupon_code=SUMMER20&max_price=500
    return {
        "category": params.category,
        "date_range": {"start": params.start, "end": params.end},
        "price_range": params.price_range,
        "discount_applied": params.has_discount,
    }
```

---

## ⏳ Background Tasks — Fire and Forget

`BackgroundTasks` lets you run code AFTER the response is sent. The client doesn't wait for it.

```python
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema   # example: send email
import logging

logger = logging.getLogger(__name__)

async def send_confirmation_email(email: str, booking_ref: str):
    """Runs after the response is already sent to the client."""
    # This could take 2-3 seconds — client doesn't wait for it
    logger.info(f"Sending confirmation to {email} for booking {booking_ref}")
    # await mail_client.send(...)
    logger.info(f"Email sent to {email}")

async def log_booking_to_analytics(booking_data: dict):
    """Write to an external analytics service asynchronously."""
    # await analytics_client.track("booking_created", booking_data)
    pass

@app.post("/bookings", status_code=201)
def create_booking(
    trip_id: int,
    user_email: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
):
    # 1. Do the synchronous work (save to DB)
    booking = create_booking_in_db(db, trip_id, user_email)
    booking_ref = f"BOOK-{booking.id}"

    # 2. Queue background work — these run AFTER the response is sent
    background_tasks.add_task(send_confirmation_email, user_email, booking_ref)
    background_tasks.add_task(log_booking_to_analytics, {"trip_id": trip_id})

    # 3. Return immediately — client doesn't wait for email/analytics
    return {"booking_ref": booking_ref, "message": "Booking confirmed"}

# ⚠️ BackgroundTasks limitations:
# - Runs in the same process — if the server crashes, tasks are lost
# - Not suitable for heavy CPU work (blocks the event loop if async, or a thread if sync)
# - For reliability, use Celery + Redis/RabbitMQ as a proper task queue
```

---

## 🚦 Rate Limiting with SlowAPI

Rate limiting prevents one client from overwhelming your API. SlowAPI integrates with FastAPI and tracks requests by IP address (or any custom key).

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from fastapi import Request

# key_func determines WHO is being rate-limited
# get_remote_address = per IP address
# Could also use: lambda req: req.headers.get("X-API-Key") for per-key limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Rate limit formats:
# "5/minute"    — 5 requests per minute per IP
# "100/hour"    — 100 per hour
# "1000/day"    — 1000 per day
# "5/minute;100/hour" — both limits apply

@app.get("/search")
@limiter.limit("10/minute")    # 10 searches per minute per IP
def search_trips(
    request: Request,          # ← REQUIRED by SlowAPI — used to identify the caller
    q: str,
):
    # If the client hits the limit, SlowAPI returns:
    # 429 Too Many Requests
    # {"error": "Rate limit exceeded: 10 per 1 minute"}
    return {"results": perform_search(q)}

@app.post("/bookings")
@limiter.limit("3/minute;20/hour")   # strict limits on writes
def create_booking(request: Request, ...):
    ...

# Exempt certain routes (e.g. health check)
@app.get("/health")
@limiter.exempt
def health_check():
    return {"status": "ok"}
```

---

## 🌍 Internationalization — Reading `Accept-Language`

The `Accept-Language` header tells your API what language the client prefers. Parse it to return localized responses.

```python
from fastapi import Header

TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to TripFinder!",
        "no_trips": "No trips found for your criteria.",
        "booking_confirmed": "Your booking is confirmed.",
    },
    "fr": {
        "welcome": "Bienvenue sur TripFinder!",
        "no_trips": "Aucun voyage trouvé pour vos critères.",
        "booking_confirmed": "Votre réservation est confirmée.",
    },
    "de": {
        "welcome": "Willkommen bei TripFinder!",
        "no_trips": "Keine Reisen für Ihre Kriterien gefunden.",
        "booking_confirmed": "Ihre Buchung ist bestätigt.",
    },
}

def get_language(
    accept_language: str | None = Header(default="en")
) -> str:
    """
    Parse Accept-Language header and return best matching language.
    Header looks like: "fr-FR,fr;q=0.9,en;q=0.8,de;q=0.7"
    We take the first language code and strip the region suffix.
    """
    if not accept_language:
        return "en"
    # Take the first preference, strip the region ("fr-FR" → "fr")
    primary = accept_language.split(",")[0].split(";")[0].strip()
    lang = primary.split("-")[0].lower()
    return lang if lang in TRANSLATIONS else "en"

Lang = Annotated[str, Depends(get_language)]

@app.get("/welcome")
def welcome(lang: Lang):
    messages = TRANSLATIONS[lang]
    return {"message": messages["welcome"], "language": lang}

@app.post("/bookings", status_code=201)
def book_trip(trip_id: int, lang: Lang, ...):
    # ... booking logic ...
    return {"message": TRANSLATIONS[lang]["booking_confirmed"]}
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| Dependencies are cached per request | Two endpoints depending on `get_db` get the SAME session — no duplicate connections |
| Raise `HTTPException` inside a dependency | FastAPI catches it and sends the error response before calling your endpoint |
| Class-based dependencies | Group many query params + nested dependencies — keeps endpoint signatures clean |
| `BackgroundTasks` for post-response work | Client gets fast response; emails/logging happen after — don't block for it |
| `request: Request` in rate-limited endpoints | SlowAPI needs the request object to identify the caller and track counts |
| `Accept-Language: fr-FR,fr;q=0.8,en;q=0.7` | First entry is primary preference — take it, strip region suffix, normalize |
| `@limiter.exempt` | Health checks and status endpoints should never be rate-limited |
