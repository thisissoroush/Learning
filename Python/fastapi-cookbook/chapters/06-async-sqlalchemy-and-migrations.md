# Chapter 6 — Async SQLAlchemy and Database Migrations

> **Project:** `ticketing_system`

---

## 🎯 What This Chapter Covers

Why you need async SQLAlchemy (and when sync is fine), how to set up `AsyncSession`, how to write async CRUD with the ORM 2.0 style (`select()` instead of `query()`), managing table relationships, and using Alembic for production-grade migrations.

---

## 🧠 Why Async SQLAlchemy?

Sync SQLAlchemy works fine — but it **blocks the event loop** when waiting for the database. If your endpoint is `async def` and calls sync SQLAlchemy, every DB query freezes all other requests.

```
Async endpoint + SYNC SQLAlchemy = BAD
  → DB query blocks the event loop
  → 100 concurrent users = all wait in line

Async endpoint + ASYNC SQLAlchemy = GOOD
  → DB query suspends the coroutine, event loop serves others
  → 100 concurrent users = queries run concurrently
```

**The trade-off:** async adds complexity. For low-traffic apps or CPU-bound work, sync SQLAlchemy with `def` endpoints is simpler and perfectly adequate.

---

## ⚙️ Setting Up Async SQLAlchemy

```python
# database.py
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

# Notice the driver: postgresql+asyncpg (not psycopg2)
# asyncpg is the async PostgreSQL driver
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/ticketdb"

def get_engine() -> AsyncEngine:
    return create_async_engine(
        DATABASE_URL,
        echo=False,       # True in development to log all SQL queries
        pool_size=10,     # max connections in pool
        max_overflow=20,  # max extra connections when pool is full
    )

def get_session_factory(engine: AsyncEngine):
    return async_sessionmaker(
        engine,
        expire_on_commit=False,  # ← CRITICAL: without this, attributes expire after commit
                                  # causing lazy-load errors when the session is closed
        class_=AsyncSession,
    )

# Dependency for FastAPI endpoints
async def get_db_session() -> AsyncSession:
    engine = get_engine()
    async_session = get_session_factory(engine)
    async with async_session() as session:
        yield session   # session auto-closes when the context exits
```

**Why `expire_on_commit=False`?** After `await session.commit()`, SQLAlchemy normally expires all attributes on ORM objects (marks them as stale). With async, if you try to access an attribute after committing (even for the return value), it tries a lazy load — but the session may be in a weird state. `expire_on_commit=False` keeps the attributes as-is after commit.

---

## 📊 ORM Models with Relationships

```python
# models.py
from sqlalchemy import ForeignKey, String, Float, Integer, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# Many-to-many: an event can have multiple sponsors, a sponsor can support multiple events
event_sponsor = Table(
    "event_sponsors",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("sponsor_id", ForeignKey("sponsors.id"), primary_key=True),
    Column("amount", Float, default=0.0),   # contribution amount
)

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    show: Mapped[str] = mapped_column(String(200), nullable=False)
    user: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # FK relationship to Event
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    event: Mapped["Event | None"] = relationship(back_populates="tickets")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)

    # One-to-many: one event has many tickets
    tickets: Mapped[list[Ticket]] = relationship(back_populates="event")

    # Many-to-many: sponsors via association table
    sponsors: Mapped[list["Sponsor"]] = relationship(
        secondary=event_sponsor,
        back_populates="events",
    )

class Sponsor(Base):
    __tablename__ = "sponsors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    events: Mapped[list[Event]] = relationship(
        secondary=event_sponsor,
        back_populates="sponsors",
    )
```

---

## 🔄 Async CRUD — ORM 2.0 Style

Async SQLAlchemy uses a different query style. `session.query()` doesn't work — you use `select()` statements from `sqlalchemy` instead.

```python
# operations.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models import Ticket, Event

# GET a single ticket by id
async def get_ticket(session: AsyncSession, ticket_id: int) -> Ticket | None:
    # select(Model) builds a SELECT statement
    result = await session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    # scalar_one_or_none() returns the object or None (raises if multiple found)
    return result.scalar_one_or_none()

# GET all tickets for a show
async def get_tickets_for_show(session: AsyncSession, show: str) -> list[Ticket]:
    result = await session.execute(
        select(Ticket)
        .where(Ticket.show == show)
        .order_by(Ticket.price)   # sorted by price ascending
    )
    return result.scalars().all()   # scalars() unwraps from Row objects

# CREATE a ticket
async def create_ticket(
    session: AsyncSession,
    show: str,
    user: str | None,
    price: float,
) -> int:
    ticket = Ticket(show=show, user=user, price=price)
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)   # re-read from DB to get generated id
    return ticket.id

# UPDATE ticket price — using ORM update statement (more efficient than load+save)
async def update_ticket_price(
    session: AsyncSession,
    ticket_id: int,
    new_price: float,
) -> bool:
    result = await session.execute(
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(price=new_price)
        .returning(Ticket.id)    # returns the id if update happened, None if not found
    )
    await session.commit()
    return result.scalar_one_or_none() is not None   # True if row was updated

# DELETE a ticket
async def delete_ticket(session: AsyncSession, ticket_id: int) -> bool:
    result = await session.execute(
        delete(Ticket)
        .where(Ticket.id == ticket_id)
        .returning(Ticket.id)
    )
    await session.commit()
    return result.scalar_one_or_none() is not None

# Partial update — update only provided fields
async def update_ticket_fields(
    session: AsyncSession,
    ticket_id: int,
    fields: dict,    # only the fields to change
) -> bool:
    if not fields:
        return True   # nothing to update

    result = await session.execute(
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(**fields)
        .returning(Ticket.id)
    )
    await session.commit()
    return result.scalar_one_or_none() is not None
```

