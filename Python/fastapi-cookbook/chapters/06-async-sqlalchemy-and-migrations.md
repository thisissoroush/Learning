# Chapter 6 — Async SQLAlchemy and Database Migrations

> **Project:** `ticketing_system`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter06)

---

## 🎯 What This Chapter Covers

Async SQLAlchemy (`AsyncSession`), async CRUD operations, Alembic migrations, and table relationships — built around a ticketing system with events, tickets, and sponsors.

---

## ⚡ Async SQLAlchemy Setup

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/ticketdb"

def get_engine() -> AsyncEngine:
    return create_async_engine(DATABASE_URL, echo=True)

def get_async_session_factory(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncSession:
    engine = get_engine()
    async_session = get_async_session_factory(engine)
    async with async_session() as session:
        yield session
```

**Key differences from sync SQLAlchemy:**
| Sync | Async |
|------|-------|
| `create_engine` | `create_async_engine` |
| `Session` | `AsyncSession` |
| `sessionmaker` | `async_sessionmaker` |
| `db.query(Model)` | `await session.execute(select(Model))` |
| `session.commit()` | `await session.commit()` |

---

## 🔄 Async CRUD Operations

```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

async def get_ticket(session: AsyncSession, ticket_id: int):
    result = await session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    return result.scalar_one_or_none()

async def create_ticket(session: AsyncSession, show: str, user: str, price: float) -> int:
    ticket = Ticket(show=show, user=user, price=price)
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket.id

async def update_ticket_price(session: AsyncSession, ticket_id: int, new_price: float) -> bool:
    result = await session.execute(
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(price=new_price)
        .returning(Ticket.id)
    )
    await session.commit()
    return result.scalar_one_or_none() is not None

async def delete_ticket(session: AsyncSession, ticket_id: int) -> bool:
    result = await session.execute(
        delete(Ticket).where(Ticket.id == ticket_id).returning(Ticket.id)
    )
    await session.commit()
    return result.scalar_one_or_none() is not None
```

---

## 🏗️ Async FastAPI Endpoints

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   # create tables
    yield
    await engine.dispose()   # cleanup connections

app = FastAPI(lifespan=lifespan)

@app.get("/ticket/{ticket_id}")
async def read_ticket(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket_id: int,
):
    ticket = await get_ticket(db_session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/ticket", response_model=dict[str, int])
async def create_ticket_route(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket: TicketRequest,
):
    ticket_id = await create_ticket(db_session, ticket.show, ticket.user, ticket.price)
    return {"ticket_id": ticket_id}

@app.delete("/ticket/{ticket_id}")
async def delete_ticket_route(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ticket_id: int,
):
    ticket = await delete_ticket(db_session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Ticket removed"}
```

---

## 📈 Alembic Migrations

```bash
# Initialize Alembic
alembic init alembic

# Create a migration (auto-detect model changes)
alembic revision --autogenerate -m "add tickets table"

# Apply migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Show history
alembic history
```

### env.py configuration for async

```python
# alembic/env.py
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
import asyncio

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL)

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_async_migrations())
```

---

## 🔗 Relationships and Custom Response Docs

```python
from pydantic import BaseModel, Field

class TicketRequest(BaseModel):
    price: float | None
    show: str | None
    user: str | None = None

# Custom OpenAPI response examples
@app.post(
    "/sponsor/{sponsor_name}",
    response_model=dict[str, int],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"sponsor_id": 12345}
                }
            },
        }
    },
)
async def register_sponsor(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    sponsor_name: str,
):
    sponsor_id = await create_sponsor(db_session, sponsor_name)
    if not sponsor_id:
        raise HTTPException(status_code=400, detail="Sponsor not created")
    return {"sponsor_id": sponsor_id}
```

---

## 🔑 Key Takeaways

- Use `create_async_engine` + `AsyncSession` for fully non-blocking DB access
- Use `select(Model).where(...)` instead of `session.query()` — ORM 2.0 style
- `await session.execute(...)` returns a `Result` — use `.scalar_one_or_none()`, `.scalars().all()`
- `Annotated[AsyncSession, Depends(get_db_session)]` — cleaner than `session: AsyncSession = Depends(...)`
- `lifespan` runs `create_all` at startup and `engine.dispose()` at shutdown
- **Alembic in production** — never use `create_all()` in production; always migrate with Alembic
- `expire_on_commit=False` in async sessions — avoids lazy-load errors after commit
