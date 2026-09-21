# Chapter 12 — Special Methods for Sequences

> *"Don't check whether it IS-a duck: check whether it QUACKS-like-a duck."*

---

## 🎯 Core Concept

By implementing `__len__` and `__getitem__`, your class becomes a sequence that works with `len()`, indexing, slicing, iteration, `in`, `sorted()`, and `reversed()` — automatically, through duck typing.

---

## 🦆 Protocols and Duck Typing

```
In Python, a protocol is an informal interface defined by convention.
The sequence protocol is: __len__ + __getitem__

If your class has these, Python treats it as a sequence everywhere.
No inheritance required.
```

```python
class Card:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

class FrenchDeck:
    def __init__(self):
        self._cards = [Card(r, s) for s in Card.suits for r in Card.ranks]

    def __len__(self):       # len(deck) works
        return len(self._cards)

    def __getitem__(self, pos):  # deck[0], deck[-1], deck[1:3] all work
        return self._cards[pos]

deck = FrenchDeck()
len(deck)            # 52
deck[0]              # Card('2', 'spades')
deck[-1]             # Card('A', 'hearts')
deck[12::13]         # all aces
for card in deck:    # iteration — no __iter__ needed!
    print(card)
random.choice(deck)  # works
sorted(deck)         # works
```

---

## 🔪 How Slicing Works

```python
class MySeq:
    def __getitem__(self, index):
        return index    # just echo to see what's passed

s = MySeq()
s[1]      # 1          — plain int
s[1:4]    # slice(1, 4, None)
s[1:4:2]  # slice(1, 4, 2)
s[1:4:2, 7:9]  # (slice(1, 4, 2), slice(7, 9, None))  — multi-dim (numpy)

# Proper slice-aware __getitem__
class Vector:
    def __getitem__(self, index):
        if isinstance(index, slice):
            cls = type(self)
            return cls(self._components[index])   # return same type
        index = operator.index(index)             # raises TypeError for floats
        return self._components[index]
```

---

## 🔮 Dynamic Attribute Access

```python
class Vector:
    shortcut_names = 'xyzt'

    def __getattr__(self, name):
        cls = type(self)
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            if 0 <= pos < len(self._components):
                return self._components[pos]
        raise AttributeError(f'{cls.__name__!r} object has no attribute {name!r}')

    def __setattr__(self, name, value):
        cls = type(self)
        if len(name) == 1:
            if name in cls.shortcut_names:
                error = 'readonly attribute {attr_name!r}'
            elif name.islower():
                error = "can't set attributes 'a' to 'z' in {cls_name!r}"
            else:
                error = ''
            if error:
                raise AttributeError(error.format(cls_name=cls.__name__, attr_name=name))
        super().__setattr__(name, value)

v = Vector(range(5))
v.x    # 0  — via __getattr__
v.y    # 1
v.x = 10  # AttributeError — protected via __setattr__
```

---

## 🔑 Key Takeaways

- The sequence protocol (`__len__` + `__getitem__`) gives you iteration, slicing, `in`, `sorted` for free
- `__getattr__` is called only when normal attribute lookup fails — not on every access
- Always pair `__getattr__` with `__setattr__` to prevent inconsistent state
- Use `operator.index(i)` in `__getitem__` to reject floats as indices
- Return the same type from slicing: `Vector[1:3]` should return a `Vector`, not a list
- Duck typing is the Python way — implement the protocol, not inherit the class
