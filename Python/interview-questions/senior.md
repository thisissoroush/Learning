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

---

## 16. What is `__class_getitem__` and how does it enable generic classes?

**A:** `__class_getitem__` is called when you use subscript syntax on a class (`MyClass[T]`). It enables generic-style annotations:

```python
class Stack:
    def __class_getitem__(cls, item):
        return type(f"Stack[{item.__name__}]", (cls,), {})

    def __init__(self):
        self._items = []

    def push(self, item): self._items.append(item)
    def pop(self): return self._items.pop()

# With typing.Generic (the real approach)
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

s: Stack[int] = Stack()
s.push(42)
```

---

## 17. How do you trace memory leaks in a Python process?

**A:**

```python
import tracemalloc

tracemalloc.start()

# ... run the code under investigation ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)

# Compare two snapshots
snap1 = tracemalloc.take_snapshot()
# ... more work ...
snap2 = tracemalloc.take_snapshot()
for stat in snap2.compare_to(snap1, "lineno")[:10]:
    print(stat)
```

Also useful:
- `objgraph` — find objects that aren't being collected
- `memory_profiler` — line-by-line memory usage
- `gc.get_referrers(obj)` — find what's holding a reference

---

## 18. How does CPython implement dictionaries internally?

**A:** CPython's `dict` is a **hash table** with open addressing:

- Each key is hashed; `hash(key) % capacity` gives the slot index
- **Collision resolution:** Linear probing with perturbation (pseudo-random walk through slots)
- **Load factor:** Resizes (doubles) when ~2/3 full
- **Compact (Python 3.6+):** Indices array + separate entries array — preserves insertion order while keeping hash lookup fast

```python
# Order is guaranteed in Python 3.7+
d = {"c": 3, "a": 1, "b": 2}
list(d.keys())  # ["c", "a", "b"] — insertion order

# Hash collisions are handled internally
hash("key1") % 8  # might collide with hash("key2") % 8
```

Key property: average O(1) lookup, O(n) worst case (all keys hash to same slot — rare with good hash functions).

---

## 19. What is `__set_name__` and how does it simplify descriptors?

**A:** `__set_name__` is called on a descriptor when the class body is processed — it receives the owner class and the attribute name:

```python
class TypedField:
    def __set_name__(self, owner, name):
        self.name = name
        self._attr = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self._attr, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} must be {self.expected_type.__name__}")
        setattr(obj, self._attr, value)

class IntField(TypedField):
    expected_type = int

class Product:
    price = IntField()    # __set_name__ called here: name="price"
    quantity = IntField() # name="quantity"

p = Product()
p.price = 100    # OK
p.price = "100"  # TypeError: price must be int
```

---

## 20. What is `__init_subclass__` vs metaclass — when do you use each?

**A:**

| | `__init_subclass__` | Metaclass |
|--|--------------------|-----------| 
| Complexity | Simple | Complex |
| Use case | Register subclasses, set class attributes | Control class creation, add methods, wrap all methods |
| Python version | 3.6+ | Always |
| Inherits | Yes, automatically | Only if metaclass is inherited |

```python
# Use __init_subclass__ for simple registration
class Handler(ABC):
    _handlers = {}
    def __init_subclass__(cls, route: str = None, **kw):
        super().__init_subclass__(**kw)
        if route: Handler._handlers[route] = cls

class HomeHandler(Handler, route="/"):
    def handle(self, request): ...

# Use metaclass when you need to transform ALL methods
class LoggingMeta(type):
    def __new__(mcs, name, bases, namespace):
        for key, val in namespace.items():
            if callable(val) and not key.startswith("_"):
                namespace[key] = log_calls(val)
        return super().__new__(mcs, name, bases, namespace)
```

---

## 21. How do you implement connection pooling in Python without a framework?

**A:**

```python
import queue
import threading
import psycopg2
from contextlib import contextmanager

class ConnectionPool:
    def __init__(self, dsn: str, size: int = 10):
        self._pool = queue.Queue(maxsize=size)
        for _ in range(size):
            self._pool.put(psycopg2.connect(dsn))

    @contextmanager
    def get(self, timeout: float = 5.0):
        conn = self._pool.get(timeout=timeout)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.put(conn)

pool = ConnectionPool("postgresql://user:pass@localhost/db", size=20)

with pool.get() as conn:
    cur = conn.cursor()
    cur.execute("SELECT 1")
```

In production, prefer `psycopg3` (built-in pooling), `asyncpg`, or SQLAlchemy's pool.

---

## 22. How does `ctypes` work and when would you use it?

**A:** `ctypes` calls functions in shared C libraries without writing C extension code:

