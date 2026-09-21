# Chapter 23 — Attribute Descriptors

> *"A descriptor is any class that defines a __get__, __set__, or __delete__ method."*

---

## 🎯 Core Concept

Descriptors are the mechanism behind `property`, `classmethod`, `staticmethod`, and functions themselves. They let you define attribute access logic once and reuse it across many classes.

---

## 🔬 Descriptor Example — Attribute Validation

```python
class Validated:
    """Abstract base class for validated descriptors."""

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name    # storage attribute

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self    # class access → return descriptor itself
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        value = self.validate(self.public_name, value)
        setattr(obj, self.private_name, value)

    def validate(self, name, value):
        raise NotImplementedError('Subclasses must override validate()')

class Quantity(Validated):
    def validate(self, name, value):
        if value <= 0:
            raise ValueError(f'{name} must be > 0, got {value!r}')
        return value

class NonBlank(Validated):
    def validate(self, name, value):
        value = value.strip()
        if not value:
            raise ValueError(f'{name} cannot be blank')
        return value

class LineItem:
    description = NonBlank()    # descriptor instance as class attribute
    weight      = Quantity()    # __set_name__ called with owner=LineItem, name='weight'
    price       = Quantity()

    def __init__(self, description, weight, price):
        self.description = description    # triggers NonBlank.__set__
        self.weight = weight              # triggers Quantity.__set__
        self.price = price

    def subtotal(self):
        return self.weight * self.price

item = LineItem('   ', 10, 1.5)   # ValueError: description cannot be blank
item = LineItem('Widget', 0, 1.5) # ValueError: weight must be > 0
```

---

## 🏷️ `__set_name__` — Automatic Naming

```python
# Without __set_name__ (Python < 3.6):
class Quantity:
    def __init__(self, storage_name):
        self.storage_name = storage_name   # must be passed explicitly

class LineItem:
    weight = Quantity('weight')   # redundant: name 'weight' twice
    price  = Quantity('price')

# With __set_name__ (Python 3.6+):
class Quantity:
    def __set_name__(self, owner, name):   # called automatically at class creation
        self.public_name = name
        self.private_name = f'_{name}'

class LineItem:
    weight = Quantity()   # name inferred from attribute name
    price  = Quantity()
```

---

## 🔄 Overriding vs. Non-Overriding Descriptors

```python
# Overriding descriptor (data descriptor): has __set__ (or __delete__)
# → Takes priority over instance __dict__
class Overriding:
    def __get__(self, obj, objtype=None):
        print(f'Overriding.__get__({obj!r})')

    def __set__(self, obj, value):
        print(f'Overriding.__set__({obj!r}, {value!r})')

# Non-overriding descriptor (non-data descriptor): only __get__
# → Instance __dict__ entry shadows the descriptor
class NonOverriding:
    def __get__(self, obj, objtype=None):
        print(f'NonOverriding.__get__({obj!r})')

class MyClass:
    over     = Overriding()
    non_over = NonOverriding()

obj = MyClass()
obj.over     # calls Overriding.__get__
obj.over = 7 # calls Overriding.__set__ — instance dict NOT written
obj.__dict__ # {} — no 'over' in instance dict (descriptor intercepted it)

obj.non_over      # calls NonOverriding.__get__
obj.non_over = 7  # writes to instance __dict__ directly (no __set__)
obj.__dict__      # {'non_over': 7}
obj.non_over      # 7 — instance __dict__ shadows the descriptor!
```

---

## 🔧 Methods Are Descriptors

```python
# Regular functions implement __get__:
# When accessed via instance, __get__ returns a bound method
# When accessed via class, __get__ returns the function itself

class Foo:
    def bar(self): pass

Foo.bar              # <function Foo.bar at 0x...>  — __get__ with obj=None
Foo().bar            # <bound method Foo.bar of <Foo object>> — __get__ bound

# This is WHY methods work:
Foo.bar(Foo())       # == Foo().bar()  — unbound vs. bound
```

---

## 💡 Descriptor Usage Tips

```
1. Use descriptors when:
   - Same validation/transformation logic needed on multiple classes
   - Building frameworks or ORMs
   - Implementing property-like features with shared behavior

2. Use properties instead when:
   - Logic is specific to one class (simpler)

3. __get__ returning self for class access:
   - Allows: LineItem.weight  → the descriptor itself
   - Useful for framework introspection

4. Store state in the managed instance's __dict__:
   - NOT in the descriptor itself (descriptor is shared among all instances of the class)
   - self.storage[obj] = value  or  obj.__dict__[self.key] = value
```

---

## 🔑 Key Takeaways

- A descriptor is a class with `__get__`, `__set__`, or `__delete__`
- **Data descriptor** (has `__set__`): overrides instance `__dict__` — like `property`
- **Non-data descriptor** (only `__get__`): can be shadowed by instance `__dict__` — like functions
- `__set_name__` is called at class creation — no need to pass attribute name explicitly
- Functions are descriptors — that's how `instance.method()` becomes a bound method call
- Store state per-instance in `obj.__dict__[key]`, not in the descriptor itself
