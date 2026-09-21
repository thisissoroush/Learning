# Chapter 19 — Concurrency Models in Python

> *"Concurrency is not parallelism, but it enables parallelism."*

---

## 🎯 Core Concept

Python offers three concurrency models: threads (I/O-bound), processes (CPU-bound), and coroutines (async I/O). The GIL limits true CPU parallelism with threads, but doesn't affect I/O-bound concurrency.

---

## 🌐 The Big Picture

```
Concurrency models in Python:
  ┌──────────────────────────────────────────────────┐
  │  threading        — OS threads, GIL limits CPU   │
  │  multiprocessing  — OS processes, true parallel  │
  │  asyncio          — single thread, event loop    │
  └──────────────────────────────────────────────────┘

CPU-bound tasks → multiprocessing
I/O-bound tasks → threading OR asyncio (asyncio preferred for new code)
Mixed           → asyncio + run_in_executor for blocking calls
```

---

## 🧵 Spinner with Threads

```python
import itertools
import time
import threading

def spin(msg: str, done: threading.Event) -> None:
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(.1):     # blocks for .1s, returns True when event set
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

def slow() -> int:
    time.sleep(3)             # simulate I/O wait
    return 42

def main():
    done = threading.Event()
    spinner = threading.Thread(target=spin, args=('thinking!', done))
    spinner.start()
    result = slow()           # blocking call on main thread
    done.set()                # signal spinner to stop
    spinner.join()
    print(f'\nAnswer: {result}')

main()
```

---

## ⚙️ Spinner with Processes

```python
import itertools, time
from multiprocessing import Process, Event, synchronize

def spin(msg: str, done: synchronize.Event) -> None:
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(.1):
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

def slow() -> int:
    time.sleep(3)
    return 42

def main():
    done = Event()
    spinner = Process(target=spin, args=('thinking!', done))
    spinner.start()
    result = slow()
    done.set()
    spinner.join()
    print(f'\nAnswer: {result}')

# Key difference: Process has its own memory — no GIL, true parallelism
# But: higher overhead, IPC needed for data sharing
```

---

## 🔄 Spinner with Coroutines

```python
import asyncio, itertools

async def spin(msg: str) -> None:
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        try:
            await asyncio.sleep(.1)    # yields control to event loop
        except asyncio.CancelledError:
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

async def slow() -> int:
    await asyncio.sleep(3)    # non-blocking I/O wait
    return 42

async def supervisor() -> int:
    spinner = asyncio.create_task(spin('thinking!'))
    result = await slow()
    spinner.cancel()
    return result

def main():
    result = asyncio.run(supervisor())
    print(f'\nAnswer: {result}')
```

---

## 🔒 The GIL — Real Impact

```
The GIL (Global Interpreter Lock):
  - Only one thread executes Python bytecode at a time
  - Released during I/O operations — threads CAN be parallel for I/O
  - NOT released during CPU computation — threads can't parallelize computation

For I/O-bound work (network, disk):
  threads and asyncio both achieve concurrency (GIL released during wait)

For CPU-bound work (computation, math):
  threading is NOT parallel (GIL prevents it)
  multiprocessing IS parallel (each process has its own GIL)
```

```python
# Demonstration: threads can't speed up CPU-bound work
import time
from threading import Thread

def cpu_work(n: int) -> int:
    return sum(i * i for i in range(n))

# Sequential
start = time.perf_counter()
cpu_work(10**7)
cpu_work(10**7)
print(f'Sequential: {time.perf_counter() - start:.2f}s')   # ~2.0s

# Threaded — NOT faster due to GIL!
start = time.perf_counter()
t1 = Thread(target=cpu_work, args=(10**7,))
t2 = Thread(target=cpu_work, args=(10**7,))
t1.start(); t2.start()
t1.join(); t2.join()
print(f'Threaded: {time.perf_counter() - start:.2f}s')     # ~2.1s — no speedup!
```

---

## 🔑 Key Takeaways

- **Threading**: I/O-bound work; threads are lightweight but GIL prevents CPU parallelism
- **Multiprocessing**: CPU-bound work; true parallelism, higher overhead, each process has own memory
- **Asyncio**: I/O-bound, high-concurrency work; single thread, low overhead, excellent for networking
- GIL is released during I/O — threads CAN improve I/O throughput
- GIL is NOT released during CPU-bound Python code — use multiprocessing for computation
- Coroutines run cooperatively — explicit `await` yields control; no preemption
