# Chapter 21 — Asynchronous Programming

> *"Asynchronous programming is all about not blocking."*

---

## 🎯 Core Concept

`asyncio` provides a single-threaded event loop that handles thousands of concurrent I/O operations via cooperative multitasking. `async def` / `await` makes async code look sequential while remaining non-blocking.

---

## 📡 asyncio Example — Domain Probing

```python
import asyncio
import socket
from keyword import kwlist

MAX_KEYWORD_LEN = 4

async def probe(domain: str) -> tuple[str, bool]:
    loop = asyncio.get_running_loop()
    try:
        await loop.getaddrinfo(domain, None)    # async DNS lookup
    except socket.gaierror:
        return (domain, False)
    return (domain, True)

async def main() -> None:
    names = (kw for kw in kwlist if len(kw) <= MAX_KEYWORD_LEN)
    domains = (f'{name}.dev'.lower() for name in names)
    coros = [probe(domain) for domain in domains]
    for coro in asyncio.as_completed(coros):    # run all concurrently
        domain, found = await coro
        mark = '+' if found else 'x'
        print(f'{mark} {domain}')

asyncio.run(main())
```

---

## ⚡ Downloading with asyncio + HTTPX

```python
import asyncio
import httpx

async def get_flag(client: httpx.AsyncClient, cc: str) -> bytes:
    url = f'https://example.com/flags/{cc}/{cc}.gif'
    resp = await client.get(url, timeout=6.1, follow_redirects=True)
    resp.raise_for_status()
    return resp.content

async def download_one(client: httpx.AsyncClient, cc: str) -> str:
    image = await get_flag(client, cc)
    (Path('downloaded') / f'{cc}.gif').write_bytes(image)
    return cc

async def supervisor(cc_list: list[str]) -> int:
    async with httpx.AsyncClient() as client:
        to_do = [download_one(client, cc) for cc in cc_list]
        results = await asyncio.gather(*to_do)   # run all concurrently
    return len(results)

def main(cc_list: list[str]) -> None:
    count = asyncio.run(supervisor(cc_list))
    print(f'Downloaded {count} flags')
```

---

## 🎛️ Throttling with Semaphore

```python
async def supervisor(cc_list: list[str], concur_req: int) -> Counter:
    counter: Counter[str] = Counter()
    semaphore = asyncio.Semaphore(concur_req)    # limit concurrent requests

    async def download_with_semaphore(cc: str) -> str:
        async with semaphore:                    # acquire before, release after
            return await download_one(cc)

    async with httpx.AsyncClient() as client:
        to_do_map = {
            asyncio.create_task(download_with_semaphore(cc)): cc
            for cc in cc_list
        }
        for coro in asyncio.as_completed(to_do_map):
            try:
                status = await coro
            except Exception as exc:
                print(f'Error: {exc}')
            else:
                counter[status] += 1
    return counter
```

---

## 🔄 Async Iteration and Generators

```python
# Asynchronous generator
async def stream_data(url: str) -> AsyncGenerator[bytes, None]:
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', url) as response:
            async for chunk in response.aiter_bytes(1024):
                yield chunk    # async yield

# Consume with async for
async def process_stream():
    async for chunk in stream_data('http://example.com/data'):
        process(chunk)

# Async comprehension
results = [x async for x in async_generator()]
results = {key: val async for key, val in async_key_value_gen()}
```

---

## 🚀 Delegating to Executor (blocking calls in async code)

```python
import asyncio

async def run_blocking_task(data: bytes) -> str:
    loop = asyncio.get_running_loop()
    # Run CPU-bound or blocking I/O in thread pool — doesn't block event loop
    result = await loop.run_in_executor(None, blocking_function, data)
    return result

# Or with explicit executor:
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor()

async def run_cpu_intensive(n: int) -> int:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, is_prime, n)
```

---

## 🔑 Key Takeaways

- `async def` defines a coroutine; `await` suspends it without blocking the event loop
- `asyncio.run()` starts the event loop and runs a single root coroutine
- `asyncio.gather(*coros)` runs multiple coroutines concurrently, waits for all
- `asyncio.as_completed(coros)` yields futures as they complete — process results immediately
- Use `asyncio.Semaphore(n)` to limit concurrent requests / resource usage
- Blocking code (file I/O, CPU work) in async code blocks the whole event loop — use `run_in_executor`
- Async is NOT parallel — it's concurrent single-threaded; CPU-bound needs processes
