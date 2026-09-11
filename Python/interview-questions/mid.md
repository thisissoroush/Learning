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
