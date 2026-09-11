# 🟡 Python — Mid-Level Interview Questions

---

## 1. What are decorators and how do they work?

**A:** A decorator is a function that wraps another function to add behavior:

```python
import functools
import time

def timer(func):
    @functools.wraps(func)  # preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

slow_function()  # slow_function took 1.0001s
```

Decorators with arguments need an extra layer:

```python
def retry(times=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorator

@retry(times=5)
def flaky_call(): ...
```

---

## 2. What are generators and `yield`?

**A:** A generator is a function that uses `yield` to produce values lazily — one at a time, without loading all into memory:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

gen = fibonacci()
next(gen)  # 0
next(gen)  # 1
next(gen)  # 1

# Generator expression (like list comprehension but lazy)
squares = (x ** 2 for x in range(1_000_000))  # no memory allocated
```

Use generators for: large datasets, infinite sequences, streaming data processing.

---

## 3. What is `async`/`await` in Python?

**A:** Python's `asyncio` provides cooperative concurrency (single thread, event loop):

```python
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)  # concurrent I/O

asyncio.run(main())
```

`async`/`await` is **concurrency, not parallelism** — the GIL is still held; ideal for I/O-bound work. For CPU-bound, use `multiprocessing` or `ProcessPoolExecutor`.

---

## 4. What is the GIL (Global Interpreter Lock)?

**A:** The GIL is a mutex in CPython that ensures only one thread executes Python bytecode at a time.

**Implications:**
- **Threading is NOT parallel for CPU-bound work** — threads take turns, not truly simultaneous
- **Threading IS fine for I/O-bound work** — GIL is released during I/O waits
- **`asyncio`** — single-threaded, no GIL concern
- **`multiprocessing`** — separate processes, separate GILs → true parallelism

```python
# CPU-bound — use multiprocessing
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as ex:
    results = list(ex.map(cpu_heavy_fn, data))

# I/O-bound — threading or asyncio work fine
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(fetch_url, urls))
```

---

## 5. What are Python's `*args` and `**kwargs` in depth?

**A:**
```python
def func(pos_only, /, normal, *, kw_only, **kwargs):
    pass

# pos_only: positional ONLY (before /)
# normal: positional or keyword
# kw_only: keyword ONLY (after *)
# kwargs: any remaining keyword args

# Unpacking at call site
args = [1, 2, 3]
func(*args)        # unpack list as positional

kwargs = {"x": 1}
func(**kwargs)     # unpack dict as keyword args
```

---

## 6. How does Python's memory management work?

**A:**
- CPython uses **reference counting** as the primary mechanism — when `refcount == 0`, memory is freed immediately
- A **cyclic garbage collector** handles reference cycles (`gc` module)
- **Memory pools** (`pymalloc`) manage small object allocation efficiently

```python
import sys
x = []
sys.getrefcount(x)  # usually 2 (x + getrefcount's arg)

import gc
gc.collect()  # force cyclic GC
gc.disable()  # disable for performance-critical sections
```

**Implications:**
- `del x` decrements refcount; doesn't guarantee immediate deallocation
- Circular references are eventually collected but can cause memory to linger

---

## 7. What is a context manager and how do you write one?

**A:** Context managers manage setup/teardown via `with`:

```python
# Class-based
class ManagedResource:
    def __enter__(self):
        print("acquire")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("release")
        return False  # False = don't suppress exceptions

with ManagedResource() as r:
    pass  # acquire → use → release

# Function-based with contextlib
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.perf_counter()
    yield
    print(f"elapsed: {time.perf_counter() - start:.4f}s")

with timer():
    do_work()
```

---

## 8. What are Python's `__dunder__` methods?

**A:** Special methods that Python calls implicitly:

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):      # repr(v)
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):  # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self):       # len(v)
        return 2

    def __eq__(self, other): # v1 == v2
        return self.x == other.x and self.y == other.y

    def __hash__(self):      # hash(v) — needed if __eq__ defined
        return hash((self.x, self.y))
```

---

## 9. What is `dataclass` and when should you use it?

**A:** `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__` from field declarations:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)   # immutable
class Point:
    x: float
    y: float
    z: float = 0.0
    tags: list = field(default_factory=list)  # mutable default

p = Point(1.0, 2.0)
print(p)   # Point(x=1.0, y=2.0, z=0.0, tags=[])
```

Use when you need a simple data container without writing boilerplate. For richer validation, consider `pydantic`.

---

## 10. What is the difference between `staticmethod`, `classmethod`, and instance methods?

**A:**
```python
class Dog:
    species = "Canis lupus"

    def __init__(self, name):
        self.name = name

    def bark(self):               # instance method — receives instance
        return f"{self.name} barks"

    @classmethod
    def create(cls, name):        # class method — receives class
        return cls(name)

    @staticmethod
    def is_valid_name(name):      # static — no implicit first arg
        return isinstance(name, str) and len(name) > 0

