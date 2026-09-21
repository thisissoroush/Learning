# Chapter 15 — More About Type Hints

> *"Variance is one of the most subtle and often misunderstood aspects of type systems."*

---

## 🎯 Core Concept

Advanced typing: function overloads, `TypedDict` for structured dicts, variance (covariance, contravariance, invariance), and implementing generic classes and protocols.

---

## 🔁 Overloaded Signatures

```python
from typing import overload

# @overload: multiple signatures for one function
# The actual implementation has no @overload
@overload
def double(input: int) -> int: ...
@overload
def double(input: str) -> str: ...
@overload
def double(input: float) -> float: ...

def double(input):
    return input * 2    # one implementation, multiple type signatures

double(3)         # mypy knows → int
double('hello')   # mypy knows → str
double(3.14)      # mypy knows → float
```

---

## 📋 TypedDict

```python
from typing import TypedDict

# TypedDict: a dict with specific key-value types
class BookDict(TypedDict):
    isbn: str
    title: str
    authors: list[str]
    pagecount: int

python_book: BookDict = {
    'isbn': '0134757599',
    'title': 'The Pragmatic Programmer',
    'authors': ['David Thomas', 'Andrew Hunt'],
    'pagecount': 352,
}

# mypy checks key names and value types
python_book['pagecount']   # int — mypy knows
python_book['year']        # mypy error: key 'year' not in BookDict

# TypedDict with total=False (all keys optional)
class Options(TypedDict, total=False):
    timeout: int
    retries: int
    verbose: bool
```

---

## 📐 Variance

```
Invariant:   only the exact type works
Covariant:   subtype is accepted (list is covariant in its element type for reading)
Contravariant: supertype is accepted (useful for callable parameter types)
```

```python
# Invariant — only exact type works
class Beverage: ...
class Juice(Beverage): ...
class OrangeJuice(Juice): ...

class Dispenser(Generic[T]):
    def __init__(self, item: T): self._item = item
    def pickup(self) -> T: return self._item
    def load(self, item: T) -> None: self._item = item

# If Dispenser were covariant, this would be unsound:
def fill(machine: Dispenser[Juice], juice: Juice) -> None:
    machine.load(juice)

oj_machine = Dispenser(OrangeJuice())
fill(oj_machine, Juice())    # WRONG if covariant — loads Juice into OrangeJuice machine

# Covariant (read-only producer) — safe
from typing import TypeVar
T_co = TypeVar('T_co', covariant=True)

class ImmutableDispenser(Generic[T_co]):
    def __init__(self, item: T_co): self._item = item
    def pickup(self) -> T_co: return self._item    # only reading

# Contravariant (write-only consumer) — safe
T_contra = TypeVar('T_contra', contravariant=True)

class Collector(Generic[T_contra]):
    def deposit(self, item: T_contra) -> None: ...  # only writing
```

---

## 🔑 Key Takeaways

- `@overload` gives one function multiple type signatures — tools see each signature, runtime uses the real implementation
- `TypedDict` adds static types to dicts — used heavily with JSON APIs and structured configs
- **Invariant**: exact type only (mutable containers)
- **Covariant**: subtype OK (read-only / producer)
- **Contravariant**: supertype OK (write-only / consumer)
- Variance matters when designing generic containers and callbacks
