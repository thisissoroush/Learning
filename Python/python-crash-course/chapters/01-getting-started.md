# Chapter 1 — Getting Started

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Setting up Python 3, VS Code, and running your first program. Understanding how to use the terminal to run Python scripts.

---

## 🐍 Your First Program

```python
# hello_world.py
print("Hello, Python world!")
```

Run it from the terminal:
```bash
python hello_world.py
# Hello, Python world!
```

---

## 🖥️ Running Python in Different Ways

```python
# 1. Interactive Python shell (REPL)
# Type python or python3 in terminal
>>> print("Hello")
Hello
>>> 1 + 2
3

# 2. Running a .py file
# python filename.py

# 3. Inside VS Code
# Click Run Python File ▶ or press Ctrl+F5
```

---

## 🔧 Python on Different Systems

```bash
# Check Python version
python --version       # Windows
python3 --version      # macOS/Linux

# Python 3.11+ recommended for this book
```

---

## ⚠️ Common Beginner Errors

```python
# SyntaxError — misspelled keyword or missing syntax
prnt("Hello")       # NameError: name 'prnt' is not defined

# Indentation matters in Python!
if True:
print("Hello")      # IndentationError
# Fix:
if True:
    print("Hello")  # correct
```

---

## 🔑 Key Takeaways

- Python is free, cross-platform, and beginner-friendly
- VS Code with the Python extension is the recommended editor
- `print()` outputs text; the Python REPL is great for quick experiments
- Every Python file ends in `.py`
- Indentation is syntax in Python — it defines code blocks
