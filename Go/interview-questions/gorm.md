# 🐘 GORM — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is GORM and what are its main features?

**A:** GORM is the most widely used ORM library for Go. It provides:
- **Auto-migrations** — generate tables from Go structs
- **CRUD operations** — `Create`, `Find`, `Save`, `Delete`
- **Associations** — `HasOne`, `HasMany`, `BelongsTo`, `ManyToMany`
- **Hooks** — `BeforeCreate`, `AfterSave`, etc.
- **Scopes** — reusable query fragments
- **Raw SQL** — escape hatch when needed
- **Multiple databases** — PostgreSQL, MySQL, SQLite, SQL Server

---

### 2. How do you define a model in GORM?

**A:**

```go
import "gorm.io/gorm"

type User struct {
    gorm.Model           // embeds ID, CreatedAt, UpdatedAt, DeletedAt (soft delete)
    Name  string         `gorm:"not null;size:200"`
    Email string         `gorm:"uniqueIndex;not null"`
    Age   int            `gorm:"check:age >= 0"`
    Role  string         `gorm:"default:user;size:50"`
    Posts []Post         // HasMany
}

type Post struct {
    ID        uint      `gorm:"primaryKey"`
    CreatedAt time.Time
    UpdatedAt time.Time
    Title     string    `gorm:"not null"`
    Body      string    `gorm:"type:text"`
    UserID    uint      // FK for BelongsTo
    User      User      // BelongsTo
    Tags      []Tag     `gorm:"many2many:post_tags;"` // ManyToMany
}

// gorm.Model adds these automatically:
// ID        uint           `gorm:"primaryKey;autoIncrement"`
// CreatedAt time.Time
// UpdatedAt time.Time
// DeletedAt gorm.DeletedAt `gorm:"index"` // soft delete
```

---

### 3. How do you connect to a database with GORM?

**A:**

```go
import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

dsn := "host=localhost user=postgres password=secret dbname=mydb port=5432 sslmode=disable"

db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
    Logger: logger.Default.LogMode(logger.Info), // log all SQL
    NowFunc: func() time.Time {
        return time.Now().UTC()
    },
    PrepareStmt: true, // cache prepared statements
})
if err != nil {
    log.Fatal("failed to connect:", err)
}

// Connection pool — access underlying *sql.DB
sqlDB, _ := db.DB()
sqlDB.SetMaxOpenConns(25)
sqlDB.SetMaxIdleConns(10)
sqlDB.SetConnMaxLifetime(5 * time.Minute)
```

---

### 4. How do you perform basic CRUD in GORM?

**A:**

```go
// Create
user := User{Name: "Alice", Email: "alice@example.com", Age: 30}
result := db.Create(&user)
// user.ID is now set
fmt.Println(result.RowsAffected, result.Error)

// Read
var user User
db.First(&user, 1)                             // by primary key
db.First(&user, "email = ?", "alice@example.com")
db.Where("age >= ? AND role = ?", 18, "admin").Find(&users)

// Update
db.Model(&user).Update("Name", "Bob")          // single field
db.Model(&user).Updates(User{Name: "Bob", Age: 31}) // struct — only non-zero fields
db.Model(&user).Updates(map[string]any{"name": "Bob", "age": 31}) // map — all fields

// Delete (soft delete if gorm.Model embedded)
db.Delete(&user, 1)
// Generates: UPDATE users SET deleted_at = NOW() WHERE id = 1

// Hard delete
db.Unscoped().Delete(&user, 1)
// Generates: DELETE FROM users WHERE id = 1
```

---

### 5. How do you query with conditions in GORM?

**A:**

```go
var users []User

// Where
db.Where("name = ?", "Alice").Find(&users)
db.Where("age BETWEEN ? AND ?", 18, 65).Find(&users)
db.Where("role IN ?", []string{"admin", "moderator"}).Find(&users)
db.Where("name LIKE ?", "%ali%").Find(&users)

// Not
db.Not("role = ?", "banned").Find(&users)

// Or
db.Where("role = ?", "admin").Or("role = ?", "superuser").Find(&users)

// Order, Limit, Offset
db.Order("created_at desc").Limit(10).Offset(20).Find(&users)

// Select specific columns
db.Select("id", "name", "email").Find(&users)

// Count
var count int64
db.Model(&User{}).Where("is_active = ?", true).Count(&count)

// First vs Find
db.First(&user)  // ORDER BY id LIMIT 1 — error if not found
db.Find(&users)  // no ordering, no error if empty
```

