# 🗄️ SQLAlchemy — Interview Questions (Junior → Architect)

Covers SQLAlchemy Core, SQLAlchemy ORM, and Alembic migrations.

---

## 🟢 Junior Level

---

### 1. What is SQLAlchemy and what are its two main layers?

**A:** SQLAlchemy is the dominant Python SQL toolkit and ORM. It has two distinct layers:

| Layer | What it is | When to use |
|-------|-----------|-------------|
| **Core** | SQL expression language — pythonic SQL builder, no ORM | Complex queries, bulk ops, raw control |
| **ORM** | Maps Python classes to tables, unit-of-work pattern | Domain models, CRUD, relationships |

```python
# Core — expression language
from sqlalchemy import create_engine, text, select, Table, MetaData

engine = create_engine("postgresql+psycopg2://user:pass@localhost/db")
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name FROM users WHERE active = true"))
    for row in result:
        print(row.id, row.name)

# ORM — declarative models
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
```

---

### 2. How do you define models with SQLAlchemy ORM 2.0?

**A:**

```python
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int]            = mapped_column(primary_key=True)
    name: Mapped[str]          = mapped_column(String(100), nullable=False)
    email: Mapped[str]         = mapped_column(String(255), unique=True, index=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool]    = mapped_column(default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationship
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int]          = mapped_column(primary_key=True)
    total: Mapped[Numeric]   = mapped_column(Numeric(10, 2))
    user_id: Mapped[int]     = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"]     = relationship(back_populates="orders")
```

`Mapped[T]` with `mapped_column()` is the SQLAlchemy 2.0 typed API — provides full type inference without `__annotations__` tricks.

---

### 3. How do you create and use a Session?

**A:**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost/mydb",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # test connections before use
)

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)

# Context manager (recommended)
with SessionFactory() as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
    print(user.id)  # populated after commit

# Query
with SessionFactory() as session:
    # ORM 2.0 style
    stmt = select(User).where(User.is_active == True).order_by(User.name)
    users = session.scalars(stmt).all()

    # Get by PK
    user = session.get(User, 42)

    # First or None
    user = session.scalars(select(User).where(User.email == "alice@example.com")).first()
```

---

### 4. How do you perform CRUD operations?

**A:**

```python
with Session(engine) as session:
    # Create
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.flush()    # sends INSERT, gets id, stays in transaction
    session.commit()   # commits transaction

    # Read
    user = session.get(User, 1)
    users = session.scalars(select(User)).all()

    # Update
    user.name = "Alice Smith"
    session.commit()   # change tracker detects the change

    # Bulk update (no ORM object load)
    session.execute(
        update(User).where(User.is_active == False).values(name="[deleted]")
    )
    session.commit()

    # Delete
    session.delete(user)
    session.commit()

    # Bulk delete
    session.execute(delete(User).where(User.created_at < cutoff))
    session.commit()
```

---

### 5. How do you filter and query with SQLAlchemy?

**A:**

```python
from sqlalchemy import select, and_, or_, not_, func

stmt = (
    select(User)
    .where(
        and_(
            User.is_active == True,
            or_(User.name.like("A%"), User.name.like("B%")),
            User.age >= 18,
        )
    )
    .order_by(User.name.asc())
    .limit(10)
    .offset(20)
)
users = session.scalars(stmt).all()

# IN clause
stmt = select(User).where(User.id.in_([1, 2, 3]))

# NOT IN
stmt = select(User).where(User.id.not_in([4, 5]))

# NULL checks
stmt = select(User).where(User.bio.is_(None))
stmt = select(User).where(User.bio.is_not(None))

# Aggregations
from sqlalchemy import func
count = session.scalar(select(func.count()).select_from(User))
avg_age = session.scalar(select(func.avg(User.age)))

# Group by
stmt = (
    select(User.department, func.count(User.id).label("count"))
    .group_by(User.department)
    .having(func.count(User.id) > 5)
)
```

---

### 6. How do you define relationships?

**A:**

```python
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")
    tags: Mapped[list["Tag"]] = relationship(secondary="book_tags", back_populates="books")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    books: Mapped[list["Book"]] = relationship(secondary="book_tags", back_populates="tags")