```python
import ctypes

# Load shared library
libc = ctypes.CDLL("libc.so.6")

# Call C function
libc.printf(b"Hello from C: %d\n", ctypes.c_int(42))

# Work with C structs
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

p = Point(1.0, 2.0)
print(p.x, p.y)

# Load custom shared library
mylib = ctypes.CDLL("./mylib.so")
mylib.add.argtypes = [ctypes.c_int, ctypes.c_int]
mylib.add.restype = ctypes.c_int
result = mylib.add(3, 4)  # 7
```

Use for: calling OS APIs, wrapping C libraries without cgo-equivalent compilation, performance-critical low-level code.

---

## 23. What is `__fspath__` and the `os.PathLike` protocol?

**A:** `os.PathLike` is the protocol for path-like objects — anything implementing `__fspath__` that returns a string or bytes path:

```python
import os
from pathlib import Path

class MyPath:
    def __init__(self, path: str):
        self._path = path

    def __fspath__(self) -> str:
        return self._path

p = MyPath("/tmp/file.txt")
os.path.exists(p)   # works — os functions accept PathLike
open(p)             # works
Path(p)             # works

# Check compliance
isinstance(p, os.PathLike)  # True
os.fspath(p)                # "/tmp/file.txt"
```

---

## 24. How do you implement a plugin system in Python?

**A:**

**Entry points (setuptools — the standard approach):**

```python
# In plugin package's pyproject.toml
[project.entry-points."myapp.plugins"]
csv_exporter = "myplugin.exporters:CSVExporter"

# In host app
import importlib.metadata

def load_plugins(group: str) -> dict:
    plugins = {}
    for ep in importlib.metadata.entry_points(group=group):
        plugins[ep.name] = ep.load()
    return plugins

exporters = load_plugins("myapp.plugins")
# {"csv_exporter": <class CSVExporter>}
```

**Alternative: directory scan + import:**
```python
import importlib, pkgutil

for finder, name, _ in pkgutil.iter_modules(["plugins/"]):
    module = importlib.import_module(f"plugins.{name}")
    # __init_subclass__ or registry pattern auto-registers on import
```

---

## 25. What is `sys.settrace` and how is it used?

**A:** `sys.settrace` installs a global trace function called on every line, call, and return — the foundation of debuggers, coverage tools, and profilers:

```python
import sys

def tracer(frame, event, arg):
    if event == "call":
        print(f"Calling {frame.f_code.co_name}")
    elif event == "line":
        print(f"  Line {frame.f_lineno}")
    elif event == "return":
        print(f"  Returning {arg!r}")
    return tracer  # must return itself to continue tracing

sys.settrace(tracer)
# ... code to trace ...
sys.settrace(None)  # stop tracing
```

`coverage.py` uses `sys.settrace` to record which lines execute. The overhead is significant — only enable for debugging/profiling, not in production.

---

## 16. How does Python's `import` system support namespace packages?

**A:** PEP 420 / PEP 402 / PEP 3147 introduced namespace packages — packages without `__init__.py` that can span multiple directories:

```python
# mypackage/ in /path/a/ and mypackage/ in /path/b/
# Both can contribute to the same "mypackage" namespace

# /path/a/mypackage/module_a.py
# /path/b/mypackage/module_b.py

import sys
sys.path.extend(["/path/a", "/path/b"])

from mypackage import module_a  # from /path/a/
from mypackage import module_b  # from /path/b/
```

**Use cases:** Plugin systems where plugins install into the same namespace, distributed package development across repos.

---

## 17. What is `__slots__` with inheritance and what are the pitfalls?

**A:**

```python
class Base:
    __slots__ = ("x",)

class Child(Base):
    __slots__ = ("y",)  # adds y; x inherited from Base

c = Child()
c.x = 1   # OK — from Base's slots
c.y = 2   # OK — from Child's slots

# Pitfall 1: If a parent doesn't define __slots__, child gets __dict__ anyway
class BadBase:
    pass  # no __slots__

class Child2(BadBase):
    __slots__ = ("z",)
# Child2 still has __dict__ from BadBase — slots benefit lost!

# Pitfall 2: Multiple inheritance with overlapping slots is problematic
# Python allows it but wastes memory (duplicate slot descriptors)
```

---

## 18. How does `asyncio` integrate with thread pools for blocking code?

**A:** `asyncio` is single-threaded; blocking calls in a coroutine block the whole event loop. Use `run_in_executor` to offload:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

async def main():
    loop = asyncio.get_event_loop()

    # Run blocking I/O in thread pool
    with ThreadPoolExecutor(max_workers=10) as pool:
        result = await loop.run_in_executor(pool, blocking_file_read, "/large/file")

    # Run CPU-bound work in process pool
    with ProcessPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, cpu_heavy_computation, data)

# asyncio.to_thread (Python 3.9+) — simpler for thread pool
async def main():
    result = await asyncio.to_thread(blocking_file_read, "/large/file")