---

### 6. How do you load associations in GORM?

**A:**

```go
// Preload — separate query (like prefetch_related in Django)
var users []User
db.Preload("Posts").Find(&users)
// SELECT * FROM users; SELECT * FROM posts WHERE user_id IN (...)

// Preload with conditions
db.Preload("Posts", "published = ?", true).Find(&users)

// Nested preload
db.Preload("Posts.Comments").Find(&users)

// Joins — SQL JOIN (like select_related in Django)
db.Joins("User").Find(&posts)
// SELECT posts.*, users.* FROM posts JOIN users ON users.id = posts.user_id

// Eager loading all associations
db.Preload(clause.Associations).First(&user, id)
```

---

### 7. How do you run auto-migrations in GORM?

**A:**

```go
// Create or update tables to match structs
err := db.AutoMigrate(
    &User{},
    &Post{},
    &Tag{},
    &Order{},
)
if err != nil {
    log.Fatal("migration failed:", err)
}
```

**Limitations of AutoMigrate:**
- Will add columns and indexes but **won't delete** removed columns or change column types
- Not suitable for production — use a proper migration tool (Goose, Migrate, Atlas)
- Good for development and tests

---

### 8. What are GORM hooks?

**A:**

```go
func (u *User) BeforeCreate(tx *gorm.DB) error {
    u.ID = uuid.New()          // set UUID before insert
    u.Password = hash(u.Password)
    return nil
}

func (u *User) AfterCreate(tx *gorm.DB) error {
    // send welcome email, audit log, etc.
    return nil
}

func (o *Order) BeforeDelete(tx *gorm.DB) error {
    if o.Status == "shipped" {
        return errors.New("cannot delete shipped order")
    }
    return nil
}
```

**Available hooks:** `BeforeCreate`, `AfterCreate`, `BeforeSave`, `AfterSave`, `BeforeUpdate`, `AfterUpdate`, `BeforeDelete`, `AfterDelete`, `AfterFind`

---

### 9. How do you handle transactions in GORM?

**A:**

```go
// Automatic transaction
err := db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&order).Error; err != nil {
        return err // auto rollback
    }
    if err := tx.Model(&inventory).Update("stock", gorm.Expr("stock - ?", qty)).Error; err != nil {
        return err // auto rollback
    }
    return nil // auto commit
})

// Manual transaction
tx := db.Begin()
defer func() {
    if r := recover(); r != nil {
        tx.Rollback()
    }
}()

if err := tx.Create(&order).Error; err != nil {
    tx.Rollback()
    return err
}

if err := tx.Commit().Error; err != nil {
    return err
}
```

---

### 10. How do you use raw SQL in GORM?

**A:**

```go
// Raw — returns rows, scan into struct
var users []User
db.Raw("SELECT * FROM users WHERE age > ? AND role = ?", 18, "admin").Scan(&users)

// Raw into custom struct
type Stats struct {
    Count   int
    Revenue float64
}
var stats Stats
db.Raw("SELECT COUNT(*) as count, SUM(total) as revenue FROM orders WHERE status = ?", "completed").
    Scan(&stats)

// Exec — non-query
db.Exec("UPDATE users SET last_login = NOW() WHERE id = ?", userID)

// Named arguments
db.Raw("SELECT * FROM users WHERE name = @name AND age = @age",
    sql.Named("name", "Alice"), sql.Named("age", 30)).Scan(&users)
```

---

## 🟡 Mid Level

---

### 11. What are GORM scopes and how do you use them?

**A:** Scopes are reusable query fragments registered as functions:

```go
// Define scopes
func ActiveUsers(db *gorm.DB) *gorm.DB {
    return db.Where("is_active = ? AND deleted_at IS NULL", true)
}

func Paginate(page, pageSize int) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        offset := (page - 1) * pageSize
        return db.Offset(offset).Limit(pageSize)
    }
}

func OrderByLatest(db *gorm.DB) *gorm.DB {
    return db.Order("created_at DESC")
}

// Use
db.Scopes(ActiveUsers, OrderByLatest, Paginate(2, 20)).Find(&users)
// Equivalent to:
// db.Where("is_active = true AND deleted_at IS NULL").Order("created_at DESC").Offset(20).Limit(20).Find(&users)
```

