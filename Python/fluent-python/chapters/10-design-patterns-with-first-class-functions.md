# Chapter 10 — Design Patterns with First-Class Functions

> *"Although design patterns are language-independent, that does not mean every pattern applies to every language."*

---

## 🎯 Core Concept

Classic OOP design patterns often require extra classes when implemented in Java or C++. In Python, first-class functions and closures allow many of these patterns to be expressed more simply — sometimes just as a function or a dict of functions.

---

## 🎭 The Strategy Pattern — Classic vs. Pythonic

```python
# CLASSIC OOP STRATEGY (Java-style in Python)
from abc import ABC, abstractmethod

class Promotion(ABC):
    @abstractmethod
    def discount(self, order) -> float: ...

class FidelityPromo(Promotion):
    def discount(self, order):
        return order.total() * .05 if order.customer.fidelity >= 1000 else 0

class BulkItemPromo(Promotion):
    def discount(self, order):
        discount = 0
        for item in order.cart:
            if item.quantity >= 20:
                discount += item.total() * .1
        return discount

class LargeOrderPromo(Promotion):
    def discount(self, order):
        distinct_items = {item.product for item in order.cart}
        if len(distinct_items) >= 10:
            return order.total() * .07
        return 0

# PYTHONIC: functions are strategies — no extra classes needed
def fidelity_promo(order):
    return order.total() * .05 if order.customer.fidelity >= 1000 else 0

def bulk_item_promo(order):
    discount = 0
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * .1
    return discount

def large_order_promo(order):
    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * .07
    return 0

# Context just calls the function
class Order:
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = cart
        self.promotion = promotion

    def discount(self):
        if self.promotion is None:
            return 0
        return self.promotion(self)   # call the function strategy

    def total(self):
        return sum(item.total() for item in self.cart)

    def due(self):
        return self.total() - self.discount()

joe = Order(customer, cart, promotion=fidelity_promo)   # pass function as strategy
```

---

## 🔍 Finding Strategies in a Module

```python
import inspect

# Automatically discover all promo functions in the module
promos = [func for _, func in inspect.getmembers(promotions, inspect.isfunction)]

# Or use a registration decorator
Promotion = Callable[[Order], float]
promos: list[Promotion] = []

def promotion(promo: Promotion) -> Promotion:
    promos.append(promo)
    return promo

@promotion
def fidelity(order: Order) -> float:
    return order.total() * .05 if order.customer.fidelity >= 1000 else 0

@promotion
def bulk_item(order: Order) -> float:
    ...

def best_promo(order: Order) -> float:
    return max(promo(order) for promo in promos)
```

---

## 🖥️ The Command Pattern — Simplified

```python
# CLASSIC: Command objects with execute()
class MacroCommand:
    def __init__(self, commands):
        self.commands = list(commands)

    def __call__(self):
        for command in self.commands:
            command()

# Each command is just a callable (function, lambda, or __call__ object)
# No need for a Command abstract class — callables ARE the interface

paste = lambda: editor.paste()
open_file = lambda: editor.open_file(path)
macro = MacroCommand([paste, open_file, paste])
macro()   # executes all three
```

---

## 💡 When to Keep Classes

```python
# Classes remain better than functions when:
# 1. The pattern has state that needs to be preserved between calls
# 2. Multiple methods are needed (not just __call__)
# 3. Subclassing and inheritance make sense for the problem

# Example: Memoizing strategy with state
class SmartPromo:
    def __init__(self):
        self.applied_count = 0

    def __call__(self, order):
        self.applied_count += 1
        return order.total() * .05

smart = SmartPromo()
smart(order1)
smart.applied_count   # 1 — stateful
```

---

## 🔑 Key Takeaways

- Classic patterns often assume languages without first-class functions
- Strategy, Command, and Template Method often collapse to plain functions in Python
- Use a registration decorator to discover strategy functions automatically
- `inspect.getmembers(module, inspect.isfunction)` finds all functions in a module
- Prefer the simplest solution: if a function works, don't add a class
- Keep classes when you need state, multiple methods, or inheritance
