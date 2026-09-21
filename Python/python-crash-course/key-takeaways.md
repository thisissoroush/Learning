# Python Crash Course 3e — Key Takeaways

Quick reference per chapter, based on the actual book content.

---

## Part I — Basics

### Ch 1 — Getting Started
- Python files end in `.py`; run with `python filename.py` or `python3 filename.py`
- Indentation is syntax — it defines code blocks (4 spaces, not tabs)
- The Python REPL (`python`) is great for quick experiments

### Ch 2 — Variables and Data Types
- Variables are labels pointing to objects, not containers
- f-strings: `f"Hello, {name.title()}!"` — the modern way to embed variables
- `str.strip()`, `removeprefix()`, `removesuffix()` clean strings
- `10 / 3` = float; `10 // 3` = floor division; `**` = exponent; `%` = modulo
- UPPERCASE for constants (convention only — Python doesn't enforce it)

### Ch 3 — Introducing Lists
- Lists are 0-indexed; `-1` is the last element
- `append()` → end; `insert(i, val)` → at index; `pop()` → remove and return
- `remove(val)` removes the first occurrence by value
- `sort()` modifies in place; `sorted()` returns a new sorted list

### Ch 4 — Working with Lists
- `for item in list:` — indent the body (4 spaces)
- `range(start, stop, step)` — stop is exclusive
- List comprehension: `[x**2 for x in range(10)]` — concise and Pythonic
- `list[1:4]` — elements at index 1, 2, 3 (stop exclusive)
- `list[:]` makes a true copy; `list2 = list1` points to the same object
- Tuples `(a, b)` are immutable; use for data that must never change

### Ch 5 — if Statements
- `==` is case-sensitive; use `.lower()` for case-insensitive comparison
- `and` requires both True; `or` requires at least one; `not` negates
- `in` and `not in` test membership
- `elif` chain: only the first matching branch runs
- Empty list, `""`, `0`, `None` are all **falsy**

### Ch 6 — Dictionaries
- `dict.get('key', default)` avoids `KeyError`
- `.items()` → (key, value) pairs; `.keys()` → keys; `.values()` → values
- `for key in sorted(d.keys())` — iterate in sorted order
- `set(d.values())` — unique values only
- Python 3.7+ preserves insertion order

### Ch 7 — User Input and while Loops
- `input()` always returns a **string** — convert with `int()` / `float()`
- Use a **flag** variable for complex loop control
- `break` exits immediately; `continue` skips to next iteration
- `while my_list:` loops until list is empty

### Ch 8 — Functions
- Positional args: order matters; keyword args: name matters
- Default values must come after required parameters
- Pass `list[:]` to prevent a function from modifying the original
- `*args` → tuple of extra positional args; `**kwargs` → dict of extra keyword args
- Prefer `import module` over `from module import *`

### Ch 9 — Classes
- `__init__` runs automatically on instance creation; `self` = current instance
- `super().__init__(...)` calls parent `__init__` — always first in child
- Override parent methods by redefining them in the child class
- Use instances as attributes to split complex classes into collaborators

### Ch 10 — Files and Exceptions
- `pathlib.Path` is the modern cross-platform file API
- `path.read_text()` reads whole file; `path.write_text(contents)` writes/creates
- `try` → risky code; `except ExcType` → handle error; `else` → runs if try succeeded
- `pass` in `except` = silent fail (acceptable when failure is expected)
- `json.dumps(data)` → JSON string; `json.loads(text)` → Python object

### Ch 11 — Testing
- pytest discovers `test_*.py` files and `test_*` functions automatically
- One test function = one specific behavior
- Fix the **code** when a test fails, not the test
- `@pytest.fixture` creates shared setup objects injected into test functions

---

## Part II — Projects

### Ch 12–14 — Alien Invasion (Pygame)
- `clock.tick(60)` caps frame rate at 60 FPS — consistent across machines
- Store position as **float** for sub-pixel movement speed
- Use **flags** (`moving_right = True/False`) for smooth continuous movement
- `pygame.sprite.groupcollide(g1, g2, True, True)` removes both on collision
- `fleet_direction = 1` (right) / `-1` (left) — multiply by speed for direction
- `pygame.font.render(text, antialias, color)` → text surface to blit

### Ch 15–17 — Data Visualization
- `fig, ax = plt.subplots()` — modern matplotlib API
- `ax.fill_between(x, y1, y2)` fills area between two lines
- `plt.savefig('file.png', bbox_inches='tight')` saves without whitespace
- Plotly creates interactive HTML charts — `fig.write_html('chart.html')`
- `requests.get(url)` → HTTP call; `r.status_code == 200` = success; `r.json()` = parsed data
- `datetime.strptime(str, '%Y-%m-%d')` parses date strings

### Ch 18–20 — Learning Log (Django)
- Django MTV: **M**odels (data), **T**emplates (HTML), **V**iews (logic)
- `makemigrations` → creates migrations; `migrate` → applies them
- `auto_now_add=True` sets timestamp automatically on creation
- `{% url 'app:view_name' %}` generates URLs by name — no hardcoding
- `@login_required` redirects unauthenticated users to login
- `filter(owner=request.user)` — users see only their own data
- `Http404` for unauthorized access — doesn't reveal data existence
- `form.save(commit=False)` → create instance without saving; add fields then `.save()`
- `DEBUG = False` in production; use environment variables for secrets
