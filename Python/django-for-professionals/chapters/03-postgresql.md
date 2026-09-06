# Chapter 3 — PostgreSQL

> *"SQLite is great for learning Django, but PostgreSQL is the production database of choice for professional Django projects."*

---

## 🎯 Core Concept

**Never use SQLite in production.** PostgreSQL is the professional standard for Django projects. This chapter shows how to run PostgreSQL inside Docker alongside your Django application — giving you a production-identical database in local development.

---

## 🗄️ Why PostgreSQL Over SQLite?

```
SQLite                          PostgreSQL
───────────────────────────────────────────────────────
File-based (single file)        Server-based (client-server)
No concurrent writes            Full concurrent read/write
No user permissions             Role-based access control
Limited data types              Rich types: UUID, JSONB, arrays
No full-text search             Built-in full-text search
Scales to ~100K rows            Scales to billions of rows
Default Django DB               Production Django DB
Good for: learning, tests       Good for: everything else
```

### The Two Scoops Rule
> **Always use the same database in development and production.** If you develop on SQLite and deploy to PostgreSQL, you will hit bugs that are impossible to reproduce locally.

---

## 🐳 Adding PostgreSQL to Docker

Update `docker-compose.yml` to add a database service:

```yaml
# docker-compose.yml
version: "3.9"

services:
  web:
    build: .
    command: python /code/manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - 8000:8000
    depends_on:       # Wait for db to be ready before starting web
      - db

  db:                 # PostgreSQL service
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/  # Persist data between restarts!
    environment:
      - "POSTGRES_HOST_AUTH_METHOD=trust"        # Allow connections without password

volumes:
  postgres_data:      # Named volume — data survives docker-compose down
```

---

## ⚙️ Configuring Django to Use PostgreSQL

Install the PostgreSQL adapter for Python:

```
# requirements.txt
django~=4.0.0
psycopg2-binary~=2.9  # PostgreSQL adapter
```

Update `django_project/settings.py`:

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",       # This matches the docker-compose service name!
        "PORT": 5432,
    }
}
```

> 🔑 **Key insight:** The `HOST` is `"db"` — not `"localhost"`. Docker networking uses service names as hostnames.

---

## 🔄 Detached Mode and Log Debugging

```bash
# Start containers in background
$ docker-compose up -d

# This is wrong! You'll see errors like:
# "No module named 'pages'"
# The fix:
$ docker-compose logs    # See what's happening
$ docker-compose down    # Stop containers
$ docker-compose up -d   # Restart (reloads settings)
```

### Why Does Adding a New App Require a Restart?

Django loads `INSTALLED_APPS` at startup. When you add a new app, the running container still has the old settings loaded in memory. Stopping and starting the container forces a fresh load.

---

## 💾 Data Persistence with Named Volumes

```
docker-compose down            ← SAFE: data persists in postgres_data volume
docker-compose down -v         ← DANGEROUS: deletes volume, all data gone!
                                 (useful for testing clean migrations)
```

```
Without volume:
  docker-compose down → All database data deleted!
  
With postgres_data volume:
  docker-compose down → Container stops, data lives in volume
  docker-compose up   → Container starts, data restored from volume
```

---

## 🔬 PostgreSQL Commands Inside Docker

```bash
# Enter the PostgreSQL shell
$ docker-compose exec db psql --username=postgres --dbname=postgres

# Inside psql:
# List all databases
postgres=# \l

# Connect to a database
postgres=# \c postgres

# List all tables
postgres=# \dt

# Exit
postgres=# \q
```

---

## 🚀 Running Migrations on PostgreSQL

```bash
# With containers running:
$ docker-compose exec web python manage.py migrate

# What this does:
# Creates Django system tables in PostgreSQL
# auth_user, django_migrations, django_content_type, etc.
```

---

## 📊 Architecture Diagram

![PostgreSQL Architecture](../images/03-postgresql.png)

---

## 🏗️ The Full Setup Pattern (Used Throughout the Book)

```bash
# 1. Start containers
$ docker-compose up -d --build

# 2. Migrate database
$ docker-compose exec web python manage.py migrate

# 3. Create superuser
$ docker-compose exec web python manage.py createsuperuser

# 4. Run tests
$ docker-compose exec web python manage.py test

# 5. Commit to git
$ git add .
$ git commit -m "ch3"
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Always use PostgreSQL** | SQLite dev → PostgreSQL prod = hidden bugs |
| **Service name = hostname** | `HOST: "db"` — Docker networking magic |
| **Named volumes persist data** | `docker-compose down` is safe; `down -v` deletes data |
| **psycopg2-binary required** | Python's PostgreSQL driver — always in requirements |
| **`depends_on` for ordering** | Ensures db starts before web |
| **Restart for settings changes** | New apps in INSTALLED_APPS require container restart |

---

*← [Back to Django for Professionals](../README.md)*