---

## 🌐 Async FastAPI Endpoints

```python
# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from database import Base, get_db_session, get_engine
from operations import (
    get_ticket, get_tickets_for_show, create_ticket,
    update_ticket_price, update_ticket_fields, delete_ticket,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all DB tables on startup, clean up on shutdown."""
    engine = get_engine()
    async with engine.begin() as conn:
        # run_sync lets you call sync operations (like create_all) from async context
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()    # close all connections in the pool

app = FastAPI(lifespan=lifespan)

# Pydantic schemas
class TicketCreate(BaseModel):
    show: str
    user: str | None = None
    price: float = Field(..., ge=0)    # price must be >= 0

class TicketUpdate(BaseModel):
    price: float | None = Field(None, ge=0)
    user: str | None = None

# Type alias for the session dependency — cleaner than repeating Annotated[...]
DBSession = Annotated[AsyncSession, Depends(get_db_session)]

@app.get("/tickets/{ticket_id}")
async def read_ticket(ticket_id: int, db: DBSession):
    ticket = await get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/tickets", status_code=201)
async def create_ticket_endpoint(ticket: TicketCreate, db: DBSession):
    ticket_id = await create_ticket(db, ticket.show, ticket.user, ticket.price)
    return {"ticket_id": ticket_id}

@app.patch("/tickets/{ticket_id}")
async def update_ticket_endpoint(ticket_id: int, update: TicketUpdate, db: DBSession):
    # Only pass the fields the client actually sent
    changes = update.model_dump(exclude_unset=True)
    updated = await update_ticket_fields(db, ticket_id, changes)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Updated"}

@app.delete("/tickets/{ticket_id}", status_code=204)
async def delete_ticket_endpoint(ticket_id: int, db: DBSession):
    deleted = await delete_ticket(db, ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")

@app.get("/shows/{show}/tickets")
async def list_show_tickets(show: str, db: DBSession):
    return await get_tickets_for_show(db, show)
```

---

## 📈 Alembic Migrations — Database Schema Evolution

`Base.metadata.create_all()` is fine for development — it creates tables if they don't exist. But in production you need **migrations**: tracked, reversible SQL scripts that evolve your schema without losing data.

```bash
# One-time setup
pip install alembic
alembic init alembic   # creates alembic/ directory and alembic.ini
```

```python
# alembic/env.py — configure Alembic to know about your models
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from models import Base   # ← import your models so Alembic sees them

config = context.config
fileConfig(config.config_file_name)

# Point Alembic at your models for autogenerate
target_metadata = Base.metadata

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/ticketdb"

def run_migrations_online():
    """Run migrations against a live database."""
    import asyncio

    async def run_async_migrations():
        engine = create_async_engine(DATABASE_URL)
        async with engine.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await engine.dispose()

    asyncio.run(run_async_migrations())

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

run_migrations_online()
```

```bash
# Generate a migration from your model changes (autogenerate compares models to DB)
alembic revision --autogenerate -m "add tickets and events tables"
# Creates: alembic/versions/abc123_add_tickets_and_events_tables.py

# Review the generated file — always check before applying!
cat alembic/versions/abc123_add_tickets_and_events_tables.py

# Apply all pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# See migration history
alembic history --verbose

# See current DB state
alembic current
```

**Migration workflow in practice:**
```
1. Change models.py (add column, rename table, etc.)
2. alembic revision --autogenerate -m "description"
3. Review the generated .py file
4. alembic upgrade head  (in dev)
5. Run tests
6. Commit models.py + the migration file together
7. Deploy → alembic upgrade head runs in deploy hook
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `postgresql+asyncpg` driver | asyncpg is the async driver — `psycopg2` is sync only |
| `expire_on_commit=False` | Without this, accessing attributes after commit triggers lazy load → errors in async |
| `select(Model)` not `session.query()` | ORM 2.0 style — required for async SQLAlchemy |
| `.scalar_one_or_none()` | Unwraps the Row result to just the ORM object — raises if multiple rows |
| `.returning(Model.id)` on update/delete | Efficient: do the operation AND check if a row was affected in one query |
| `run_sync(fn)` in async context | Bridges sync code (like `create_all`) into async context |
| Alembic over `create_all` in production | Alembic is reversible, tracked, and handles column renames/type changes |
