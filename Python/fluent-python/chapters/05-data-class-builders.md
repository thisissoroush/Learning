# Chapter 5 — Data Class Builders

> *"Data classes are like children. It is fine to let them manage their own data, but they should not make decisions."*

---

## 🎯 Core Concept

Python offers three ways to build data-holding classes: `collections.namedtuple`, `typing.NamedTuple`, and `@dataclass`. Each reduces boilerplate while providing `__init__`, `__repr__`, and `__eq__` automatically.

---

## 🏗️ Overview: Three Builders

```
                namedtuple    NamedTuple    @dataclass
─────────────────────────────────────────────────────
Mutable            ❌            ❌           ✅ (default)
Type hints         ❌            ✅           ✅
Default values     limited       ✅           ✅
__repr__           ✅            ✅           ✅
__eq__             ✅            ✅           ✅
__hash__           ✅(tuple)     ✅(tuple)    (see frozen=)
__lt__ etc.        ✅(tuple)     ✅(tuple)    optional (order=True)
dict export        ._asdict()   ._asdict()   dataclasses.asdict()
Inheritance        limited       limited      ✅
```

---

## 🏷️ Classic `namedtuple`

```python
from collections import namedtuple

# Define
Coordinate = namedtuple('Coordinate', ['lat', 'lon'])
City = namedtuple('City', 'name country population coordinates')

# Use
moscow = City('Moscow', 'RU', 10.9, Coordinate(55.756, 37.617))
moscow.name           # 'Moscow'
moscow.coordinates.lat  # 55.756
moscow._asdict()      # {'name': 'Moscow', 'country': 'RU', ...}
lat, lon = moscow.coordinates  # unpacking works

# With defaults
Card = namedtuple('Card', ['rank', 'suit'])
Card._fields          # ('rank', 'suit')

# Add methods via _make and _replace
Coordinate(55.756, 37.617)  # from iterable
moscow._replace(population=11.0)  # new object with changed field
```

---

## 🔤 Typed `NamedTuple`

```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float
    reference: str = 'WGS84'   # default value

    def __str__(self):
        ns = 'N' if self.lat >= 0 else 'S'
        we = 'E' if self.lon >= 0 else 'W'
        return f'{abs(self.lat):.1f}°{ns}, {abs(self.lon):.1f}°{we}'

c = Coordinate(55.756, 37.617)
str(c)           # '55.8°N, 37.6°E'
c.reference      # 'WGS84'
isinstance(c, tuple)  # True
```

---

## 🎪 `@dataclass`

```python
from dataclasses import dataclass, field

@dataclass
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)  # mutable default — MUST use field()
    athlete: bool = False

m = ClubMember('John Doe')
m.guests.append('Alice')
m  # ClubMember(name='John Doe', guests=['Alice'], athlete=False)

# dataclass parameters
@dataclass(
    order=True,    # generates __lt__, __le__, __gt__, __ge__
    frozen=True,   # immutable + __hash__ (like a record)
    slots=True,    # __slots__ for memory efficiency (Python 3.10+)
    eq=True,       # __eq__ (default True)
    repr=True,     # __repr__ (default True)
)
class Vector:
    x: float = 0.0
    y: float = 0.0
```

---

## ⚙️ Field Options

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class HackerClubMember:
    name: str
    guests: list[str] = field(default_factory=list)
    handle: str = field(default='', init=False)   # excluded from __init__

    # Class variable — not a field
    all_handles: ClassVar[set[str]] = set()

    def __post_init__(self):
        # Runs after __init__
        cls = self.__class__
        if self.handle == '':
            self.handle = self.name.split()[0]
        if self.handle in cls.all_handles:
            msg = f'handle {self.handle!r} already exists'
            raise ValueError(msg)
        cls.all_handles.add(self.handle)

m1 = HackerClubMember('Alice Smith')
m1.handle     # 'Alice' — set in __post_init__
```

---

## 🧬 Pattern Matching with Class Instances

```python
@dataclass
class Point:
    x: float
    y: float

def describe_point(point):
    match point:
        case Point(x=0, y=0):
            print('Origin')
        case Point(x=0, y=y):
            print(f'Y-axis at y={y}')
        case Point(x=x, y=0):
            print(f'X-axis at x={x}')
        case Point(x=x, y=y):
            print(f'Arbitrary point ({x}, {y})')
        case _:
            raise ValueError('not a point')

describe_point(Point(0, 5))   # Y-axis at y=5
describe_point(Point(3, 4))   # Arbitrary point (3, 4)
```

---

## ⚠️ Data Class as a Code Smell

```
A data class with no logic is a symptom of:
  - Logic that should live IN the class scattered elsewhere
  - An anemic domain model (anti-pattern in DDD)

As scaffolding → OK (start here, add behavior later)
As intermediate representation (JSON→dataclass→JSON) → OK
As permanent "bag of attributes" with logic in services → reconsider
```

---

## 🔑 Key Takeaways

- `namedtuple` — simple, immutable, behaves like tuple; good for coordinates, records
- `NamedTuple` — type hints + methods; still a tuple subclass
- `@dataclass` — most flexible; mutable by default; use `frozen=True` for immutability
- Never use mutable defaults directly: `list = []` fails — use `field(default_factory=list)`
- `__post_init__` for validation and derived field computation
- `ClassVar[T]` for class-level attributes that are not fields
- Rich classes (with behavior) are better than thin data classes with logic elsewhere