Dog.create("Rex")       # classmethod — works with subclasses
Dog.is_valid_name("Rex") # staticmethod
```

---

## 11. What are Python's `property` descriptors?

**A:**
```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float):
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32

t = Temperature(100)
t.celsius = 200         # calls setter
print(t.fahrenheit)     # 392.0
```

---

## 12. How do you write unit tests in Python?

**A:**
```python
# test_math.py
import pytest

def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# Mocking
from unittest.mock import MagicMock, patch

def test_service():
    with patch("mymodule.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = my_service.fetch()
        assert result["status"] == "ok"
```

```bash
pytest tests/ -v --cov=mymodule --cov-report=term
```

---

## 13. What is `functools.lru_cache` and when do you use it?

**A:** Memoization decorator — caches the results of expensive function calls:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

fib(50)   # fast — cached recursive calls
fib.cache_info()   # CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)
fib.cache_clear()  # invalidate
```

`@cache` (Python 3.9+) is equivalent to `@lru_cache(maxsize=None)`.

---

## 14. What is type hinting and why does it matter?

**A:** Type hints (PEP 484) annotate function signatures and variables for static analysis:

```python
from typing import Optional, Union, TypeVar

def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

def find_user(id: int) -> Optional[dict]:
    ...

T = TypeVar("T")
def first(items: list[T]) -> T:
    return items[0]
```

Type hints are **not enforced at runtime** — use `mypy` or `pyright` for static checking:
```bash
mypy mymodule.py --strict
```

Benefits: IDE autocompletion, early bug detection, living documentation.

---

## 15. What is Django's ORM and how does queryset laziness work?

**A:** Django's ORM maps Python classes to DB tables:

```python
# QuerySets are lazy — no SQL until evaluated
users = User.objects.filter(is_active=True).order_by("name")
# ↑ No SQL yet

for u in users:   # SQL executed HERE
    print(u.name)

# Force evaluation
user_list = list(users)   # executes SQL
count = users.count()     # SELECT COUNT(*)

# select_related — JOIN for ForeignKey (avoids N+1)
posts = Post.objects.select_related("author").filter(published=True)

# prefetch_related — separate query for M2M/reverse FK
posts = Post.objects.prefetch_related("tags").all()
```

Always use `select_related`/`prefetch_related` when accessing related objects in a loop to avoid the N+1 query problem.

---

## 16. What is `functools.wraps` and why is it important?

**A:** Without `@functools.wraps`, a decorator replaces the wrapped function's metadata (`__name__`, `__doc__`, etc.):

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # preserves original metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greet someone."""
    return f"Hello, {name}"

print(greet.__name__)  # "greet" (not "wrapper")
print(greet.__doc__)   # "Greet someone."
```

Especially important when using multiple decorators or tools that inspect function metadata (pytest, Sphinx, FastAPI).

---

## 17. What is `__enter__` and `__exit__` — how do context managers suppress exceptions?

**A:**
```python
class SuppressError:
    def __init__(self, *exc_types):
        self.exc_types = exc_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.exc_types):
            return True  # True = suppress the exception
        return False     # False = let it propagate

with SuppressError(ValueError):
    int("bad")  # ValueError is swallowed
print("continues here")
```

`contextlib.suppress` does exactly this in the standard library.

---

## 18. What is `asyncio.gather` vs `asyncio.wait`?

**A:**
```python
# gather — run coroutines concurrently, return results in ORDER
results = await asyncio.gather(
    fetch(url1),
    fetch(url2),
    fetch(url3),
    return_exceptions=True  # exceptions returned, not raised
)

# wait — more control: returns sets of done/pending tasks
tasks = [asyncio.create_task(fetch(u)) for u in urls]
done, pending = await asyncio.wait(tasks, timeout=5.0)
for task in pending:
    task.cancel()
```

Use `gather` for the common case. Use `wait` when you need `FIRST_COMPLETED`, `FIRST_EXCEPTION`, or fine-grained timeout handling.

---

## 19. What is `__repr__` vs `__str__`?

**A:**
- `__str__` — human-readable, called by `str()` and `print()`
- `__repr__` — unambiguous, developer-facing, called by `repr()` and in the REPL; should ideally be eval-able

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"  # Point(1, 2)

    def __str__(self):
        return f"({self.x}, {self.y})"             # (1, 2)

p = Point(1, 2)
repr(p)  # "Point(1, 2)"
str(p)   # "(1, 2)"
print(p) # "(1, 2)" — uses __str__
```

If you only implement one, implement `__repr__` — it serves as a fallback for `__str__`.

---

## 20. How does Django's middleware stack work?

**A:** Middleware is a chain of hooks applied to every request/response:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "myapp.middleware.TimingMiddleware",
    ...
]
```

**Order matters:** Request flows top → bottom, response flows bottom → top.

```
Request  → SecurityMiddleware → SessionMiddleware → TimingMiddleware → View
Response ← SecurityMiddleware ← SessionMiddleware ← TimingMiddleware ← View
```

```python
class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code here runs before the view
        response = self.get_response(request)
        # Code here runs after the view
        return response