```

---

## 19. What is `__prepare__` in metaclasses?

**A:** `__prepare__` returns the namespace dict used during class body execution — allows customizing the dict type:

```python
from collections import OrderedDict

class OrderedMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()  # class body uses an OrderedDict

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, dict(namespace))
        cls._field_order = list(namespace.keys())
        return cls

class Model(metaclass=OrderedMeta):
    name = "string"
    age = "integer"
    email = "string"

print(Model._field_order)  # ["name", "age", "email"] — insertion order preserved
```

Used by Python's `Enum` to preserve declaration order, and by some ORMs to track field definition order.

---

## 20. How does Django's signal system work and what are its pitfalls?

**A:**

```python
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if created:
        send_welcome_email.delay(instance.id)

# Custom signals
from django.dispatch import Signal

order_shipped = Signal()

# Emit
order_shipped.send(sender=Order, order=order, tracking_number="1Z...")

# Listen
def on_order_shipped(sender, order, tracking_number, **kwargs):
    notify_customer(order.customer, tracking_number)

order_shipped.connect(on_order_shipped)
```

**Pitfalls:**
- Signals are synchronous — a slow handler blocks the request
- Signals are not transactional — post_save fires even if the outer transaction rolls back; use `transaction.on_commit`
- Hidden coupling — hard to trace which handlers fire for a given event
- Hard to test in isolation

**Better alternatives for complex flows:** Explicit service calls, Celery tasks, or domain events with explicit dispatch.

---

## 21. How does `weakref` work and when should you use it?

**A:** A weak reference doesn't prevent an object from being garbage collected:

```python
import weakref

class Cache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        self._cache[key] = value  # doesn't keep value alive

obj = SomeObject()
cache = Cache()
cache.set("key", obj)

del obj  # obj can now be GC'd
cache.get("key")  # might return None — the object was collected
```

**Use cases:**
- Caches that shouldn't prevent GC (object doesn't need to stay alive just because it's cached)
- Observer patterns where observers shouldn't prevent subjects from being collected
- Circular reference breaking

---

## 22. What is `__missing__` in dict subclasses?

**A:** Called when `__getitem__` is invoked with a key that doesn't exist — the basis for `defaultdict`:

```python
class AutoDict(dict):
    def __missing__(self, key):
        value = self[key] = self._factory(key)
        return value

    def _factory(self, key):
        return f"computed_{key}"

d = AutoDict()
d["x"]  # "computed_x" — computed and cached
d["x"]  # "computed_x" — now in dict, __missing__ not called

# This is how defaultdict works:
from collections import defaultdict
d = defaultdict(list)
d["key"].append(1)  # __missing__ called, list() created
```

---

## 23. How do you use `memoryview` for zero-copy buffer operations?

**A:** `memoryview` exposes the buffer of a bytes-like object without copying:

```python
data = bytearray(b"Hello, World!")

# Slice without copy
view = memoryview(data)
sub = view[7:12]   # memoryview slice — no copy
print(bytes(sub))  # b"World"

# Modify in-place
view[0:5] = b"HELLO"
print(data)  # bytearray(b'HELLO, World!')

# Use with struct for binary protocol parsing
import struct
header = memoryview(data)[0:4]
magic, version = struct.unpack_from("HH", header)
```

Critical for network programming, file I/O, and binary protocol parsing where copying large buffers would be expensive.

---

## 24. How do you write a C extension for Python?

**A:** Using the Python C API:

```c
// mymodule.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* fast_add(PyObject* self, PyObject* args) {
    long a, b;
    if (!PyArg_ParseTuple(args, "ll", &a, &b))
        return NULL;
    return PyLong_FromLong(a + b);
}

static PyMethodDef MyMethods[] = {
    {"fast_add", fast_add, METH_VARARGS, "Add two integers in C"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mymodule = {
    PyModuleDef_HEAD_INIT, "mymodule", NULL, -1, MyMethods
};

PyMODINIT_FUNC PyInit_mymodule(void) {
    return PyModule_Create(&mymodule);
}
```

**Alternatives with less boilerplate:**
- `cffi` — call C from Python without writing C extension glue
- `Cython` — Python-like syntax compiled to C
- `pybind11` — C++ bindings with minimal code
- `mypyc` — compile type-annotated Python to C extension

---

## 25. What is `PEP 695` (Python 3.12) type parameter syntax?

**A:** Python 3.12 introduced cleaner generic type syntax:

```python
# Before 3.12
from typing import TypeVar
T = TypeVar("T")
def first(items: list[T]) -> T:
    return items[0]

# Python 3.12+ — type[T] inline
def first[T](items: list[T]) -> T:
    return items[0]

# Generic class
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Type alias (PEP 695)
type Vector[T] = list[T]
```

This makes Python's generic syntax much closer to other statically-typed languages.
