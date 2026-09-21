# Chapter 2 — Variables and Simple Data Types

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Variables, strings, numbers, constants, comments, and the Zen of Python.

---

## 📦 Variables

```python
message = "Hello, Python world!"
print(message)         # Hello, Python world!

message = "Hello, Python Crash Course!"
print(message)         # reassigned — variables can change

# Naming rules:
# - Letters, numbers, underscores only
# - Cannot start with a number
# - No spaces (use underscores: my_variable)
# - Cannot be a keyword (if, for, while...)
# - Lowercase with underscores (snake_case) — PEP 8 convention
```

**Variables are labels** — they point to objects, not contain values. Reassigning a variable just moves the label.

---

## 🔤 Strings

```python
"This is a string"
'This is also a string'

name = "ada lovelace"

# Case methods
name.title()     # 'Ada Lovelace'
name.upper()     # 'ADA LOVELACE'
name.lower()     # 'ada lovelace'

# f-strings (Python 3.6+) — the modern way
first = "ada"
last = "lovelace"
full_name = f"{first} {last}"
print(f"Hello, {full_name.title()}!")   # Hello, Ada Lovelace!

# Whitespace
print("Languages:\n\tPython\n\tJavaScript")
# Languages:
#     Python
#     JavaScript

# Stripping whitespace
name = "   python   "
name.rstrip()     # '   python'
name.lstrip()     # 'python   '
name.strip()      # 'python'

# Removing prefixes/suffixes (Python 3.9+)
url = "https://python.org"
url.removeprefix("https://")    # 'python.org'

filename = "my_script.py"
filename.removesuffix(".py")    # 'my_script'
```

---

## 🔢 Numbers

```python
# Integers
2 + 3      # 5
3 - 2      # 1
2 * 3      # 6
3 / 2      # 1.5  (always float division)
3 ** 2     # 9    (exponent)
10 % 3     # 1    (modulo — remainder)

# Floats
0.1 + 0.2  # 0.30000000000000004  (floating point!)
round(0.1 + 0.2, 2)  # 0.3

# Underscores in numbers (Python 3.6+) — readability
universe_age = 14_000_000_000
print(universe_age)   # 14000000000

# Multiple assignment
x, y, z = 0, 0, 0

# Constants — UPPERCASE by convention (Python has no true constants)
MAX_CONNECTIONS = 5_000
PI = 3.14159
```

---

## 💬 Comments

```python
# This is a single-line comment

# Write comments that explain WHY, not WHAT:
# Bad: x = x + 1  # increment x by 1
# Good: x = x + 1  # move x one step to the right

# TODO: add input validation here
```

---

## 🧘 The Zen of Python

```python
import this
# Beautiful is better than ugly.
# Explicit is better than implicit.
# Simple is better than complex.
# Readability counts.
# Errors should never pass silently.
# ...
```

---

## 🔑 Key Takeaways

- Variable names: snake_case, descriptive, no keywords
- f-strings: `f"Hello, {variable}"` — cleaner than concatenation
- `str.strip()` / `removeprefix()` / `removesuffix()` for string cleaning
- `10 / 3` = `3.333...` (float); `10 // 3` = `3` (floor division)
- `**` is exponent; `%` is modulo (remainder)
- Constants in UPPERCASE by convention — Python doesn't enforce it
- Comments explain *why*, not *what*
