# Chapter 3 — Dictionaries and Sets

> *"Dictionaries are so widely used in Python that the CPython implementation has been fine-tuned for them over the years."*

---

## 🎯 Core Concept

`dict` and `set` are built on hash tables — understanding how hashing works explains their O(1) average performance, their ordering guarantees (Python 3.7+), and the rules for what can be a key.

---

## 🔧 Modern dict Syntax

```python
# dict comprehension
dial_codes = {
    'BD': 880, 'BR': 55, 'CN': 86,
    'IN': 91, 'US': 1,  'JP': 81,
}
country_by_dial = {code: country for country, code in dial_codes.items()}

# Unpacking into dict literals (Python 3.9+)
defaults = {'timeout': 30, 'retries': 3}
custom   = {'retries': 5, 'verbose': True}
config   = {**defaults, **custom}   # {'timeout': 30, 'retries': 5, 'verbose': True}
# custom values override defaults

# Merge operator | (Python 3.9+)
merged = defaults | custom          # same result
defaults |= custom                  # in-place merge
```

---

## 🗄️ Standard Mapping API

```python
d = {'a': 1, 'b': 2}

# Safe access
d.get('x', 0)           # 0 (not KeyError)
d.setdefault('c', []).append(3)   # get or insert, then append

# Checking
'a' in d                # True  (tests keys, O(1))
'a' not in d            # False

# Views (live, not copies)
d.keys()                # dict_keys(['a', 'b'])
d.values()              # dict_values([1, 2])
d.items()               # dict_items([('a', 1), ('b', 2)])

# Update
d.update({'c': 3})
d['d'] = 4

# Pop
d.pop('a')              # 1 — removes and returns
d.popitem()             # removes last inserted item (LIFO)
```

---

## 🔑 What Is Hashable?

An object is hashable if:
1. It has a `__hash__()` method that returns an integer that never changes during its lifetime
2. It has an `__eq__()` method comparable to other objects

```python
# Hashable — can be dict keys and set members
hash(1)           # 1
hash('hello')     # some int
hash((1, 2))      # tuple of hashables → hashable

# Not hashable — mutable containers
hash([1, 2])      # TypeError: unhashable type: 'list'
hash({'a': 1})    # TypeError: unhashable type: 'dict'
hash({1, 2})      # TypeError: unhashable type: 'set'

# frozenset IS hashable
hash(frozenset([1, 2, 3]))   # works!
```

---

## 🚪 Handling Missing Keys

```python
# 1. setdefault — insert default on miss, return value
word_index = {}
for word in text.split():
    word_index.setdefault(word, []).append(location)
# Equivalent but more concise than get + assign

# 2. defaultdict — auto-creates default on __getitem__ miss
from collections import defaultdict
word_index = defaultdict(list)
for word in text.split():
    word_index[word].append(location)   # list created automatically on first access

# 3. __missing__ — hook called by __getitem__ on miss
class StrKeyDict(dict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]     # try string version of the key

    def get(self, key, default=None):
        try:
            return self[key]      # delegates to __getitem__ → __missing__
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys() or str(key) in self.keys()

d = StrKeyDict({'2': 'two', '4': 'four'})
d[2]          # 'two'  — int key → __missing__ → tries '2'
d.get(2)      # 'two'
2 in d        # True
```

---

## 📦 Variations of `dict`

```python
from collections import OrderedDict, ChainMap, Counter
import shelve

# OrderedDict — preserves insertion order AND has move_to_end
od = OrderedDict(a=1, b=2)
od.move_to_end('a')        # move 'a' to the end
od.move_to_end('b', last=False)  # move 'b' to front

# ChainMap — logical merge of multiple dicts (first match wins)
import os
app_config = {'debug': False, 'port': 8080}
env_config  = {'port': 9090}
cli_config  = {'debug': True}
config = ChainMap(cli_config, env_config, app_config)
config['port']   # 9090 — env_config wins over app_config
config['debug']  # True  — cli_config wins

# Counter — counts hashable objects
from collections import Counter
ct = Counter('abracadabra')
ct.most_common(3)   # [('a', 5), ('b', 2), ('r', 2)]
ct['a']             # 5
ct.update('aaaaaa') # add more counts
ct + Counter('abcd') # add two counters

# UserDict — subclass this, not dict
from collections import UserDict
class TransformDict(UserDict):
    def __setitem__(self, key, value):
        self.data[key.lower()] = value   # store keys as lowercase

    def __getitem__(self, key):
        return self.data[key.lower()]
```

---

## 🔍 Dictionary Views

```python
d1 = {'a': 1, 'b': 2}
d2 = {'b': 2, 'c': 3}

# Views support set operations
d1.keys() & d2.keys()    # {'b'} — intersection
d1.keys() | d2.keys()    # {'a', 'b', 'c'} — union
d1.keys() - d2.keys()    # {'a'} — difference

# Views are dynamic — reflect current dict state
keys = d1.keys()
d1['z'] = 99
print(keys)    # dict_keys(['a', 'b', 'z']) — updated!
```

---

## ∞ Set Theory

```python
# Literals
s = {1, 2, 3}
empty = set()       # NOT {} (that's an empty dict)

# Set comprehension
{x**2 for x in range(10) if x % 2 == 0}   # {0, 4, 16, 36, 64}

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b       # {1, 2, 3, 4, 5, 6}  union
a & b       # {3, 4}              intersection
a - b       # {1, 2}              difference (in a, not in b)
a ^ b       # {1, 2, 5, 6}       symmetric difference
a <= b      # subset check
a < b       # proper subset
a >= b      # superset check
```

---

## 💡 How Hash Tables Work (Internals)

```
dict storage (simplified):
  hash(key) % table_size → bucket index
  Collision → probe next bucket (open addressing)
  Load factor ~2/3 → resize (double) to keep lookups fast

Practical consequences:
  ✅ O(1) average for get/set/delete/in
  ⚠️  Key objects must be IMMUTABLE and HASHABLE
  ⚠️  Memory overhead (hash table is sparse by design)
  ✅ Insertion order preserved since Python 3.7 (CPython 3.6)
  ⚠️  Iterating while adding keys → RuntimeError
```

---

## 🔑 Key Takeaways

- Use `d.get(key, default)` to avoid `KeyError` on optional keys
- `defaultdict(list)` is cleaner than `setdefault()` for grouping
- Subclass `UserDict`, not `dict`, for custom mappings (avoids override pitfalls)
- `Counter` and `ChainMap` solve common problems elegantly
- Sets are backed by hash tables — membership test `x in s` is O(1), not O(n) like lists
- Dict views (`keys()`, `values()`, `items()`) support set operations and are live