---

### 12. How do you handle soft delete in GORM?

**A:** Embedding `gorm.Model` or `gorm.DeletedAt` enables soft delete automatically:

```go
type User struct {
    gorm.Model // includes gorm.DeletedAt
    Name string
}

// Soft delete — sets deleted_at
db.Delete(&user, 1)
// UPDATE users SET deleted_at = '2024-01-15' WHERE id = 1

// Queries automatically exclude soft-deleted records
db.Find(&users)
// SELECT * FROM users WHERE deleted_at IS NULL

// Include soft-deleted records
db.Unscoped().Find(&users)
// SELECT * FROM users

// Hard delete
db.Unscoped().Delete(&user, 1)
// DELETE FROM users WHERE id = 1

// Custom soft-delete field
type Order struct {
    ID        uint
    IsDeleted bool           `gorm:"default:false"`
    DeletedAt *time.Time
}
```

---

### 13. How do you use GORM with context for cancellation?

**A:**

```go
// Always pass context for cancellation and tracing
func (r *UserRepository) GetByID(ctx context.Context, id uint) (*User, error) {
    var user User
    result := r.db.WithContext(ctx).First(&user, id)
    if result.Error != nil {
        if errors.Is(result.Error, gorm.ErrRecordNotFound) {
            return nil, ErrNotFound
        }
        return nil, result.Error
    }
    return &user, nil
}

// HTTP handler
func getUser(c *gin.Context) {
    user, err := userRepo.GetByID(c.Request.Context(), id)
    // If client disconnects, context is cancelled, GORM query is cancelled
}
```

---

### 14. How do you handle many-to-many associations in GORM?

**A:**

```go
type User struct {
    gorm.Model
    Roles []Role `gorm:"many2many:user_roles;"`
}

type Role struct {
    gorm.Model
    Name  string
    Users []User `gorm:"many2many:user_roles;"`
}

// Add to association
db.Model(&user).Association("Roles").Append(&adminRole)

// Replace all
db.Model(&user).Association("Roles").Replace(&roleA, &roleB)

// Remove from association
db.Model(&user).Association("Roles").Delete(&adminRole)

// Clear all
db.Model(&user).Association("Roles").Clear()

// Count
count := db.Model(&user).Association("Roles").Count()

// Custom join table with extra fields
type UserRole struct {
    UserID    uint
    RoleID    uint
    AssignedAt time.Time
    AssignedBy uint
}
// Register as join table
db.SetupJoinTable(&User{}, "Roles", &UserRole{})
```

---

### 15. How do you implement custom data types in GORM?

**A:**

```go
// JSON column
type StringSlice []string

func (s StringSlice) Value() (driver.Value, error) {
    return json.Marshal(s)
}
func (s *StringSlice) Scan(value any) error {
    bytes, ok := value.([]byte)
    if !ok { return errors.New("type assertion failed") }
    return json.Unmarshal(bytes, s)
}

type Product struct {
    ID   uint
    Tags StringSlice `gorm:"type:json"`
}

// PostgreSQL JSONB with proper driver support
import "github.com/lib/pq"
type Product struct {
    Tags pq.StringArray `gorm:"type:text[]"`
}
```

---

### 16. What are GORM's performance pitfalls and how do you avoid them?

**A:**

```go
// N+1 problem — BAD
users, _ := db.Find(&users)
for _, u := range users {
    db.Where("user_id = ?", u.ID).Find(&u.Posts) // 1 query per user!
}

// FIX: Preload
db.Preload("Posts").Find(&users) // 2 queries total

// Selecting all columns — BAD for wide tables
db.Find(&users)

// FIX: select only needed columns
db.Select("id", "name", "email").Find(&users)

// Scanning into full model for read-only — BAD (change tracking overhead)
// GORM doesn't have tracking like EF Core, but full model scan is wasteful

// FIX: scan into lightweight DTO
type UserDTO struct { ID uint; Name string }
var dtos []UserDTO
db.Model(&User{}).Select("id", "name").Scan(&dtos)

// Missing indexes
// Always index FKs and commonly filtered columns
// Verify with db.Migrator().HasIndex(&User{}, "idx_email")
```

---

## 🔴 Senior Level

---

### 17. How do you implement a repository pattern with GORM?

**A:**

