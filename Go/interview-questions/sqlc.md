# 🔧 SQLC — Interview Questions (Junior → Architect)

SQLC generates type-safe Go code from SQL queries — you write SQL, SQLC writes the Go.

---

## 🟢 Junior Level

---

### 1. What is SQLC and what problem does it solve?

**A:** SQLC is a code generator — you write raw SQL queries in `.sql` files and SQLC generates idiomatic, type-safe Go code from them.

**Problem it solves:**
- ORMs hide SQL and make complex queries awkward
- Raw `database/sql` is verbose and error-prone (manual `Scan`, no type safety)
- SQLC gives you full SQL control + compile-time type safety + zero runtime overhead

```
Your SQL  →  sqlc generate  →  Type-safe Go functions
```

**Workflow:**
```bash
# 1. Write your schema and queries
# 2. Run code generation
sqlc generate

# 3. Use generated functions in your app
users, err := queries.ListActiveUsers(ctx)
```

---

### 2. How do you set up a SQLC project?

**A:**

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "./queries"      # .sql files with your queries
    schema: "./migrations"    # .sql files with your schema
    gen:
      go:
        package: "db"
        out: "./internal/db"
        emit_json_tags: true
        emit_interface: true         # generates Querier interface
        emit_db_tags: true
        emit_prepared_queries: false
        null_style: "omit_null"      # or "sql_null_type"
```

```bash
# Install
go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest

# Generate
sqlc generate

# Verify queries compile against schema
sqlc vet
```

---

### 3. How do you write queries for SQLC?

**A:**

```sql
-- queries/users.sql

-- name: GetUser :one
SELECT id, name, email, created_at
FROM users
WHERE id = $1;

-- name: ListUsers :many
SELECT id, name, email, created_at
FROM users
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: CreateUser :one
INSERT INTO users (name, email)
VALUES ($1, $2)
RETURNING *;

-- name: UpdateUser :one
UPDATE users
SET name = $1, email = $2, updated_at = NOW()
WHERE id = $3
RETURNING *;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;

-- name: CountActiveUsers :one
SELECT COUNT(*) FROM users WHERE is_active = true;
```

Query annotations:
- `:one` → returns one row
- `:many` → returns slice
- `:exec` → no rows returned (returns `error`)
- `:execresult` → returns `sql.Result`

---

### 4. What does the generated code look like?

**A:**

```go
// internal/db/users.sql.go (generated — do not edit)

