# 🔴 Python — Senior Interview Questions

---

## 1. How does Python's import system work? What is `sys.modules`?

**A:** When you `import foo`:
1. Python checks `sys.modules` — if found, returns the cached module (no re-execution)
2. Searches `sys.path` for `foo.py` or `foo/__init__.py`
3. Compiles to bytecode (`.pyc` in `__pycache__`)
4. Executes the module code, populates `sys.modules["foo"]`

```python
import sys

# Already imported?
"os" in sys.modules  # True after `import os`

# Force re-import
import importlib
importlib.reload(mymodule)

# Import hook — custom importer
class MyFinder:
    def find_spec(self, fullname, path, target=None): ...

sys.meta_path.append(MyFinder())
```

**Circular imports:** Happen when A imports B and B imports A. Fix by deferring imports inside functions or restructuring.

---

## 2. Explain Python descriptors.

**A:** A descriptor is any object defining `__get__`, `__set__`, or `__delete__`. They power `property`, `staticmethod`, `classmethod`, and ORM fields:

```python
class Validator:
    def __set_name__(self, owner, name):
        self.name = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # class-level access returns descriptor
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{self.name} must be a non-negative int")
        setattr(obj, self.private, value)

class Product:
    quantity = Validator()  # descriptor instance at class level
    price = Validator()

p = Product()
p.quantity = 5    # calls __set__
p.quantity        # calls __get__
```

---

## 3. What is `__slots__` and when does it help?

**A:** By default, Python objects store attributes in a `__dict__` (a dict per instance — expensive). `__slots__` replaces the dict with a fixed set of slots:

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

import sys
sys.getsizeof(Point(1, 2))  # ~56 bytes vs ~184 bytes without slots
```

**Benefits:** ~3x memory reduction per instance, slightly faster attribute access.

**Trade-offs:** Cannot add arbitrary attributes; can't use `__dict__`; complicates multiple inheritance with slots.

**Use when:** Creating millions of small instances (parsing, data pipelines, coordinate systems).

---

## 4. How do you profile and optimize Python code?

**A:**

```python
# cProfile — call-level profiling
import cProfile
cProfile.run("main()", sort="cumulative")

# or from command line
python -m cProfile -s cumulative script.py

# line_profiler — line-by-line (pip install line_profiler)
@profile
def hot_function():
    ...
kernprof -l -v script.py

# memory_profiler
@profile
def memory_heavy():
    ...

# timeit — micro-benchmarks
import timeit
timeit.timeit("'-'.join(str(n) for n in range(100))", number=10000)
```

**Optimization strategies (in order):**
1. Algorithmic improvement (O(n²) → O(n log n))
2. Use built-ins (`sum`, `sorted`, `map`) — implemented in C
3. Avoid Python loops on large data → NumPy vectorization
4. Use `__slots__` for high-volume objects
5. Caching with `functools.lru_cache`
6. Move hot code to Cython/C extension

---

## 5. How does Python's `asyncio` event loop work internally?

**A:** The event loop is a single-threaded I/O multiplexer:

1. Maintains a queue of ready callbacks (coroutines to resume)
2. On each tick: runs all ready callbacks
3. Calls OS `select`/`epoll`/`kqueue` for I/O readiness — collects ready FDs
4. Schedules callbacks for coroutines awaiting those FDs
5. Repeat

```python
import asyncio

loop = asyncio.get_event_loop()

# Low-level — add callback to the loop
loop.call_soon(callback)
loop.call_later(delay, callback)

# Schedule coroutine
loop.create_task(coro())

# Inspect running tasks
asyncio.all_tasks()
asyncio.current_task()
```

**Key insight:** `await` doesn't block the thread — it suspends the coroutine and lets the event loop run other coroutines. The OS does the actual waiting.

---

## 6. What is `multiprocessing` and when do you use it vs `threading` vs `asyncio`?

**A:**

| | `threading` | `asyncio` | `multiprocessing` |
|--|------------|-----------|------------------|
| GIL | Subject to | Subject to | Bypasses (separate process) |
| I/O-bound | ✅ | ✅ (preferred) | Overkill |
| CPU-bound | ❌ | ❌ | ✅ |
| Memory | Shared | Shared | Separate (IPC needed) |
| Overhead | Low | Very low | High (process spawn) |

```python
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor

# ProcessPoolExecutor (recommended)
with ProcessPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(cpu_heavy, data_chunks))