```go
type UserRepository interface {
    GetByID(ctx context.Context, id uint) (*User, error)
    List(ctx context.Context, filter UserFilter) ([]User, int64, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User, fields ...string) error
    Delete(ctx context.Context, id uint) error
}

type gormUserRepository struct {
    db *gorm.DB
}

func (r *gormUserRepository) GetByID(ctx context.Context, id uint) (*User, error) {
    var user User
    err := r.db.WithContext(ctx).First(&user, id).Error
    if errors.Is(err, gorm.ErrRecordNotFound) {
        return nil, ErrNotFound
    }
    return &user, err
}

func (r *gormUserRepository) Update(ctx context.Context, user *User, fields ...string) error {
    q := r.db.WithContext(ctx).Model(user)
    if len(fields) > 0 {
        q = q.Select(fields) // only update specified columns
    }
    return q.Updates(user).Error
}

func (r *gormUserRepository) List(ctx context.Context, f UserFilter) ([]User, int64, error) {
    var users []User
    var total int64

    q := r.db.WithContext(ctx).Model(&User{})
    if f.Role != "" { q = q.Where("role = ?", f.Role) }
    if f.IsActive != nil { q = q.Where("is_active = ?", *f.IsActive) }

    q.Count(&total)
    err := q.Scopes(Paginate(f.Page, f.PageSize)).Find(&users).Error
    return users, total, err
}
```

---

### 18. How do you handle database migrations properly (not AutoMigrate)?

**A:** For production, use a dedicated migration tool:

**Goose:**
```bash
goose -dir migrations postgres "$DSN" up
goose create add_user_index sql
```

```sql
-- migrations/20240115_add_user_index.sql
-- +goose Up
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- +goose Down
DROP INDEX idx_users_email;
```

**golang-migrate:**
```bash
migrate -path migrations -database "$DSN" up
migrate create -ext sql -dir migrations -seq add_user_index
```

**Integration with GORM:** Use GORM only for model definitions; run migrations separately before deploying:
```go
// In main() or init container
if err := runMigrations(dsn); err != nil {
    log.Fatal(err)
}
db, _ := gorm.Open(postgres.Open(dsn), &gorm.Config{})
```

---

### 19. How do you implement multi-tenancy with GORM?

**A:**

```go
// Row-level: scope all queries
func TenantScope(tenantID string) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Where("tenant_id = ?", tenantID)
    }
}

// In repository
func (r *OrderRepo) ListOrders(ctx context.Context, tenantID string) ([]Order, error) {
    var orders []Order
    err := r.db.WithContext(ctx).Scopes(TenantScope(tenantID)).Find(&orders).Error
    return orders, err
}

// Schema-level: switch schema per request
func WithTenantSchema(db *gorm.DB, schema string) *gorm.DB {
    return db.Exec("SET search_path = " + schema).Session(&gorm.Session{})
}

// Plugin-based: automatically inject tenant_id
type TenantPlugin struct{ TenantID string }

func (p *TenantPlugin) Name() string { return "tenant" }
func (p *TenantPlugin) Initialize(db *gorm.DB) error {
    db.Callback().Create().Before("gorm:create").Register("tenant:create", func(db *gorm.DB) {
        if db.Statement.Schema != nil {
            if _, ok := db.Statement.Schema.FieldsByName["TenantID"]; ok {
                db.Statement.SetColumn("TenantID", p.TenantID)
            }
        }
    })
    return nil
}
```

---

## 🏛️ Architect Level

---

### 20. When should you choose GORM over SQLC or raw database/sql?

**A:**

| | GORM | SQLC | `database/sql` + Dapper-style |
|--|------|------|-------------------------------|
| SQL control | Low (generated) | Full | Full |
| Type safety | Runtime | Compile-time | Runtime |
| Boilerplate | Low | Medium | High |
| Migrations | AutoMigrate (dev only) | External | External |
| Associations | Rich | Manual | Manual |
| Performance | Good with tuning | Excellent | Excellent |
| Learning curve | Low | Medium | Low |

**Choose GORM when:** Rapid development, standard CRUD, team not confident in SQL.

**Choose SQLC when:** Performance is critical, you want compile-time query validation, complex queries are common.

**Choose raw `database/sql`:** When you need maximum control, zero overhead, or you're building a library.

**Hybrid:** GORM for writes (Create/Update/Delete), SQLC or raw SQL for complex reads — matches CQRS naturally.
