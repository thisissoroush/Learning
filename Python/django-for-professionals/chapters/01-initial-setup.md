# Chapter 1 — Initial Set Up

> *"Configuring a software development environment is no easy task. You should now have Python 3, Git, and a modern text editor all installed and configured."*

---

## 🎯 Core Concept

Before writing a single line of Django code, you need a **properly configured development machine**. This chapter sets up the three pillars of modern Django development:

1. **The Command Line** — your primary interface with Django
2. **Python 3** — the language Django runs on
3. **Git** — version control from day zero

---

## 🖥️ The Command Line

The command line isn't optional for professional Django development. Every important Django task happens here:

```
Running servers:          python manage.py runserver
Database migrations:      python manage.py migrate
Creating superusers:      python manage.py createsuperuser
Running tests:            python manage.py test
Docker operations:        docker-compose up -d
Dependency management:    pip install django
```

**macOS/Linux:** Use Terminal (Bash or Zsh)  
**Windows:** Use PowerShell or WSL (Windows Subsystem for Linux)

### Essential Commands to Know

```bash
# Navigate directories
$ pwd                    # Print working directory
$ ls                     # List files
$ cd myproject           # Change directory
$ cd ..                  # Go up one level

# File operations
$ mkdir mydir            # Create directory
$ touch myfile.txt       # Create empty file
$ cat myfile.txt         # Print file contents

# Install Python packages
$ pip install django
$ pip freeze > requirements.txt
```

---

## 🐍 Python 3

**Always use Python 3.** Python 2 reached end-of-life in 2020. All modern Django development uses Python 3.

### Virtual Environments — Why They Matter

```
Without virtual environments (BAD):
System Python ──→ Django 4.0 installed globally
                  If you upgrade to Django 4.1, all projects break!

With virtual environments (GOOD):
Project A ──→ .venv/ ──→ Django 4.0, Python 3.10
Project B ──→ .venv/ ──→ Django 3.2, Python 3.9
Each project is isolated. No conflicts.
```

### Creating a Virtual Environment

```bash
# Create virtual environment
$ python3 -m venv .venv

# Activate it
$ source .venv/bin/activate    # macOS/Linux
$ .venv\Scripts\Activate.ps1   # Windows

# Your prompt changes to show the active venv:
(.venv) $

# Install Django into this venv
(.venv) $ pip install django~=4.0.0

# Save dependencies
(.venv) $ pip freeze > requirements.txt

# Deactivate when done
(.venv) $ deactivate
```

> ⚠️ **Note:** In most of this book, Docker replaces the local virtual environment for running the app. But you still need Python locally for the initial `django-admin startproject` command.

---

## 📝 Text Editor: VS Code

The book recommends VS Code with two essential extensions:

| Extension | Purpose |
|-----------|---------|
| **Python** (by Microsoft) | Syntax highlighting, linting, autocomplete |
| **Docker** (by Microsoft) | Dockerfile and docker-compose.yml support |

---

## 🔀 Git: Version Control from Day One

Every professional Django project uses Git. Never start a project without it.

### One-Time Setup

```bash
# Set your identity (used in every commit)
$ git config --global user.name "Your Name"
$ git config --global user.email "yourname@email.com"

# Set default branch name
$ git config --global init.defaultBranch main
```

### The Workflow Used in Every Chapter

```bash
# Start of chapter: check current state
$ git status

# After making changes: stage and commit
$ git add .
$ git commit -m "ch1 initial setup"
```

### Why Version Control Matters

```
Without Git:                        With Git:
"It was working yesterday..."  →    git log → find exact commit
"Who changed this?"            →    git blame → see every change
"I broke everything!"          →    git checkout . → instantly undo
"Deploy this feature"          →    git push → automated pipeline
```

---

## 🔄 The Professional Setup Flow

```
Install Python 3
      ↓
Create virtual environment (.venv)
      ↓
Activate virtual environment
      ↓
Install Django
      ↓
Create Django project (django-admin startproject)
      ↓
Initialize Git repository (git init)
      ↓
Create .gitignore (exclude .venv, __pycache__, .env)
      ↓
First commit (git add . && git commit -m "initial")
      ↓
Switch to Docker (next chapter)
```

---

## 📋 What Goes in .gitignore

```gitignore
# Virtual environment
.venv/

# Python bytecode
__pycache__/
*.pyc

# Environment variables (NEVER commit these)
.env

# Database files
db.sqlite3

# Editor files
.vscode/
.idea/

# OS files
.DS_Store
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Always use Python 3** | Python 2 is dead — no exceptions |
| **Virtual environments are mandatory** | Isolate dependencies per project |
| **Git from day one** | Version control is not optional |
| **Learn the command line** | GUI tools won't help you in production |
| **Save requirements** | `pip freeze > requirements.txt` before Docker |

---

*← [Back to Django for Professionals](../README.md)*
