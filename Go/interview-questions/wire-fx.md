# 💉 Dependency Injection in Go — Wire & Uber Fx — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. Why does Go need DI frameworks when it has no built-in DI?

**A:** Go has no DI container built in. Without a framework, wiring dependencies manually leads to:

```go
// Manual wiring — works fine for small apps, painful at scale
func main() {
    db := database.NewPostgres(config.DSN)
    cache := redis.NewClient(config.RedisURL)
    userRepo := repository.NewUserRepository(db, cache)
    orderRepo := repository.NewOrderRepository(db)
    emailSvc := email.NewSMTPSender(config.SMTP)
    userSvc := service.NewUserService(userRepo, emailSvc)
    orderSvc := service.NewOrderService(orderRepo, userSvc)
    handler := handler.NewHTTPHandler(userSvc, orderSvc)
    // ...30 more lines of wiring
}
```

**DI frameworks solve:**
- Compile-time validation that all dependencies are satisfied (Wire)
- Lifecycle management — start/stop in the right order (Fx)
- Reduced boilerplate
- Easier testing via dependency replacement

---

### 2. What is Google Wire and how does it work?

**A:** Wire is a **compile-time** code generation tool — it reads your providers and generates the wiring code for you:

```go
// 1. Define providers — functions that construct a type
func NewDB(cfg Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.DSN)
}

func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}

func NewUserService(repo *UserRepository, email EmailSender) *UserService {
    return &UserService{repo: repo, email: email}
}

// 2. Define injector — tells Wire what to build
//go:build wireinject
// +build wireinject

func InitializeUserService(cfg Config) (*UserService, error) {
    wire.Build(
        NewDB,
        NewUserRepository,
        NewEmailSender,
        NewUserService,
    )
    return nil, nil // Wire replaces this
}
```

```bash
# Wire reads providers and generates wire_gen.go
wire gen ./...
```

```go
// Generated wire_gen.go (never edit manually)
func InitializeUserService(cfg Config) (*UserService, error) {
    db, err := NewDB(cfg)
    if err != nil { return nil, err }
    repo := NewUserRepository(db)
    email := NewEmailSender(cfg)
    svc := NewUserService(repo, email)
    return svc, nil
}
```

---

### 3. What is Uber Fx and how does it differ from Wire?

**A:**

| | Wire | Uber Fx |
|--|------|---------|
| Type | Code generator | Runtime DI container |
| Validation | Compile-time | Startup-time |
| Lifecycle | Manual | Built-in Start/Stop |
| Approach | Generate wiring code | Register providers + run |
| Best for | Libraries, simple apps | Long-running services |

```go
// Uber Fx
import "go.uber.org/fx"

func main() {
    app := fx.New(
        fx.Provide(
            NewConfig,
            NewDB,
            NewUserRepository,
            NewEmailSender,
            NewUserService,
            NewHTTPServer,
        ),
        fx.Invoke(func(srv *http.Server) {}), // ensure server is built
    )
    app.Run() // starts all, blocks, graceful shutdown on SIGTERM
}
```

---

### 4. How do you define Wire providers with sets?

**A:** `wire.NewSet` groups related providers — the equivalent of a module:

```go
// repository/wire.go
var RepositorySet = wire.NewSet(
    NewUserRepository,
    NewOrderRepository,
    NewProductRepository,
)

// service/wire.go
var ServiceSet = wire.NewSet(
    NewUserService,
    NewOrderService,
    NewProductService,
)

// main.go wire injector
func InitializeApp(cfg Config) (*App, error) {
    wire.Build(
        NewDB,
        NewRedis,
        repository.RepositorySet,
        service.ServiceSet,
        handler.HandlerSet,
        NewApp,
    )
    return nil, nil
}
```

---

### 5. How do you handle interfaces in Wire?

**A:** Wire needs to know which implementation to use for an interface — use `wire.Bind`:

```go
type EmailSender interface {
    Send(to, subject, body string) error
}

type SMTPSender struct{}
func (s *SMTPSender) Send(to, subject, body string) error { ... }

func NewSMTPSender(cfg Config) *SMTPSender {
    return &SMTPSender{}
}

// Bind the interface to the concrete type
var EmailSet = wire.NewSet(
    NewSMTPSender,
    wire.Bind(new(EmailSender), new(*SMTPSender)),
)

// Now Wire injects EmailSender interface wherever needed
func NewUserService(repo *UserRepository, email EmailSender) *UserService { ... }
```

---

## 🟡 Mid Level

---

### 6. How do you manage lifecycle with Uber Fx?

