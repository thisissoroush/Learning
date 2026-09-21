# Chapter 9 — Decorators and Closures

> *"Function decorators let us mark functions in source code to enhance their behavior."*

---

## 🎯 Core Concept

Decorators are a powerful Python feature for wrapping functions to add behavior (logging, caching, retry, auth). Understanding them requires understanding closures and variable scoping first.

---

## 🎨 Decorator Basics

```python
# A decorator is a callable that takes a function and returns another function

def decorate(func):
    def inner(*args, **kwargs):
        print(f'Calling {func.__name__}')
        result = func(*args, **kwargs)
        print(f'Done with {func.__name__}')
        return result
    return inner

@decorate
def greet(name):
    print(f'Hello, {name}')

# @decorate is syntactic sugar for:
# greet = decorate(greet)

greet('Alice')
# Calling greet
# Hello, Alice
# Done with greet
```

---

## 🕐 When Python Executes Decorators

```python
# Decorators run at IMPORT TIME (module load), not at call time
registry = []

def register(func):
    print(f'running register({func})')
    registry.append(func)
    return func     # returns func unchanged (registration decorator)

@register
def f1():
    print('running f1()')

@register
def f2():
    print('running f2()')

# Output when module is imported:
# running register(<function f1 at 0x...>)
# running register(<function f2 at 0x...>)

# registry = [f1, f2]  — before f1() or f2() is ever called
```

---

## 🔒 Variable Scope Rules

```python
b = 6

def f1(a):
    print(a)
    print(b)    # 6 — reads outer scope

f1(3)   # 3, 6

def f2(a):
    print(a)
    print(b)    # UnboundLocalError! Python sees b assigned below
    b = 9       # b is local because of this assignment

# Fix with global
def f3(a):
    global b
    print(a)
    print(b)
    b = 9
```

---

## 🧊 Closures

```python
# A closure retains access to variables from the enclosing scope, even after that scope exits

def make_averager():
    series = []    # free variable — captured by closure

    def averager(new_value):
        series.append(new_value)   # series is a free variable (closure cell)
        return sum(series) / len(series)

    return averager

avg = make_averager()
avg(10)    # 10.0
avg(11)    # 10.5
avg(12)    # 11.0

avg.__code__.co_freevars    # ('series',)
avg.__closure__[0].cell_contents  # [10, 11, 12]  — the actual list

# nonlocal — for rebinding immutables in closure
def make_averager_v2():
    count = 0
    total = 0.0

    def averager(new_value):
        nonlocal count, total    # allows rebinding (not just mutation)
        count += 1
        total += new_value
        return total / count

    return averager
```

---

## 🏗️ Implementing a Decorator Properly

```python
import time
import functools

def clock(func):
    @functools.wraps(func)     # preserves __name__, __doc__, etc.
    def clocked(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        name = func.__name__
        arg_str = ', '.join(repr(a) for a in args)
        print(f'[{elapsed:.8f}s] {name}({arg_str}) -> {result!r}')
        return result
    return clocked

@clock
def snooze(seconds):
    time.sleep(seconds)

@clock
def factorial(n):
    return 1 if n < 2 else n * factorial(n - 1)

factorial(6)
# [0.00000036s] factorial(1) -> 1
# [0.00001100s] factorial(2) -> 2
# ...
# [0.00009800s] factorial(6) -> 720
```

---

## ⚡ Standard Library Decorators

```python
from functools import cache, lru_cache, singledispatch

# @cache — memoize with unlimited cache (Python 3.9+)
@cache
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n - 2) + fibonacci(n - 1)

fibonacci(30)    # fast — each value computed once

# @lru_cache — memoize with LRU eviction (bounded cache)
@lru_cache(maxsize=128)
def get_exchange_rate(currency):
    return external_api.get_rate(currency)

# @singledispatch — type-based dispatch (overloading by first arg type)
from functools import singledispatch

@singledispatch
def htmlize(obj):
    content = html.escape(repr(obj))
    return f'<pre>{content}</pre>'

@htmlize.register(str)
def _(text):
    content = html.escape(text).replace('\n', '<br/>\n')
    return f'<p>{content}</p>'

@htmlize.register(list)
@htmlize.register(tuple)
def _(seq):
    inner = '</li>\n<li>'.join(htmlize(item) for item in seq)
    return '<ul>\n<li>' + inner + '</li>\n</ul>'

htmlize({1, 2, 3})         # uses default
htmlize('hello\nworld')    # uses str handler
htmlize([1, 2, 'three'])   # uses list handler
```

---

## 🔧 Parameterized Decorators

```python
# A decorator factory returns the actual decorator

REGISTRY = {}
DEFAULT_FMT = '[{elapsed:.8f}s] {name}({args}) -> {result}'

def clock(fmt=DEFAULT_FMT):    # clock is a decorator FACTORY
    def decorate(func):        # decorate is the actual decorator
        @functools.wraps(func)
        def clocked(*_args, **_kwargs):
            t0 = time.perf_counter()
            _result = func(*_args, **_kwargs)
            elapsed = time.perf_counter() - t0
            name = func.__name__
            args = ', '.join(repr(a) for a in _args)
            result = repr(_result)
            print(fmt.format(**locals()))
            return _result
        return clocked
    return decorate

@clock()                        # note: called with ()
def snooze(seconds):
    time.sleep(seconds)

@clock('{name}: {elapsed:.3f}s')  # custom format
def factorial(n):
    return 1 if n < 2 else n * factorial(n - 1)
```

---

## 🔑 Key Takeaways

- `@decorator` is sugar for `func = decorator(func)` — applied at module load time
- Use `@functools.wraps(func)` inside every decorator to preserve metadata
- Closures capture variables from the enclosing scope via closure cells
- Use `nonlocal` to rebind (not just mutate) a closure variable
- `@cache` / `@lru_cache` for memoization — avoid recomputing expensive calls
- Parameterized decorators need three levels of nesting: factory → decorator → wrapper
- `@singledispatch` provides type-based overloading without `if isinstance` chains
