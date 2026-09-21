# Chapter 20 — Concurrent Executors

> *"concurrent.futures provides a high-level API for threads and processes."*

---

## 🎯 Core Concept

`concurrent.futures` unifies thread pools and process pools behind one `Executor` API. Switch between `ThreadPoolExecutor` (I/O-bound) and `ProcessPoolExecutor` (CPU-bound) with minimal code change.

---

## 🌐 Sequential vs. Concurrent Downloads

```python
import time
from pathlib import Path
import httpx

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('downloaded')

def get_flag(base_url: str, cc: str) -> bytes:
    url = f'{base_url}/{cc}/{cc}.gif'
    resp = httpx.get(url, timeout=6.1, follow_redirects=True)
    resp.raise_for_status()
    return resp.content

# Sequential — one at a time
def download_many_sequential(cc_list: list[str]) -> int:
    for cc in sorted(cc_list):
        image = get_flag(BASE_URL, cc)
        (DEST_DIR / f'{cc}.gif').write_bytes(image)
    return len(cc_list)

# Concurrent with ThreadPoolExecutor
from concurrent import futures

def download_many_concurrent(cc_list: list[str]) -> int:
    workers = min(MAX_WORKERS, len(cc_list))
    with futures.ThreadPoolExecutor(workers) as executor:
        results = executor.map(lambda cc: get_flag(BASE_URL, cc), sorted(cc_list))
    return len(list(results))   # raises any exceptions here
```

---

## 🔮 Futures Explained

```python
from concurrent.futures import ThreadPoolExecutor, Future

with ThreadPoolExecutor(max_workers=3) as executor:
    future = executor.submit(get_flag, BASE_URL, 'CN')   # returns immediately
    # future is a Future object — represents a pending result

    print(future.done())    # False — still running
    result = future.result()  # blocks until done
    print(future.done())    # True
    print(result)           # bytes of the flag image

# futures.as_completed — process results as they finish (not submission order)
def download_many_as_completed(cc_list: list[str]) -> int:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        to_do: dict[Future, str] = {}
        for cc in sorted(cc_list):
            future = executor.submit(get_flag, BASE_URL, cc)
            to_do[future] = cc

        for future in futures.as_completed(to_do):
            cc = to_do[future]
            try:
                image = future.result()
                (DEST_DIR / f'{cc}.gif').write_bytes(image)
            except httpx.HTTPError as exc:
                print(f'{cc}: HTTP error {exc.response.status_code}')
    return len(to_do)
```

---

## ⚙️ ProcessPoolExecutor — CPU-Bound Work

```python
from concurrent.futures import ProcessPoolExecutor
import math

def is_prime(n: int) -> bool:
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    root = math.isqrt(n)
    for i in range(3, root + 1, 2):
        if n % i == 0:
            return False
    return True

NUMBERS = [
    9999999999999937,
    9999999999999843,
    9999999999999601,
]

# With processes — true parallelism for CPU-bound work
def check_primes_parallel(numbers: list[int]) -> None:
    with ProcessPoolExecutor() as executor:  # defaults to cpu_count() workers
        results = executor.map(is_prime, numbers)
        for n, prime in zip(numbers, results):
            print(f'{n:20d} {"P" if prime else "X"}')

# ThreadPoolExecutor would NOT speed this up (GIL prevents CPU parallelism)
# ProcessPoolExecutor DOES speed this up (each process has own GIL)
```

---

## 🔄 `executor.map` vs `as_completed`

```
executor.map(fn, items):
  ✅ Simple — submit all, get results in SUBMISSION ORDER
  ⚠️  All must complete before any results available? No — lazy iterator
  ⚠️  First exception stops iteration

futures.as_completed(future_dict):
  ✅ Process results as they finish — any order
  ✅ Handle exceptions per-future independently
  ✅ Better for mixed success/failure scenarios
  ⚠️  Slightly more code
```

---

## 🔑 Key Takeaways

- `ThreadPoolExecutor` → I/O-bound work (downloads, API calls, DB queries)
- `ProcessPoolExecutor` → CPU-bound work (computation, image processing, math)
- `executor.map(fn, items)` → results in order; `futures.as_completed(futures_dict)` → results as they arrive
- `Future.result()` blocks until done; `future.done()` is non-blocking
- Both executors implement `__enter__`/`__exit__` — use as context managers
- `max_workers` matters: too few → slow, too many → resource exhaustion (threads are ~8MB each)