# Association table for M2M
book_tags = Table(
    "book_tags", Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("tag_id",  ForeignKey("tags.id"),  primary_key=True),
)
```

---

### 7. What is lazy loading vs eager loading in SQLAlchemy?

**A:**

```python
# Lazy loading (default) — loads relationship on access → N+1 risk
author = session.get(Author, 1)
for book in author.books:   # SELECT * FROM books WHERE author_id = 1 (on access)
    print(book.title)

# Eager loading — selectin (recommended) — separate IN query
from sqlalchemy.orm import selectinload

stmt = select(Author).options(selectinload(Author.books))
authors = session.scalars(stmt).all()
# 1 query for authors + 1 query: SELECT * FROM books WHERE author_id IN (...)

# Joined loading — SQL JOIN
from sqlalchemy.orm import joinedload
stmt = select(Author).options(joinedload(Author.books))
# 1 JOIN query — good for single object, bad for lists (row multiplication)

# Configure default lazy strategy
class Author(Base):
    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        lazy="selectin"  # always eager with selectin
    )
```

---

### 8. How do you use Alembic for migrations?

**A:**

```bash
# Install and init
pip install alembic
alembic init alembic

# alembic.ini — set sqlalchemy.url
# alembic/env.py — import your Base

# Generate migration
alembic revision --autogenerate -m "add users table"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
alembic downgrade base   # all the way back

# Status
alembic current
alembic history --verbose
```

```python
# alembic/env.py
from myapp.models import Base
target_metadata = Base.metadata

# Generated migration file
def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

def downgrade() -> None:
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
```

---

## 🟡 Mid Level

---

### 9. How do you handle transactions in SQLAlchemy?

**A:**

```python
# Session is always within a transaction
# session.commit() commits, session.rollback() rolls back

# Explicit savepoints (nested transactions)
with Session(engine) as session:
    with session.begin():
        user = User(name="Alice")
        session.add(user)

        # Savepoint — partial rollback
        with session.begin_nested():
            order = Order(user=user, total=100)
            session.add(order)
            # If this block raises, only the order is rolled back
            # user.add() is still committed

# Manual transaction
session = Session(engine)
try:
    session.add(user)
    session.add(order)
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()

# Core level — explicit transaction
with engine.begin() as conn:   # commits on exit, rolls back on exception
    conn.execute(insert(users_table).values(name="Alice"))
    conn.execute(update(orders_table).where(...).values(status="new"))
```

---

### 10. How do you use Core SQL expressions for complex queries?

**A:**

```python
from sqlalchemy import select, join, func, case, literal_column, text

# JOIN
stmt = (
    select(User.name, func.count(Order.id).label("order_count"), func.sum(Order.total).label("revenue"))
    .select_from(User)
    .join(Order, Order.user_id == User.id, isouter=True)  # LEFT JOIN
    .group_by(User.id, User.name)
    .having(func.count(Order.id) > 0)
    .order_by(func.sum(Order.total).desc())
)

# CASE expression
status_label = case(
    (Order.total >= 1000, "vip"),
    (Order.total >= 100, "regular"),
    else_="small"
).label("tier")

# CTE (Common Table Expression)
cte = (
    select(Order.user_id, func.sum(Order.total).label("total_spent"))
    .group_by(Order.user_id)
    .cte("user_totals")
)
stmt = select(User, cte.c.total_spent).join(cte, cte.c.user_id == User.id)