**A:** Fx provides `OnStart` and `OnStop` hooks for graceful startup and shutdown:

```go
func NewHTTPServer(lc fx.Lifecycle, handler http.Handler) *http.Server {
    srv := &http.Server{Addr: ":8080", Handler: handler}

    lc.Append(fx.Hook{
        OnStart: func(ctx context.Context) error {
            go func() {
                if err := srv.ListenAndServe(); err != http.ErrServerClosed {
                    log.Printf("HTTP server error: %v", err)
                }
            }()
            return nil
        },
        OnStop: func(ctx context.Context) error {
            return srv.Shutdown(ctx)
        },
    })

    return srv
}

func NewKafkaConsumer(lc fx.Lifecycle, cfg Config) *kgo.Client {
    client, _ := kgo.NewClient(kgo.SeedBrokers(cfg.KafkaBrokers))

    lc.Append(fx.Hook{
        OnStart: func(ctx context.Context) error {
            go consumeLoop(ctx, client)
            return nil
        },
        OnStop: func(ctx context.Context) error {
            client.Close()
            return nil
        },
    })

    return client
}

// Fx starts all OnStart hooks in registration order
// Stops all OnStop hooks in reverse order (LIFO) on SIGTERM
```

---

### 7. How do you provide multiple implementations of the same type with Fx?

**A:** Use `fx.Annotate` with named values or `fx.Tag`:

```go
// Named values
func NewPrimaryDB(cfg Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.PrimaryDSN)
}

func NewReplicaDB(cfg Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.ReplicaDSN)
}

app := fx.New(
    fx.Provide(
        fx.Annotate(NewPrimaryDB, fx.ResultTags(`name:"primary"`)),
        fx.Annotate(NewReplicaDB, fx.ResultTags(`name:"replica"`)),
    ),
    fx.Provide(
        fx.Annotate(NewOrderRepository, fx.ParamTags(`name:"primary"`, `name:"replica"`)),
    ),
)

func NewOrderRepository(
    primary *sql.DB, // injected by name
    replica *sql.DB,
) *OrderRepository {
    return &OrderRepository{write: primary, read: replica}
}
```

---

### 8. How do you use Fx modules for organizing large applications?

**A:**

```go
// internal/database/module.go
var Module = fx.Module("database",
    fx.Provide(NewPostgres),
    fx.Provide(NewRedis),
)

// internal/repository/module.go
var Module = fx.Module("repository",
    fx.Provide(NewUserRepository),
    fx.Provide(NewOrderRepository),
)

// internal/service/module.go
var Module = fx.Module("service",
    fx.Provide(NewUserService),
    fx.Provide(NewOrderService),
)

// internal/handler/module.go
var Module = fx.Module("handler",
    fx.Provide(NewHTTPHandler),
    fx.Provide(NewGRPCHandler),
)

// cmd/server/main.go
func main() {
    fx.New(
        database.Module,
        repository.Module,
        service.Module,
        handler.Module,
        fx.Invoke(registerRoutes),
    ).Run()
}
```

---

### 9. How do you test with Wire-generated code?

**A:**

```go
// Replace a real provider with a test provider in the injector
//go:build wireinject

func InitializeTestApp(db *sql.DB) (*App, error) {
    wire.Build(
        // Use provided test DB instead of NewDB
        NewUserRepository, // receives the test DB
        NewMockEmailSender, // mock instead of real SMTP
        NewUserService,
        NewApp,
    )
    return nil, nil
}

// In test
func TestUserService(t *testing.T) {
    db := startTestDB(t)
    app, err := InitializeTestApp(db)
    require.NoError(t, err)
    // test with real repo but mock email
}
```

---

### 10. How do you test with Fx?

**A:**

```go
import "go.uber.org/fx/fxtest"

func TestUserService(t *testing.T) {
    var svc *UserService

    app := fxtest.New(t,
        fx.Provide(func() *sql.DB { return startTestDB(t) }),
        fx.Provide(NewUserRepository),
        fx.Provide(NewMockEmailSender), // inject mock
        fx.Provide(NewUserService),
        fx.Populate(&svc), // extract the built service
    )

    app.RequireStart()
    defer app.RequireStop()

    user, err := svc.CreateUser(context.Background(), "Alice", "alice@test.com")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}
```

---

## 🔴 Senior Level

---

### 11. How do you handle configuration injection cleanly in Wire?

**A:**

