# Chapter 8 — Type Hints in Functions

> *"Gradual typing: you can add type hints incrementally — the type checker ignores unannotated parts."*

---

## 🎯 Core Concept

Python's type hints are optional annotations that enable static analysis tools like `mypy` and `pyright` to catch bugs before runtime. They don't affect execution — they're metadata for tools.

---

## 🔬 Gradual Typing

```python
# No annotations — valid Python, no static checking
def double(x):
    return x * 2

# With annotations — enables static checking
def double(x: float) -> float:
    return x * 2

# Gradual: annotate incrementally — tools check what's annotated, ignore the rest
def greet(name: str) -> str:    # checked
    return 'Hello, ' + name

def make_something(config):     # not checked — Any by default
    ...
```

---

## 🧰 Types You Can Annotate With

```python
from typing import Optional, Union, Any, TypeVar, Callable, Iterator, Sequence
from collections.abc import Sequence as AbcSequence

# Simple types
x: int = 42
s: str = 'hello'
d: dict = {}

# Optional — either T or None (most common)
def find(name: str) -> Optional[str]:   # str | None in Python 3.10+
    ...

# Union — one of several types
def parse(value: Union[str, bytes]) -> str:
    ...
# Python 3.10+ syntax:
def parse(value: str | bytes) -> str:
    ...

# Generic collections — use lowercase in Python 3.9+
def process(items: list[str]) -> dict[str, int]:
    ...

# Abstract base classes — accept any Sequence, not just list
def first(seq: Sequence[float]) -> float:
    return seq[0]

first([1, 2, 3])    # works
first((4, 5, 6))    # works — tuple is also Sequence
```

---

## 🔠 TypeVar — Generic Functions

```python
from typing import TypeVar

T = TypeVar('T')

def first(seq: Sequence[T]) -> T:
    return seq[0]

# Now return type matches element type of the sequence:
result: int = first([1, 2, 3])     # mypy knows result is int
result: str = first(['a', 'b'])    # mypy knows result is str

# Bounded TypeVar
Comparable = TypeVar('Comparable', bound='SupportsLessThan')

def top(series: Iterable[Comparable], length: int) -> list[Comparable]:
    ordered = sorted(series, reverse=True)
    return ordered[:length]
```

---

## 📐 Static Protocols

```python
from typing import Protocol, runtime_checkable

class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...

# Any class with __lt__ satisfies this protocol — no inheritance needed
# (duck typing with static checking)

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print('O')

isinstance(Circle(), Drawable)   # True — runtime check (only checks method existence)
```

---

## 📞 Callable Type Hints

```python
from collections.abc import Callable

# Callable[[arg_types], return_type]
def apply(func: Callable[[float, float], float], a: float, b: float) -> float:
    return func(a, b)

apply(pow, 2, 10)    # 1024.0

# No-arg callable returning str
def call_later(func: Callable[[], str]) -> str:
    return func()

# Variable args callable
def apply_many(func: Callable[..., int], args: list) -> list[int]:
    return [func(*a) for a in args]
```

---

## 🔕 `NoReturn` and `Never`

```python
from typing import NoReturn

def raise_error(msg: str) -> NoReturn:
    raise RuntimeError(msg)
# Return type NoReturn: function never returns normally (always raises or loops forever)

# Never (Python 3.11+) — value that cannot exist
from typing import Never
def assert_never(arg: Never) -> Never:
    raise AssertionError(f"Expected dead code: {arg!r}")
```

---

## 💡 Imperfect Typing + Strong Testing

```python
# Types cannot express all constraints:
def double(x: float) -> float: ...  # mypy won't catch double("oops") at runtime

# When to use type hints:
# ✅ Public APIs — documenting what callers should pass
# ✅ Large codebases — catching errors across module boundaries
# ✅ Long-lived code — helping future maintainers

# When to be pragmatic:
# ✅ Use Any for complex runtime types you can't easily express
# ✅ Combine with docstrings for nuances types can't capture
# ✅ Strong tests remain essential — types are not a substitute
```

---

## 🔑 Key Takeaways

- Type hints are for tools (mypy, pyright, IDEs) — they don't affect runtime
- Gradual typing: annotate incrementally without breaking existing code
- Prefer abstract types (`Sequence`, `Iterable`, `Mapping`) over concrete (`list`, `dict`)
- Use `str | None` (Python 3.10+) instead of `Optional[str]`
- `TypeVar` enables generic functions that preserve element types
- `Protocol` enables structural typing (duck typing with static checking)
- Types + tests: neither replaces the other — both are necessary
