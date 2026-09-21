# Chapter 24 — Class Metaprogramming

> *"Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't."*

---

## 🎯 Core Concept

Metaprogramming lets you create or customize classes at runtime. Python provides a spectrum of tools — from simple class factory functions to `__init_subclass__`, class decorators, and metaclasses — in increasing order of power and complexity.

---

## 🏭 Classes as Objects — `type()`

```python
# Every class is an instance of type
type(int)       # <class 'type'>
type(str)       # <class 'type'>
type(list)      # <class 'type'>

class Dog:
    pass

type(Dog)       # <class 'type'>

# type() as a class factory: type(name, bases, dict)
Dog = type('Dog', (object,), {'legs': 4, 'bark': lambda self: 'Woof!'})
rex = Dog()
rex.legs        # 4
rex.bark()      # 'Woof!'
```

---

## 🏗️ Class Factory Function

```python
def checked_class(cls):
    """Class decorator that enforces field validation."""
    for name, constructor in _fields(cls).items():
        setattr(cls, name, Validated.build(constructor))
    cls.__init__ = _init(cls)
    return cls

def _fields(cls: type) -> dict[str, type]:
    return {
        name: constructor
        for name, constructor in cls.__annotations__.items()
        if isinstance(constructor, type)
    }

@checked_class
class Movie:
    title: str
    year: int
    box_office: float
```

---

## 🔌 `__init_subclass__` — Hook on Subclassing

```python
class Checked:
    """Base class: validates fields declared as class annotations."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Called when any class inherits from Checked
        # cls is the NEW subclass being created
        for name, constructor in cls.__annotations__.items():
            setattr(cls, name, Field(constructor))   # replace annotation with descriptor

    def __init__(self, **kwargs):
        for name in self.__class__.__annotations__:
            value = kwargs.pop(name, ...)
            if value is ...:
                raise TypeError(f'Missing required field: {name!r}')
            setattr(self, name, value)     # triggers descriptor __set__
        if kwargs:
            raise TypeError(f'Unexpected fields: {sorted(kwargs)}')

class Movie(Checked):
    title: str
    year: int
    box_office: float

m = Movie(title='Gattaca', year=1997, box_office=12.4)
m.title = 42    # TypeError — descriptor enforces str
```

---

## 🎨 Enhancing Classes with Class Decorators

```python
from dataclasses import dataclass, fields

@dataclass
class Movie:
    title: str
    year: int = 0

# @dataclass IS a class decorator — it inspects annotations and adds __init__, __repr__, etc.

# Custom class decorator
def register_species(cls):
    Animal._registry[cls.__name__] = cls
    return cls

class Animal:
    _registry = {}

@register_species
class Dog(Animal):
    def speak(self): return 'Woof'

@register_species
class Cat(Animal):
    def speak(self): return 'Meow'

Animal._registry   # {'Dog': <class 'Dog'>, 'Cat': <class 'Cat'>}
```

---

## ⏱️ Import Time vs. Runtime

```python
# Key insight: class body executes at IMPORT time, not when instantiated

print('Module start')

class Spam:
    print('Spam class body start')      # runs at import
    def method(self):
        print('Spam.method called')     # runs at call time

print('Module end')

# Output (on import):
# Module start
# Spam class body start
# Module end

# Decorators also run at import time
@some_decorator  # called at class creation
class MyClass: ...
```

---

## 🧬 Metaclasses 101

```python
# A metaclass is a class whose instances are classes
# type is the default metaclass of all classes

class MyMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Called when a class with metaclass=MyMeta is created
        print(f'Creating class {name}')
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

class MyClass(metaclass=MyMeta):    # MyMeta creates MyClass
    pass

# Output: Creating class MyClass

# Metaclass example: auto-add validation
class ValidatedMeta(type):
    def __new__(mcs, name, bases, namespace):
        for attr_name, value in namespace.items():
            if isinstance(value, type):    # field annotation
                namespace[attr_name] = Field(value)
        return super().__new__(mcs, name, bases, namespace)

class Person(metaclass=ValidatedMeta):
    name: str
    age: int
```

---

## 🔧 Modern Alternatives to Metaclasses

```
Feature                          Modern replacement
─────────────────────────────────────────────────────────
Class creation hook              __init_subclass__
Field processing at class time   @dataclass or class decorator
Method decoration at class time  __set_name__ + descriptors
ORM field registration           __init_subclass__ + descriptors
Dynamic class creation           type() function
```

---

## 🔑 Key Takeaways

- `type(name, bases, dict)` creates classes at runtime — classes are objects
- `__init_subclass__` runs when a subclass is created — the modern hook for framework magic
- Class decorators intercept class creation cleanly — simpler than metaclasses for most cases
- Metaclasses: `type` is the default metaclass; create a custom metaclass only when `__init_subclass__` can't do the job
- Class bodies execute at **import time** — decorators, descriptors, `__init_subclass__` all run then
- **Use the simplest tool**: `__init_subclass__` > class decorator > metaclass