# Shared memory (Python 3.8+)
from multiprocessing.shared_memory import SharedMemory
shm = SharedMemory(create=True, size=1024)
```

---

## 7. How does Django handle database connection pooling?

**A:** Django does **not** provide connection pooling natively — it creates one connection per thread/coroutine.

**Solutions:**

1. **PgBouncer** (recommended for Postgres) — external pooler at the DB layer:
   - Transaction mode: best throughput for Django
   - Session mode: compatible with all features

2. **django-db-connection-pool** — `SQLAlchemy`-backed pool:
```python
DATABASES = {
    "default": {
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "POOL_OPTIONS": {
            "POOL_SIZE": 10,
            "MAX_OVERFLOW": 20,
            "RECYCLE": 300,
        }
    }
}
```

3. For async Django (ASGI): use `databases` library or `django-async-orm`.

---

## 8. How do you handle long-running tasks in a Django/Python web app?

**A:** Offload to a task queue — never block the web worker:

**Celery + Redis/RabbitMQ:**
```python
# tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        send_email(user.email)
    except Exception as exc:
        raise self.retry(exc=exc)

# In view
send_email_task.delay(user.id)  # enqueue, return immediately
```

**Monitoring:** Flower for Celery, or use Django Q, Huey for lighter alternatives.

**Redis Streams** for high-throughput event processing without Celery overhead.

---

## 9. How do you implement caching in Django and what are the invalidation strategies?

**A:**

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Low-level cache API
from django.core.cache import cache

cache.set("user:42", user_data, timeout=300)
data = cache.get("user:42")
cache.delete("user:42")
cache.get_many(["user:1", "user:2"])

# Per-view caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def my_view(request): ...

# Template fragment caching
{% load cache %}
{% cache 500 sidebar user.id %}
    ... expensive template fragment ...
{% endcache %}
```

**Invalidation strategies:**
- **TTL-based** — simplest, eventual consistency
- **Cache-aside + explicit invalidation** — `cache.delete("user:42")` on write
- **Write-through** — update cache on every write (strong consistency)
- **Event-driven** — Django signals → invalidate on model save/delete

---

## 10. Explain Python's metaclasses.

**A:** A metaclass is the "class of a class" — controls how classes are created:

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connected = False

db1 = Database()
db2 = Database()
assert db1 is db2  # True
```

**Common uses:** ORMs (Django models), API frameworks (DRF serializers), singleton enforcement, interface checking.

```python
# Django's Model metaclass registers every subclass
class ModelBase(type):
    def __new__(cls, name, bases, namespace):
        new_cls = super().__new__(cls, name, bases, namespace)
        # register in app registry, set up fields, etc.
        return new_cls
```

---

## 11. How do you secure a Django application?

**A:** Django's built-in security checklist + hardening:

```python
# settings.py — production hardening
DEBUG = False
SECRET_KEY = env("SECRET_KEY")  # never hardcode
ALLOWED_HOSTS = ["api.example.com"]

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Headers
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

**Code-level:**
- Use parameterized queries (ORM) — never raw `f"SELECT ... {user_input}"`
- Validate all input — `ModelForm`, DRF `Serializer`
- Rate-limit auth endpoints — `django-ratelimit`
- Keep dependencies updated — `safety check`
- Audit with `bandit`: `bandit -r myapp/`

---

## 12. How do you implement a custom Django middleware?

**A:**
```python
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # called once at startup

    def __call__(self, request):
        start = time.perf_counter()

        response = self.get_response(request)  # call next middleware/view

        duration = time.perf_counter() - start
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
        response["X-Request-Duration-Ms"] = str(round(duration * 1000, 2))
        return response

# settings.py
MIDDLEWARE = [
    "myapp.middleware.RequestTimingMiddleware",
    ...
]
```

---

## 13. What is `__new__` vs `__init__`?

**A:**
- `__new__` — creates the object (allocates memory, returns the instance)
- `__init__` — initializes the already-created object

```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        print("Creating instance")
        instance = super().__new__(cls)
        return instance

    def __init__(self, value):
        print("Initializing instance")
        self.value = value
```

**Use `__new__` for:**
- Singleton pattern
- Immutable types (subclassing `int`, `str`, `tuple`)
- Custom metaclass behavior

```python
class PositiveInt(int):
    def __new__(cls, value):
        if value <= 0:
            raise ValueError("Must be positive")
        return super().__new__(cls, value)
```

---

## 14. How do you write production-grade logging in Python?

**A:**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "trace_id": getattr(record, "trace_id", None),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger(__name__)

# Usage with context
logger.info("Order created", extra={"trace_id": trace_id, "order_id": order.id})
```

Use `structlog` for more ergonomic structured logging in Python.

---

## 15. What is `__future__` and what are common uses?

**A:** `from __future__ import` enables features from future Python versions (backports):

```python
from __future__ import annotations  # PEP 563: postponed evaluation of annotations

# Allows forward references in type hints without quotes
class Node:
    def __init__(self, next: Node | None = None):  # "Node" before it's defined
        self.next = next
```

**Common imports:**
- `annotations` — postponed annotation evaluation (default in Python 3.10+)
- `print_function` — Python 3 print in Python 2 (historical)
- `division` — true division in Python 2 (historical)

`from __future__ import annotations` is the only one still actively relevant in modern Python for clean generic type hints with self-references.
