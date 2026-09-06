# Chapter 2 — The Optimal Django Environment Setup

> *"What works on a programmer's laptop might not work in production. Use the same database and tools everywhere."*

---

## 🎯 Core Concept

The root cause of "it works on my machine" bugs is **environment differences**. This chapter establishes the tools that eliminate those differences: the same database everywhere, pip for dependencies, virtualenv for isolation, Git for version control, and Docker for full parity.

---

## 🗄️ Rule #1: Same Database in Dev and Production

The most important rule in this chapter:

```
❌ Development: SQLite  →  Production: PostgreSQL
✅ Development: PostgreSQL  →  Production: PostgreSQL

Why?
- SQLite has no user permissions system
- SQLite doesn't enforce strict types the same way
- PostgreSQL has features (JSONB, full-text, arrays) SQLite lacks
- Bugs that appear in PostgreSQL are invisible in SQLite
```

### Concrete Example of the Problem

```python
# Works on SQLite, fails on PostgreSQL:
MyModel.objects.filter(name__icontains=some_variable)

# If some_variable is None:
# SQLite: silently returns all results (wrong!)
# PostgreSQL: raises OperationalError (correct — fails fast!)
```

**Fixtures are not the solution.** Fixtures are data snapshots, not environment parity.

---

## 📦 Rule #2: pip + virtualenv/venv

```bash
# Create isolated environment per project
$ python3 -m venv .venv

# Activate
$ source .venv/bin/activate

# Install project dependencies
$ pip install django~=3.2
$ pip install djangorestframework
$ pip install psycopg2-binary

# Freeze exact versions (very important!)
$ pip freeze > requirements.txt
```

### Pin Your Requirements

```
# requirements.txt — pin exact versions for reproducibility
Django==3.2.13
djangorestframework==3.13.1
psycopg2-binary==2.9.3

# NOT:
Django>=3.0  ← This could install Django 4.0 and break your app!
```

---

## 🔗 Rule #3: Version Control with Git

```bash
# Initialize git in every project
$ git init

# Essential .gitignore for Django:
echo ".venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
db.sqlite3
.env
*.log
media/
staticfiles/" > .gitignore

# First commit
$ git add .
$ git commit -m "initial django project"
```

**Recommended hosting**: GitHub or GitLab. Always have a remote backup.

---

## 🐳 Rule #4: Identical Environments with Docker

Docker eliminates three types of environment differences:

```
1. Operating System differences
   Dev: macOS → Prod: Ubuntu Linux
   Without Docker: "Works on my Mac but not on the server"
   With Docker: Same Linux container everywhere

2. Python setup differences
   Dev: Python 3.9 → Prod: Python 3.8
   Without Docker: Version-specific bugs
   With Docker: Exact Python version pinned in Dockerfile

3. Developer-to-developer differences
   New developer joins: spends 2 days setting up
   Without Docker: Long README, multiple failures
   With Docker: docker-compose up → everything works
```

---

## 📁 Virtual Environment Location

```
# Keep virtualenv OUT of the project directory
$ python3 -m venv ~/.venvs/myproject

# OR use virtualenvwrapper for nice commands:
$ pip install virtualenvwrapper
$ mkvirtualenv myproject
$ workon myproject
$ deactivate

# Why NOT in project directory?
# - Accidentally committing .venv to git
# - Confusion with project files
# - Most tools handle external venvs better
```

---

## 💡 Key Takeaways

| Rule | Rationale |
|------|-----------|
| **Same DB in dev and prod** | Different DBs = hidden bugs that surface in production |
| **Fixtures ≠ DB parity** | Fixtures are data, not engine behavior |
| **Pin exact versions** | `Django==3.2.13` not `Django>=3.0` |
| **Git from day zero** | Version control is not optional |
| **Docker for team environments** | Eliminates "works on my machine" entirely |

---

*← [Back to Two Scoops of Django](../README.md)*