type User struct {
    ID        int64     `json:"id"         db:"id"`
    Name      string    `json:"name"       db:"name"`
    Email     string    `json:"email"      db:"email"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
}

type CreateUserParams struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

type ListUsersParams struct {
    Limit  int32 `json:"limit"`
    Offset int32 `json:"offset"`
}

// Querier interface (when emit_interface: true)
type Querier interface {
    GetUser(ctx context.Context, id int64) (User, error)
    ListUsers(ctx context.Context, arg ListUsersParams) ([]User, error)
    CreateUser(ctx context.Context, arg CreateUserParams) (User, error)
    UpdateUser(ctx context.Context, arg UpdateUserParams) (User, error)
    DeleteUser(ctx context.Context, id int64) error
}

func (q *Queries) GetUser(ctx context.Context, id int64) (User, error) {
    row := q.db.QueryRowContext(ctx, getUser, id)
    var i User
    err := row.Scan(&i.ID, &i.Name, &i.Email, &i.CreatedAt)
    return i, err
}
```

---

### 5. How do you use the generated code?

**A:**

```go
import (
    "database/sql"
    "myapp/internal/db"

    _ "github.com/lib/pq" // or pgx
)

func main() {
    conn, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    queries := db.New(conn)

    // Create
    user, err := queries.CreateUser(ctx, db.CreateUserParams{
        Name:  "Alice",
        Email: "alice@example.com",
    })

    // Get
    user, err := queries.GetUser(ctx, 42)

    // List with pagination
    users, err := queries.ListUsers(ctx, db.ListUsersParams{
        Limit:  20,
        Offset: 40,
    })

    // Delete
    err = queries.DeleteUser(ctx, 42)
}
```

---

### 6. How do you handle nullable columns?

**A:**

```sql
-- Schema with nullable column
CREATE TABLE users (
    id      BIGSERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    bio     TEXT,           -- nullable
    age     INT             -- nullable
);

-- Query
-- name: GetUser :one
SELECT id, name, bio, age FROM users WHERE id = $1;
```

```go
// Generated with null_style: "sql_null_type"
type User struct {
    ID   int64          `json:"id"`
    Name string         `json:"name"`
    Bio  sql.NullString `json:"bio"`   // nullable
    Age  sql.NullInt32  `json:"age"`   // nullable
}

// Usage
if user.Bio.Valid {
    fmt.Println(user.Bio.String)
}

// With pgx driver and null_style: "pgx"
type User struct {
    Bio  pgtype.Text `json:"bio"`
}
```

---

### 7. How does SQLC handle transactions?

**A:** SQLC generates a `WithTx` method to use the same queries within a transaction:

```go
// Generated automatically
func (q *Queries) WithTx(tx *sql.Tx) *Queries {
    return &Queries{db: tx}
}

// Usage
func transferFunds(ctx context.Context, db *sql.DB, queries *db.Queries, fromID, toID int64, amount int64) error {
    tx, err := db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback()

    qtx := queries.WithTx(tx)

    if err := qtx.DeductBalance(ctx, db.DeductBalanceParams{ID: fromID, Amount: amount}); err != nil {
        return err
    }
    if err := qtx.AddBalance(ctx, db.AddBalanceParams{ID: toID, Amount: amount}); err != nil {
        return err
    }

    return tx.Commit()
}
```

---

## 🟡 Mid Level

---

### 8. How do you use SQLC with `pgx` instead of `database/sql`?

**A:** `pgx` is the recommended PostgreSQL driver for Go — faster, supports more PostgreSQL types:

```yaml
# sqlc.yaml
sql:
  - engine: "postgresql"
    gen:
      go:
        sql_package: "pgx/v5"   # use pgx instead of database/sql
```

```go
import (
    "github.com/jackc/pgx/v5/pgxpool"
    "myapp/internal/db"
)

pool, err := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
queries := db.New(pool)

// pgx supports native PostgreSQL types
// - pgtype.Text instead of sql.NullString
// - pgtype.Timestamptz, pgtype.UUID, etc.
// - COPY protocol for bulk inserts
// - Named arguments
```

---

### 9. How do you write complex queries with joins and aggregates?

**A:**

```sql
-- name: GetOrderSummary :one
SELECT
    o.id,
    o.total,
    o.status,
    c.name    AS customer_name,
    c.email   AS customer_email,
    COUNT(i.id)          AS item_count,
    SUM(i.qty * p.price) AS line_total
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN order_items i ON i.order_id = o.id
JOIN products p ON p.id = i.product_id
WHERE o.id = $1
GROUP BY o.id, o.total, o.status, c.name, c.email;

-- name: ListOrdersByStatus :many
SELECT
    o.id,
    o.created_at,
    o.total,
    o.status,
    c.name AS customer_name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = $1
ORDER BY o.created_at DESC
LIMIT $2 OFFSET $3;
```

SQLC generates a `GetOrderSummaryRow` struct with all the selected columns — no manual mapping.

---

### 10. How do you handle dynamic/optional filters with SQLC?

**A:** SQLC doesn't support fully dynamic WHERE clauses — you have several options:

**Option 1: Multiple specialized queries (preferred)**
```sql
-- name: ListUsers :many
SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2;

-- name: ListUsersByRole :many
SELECT * FROM users WHERE role = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3;

-- name: ListUsersByRoleAndStatus :many
SELECT * FROM users WHERE role = $1 AND is_active = $2
ORDER BY created_at DESC LIMIT $3 OFFSET $4;
```

**Option 2: COALESCE trick for optional filters**
```sql
-- name: SearchUsers :many
SELECT * FROM users
WHERE
    ($1::text IS NULL OR name ILIKE '%' || $1 || '%') AND
    ($2::text IS NULL OR role = $2) AND
    ($3::bool IS NULL OR is_active = $3)
ORDER BY created_at DESC;
```

**Option 3: Raw `database/sql` for truly dynamic queries** — SQLC and raw SQL coexist fine in the same codebase.

---

### 11. How do you do batch inserts with SQLC?

**A:**

```sql
-- name: BulkCreateUsers :batchone
INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *;
```

```go
// Generated batch API (pgx only)
batch := queries.BulkCreateUsers(ctx, []db.BulkCreateUsersParams{
    {Name: "Alice", Email: "alice@example.com"},
    {Name: "Bob",   Email: "bob@example.com"},
})

batch.QueryRow(func(i int, user db.User, err error) {
    if err != nil {
        log.Printf("row %d failed: %v", i, err)
        return
    }
    fmt.Println("Created:", user.ID)
})

if err := batch.Close(); err != nil {
    log.Fatal(err)
}
```

For large bulk inserts (thousands of rows), use `pgx`'s `CopyFrom`:
```go
rows := pgx.CopyFromRows(data)
n, err := pool.CopyFrom(ctx, pgx.Identifier{"users"}, []string{"name", "email"}, rows)
```

---

### 12. How do you test SQLC-generated code?

**A:**

```go
// Option 1: Test against a real DB (recommended — use testcontainers)
func TestCreateUser(t *testing.T) {
    ctx := context.Background()
    container, connStr := startPostgres(t) // testcontainers-go

    pool, _ := pgxpool.New(ctx, connStr)
    runMigrations(connStr)

    q := db.New(pool)

    user, err := q.CreateUser(ctx, db.CreateUserParams{
        Name:  "Alice",
        Email: "alice@test.com",
    })
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    assert.NotZero(t, user.ID)
}

// Option 2: Mock via the Querier interface
type MockQuerier struct {
    mock.Mock
}

func (m *MockQuerier) GetUser(ctx context.Context, id int64) (db.User, error) {
    args := m.Called(ctx, id)
    return args.Get(0).(db.User), args.Error(1)
}

func TestOrderService(t *testing.T) {
    mockQ := new(MockQuerier)
    mockQ.On("GetUser", ctx, int64(1)).Return(db.User{ID: 1, Name: "Alice"}, nil)

    svc := NewOrderService(mockQ)
    // ...
}
```

---

## 🔴 Senior Level

---

### 13. How do you structure a SQLC project for a large codebase?

**A:**

```
internal/
└── db/
    ├── sqlc.yaml           # config
    ├── schema/
    │   ├── 001_users.sql
    │   ├── 002_orders.sql
    │   └── 003_inventory.sql
    ├── queries/
    │   ├── users.sql
    │   ├── orders.sql
    │   └── reports.sql
    └── generated/          # never edit these
        ├── db.go
        ├── models.go
        ├── users.sql.go
        └── orders.sql.go
```

**Tips:**
- One `.sql` file per domain (users, orders, products)
- Keep schema and queries separate directories
- Generated code goes in its own package — import it, never edit it
- Use `sqlc vet` in CI to catch query errors before deployment

---

### 14. How do you implement the repository pattern with SQLC?

**A:**

```go
// Repository wraps SQLC queries — adds business logic, error translation
type UserRepository interface {
    GetByID(ctx context.Context, id int64) (*domain.User, error)
    GetByEmail(ctx context.Context, email string) (*domain.User, error)
    Create(ctx context.Context, params domain.CreateUserParams) (*domain.User, error)
}

type sqlcUserRepository struct {
    q db.Querier // SQLC-generated interface
}

func (r *sqlcUserRepository) GetByID(ctx context.Context, id int64) (*domain.User, error) {
    dbUser, err := r.q.GetUser(ctx, id)
    if errors.Is(err, pgx.ErrNoRows) {
        return nil, domain.ErrNotFound
    }
    if err != nil {
        return nil, fmt.Errorf("GetByID: %w", err)
    }
    return toDomainUser(dbUser), nil
}

// toDomainUser maps DB model → domain model
func toDomainUser(u db.User) *domain.User {
    return &domain.User{
        ID:    u.ID,
        Name:  u.Name,
        Email: u.Email,
    }
}
```

---

### 15. When should you choose SQLC over GORM?

**A:**

**Choose SQLC when:**
- Complex queries are the norm (reporting, analytics, CTEs, window functions)
- Compile-time SQL validation matters (errors caught before deployment)
- Performance is critical — zero ORM overhead, direct SQL
- Team is comfortable writing SQL
- Read-heavy CQRS architecture

**Choose GORM when:**
- Rapid prototyping
- Standard CRUD is most of your workload
- Team prefers Go-native query building
- AutoMigrate is acceptable for the project phase

**Hybrid (common in production):**
```
SQLC      → complex reads, reports, search
GORM      → simple CRUD writes, association management
Raw pgx   → bulk operations (COPY), real-time streams
```

---

## 🏛️ Architect Level

---

### 16. How do you design a data access layer with SQLC in a CQRS architecture?

**A:**

```go
// Command side — writes using SQLC (or GORM)
type CreateOrderCommandHandler struct {
    q   db.Querier
    pub EventPublisher
}

func (h *CreateOrderCommandHandler) Handle(ctx context.Context, cmd CreateOrderCommand) error {
    tx, err := h.pool.Begin(ctx)
    if err != nil { return err }
    defer tx.Rollback(ctx)

    qtx := h.q.WithTx(tx)

    order, err := qtx.CreateOrder(ctx, db.CreateOrderParams{
        CustomerID: cmd.CustomerID,
        Total:      cmd.Total,
    })
    if err != nil { return err }

    // Outbox — atomic event recording
    err = qtx.InsertOutboxMessage(ctx, db.InsertOutboxMessageParams{
        Type:    "OrderCreated",
        Payload: mustJSON(OrderCreatedEvent{OrderID: order.ID}),
    })
    if err != nil { return err }

    return tx.Commit(ctx)
}

// Query side — optimized reads with SQLC
type GetOrderDashboardHandler struct {
    q db.Querier
}

func (h *GetOrderDashboardHandler) Handle(ctx context.Context, q GetDashboardQuery) (*DashboardDTO, error) {
    // One SQL query with CTEs, window functions, aggregates
    stats, err := h.q.GetOrderDashboard(ctx, db.GetOrderDashboardParams{
        TenantID: q.TenantID,
        From:     q.From,
        To:       q.To,
    })
    return mapToDashboardDTO(stats), err
}
```
