# Chapter 2 — Docker Hello, World!

> *"With Docker it's finally possible to faithfully and dependably reproduce a production environment locally — from the proper Python version to installing Django and running additional services like a production-level database."*

---

## 🎯 Core Concept

**Docker solves the "works on my machine" problem.** By packaging your application and all its dependencies into a container, Docker guarantees that every developer on the team — and production — runs the exact same environment.

---

## 🐳 What Is Docker?

### The Virtualization Hierarchy

```
Physical Server
│
├── Traditional Virtual Machines (VMs):
│   ├── Guest OS 1 (700MB+)  ← Each VM has its own full OS
│   ├── Guest OS 2 (700MB+)
│   └── Guest OS 3 (700MB+)
│
└── Docker Containers:
    ├── Shared Linux Kernel   ← All containers share the host OS
    ├── Container 1 (app)     ← Only application differences
    └── Container 2 (db)      ← Much lighter than full VMs
```

### The Apartment Analogy

> 🏠 **Virtual Machines** = Houses (full infrastructure per tenant)
> 🏢 **Docker Containers** = Apartments (shared infrastructure, isolated units)

Containers are faster to start, use less disk space, and are more portable than VMs.

---

## 🔧 Virtual Environments vs. Containers

This is a common point of confusion:

| Feature | Virtual Environment | Docker Container |
|---------|--------------------|--------------------|
| **Isolates** | Python packages only | Everything (OS, Python, DB, services) |
| **DB isolation** | ❌ No | ✅ Yes |
| **Cross-platform** | ❌ Still needs same OS | ✅ Runs same on Mac/Win/Linux |
| **Team sharing** | README with steps | Just share Dockerfile + docker-compose.yml |
| **Production parity** | Low (different OS) | High (same container in prod) |

**Use both:** virtual envs for local initial setup, Docker for running the app.

---

## 📄 The Dockerfile — Blueprint for Your Image

A `Dockerfile` is a recipe for building a Docker **image** (a snapshot of your application environment):

```dockerfile
# Dockerfile

# 1. Start from a base Python image
FROM python:3.10.4-slim-bullseye

# 2. Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1  # Don't nag about pip updates
ENV PYTHONDONTWRITEBYTECODE 1        # No .pyc files
ENV PYTHONUNBUFFERED 1               # See logs in real-time

# 3. Set working directory inside container
WORKDIR /code

# 4. Install Python dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# 5. Copy project code
COPY . .
```

### Layer Caching — Why Order Matters

```
Dockerfile layers (each line = a layer):

FROM python → cached ✓
ENV ...     → cached ✓
WORKDIR     → cached ✓
COPY requirements.txt → cached ✓ (only invalidated when requirements change)
RUN pip install → cached ✓ (expensive! only runs when requirements.txt changes)
COPY . .   → runs every build (code changes constantly)

Rule: Put stable layers first, changing layers last
```

---

## 🐙 docker-compose.yml — Orchestrating Multiple Services

`docker-compose.yml` defines the services your application needs and how they connect:

```yaml
# docker-compose.yml
version: "3.9"

services:
  web:                           # Our Django application
    build: .                     # Build from Dockerfile in current directory
    command: python /code/manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code                  # Sync local code with container (live reload!)
    ports:
      - 8000:8000                # Map host port 8000 to container port 8000
    environment:
      - DEBUG=True
```

---

## 🚀 Essential Docker Commands

```bash
# Build the image from Dockerfile
$ docker build .

# Start containers (foreground - see logs)
$ docker-compose up

# Start containers (background - detached mode)
$ docker-compose up -d

# Stop containers
$ docker-compose down

# View logs (important when running detached)
$ docker-compose logs

# Run a management command inside the container
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
$ docker-compose exec web python manage.py test

# Rebuild after adding new dependencies
$ docker-compose up -d --build
```

---

## 📁 .dockerignore — Exclude Unnecessary Files

```dockerignore
# .dockerignore
.venv         # Don't copy local virtual env into container
.git          # Don't include git history (saves space)
.gitignore
```

---

## 🔄 The Django + Docker Workflow

```
Developer writes code
         ↓
Code saved to local filesystem
         ↓
Docker volumes sync local → container (instant!)
         ↓
Django dev server sees changes (auto-reload)
         ↓
Browser at localhost:8000 shows updates

No docker-compose down/up needed for code changes!
Only needed for: new packages, settings changes, new apps
```

---

## 📊 Architecture Diagram

![Docker Architecture](../images/02-docker.png)

---

## 🌐 "Hello, World!" with Docker

```bash
# 1. Create Django project locally first
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install django~=4.0.0
(.venv) $ django-admin startproject django_project .
(.venv) $ pip freeze > requirements.txt
(.venv) $ deactivate

# 2. Create Dockerfile and docker-compose.yml
# (see above)

# 3. Create .dockerignore

# 4. Build and run
$ docker-compose up -d --build

# 5. Confirm at http://127.0.0.1:8000/
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Docker containers ≠ VMs** | Containers share the host OS kernel — lighter and faster |
| **Dockerfile = blueprint** | Build once, run anywhere |
| **docker-compose = orchestration** | Defines and connects multiple services |
| **Volumes = live sync** | Code changes appear instantly without rebuilding |
| **Layer caching** | Put slow/stable steps first in Dockerfile |
| **Detached mode** | `-d` runs containers in background; use `docker-compose logs` to debug |

---

*← [Back to Django for Professionals](../README.md)*
