# Chapter 22 — Dynamic Attributes and Properties

> *"Data attributes and methods are collectively known as attributes in Python."*

---

## 🎯 Core Concept

`__getattr__` enables dynamic attribute access. `property` turns method calls into attribute syntax with validation. Together they give you flexible, safe object APIs.

---

## 🔮 Dynamic Attributes with `__getattr__`

```python
import json
from pathlib import Path

class FrozenJSON:
    """Read-only JSON data accessed as attributes."""

    def __new__(cls, arg):
        if isinstance(arg, dict):
            return super().__new__(cls)     # create FrozenJSON
        elif isinstance(arg, list):
            return [cls(item) for item in arg]  # return a list
        else:
            return arg      # leaf value — return as-is

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'              # avoid shadowing Python keywords
            self.__data[key] = value

    def __getattr__(self, name):
        # Called when normal attribute lookup fails
        try:
            return getattr(self.__data, name)   # delegate to dict methods (keys, values)
        except AttributeError:
            return FrozenJSON(self.__data[name])  # wrap nested dicts

raw_feed = json.loads(Path('feed.json').read_text())
feed = FrozenJSON(raw_feed)
feed.schedule.speakers[40].name     # works as attribute access
feed.Schedule.events[40].name       # ← AttributeError: only keys in JSON work
```

---

## 🏗️ Flexible Object Creation with `__new__`

```python
class Foo:
    def __new__(cls, *args, **kwargs):
        # __new__ creates the object
        print(f'Creating {cls.__name__}')
        instance = super().__new__(cls)
        return instance

    def __init__(self, x):
        # __init__ initializes the object
        self.x = x

# __new__ flow:
# 1. Python calls cls.__new__(cls, *args)
# 2. If result is instance of cls → call __init__ on it
# 3. If result is NOT instance of cls → skip __init__

# Use case: returning a singleton, or different type based on args
class FlexJSON(FrozenJSON):
    def __new__(cls, arg):
        if isinstance(arg, dict):
            return super().__new__(cls)
        elif isinstance(arg, MutableMapping):
            return dict(arg)  # returns a dict, not FlexJSON!
        else:
            return arg
```

---

## 🔒 Properties for Validation

```python
class LineItem:
    def __init__(self, description: str, weight: float, price: float):
        self.description = description
        self.weight = weight     # triggers setter validation
        self.price = price

    def subtotal(self):
        return self.weight * self.price

    @property
    def weight(self) -> float:
        return self.__weight

    @weight.setter
    def weight(self, value: float):
        if value > 0:
            self.__weight = value
        else:
            raise ValueError('weight must be > 0')

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value: float):
        if value > 0:
            self.__price = value
        else:
            raise ValueError('price must be > 0')

item = LineItem('Widget', weight=10, price=19.99)
item.weight = -1    # ValueError!
```

---

## 🏭 Property Factory

```python
def quantity(storage_name: str):
    """Property factory: creates a validated quantity property."""
    def qty_getter(instance):
        return instance.__dict__[storage_name]

    def qty_setter(instance, value):
        if value > 0:
            instance.__dict__[storage_name] = value
        else:
            raise ValueError(f'{storage_name} must be > 0')

    return property(qty_getter, qty_setter)

class LineItem:
    weight = quantity('weight')   # class attribute: property
    price  = quantity('price')    # class attribute: property

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight    # calls weight.setter
        self.price = price

    def subtotal(self):
        return self.weight * self.price
```

---

## ⚡ Caching Properties

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    # functools.cached_property — computed once, cached in instance __dict__
    @functools.cached_property
    def area(self):
        print('Computing area...')
        return math.pi * self.radius ** 2

c = Circle(5)
c.area    # "Computing area..." → 78.53...
c.area    # no computation — reads from __dict__

# Note: cached_property doesn't work with __slots__ (no __dict__)
# Use regular property + manual cache dict in that case
```

---

## 🔑 Key Takeaways

- `__getattr__` is called only when normal lookup fails — use it for dynamic attribute access from external data (JSON, config)
- `__setattr__` is called on EVERY attribute assignment — be careful not to call `self.x = y` inside it (causes infinite recursion)
- `property` adds validation without changing the public API: `obj.weight = -1` raises `ValueError`
- Properties are class attributes that override instance `__dict__` on access
- `@functools.cached_property` computes once on first access, then stores in instance `__dict__`
- Use a property factory when you need the same validation logic for multiple attributes