# Window functions
from sqlalchemy import over
rank = func.rank().over(
    order_by=Order.total.desc(),
    partition_by=Order.user_id
).label("rank")
```

---

### 11. How do you implement the repository pattern with SQLAlchemy?

**A:**

```python
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> User | None: ...
    @abstractmethod
    def list_active(self, limit: int, offset: int) -> list[User]: ...
    @abstractmethod
    def save(self, user: User) -> User: ...

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, id: int) -> User | None:
        return self._session.get(User, id)

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalars(
            select(User).where(User.email == email)
        ).first()

    def list_active(self, limit: int = 20, offset: int = 0) -> list[User]:
        return self._session.scalars(
            select(User).where(User.is_active == True)
                        .order_by(User.created_at.desc())
                        .limit(limit).offset(offset)
        ).all()

    def save(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()   # get id without committing
        return user

    def delete(self, user: User) -> None:
        self._session.delete(user)
```

---

### 12. How do you use async SQLAlchemy?

**A:**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    pool_size=10,
    max_overflow=20,
)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)

# FastAPI dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session

# Usage
async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def list_users(session: AsyncSession) -> list[User]:
    result = await session.execute(
        select(User)
        .options(selectinload(User.orders))
        .where(User.is_active == True)
    )
    return result.scalars().all()

async def create_user(session: AsyncSession, name: str, email: str) -> User:
    user = User(name=name, email=email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

---

### 13. How do you handle pagination?

**A:**

```python
# Offset pagination — simple but slow for large offsets
def paginate_offset(session: Session, page: int, size: int) -> dict:
    total = session.scalar(select(func.count()).select_from(User))
    users = session.scalars(
        select(User).order_by(User.id).limit(size).offset((page - 1) * size)
    ).all()
    return {"items": users, "total": total, "page": page, "size": size}

# Keyset / cursor pagination — efficient for large tables
def paginate_cursor(session: Session, after_id: int | None, size: int) -> dict:
    stmt = select(User).order_by(User.id).limit(size)
    if after_id:
        stmt = stmt.where(User.id > after_id)
    users = session.scalars(stmt).all()
    next_cursor = users[-1].id if len(users) == size else None
    return {"items": users, "next_cursor": next_cursor}
```

---

### 14. How do you implement soft delete in SQLAlchemy?

**A:**

```python
from sqlalchemy import event
from datetime import datetime

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

class User(SoftDeleteMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

# Override delete to set deleted_at
@event.listens_for(Session, "before_flush")
def soft_delete(session, flush_context, instances):
    for obj in session.deleted:
        if isinstance(obj, SoftDeleteMixin):
            obj.deleted_at = datetime.utcnow()
            session.expunge(obj)
            session.add(obj)

# Query filter — always exclude deleted
def active_users(session: Session) -> list[User]:
    return session.scalars(
        select(User).where(User.deleted_at.is_(None))
    ).all()
```

---

### 15. How do you use events and listeners in SQLAlchemy?

**A:**

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

# Model-level events
@event.listens_for(User, "before_insert")
def hash_password(mapper, connection, target: User):
    if target.password:
        target.password = bcrypt.hash(target.password)

@event.listens_for(User, "after_update")
def audit_user_change(mapper, connection, target: User):
    AuditLog.record(target, "updated")

# Session-level events
@event.listens_for(Session, "after_commit")
def publish_domain_events(session: Session):
    for obj in session.identity_map.values():
        if hasattr(obj, "_domain_events"):
            for event in obj._domain_events:
                event_bus.publish(event)
            obj._domain_events.clear()

# Engine events — query logging
@event.listens_for(engine, "before_cursor_execute")
def log_query(conn, cursor, statement, parameters, context, executemany):
    if slow := context.engine_events.get("slow_query_threshold"):
        context._query_start_time = time.time()
```

---

## 🔴 Senior Level

---

### 16. How do you optimize SQLAlchemy for high-throughput writes?

**A:**

```python
# 1. Bulk insert — bypass ORM, no events or history
session.execute(
    insert(User),
    [{"name": "Alice", "email": "a@x.com"}, {"name": "Bob", "email": "b@x.com"}]
)
session.commit()

# 2. bulk_insert_mappings (faster than add_all, slower than execute)
session.bulk_insert_mappings(User, [{"name": "Alice"}, {"name": "Bob"}])

# 3. COPY for Postgres (fastest — psycopg2)
from io import StringIO
import csv

buf = StringIO()
writer = csv.writer(buf)
writer.writerows([(u["name"], u["email"]) for u in users])
buf.seek(0)

conn = engine.raw_connection()
cur = conn.cursor()
cur.copy_from(buf, "users", columns=("name", "email"), sep=",")
conn.commit()

# 4. Disable autoflush during batch operations
with session.no_autoflush:
    for chunk in chunks(large_list, 1000):
        session.bulk_insert_mappings(User, chunk)
        session.flush()

# 5. expire_on_commit=False — avoid re-SELECT after commit
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)
```

---

### 17. How do you implement optimistic locking in SQLAlchemy?

**A:**

```python
from sqlalchemy import Integer

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int]      = mapped_column(primary_key=True)
    total: Mapped[float]
    version: Mapped[int] = mapped_column(Integer, default=1)

    __mapper_args__ = {"version_id_col": version}  # enable optimistic locking

# SQLAlchemy automatically:
# SELECT * FROM orders WHERE id = 1
# UPDATE orders SET total = 200, version = 2 WHERE id = 1 AND version = 1
# If 0 rows updated → raises StaleDataError (concurrent modification detected)

from sqlalchemy.orm.exc import StaleDataError

try:
    order.total = 200
    session.commit()
except StaleDataError:
    session.rollback()
    # Reload and retry, or return conflict to caller
    raise ConflictException("Order was modified concurrently")
```

---

### 18. How do you handle connection pooling and health checks?

**A:**

```python
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost/mydb",
    poolclass=QueuePool,
    pool_size=10,           # persistent connections
    max_overflow=20,        # temporary connections when pool full
    pool_timeout=30,        # seconds to wait for connection
    pool_recycle=1800,      # recycle connections older than 30 min
    pool_pre_ping=True,     # test with SELECT 1 before using connection
)

# Pool events for monitoring
@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    # Track connection checkout
    metrics.increment("db.pool.checkout")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    metrics.increment("db.pool.checkin")

# Health check
def db_health_check() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

# Async pool
from sqlalchemy.ext.asyncio import create_async_engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    pool_size=10, max_overflow=20,
    pool_pre_ping=True,
)
```

---

### 19. How do you integrate SQLAlchemy with FastAPI?

**A:**

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/mydb")
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSession() as session:
        yield session

app = FastAPI()

@app.post("/users/", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check duplicate
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(**body.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

### 20. How do you use SQLAlchemy with Alembic for zero-downtime migrations?

**A:**

**Expand-contract pattern:**

```python
# Step 1: Add nullable column (deploy migration first)
def upgrade():
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=True))

# Step 2: Deploy new code that writes to new column
# Step 3: Backfill in a data migration
def upgrade():
    op.execute("UPDATE users SET email_verified = FALSE WHERE email_verified IS NULL")

# Step 4: Add NOT NULL constraint (safe now — all rows populated)
def upgrade():
    op.alter_column("users", "email_verified", nullable=False)
```

**Non-locking index creation (Postgres):**
```python
from alembic.operations import ops

def upgrade():
    # CREATE INDEX CONCURRENTLY — doesn't lock table
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_users_email", "users", ["email"],
            unique=True,
            postgresql_concurrently=True
        )
```

---

## 🏛️ Architect Level

---

### 21. How do you design a SQLAlchemy data layer for a CQRS architecture?

**A:**

```python
# Write side — ORM with full session, events, versioning
class OrderRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, order: Order) -> Order:
        self._session.add(order)
        await self._session.flush()
        return order

    async def get_for_update(self, order_id: int) -> Order:
        return await self._session.scalar(
            select(Order)
            .where(Order.id == order_id)
            .with_for_update()  # pessimistic lock
        )

# Read side — raw Core, no ORM objects, DTOs
class OrderQueryService:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def get_dashboard(self, tenant_id: int) -> list[dict]:
        async with self._engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT o.id, o.total, o.status,
                       u.name AS customer_name,
                       COUNT(i.id) AS item_count
                FROM orders o
                JOIN users u ON u.id = o.user_id
                JOIN order_items i ON i.order_id = o.id
                WHERE o.tenant_id = :tenant_id
                GROUP BY o.id, o.total, o.status, u.name
                ORDER BY o.created_at DESC
                LIMIT 50
            """), {"tenant_id": tenant_id})
            return [dict(row) for row in result.mappings()]
```

---

### 22. How do you implement multi-tenancy with SQLAlchemy?

**A:**

```python
# Row-level — tenant_id on every table
class TenantMixin:
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)

class Order(TenantMixin, Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)

# Global filter — inject tenant into every query
from sqlalchemy.orm import with_loader_criteria

def tenant_session(session: Session, tenant_id: int) -> Session:
    """Wrap a session so all queries auto-filter by tenant_id."""
    @event.listens_for(session, "do_orm_execute")
    def add_tenant_filter(execute_state):
        if not execute_state.is_column_load and not execute_state.is_relationship_load:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(TenantMixin, lambda cls: cls.tenant_id == tenant_id, include_aliases=True)
            )
    return session

# Schema-per-tenant (PostgreSQL search_path)
@event.listens_for(engine, "connect")
def set_schema(dbapi_connection, connection_record):
    tenant_id = current_tenant.get()
    if tenant_id:
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path = tenant_{tenant_id}, public")
        cursor.close()
```