```go
// Config struct with sub-configs
type Config struct {
    DB    DBConfig
    Redis RedisConfig
    HTTP  HTTPConfig
    SMTP  SMTPConfig
}

// Wire value sets — inject sub-configs without passing the whole Config
func ProvideDBConfig(cfg Config) DBConfig       { return cfg.DB }
func ProvideRedisConfig(cfg Config) RedisConfig { return cfg.Redis }
func ProvideSMTPConfig(cfg Config) SMTPConfig   { return cfg.SMTP }

var ConfigSet = wire.NewSet(
    ProvideDBConfig,
    ProvideRedisConfig,
    ProvideSMTPConfig,
)

// Providers only declare what they need
func NewDB(cfg DBConfig) (*sql.DB, error) {
    return sql.Open("postgres", cfg.DSN)
}

func NewSMTPSender(cfg SMTPConfig) *SMTPSender {
    return &SMTPSender{host: cfg.Host}
}

// Injector
func InitializeApp(cfg Config) (*App, error) {
    wire.Build(ConfigSet, NewDB, NewRedis, NewSMTPSender, ...)
    return nil, nil
}
```

---

### 12. How do you structure a large Go application with Fx for clean architecture?

**A:**

```go
// Enforce dependency direction through Fx module boundaries
// domain ← service ← handler

// Domain layer — no Fx dependency (pure Go)
package domain
// no fx.Provide here — domain doesn't know about DI

// Infrastructure layer — provides implementations
package postgres
var Module = fx.Module("postgres",
    fx.Provide(func(cfg Config) (domain.UserRepository, error) {
        db, err := NewDB(cfg)
        return NewPostgresUserRepository(db), err
    }),
)

// Service layer
package service
var Module = fx.Module("service",
    fx.Provide(NewUserService), // receives domain.UserRepository interface
)

// Handler layer
package handler
var Module = fx.Module("handler",
    fx.Provide(NewHTTPServer),
    fx.Provide(NewGRPCServer),
)

// Composition root — only place that knows about all layers
func main() {
    fx.New(
        config.Module,       // loads config
        postgres.Module,     // implements domain.UserRepository
        redis.Module,        // implements domain.CacheRepository
        service.Module,      // business logic
        handler.Module,      // HTTP/gRPC
    ).Run()
}
```

---

## 🏛️ Architect Level

---

### 13. When should you use Wire vs Fx vs manual wiring?

**A:**

**Manual wiring — choose when:**
- Small application (< 10 dependencies)
- CLI tool or script
- Team unfamiliar with DI frameworks
- Startup time is critical (no framework overhead)

```go
func main() {
    cfg := config.Load()
    db := postgres.New(cfg.DSN)
    repo := repository.NewUser(db)
    svc := service.NewUser(repo)
    srv := handler.NewHTTP(svc)
    srv.Start()
}
```

**Wire — choose when:**
- Medium to large app
- Want compile-time safety (no missing dependency surprises at runtime)
- Teams that prefer generated code over runtime magic
- Microservice with no complex lifecycle management

**Fx — choose when:**
- Complex lifecycle (multiple servers, consumers, background workers to start/stop in order)
- Large monolith with many modules
- Need dynamic module composition
- Teams comfortable with runtime framework

**Anti-patterns to avoid:**
```go
// Don't use global variables as poor man's DI
var globalDB *sql.DB // hard to test, hidden dependency

// Don't use init() for wiring — order is unpredictable
func init() {
    globalDB = connectDB()
}

// Don't inject the container itself
func NewService(container *fx.App) *Service // violates DI principle
```

---

### 14. How do you design providers for testability with Wire?

**A:**

```go
// Define a TestProviderSet for tests — swaps real implementations
var TestProviderSet = wire.NewSet(
    NewTestDB,           // in-memory or testcontainers DB
    NewMockEmailSender,  // no real emails
    NewMockStripeClient, // no real charges
    wire.Bind(new(EmailSender), new(*MockEmailSender)),
    wire.Bind(new(StripeClient), new(*MockStripeClient)),
)

var ProductionProviderSet = wire.NewSet(
    NewPostgresDB,
    NewSMTPEmailSender,
    NewRealStripeClient,
    wire.Bind(new(EmailSender), new(*SMTPEmailSender)),
    wire.Bind(new(StripeClient), new(*RealStripeClient)),
)

// Test injector
//go:build wireinject

func InitializeTestApp(t *testing.T) (*App, func()) {
    wire.Build(TestProviderSet, NewApp)
    return nil, nil
}

// Production injector
func InitializeApp(cfg Config) (*App, error) {
    wire.Build(ProductionProviderSet, NewApp)
    return nil, nil
}
```
