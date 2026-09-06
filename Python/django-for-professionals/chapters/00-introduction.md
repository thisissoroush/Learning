# Introduction — Django for Professionals

> *"There is a massive gulf between building simple 'toy apps' and what it takes to build a 'production-ready' web application suitable for deployment to thousands or even millions of users."*

---

## 🎯 Core Concept

The introduction sets the stage for the entire book: **Django's default settings are optimized for beginners, not production**. When you run `django-admin startproject`, you get SQLite, DEBUG=True, local static files, and a built-in User model — all fine for learning, but **wrong for shipping**.

This book bridges the gap by building a real **Bookstore** web application from scratch using industry best practices.

---

## 🗺️ What Changes When You Go Professional?

```
DEFAULT DJANGO (dev)          PROFESSIONAL DJANGO (prod)
────────────────────────────────────────────────────────────
SQLite database       →       PostgreSQL
Local virtual env     →       Docker containers
Built-in User model   →       Custom User model
DEBUG=True            →       DEBUG=False + env vars
Local static files    →       WhiteNoise / S3
No auth flow          →       django-allauth (email + social)
No email              →       SendGrid / Mailgun
No HTTPS              →       HTTPS + HSTS + Secure cookies
Manual deploy         →       Heroku + Docker
```

---

## 📚 The Project: Online Bookstore

Every chapter builds on a **single project** (unlike Two Scoops, which uses isolated examples):

```
Bookstore Features Built Throughout the Book:
├── Custom User Model (AbstractUser)
├── Docker + PostgreSQL local environment
├── User Registration (built-in auth + django-allauth)
├── Static Assets (CSS, JS, images + Bootstrap)
├── Books App (CRUD with UUID primary keys)
├── Reviews (ForeignKey relationships)
├── Image Uploads (file handling + S3)
├── Search (full-text with Q objects)
├── Permissions (groups + login_required)
├── Performance (indexes, select_related, caching)
├── Security (HTTPS, CSRF, CSP, admin hardening)
└── Deployment (Heroku + Docker + PostgreSQL)
```

---

## 🔑 Book Philosophy

### 1. Show One Right Way
Rather than listing all options, the book picks one opinionated approach for each problem. This matches how real teams work — you don't debate every choice from scratch.

### 2. Test Everything
**Every new feature comes with tests.** The book treats testing as a non-negotiable part of professional development, not an afterthought.

### 3. The 12-Factor App
The book follows [12factor.net](https://12factor.net) principles throughout:
- Store config in the environment (not in code)
- Treat backing services as attached resources
- Keep dev/prod parity

---

## ⚙️ Prerequisites

| Requirement | Why |
|-------------|-----|
| Django for Beginners (or equivalent) | This book moves fast — no hand-holding on basics |
| Python 3.10+ | All code examples use modern Python |
| Command Line familiarity | Docker, Git, Django management commands |
| Git basics | Every chapter ends with `git commit` |

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Django defaults aren't production-ready | Always change them before shipping |
| One project, built incrementally | Real professional skills come from building real things |
| Testing is non-negotiable | Every chapter includes tests |
| Docker from day one | No "it works on my machine" excuses |

---

*← [Back to Django for Professionals](../README.md)*
