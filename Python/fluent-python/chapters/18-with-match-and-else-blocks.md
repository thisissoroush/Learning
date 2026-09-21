# Chapter 18 — `with`, `match`, and `else` Blocks

> *"The with statement is designed to simplify the try/finally pattern."*

---

## 🎯 Core Concept

Context managers (`with`) guarantee cleanup even on exceptions. `match/case` provides powerful structural pattern matching. `else` on loops and `try` blocks reduces flag variables.

---

## 🔒 Context Managers

```python
# Context manager protocol: __enter__ + __exit__
class LookingGlass:
    def __enter__(self):
        import sys
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write
        return 'JABBERWOCKY'   # bound to 'as' target

    def reverse_write(self, text):
        self.original_write(text[::-1])

    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        sys.stdout.write = self.original_write
        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True    # suppress the exception
        return False       # propagate other exceptions

with LookingGlass() as what:
    print('Alice, Kitty and Snowdrop')   # pordwonS dna yttiK ,ecilA
    print(what)                          # YKCOWREBBAJ
# back to normal here
```

---

## 🎛️ `@contextmanager`

```python
from contextlib import contextmanager

@contextmanager
def looking_glass():
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'    # value bound to 'as' target
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
    finally:
        sys.stdout.write = original_write  # always restore
        if msg:
            print(msg)

with looking_glass() as what:
    print('Alice, Kitty')    # yttiK ,ecilA

# @contextmanager turns a generator into a context manager:
#   before yield → __enter__
#   yield value → bound to 'as' target
#   after yield → __exit__ (including exceptions)
```

---

## 🎯 Structural Pattern Matching (`match`/`case`)

```python
# match/case deconstructs data structures

def evaluate(exp, env):
    match exp:
        case int(x):                        # numeric literal
            return x
        case Symbol(id=name):               # symbol lookup
            return env[name]
        case ['if', test, consequence, alternative]:
            if evaluate(test, env):
                return evaluate(consequence, env)
            else:
                return evaluate(alternative, env)
        case ['lambda', [*parms], *body]:   # lambda expression
            return Procedure(parms, body, env)
        case ['define', Symbol(id=name), value_exp]:
            env[name] = evaluate(value_exp, env)
        case [func_exp, *args]:             # function call
            proc = evaluate(func_exp, env)
            return proc(*(evaluate(a, env) for a in args))
        case _:
            raise SyntaxError(exp)

# OR patterns
def handle_status(status):
    match status:
        case 400 | 401 | 403:
            return 'client error'
        case 500 | 502 | 503:
            return 'server error'
        case 200 | 201 | 204:
            return 'success'
```

---

## 🔁 `else` Beyond `if`

```python
# for...else: else runs if loop completed WITHOUT break
for item in items:
    if item.value > threshold:
        break
else:
    raise ValueError('No item above threshold')   # no break occurred

# while...else: else runs if condition became False (not via break)
i = 0
while i < 10:
    if data[i] == target:
        break
    i += 1
else:
    raise LookupError('target not found')

# try...else: else runs if NO exception was raised in try block
try:
    dangerous_call()
except ValueError as e:
    handle_error(e)
else:
    # only runs if no exception — keep try block minimal
    process_result()
finally:
    cleanup()    # always runs
```

---

## 🔑 Key Takeaways

- Context managers guarantee cleanup: `__exit__` is called even on exception
- `@contextmanager` turns a generator with one `yield` into a context manager — cleaner than a class
- Return `True` from `__exit__` to suppress an exception; `False`/`None` to propagate
- Pattern matching (`match`) deconstructs: literals, classes, sequences, mappings, OR patterns, guards (`if`)
- `for/else`, `while/else`: `else` runs on natural completion (no `break`)
- `try/else`: `else` runs when `try` succeeds — put only truly risky code in `try`
