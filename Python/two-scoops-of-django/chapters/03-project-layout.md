# Chapter 3 — How to Lay Out Django Projects

> *"Django's default project layout is a starting point, not an ending point. Modify it for real projects."*

---

## 🎯 Core Concept

Django's `startproject` generates a workable layout, but it conflates the configuration and project directories in ways that cause problems at scale. The **Two Scoops recommended layout** separates the repository root, project root, and configuration root into distinct directories.

---

## ❌ Django's Default Layout (The Problem)

```bash
$ django-admin startproject mysite
$ django-admin startapp my_app
```

Produces:
```
mysite/               ← repo root AND project root (confused!)
├── manage.py
├── my_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── mysite/           ← configuration root (same name as repo root!)
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

**Problems:**
1. Repo root and project root have the same name → confusing
2. No clear place for docs, requirements, Makefile, etc.
3. Hard to add multiple apps cleanly

---

## ✅ The Two Scoops Recommended Layout

```
<repository_root>/          ← Git repository, README, Makefile, etc.
├── .gitignore
├── Makefile
├── README.md
├── requirements/           ← Organized requirements files
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── docs/                   ← Project documentation
├── manage.py               ← Django management command entry point
│
├── <django_project_root>/  ← Django project (named after your project)
│   ├── __init__.py
│   ├── settings/           ← MOVED: multiple settings files
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
└── apps/                   ← All Django apps live here
    ├── accounts/
    ├── flavors/
    └── stores/
```

---

## 📂 Three Levels Explained

### Level 1: Repository Root

Everything the project needs to exist as a codebase:

```
<repository_root>/
├── README.md               ← Project documentation, setup instructions
├── requirements/           ← Dependency files
├── .gitignore              ← Files excluded from version control
├── Makefile                ← Common tasks (make test, make migrate)
├── docs/                   ← Technical documentation
└── manage.py               ← Django entry point
```

### Level 2: Django Project Root

The actual Django project — Python code:

```
<django_project_root>/
├── settings/               ← Configuration per environment
├── urls.py                 ← URL configuration
├── wsgi.py                 ← WSGI entry point
└── asgi.py                 ← ASGI entry point (async Django)
```

### Level 3: Configuration Root

Settings module (now a package for multiple environments):

```
settings/
├── __init__.py     ← Empty, makes settings a Python package
├── base.py         ← Common to all environments
├── local.py        ← Development only
├── staging.py      ← Staging environment
└── production.py   ← Production only
```

---

## 🍪 Sample Project: icecreamlandia

```
icecreamlandia/              ← Repository root
├── README.md
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── docs/
│   └── api.md
│
├── config/                  ← Configuration root (renamed from project name)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
└── icecreamlandia/          ← Django project root
    ├── flavors/
    │   ├── models.py
    │   ├── views.py
    │   └── tests/
    ├── stores/
    └── users/
```

---

## 🔧 Cookiecutter Django — Bootstrap Your Project

Instead of `startproject`, use [Cookiecutter Django](https://cookiecutter-django.readthedocs.io/):

```bash
$ pip install cookiecutter
$ cookiecutter gh:cookiecutter/cookiecutter-django

# Creates a complete professional Django project with:
# ✓ Proper directory structure
# ✓ Multiple settings files (base/local/production)
# ✓ Requirements split (base/local/production)
# ✓ Docker support
# ✓ PostgreSQL configured
# ✓ Custom user model
# ✓ Pre-configured admin
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Three levels** | Repository root → Project root → Config root |
| **Split settings** | base.py (common) + local.py + production.py |
| **Split requirements** | base.txt + local.txt + production.txt |
| **Rename configuration root** | Call it `config/` not same name as project |
| **Cookiecutter Django** | Best way to start a professional project |

---

*← [Back to Two Scoops of Django](../README.md)*
