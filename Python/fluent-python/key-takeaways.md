# Fluent Python 2e — Key Takeaways

Quick-reference summary of the most important concepts from each chapter.

---

## Part I: Data Structures

### Ch 1 — Python Data Model
- Implement `__len__` + `__getitem__` and your object works with `len()`, `for`, slicing, `sorted()`, `random.choice()` — for free
- `__repr__` is used everywhere (REPL, logging, debugging) — always implement it
- `__bool__` → `bool()` → `if obj:` — falsy when 0 or empty

### Ch 2 — Sequences
- List comprehension is the Pythonic way to build lists; generator expressions for other iterables
- Prefer tuples as immutable records; namedtuples add field names without overhead
- `array.array` for large homogeneous numeric data; `memoryview` for zero-copy slicing

### Ch 3 — Dicts and Sets
- `dict` is a hash table — O(1) lookup; key must be hashable (implements `__hash__` + `__eq__`)
- `dict.setdefault(key, [])` avoids double lookup; `collections.defaultdict` auto-creates missing keys
- Set operations: `|` union, `&` intersection, `-` difference, `^` symmetric difference

### Ch 4 — Unicode
- Always decode on input; always encode on output; work with `str` internally — the Unicode sandwich
- `'café'.encode('utf-8')` → `bytes`; `b'caf\xc3\xa9'.decode('utf-8')` → `str`
- `unicodedata.normalize('NFC', text)` before comparing strings with accented chars

### Ch 5 — Data Classes
- `@dataclass` generates `__init__`, `__repr__`, `__eq__` automatically from annotations
- `@dataclass(frozen=True)` → immutable + hashable (auto `__hash__`)
- Prefer `@dataclass` over `namedtuple` when you need default values or mutability control

### Ch 6 — References & Mutability
- Variables are labels (references), not boxes — assignment binds a label to an object
- `a = b` makes both labels point to the **same** object; `a = b[:]` makes a shallow copy
- Use `copy.deepcopy()` only when truly needed; most of the time shallow copy is correct and cheaper

---

## Part II: Functions as Objects

### Ch 7 — Functions as First-Class Objects
- Functions are objects: store in variables, pass as arguments, return, put in dicts
- `functools.partial(fn, arg)` freezes arguments to create specialized functions
- Prefer `operator.mul` / `itemgetter` / `attrgetter` over `lambda` — more readable

### Ch 8 — Type Hints
- Gradual typing: annotate incrementally; type checker ignores unannotated parts
- Use abstract types (`Sequence`, `Iterable`, `Mapping`) not concrete (`list`, `dict`)
- `str | None` (3.10+) instead of `Optional[str]`; `TypeVar` for generic type preservation

### Ch 9 — Decorators & Closures
- `@decorator` = `func = decorator(func)` — runs at import time
- Always use `@functools.wraps(func)` inside decorators to preserve `__name__`, `__doc__`
- `@functools.cache` for memoization; `@functools.singledispatch` for type-based dispatch

### Ch 10 — Design Patterns with Functions
- Strategy and Command often collapse to plain callables in Python — no extra class needed
- Use a registration decorator to discover strategy functions automatically
- The simplest working solution wins: if a function works, don't add a class

---

## Part III: Classes and Protocols

### Ch 11 — Pythonic Object
- Always implement `__repr__`; implement `__str__` for user-friendly display
- If `__eq__` → must implement `__hash__` too (objects that compare equal must hash equal)
- `@property` + private `__x` (name mangling) → read-only attribute; `__slots__` → ~50% memory saving

### Ch 12 — Sequences via Special Methods
- Sequence protocol = `__len__` + `__getitem__` → iteration, slicing, `in`, `sorted` for free
- Always pair `__getattr__` with `__setattr__` to prevent inconsistent state
- Slicing `obj[1:3]` passes a `slice(1, 3, None)` to `__getitem__`

### Ch 13 — Interfaces, Protocols, ABCs
| Approach | When | Check |
|---------|------|-------|
| Duck typing | Flexible code | Runtime (on use) |
| ABC `isinstance` | Enforcement | Runtime fast |
| `@register` | Third-party classes | Runtime |
| `typing.Protocol` | Static + structural | Type checker |

### Ch 14 — Inheritance
- Subclassing built-ins (`dict`, `list`) is unreliable — use `UserDict`, `UserList` instead
- `super()` follows MRO, not direct parent — critical in multiple inheritance
- Mixins: no state, no `__init__`, single purpose, listed first in base classes

### Ch 15 — Advanced Type Hints
- `@overload` gives one function multiple type signatures for static analysis
- `TypedDict` adds types to dict-like structures (JSON configs, API payloads)
- Invariant (mutable), covariant (read-only producer), contravariant (write-only consumer)

---

## Part IV: Control Flow

### Ch 16 — Operator Overloading
- Return `NotImplemented` (not raise!) when you can't handle an operand — lets Python try the reflected method
- Define `__add__` + `__radd__` for commutative operators; never mutate `self` in arithmetic ops
- Defining `__eq__` requires defining `__hash__`

### Ch 17 — Iterators & Generators
- Generator functions (`yield`) produce lazy sequences — O(1) memory regardless of length
- `yield from subgen` delegates to a subgenerator transparently
- Don't make an iterable its own iterator — separate iterable (reusable) from iterator (one-pass)

### Ch 18 — `with`, `match`, `else`
- Context managers guarantee cleanup: `__exit__` called even on exception
- `@contextmanager` turns a one-yield generator into a context manager — simpler than a class
- `for/else`: `else` runs when loop completes without `break`; `try/else`: runs when `try` succeeds

### Ch 19 — Concurrency Models
| Model | Best for | GIL impact |
|-------|---------|------------|
| `threading` | I/O-bound | Released during I/O — ok |
| `multiprocessing` | CPU-bound | Each process has own GIL |
| `asyncio` | High-concurrency I/O | Single-threaded |

### Ch 20 — Concurrent Executors
- `ThreadPoolExecutor` → I/O-bound; `ProcessPoolExecutor` → CPU-bound — same API
- `executor.map` → results in order; `futures.as_completed` → results as they arrive
- `max_workers` matters: threads are ~8MB each; too many = resource exhaustion

### Ch 21 — Async Programming
- `await` suspends a coroutine without blocking the event loop
- `asyncio.gather(*coros)` → run all concurrently, wait for all
- `asyncio.Semaphore(n)` → limit concurrent requests; `run_in_executor` for blocking code

---

## Part V: Metaprogramming

### Ch 22 — Dynamic Attributes & Properties
- `__getattr__` called only on lookup failure — good for wrapping external data (JSON, config)
- `@property` + private `__name` → validated attribute with no API change
- `@functools.cached_property` → computed once, cached in `__dict__`

### Ch 23 — Descriptors
- Data descriptor (`__set__`) overrides instance `__dict__`; non-data (only `__get__`) can be shadowed
- `__set_name__` auto-receives the attribute name at class creation — no redundant naming
- Functions are descriptors — that's how `instance.method()` binds `self`

### Ch 24 — Class Metaprogramming
- `type(name, bases, dict)` creates classes dynamically at runtime
- `__init_subclass__` runs on subclass creation — modern replacement for most metaclass use cases
- **Use the simplest tool**: `__init_subclass__` > class decorator > metaclass