```

---

## 21. What is `@cached_property`?

**A:** `cached_property` computes a property once and caches the result on the instance:

```python
from functools import cached_property

class DataSet:
    def __init__(self, data):
        self.data = data

    @cached_property
    def median(self):
        print("computing...")
        return sorted(self.data)[len(self.data) // 2]

ds = DataSet([5, 1, 3, 2, 4])
ds.median  # "computing..." → 3
ds.median  # 3 (no recomputation)
```

Cached in `instance.__dict__` — setting the attribute invalidates the cache.

---

## 22. What are `typing.Protocol` and structural subtyping?

**A:** `Protocol` enables structural typing (duck typing + static analysis) without inheritance:

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # OK — Circle satisfies Drawable structurally
render(Square())  # OK — no inheritance needed
```

`mypy` enforces this at type-check time. Similar to Go's implicit interfaces.

---

## 23. What is `itertools` and what are its most useful functions?

**A:**
```python
import itertools

# chain — flatten multiple iterables
list(itertools.chain([1,2], [3,4], [5])) # [1,2,3,4,5]

# product — cartesian product
list(itertools.product([1,2], ["a","b"])) # [(1,'a'),(1,'b'),(2,'a'),(2,'b')]

# groupby — group consecutive items (sort first!)
data = sorted([("a",1),("b",2),("a",3)], key=lambda x: x[0])
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(key, list(group))

# islice — lazy slice of iterator
first_10 = list(itertools.islice(infinite_gen(), 10))

# batched (Python 3.12+)
list(itertools.batched([1,2,3,4,5], 2)) # [(1,2),(3,4),(5,)]
```

---

## 24. How do you implement retry logic in Python?

**A:**
```python
import time
import functools

def retry(times=3, delay=1.0, backoff=2.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times - 1:
                        raise
                    time.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator

@retry(times=5, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def call_external_api():
    ...
```

Or use `tenacity` library for production-grade retry with jitter.

---

## 25. What is `abc.ABC` and abstract base classes?

**A:**
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self):  # concrete method shared by all
        return f"Area: {self.area():.2f}"

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius

# Shape() — TypeError: Can't instantiate abstract class
c = Circle(5)  # OK
```

---

## 26. What is `Pydantic` and why is it used?

**A:** Pydantic provides runtime data validation using Python type annotations:

```python
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    created_at: datetime = datetime.utcnow()

    @validator("age")
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("age must be positive")
        return v

# Automatic parsing + validation
user = UserCreate(name="Alice", email="alice@example.com", age=30)

# Invalid data raises ValidationError with field-level details
try:
    UserCreate(name="Bob", email="not-an-email", age=-5)
except ValueError as e:
    print(e)
```

Backbone of FastAPI. Also used for config management, ETL validation, and CLI tools.

---

## 27. What is Django's `select_for_update`?

**A:** `select_for_update()` adds `SELECT ... FOR UPDATE` — a pessimistic row lock preventing concurrent modifications:

```python
from django.db import transaction

@transaction.atomic
def transfer(from_id, to_id, amount):
    # Lock both rows for the duration of the transaction
    accounts = Account.objects.select_for_update().filter(id__in=[from_id, to_id])
    from_acc = next(a for a in accounts if a.id == from_id)
    to_acc   = next(a for a in accounts if a.id == to_id)

    if from_acc.balance < amount:
        raise ValueError("Insufficient funds")

    from_acc.balance -= amount
    to_acc.balance += amount
    Account.objects.bulk_update([from_acc, to_acc], ["balance"])
```

Without this, two concurrent transfers could read the same balance and cause a race condition.

---

## 28. What is `__init_subclass__` and when is it useful?

**A:** Called on a base class whenever it is subclassed — useful for registering subclasses without a metaclass:

```python
class Plugin:
    _registry = {}

    def __init_subclass__(cls, plugin_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_name:
            Plugin._registry[plugin_name] = cls

class JSONPlugin(Plugin, plugin_name="json"):
    def process(self, data): ...

class CSVPlugin(Plugin, plugin_name="csv"):
    def process(self, data): ...

Plugin._registry["json"]  # JSONPlugin
```

Cleaner than metaclasses for simple registration patterns.

---

## 29. What is `dataclasses.field` and `__post_init__`?

**A:**
```python
from dataclasses import dataclass, field

@dataclass
class Order:
    customer_id: str
    items: list = field(default_factory=list)  # mutable default — MUST use field()
    total: float = field(init=False)            # excluded from __init__
    _internal: str = field(default="x", repr=False, compare=False)

    def __post_init__(self):
        # Runs after __init__ — for derived fields and validation
        self.total = sum(item.price for item in self.items)
        if not self.customer_id:
            raise ValueError("customer_id required")
```

---

## 30. How does `logging` configuration work in production Python apps?

**A:**
```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.db.backends": {"level": "WARNING"},  # suppress SQL logs
        "myapp": {"level": "DEBUG"},
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info("App started", extra={"version": "1.2.3"})
```
