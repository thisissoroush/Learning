# Chapter 10 — Files and Exceptions

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Reading and writing files with `pathlib`, handling exceptions with `try/except`, storing data as JSON.

---

## 📂 Reading Files with `pathlib`

```python
from pathlib import Path

# Read entire file as a string
path = Path('pi_digits.txt')
contents = path.read_text()
print(contents)

# Strip trailing whitespace
print(contents.rstrip())

# Relative vs absolute paths
path = Path('text_files/filename.txt')          # relative
path = Path('/home/eric/data/filename.txt')     # absolute

# Access each line
lines = contents.splitlines()
for line in lines:
    print(line)

# Build a string from lines
pi_string = ''
for line in lines:
    pi_string += line.lstrip()   # remove leading whitespace
print(pi_string)
print(len(pi_string))

# Search file contents
birthday = input("Enter your birthday (mmddyy): ")
if birthday in pi_string:
    print("Your birthday appears in the first million digits of pi!")
else:
    print("Your birthday does not appear in the first million digits of pi.")
```

---

## ✍️ Writing Files

```python
from pathlib import Path

# Write a single line (overwrites existing content)
path = Path('programming.txt')
path.write_text("I love programming.")

# Write multiple lines — join with \n
contents = "I love programming.\n"
contents += "I love creating new games.\n"
contents += "I also love working with data.\n"
path.write_text(contents)
```

---

## ⚠️ Exceptions

```python
# ZeroDivisionError
try:
    print(5/0)
except ZeroDivisionError:
    print("You can't divide by zero!")

# try-except-else pattern
print("Give me two numbers, and I'll divide them.")
print("Enter 'q' to quit.")

while True:
    first_number = input("\nFirst number: ")
    if first_number == 'q':
        break
    second_number = input("Second number: ")
    if second_number == 'q':
        break
    try:
        answer = int(first_number) / int(second_number)
    except ZeroDivisionError:
        print("You can't divide by 0!")
    else:
        print(answer)      # only runs if try succeeded

# FileNotFoundError
path = Path('alice.txt')
try:
    contents = path.read_text(encoding='utf-8')
except FileNotFoundError:
    print(f"Sorry, the file {path} does not exist.")

# Working with multiple files
def count_words(path):
    try:
        contents = path.read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"Sorry, the file {path} does not exist.")
    else:
        words = contents.split()
        num_words = len(words)
        print(f"The file {path} has about {num_words} words.")

filenames = ['alice.txt', 'siddhartha.txt', 'moby_dick.txt']
for filename in filenames:
    count_words(Path(filename))

# Failing silently — suppress the error
def count_words(path):
    try:
        contents = path.read_text(encoding='utf-8')
    except FileNotFoundError:
        pass    # do nothing — silent fail
    else:
        ...
```

---

## 💾 Storing Data with JSON

```python
import json
from pathlib import Path

# Save data
numbers = [2, 3, 5, 7, 11, 13]
path = Path('numbers.json')
contents = json.dumps(numbers)
path.write_text(contents)

# Load data
contents = path.read_text()
numbers = json.loads(contents)
print(numbers)   # [2, 3, 5, 7, 11, 13]

# Real example: remember a username
def get_stored_username(path):
    """Get stored username if available."""
    if path.exists():
        contents = path.read_text()
        username = json.loads(contents)
        return username
    return None

def greet_user():
    path = Path('username.json')
    username = get_stored_username(path)
    if username:
        print(f"Welcome back, {username}!")
    else:
        username = input("What is your name? ")
        contents = json.dumps(username)
        path.write_text(contents)
        print(f"We'll remember you when you come back, {username}!")

greet_user()
```

---

## 🔑 Key Takeaways

- `pathlib.Path` is the modern, cross-platform way to work with files
- `path.read_text()` reads the whole file; `.splitlines()` gives a list of lines
- `path.write_text(contents)` creates or overwrites a file
- `try` block: risky code; `except ExcType:` handles the error; `else:` runs if no error
- `pass` in `except` silently ignores an error — use when failure is expected/acceptable
- `json.dumps(data)` converts Python object → JSON string; `json.loads(text)` does the reverse
- `path.exists()` checks if a file exists before trying to read it
