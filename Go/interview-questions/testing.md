# 🧪 Testing in Go — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. How does Go's built-in testing package work?

**A:**

```go
// math_test.go
package math_test  // black-box test (or package math for white-box)

import (
    "testing"
    "github.com/myorg/myapp/math"
)

func TestAdd(t *testing.T) {
    got := math.Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2, 3) = %d; want %d", got, want)
    }
}

func TestAdd_Negative(t *testing.T) {
    got := math.Add(-1, 1)
    if got != 0 {
        t.Errorf("got %d; want 0", got)
    }
}
```

```bash
go test ./...             # all packages
go test -v ./...          # verbose output
go test -run TestAdd      # run specific test(s)
go test -run TestAdd/Case # run subtest
go test -count=1 ./...    # disable test caching
go test -race ./...       # race detector
go test -cover ./...      # coverage
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

---

### 2. What is table-driven testing and why is it idiomatic in Go?

**A:**

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    float64
        want    float64
        wantErr bool
    }{
        {"positive", 10, 2, 5, false},
        {"negative", -10, 2, -5, false},
        {"zero dividend", 0, 5, 0, false},
        {"divide by zero", 10, 0, 0, true},
        {"both negative", -10, -2, 5, false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)

            if (err != nil) != tt.wantErr {
                t.Errorf("Divide() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if !tt.wantErr && got != tt.want {
                t.Errorf("Divide() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

Benefits: one loop handles all cases, easy to add new cases, each case has a name for clear failure messages, subtests can be run individually (`-run TestDivide/divide_by_zero`).

---

### 3. How do you use `t.Helper`, `t.Fatal`, `t.Error`, and `t.Skip`?

**A:**

```go
// t.Error — marks test as failed but continues
t.Error("something went wrong but test continues")

// t.Errorf — with formatting
t.Errorf("got %v; want %v", got, want)

// t.Fatal — marks test as failed and stops immediately (calls t.FailNow)
t.Fatal("setup failed, can't continue")
t.Fatalf("could not connect to DB: %v", err)

// t.Skip — skip the test (useful for integration tests)
if os.Getenv("INTEGRATION") == "" {
    t.Skip("skipping integration test")
}

// t.Helper — marks function as a test helper
// Error messages report the caller's line, not the helper's
func assertEqual(t *testing.T, got, want any) {
    t.Helper()
    if got != want {
        t.Errorf("got %v; want %v", got, want)
    }
}
```

---

### 4. What are benchmarks in Go?

**A:**

```go
func BenchmarkFibonacci(b *testing.B) {
    for i := 0; i < b.N; i++ { // b.N is auto-calibrated
        Fibonacci(20)
    }
}

// With setup that shouldn't be measured
func BenchmarkProcess(b *testing.B) {
    data := generateTestData(10000) // setup
    b.ResetTimer()                  // exclude setup from measurement

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

// Parallel benchmark
func BenchmarkParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Process(data)
        }
    })
}
```

```bash
go test -bench=. -benchmem -benchtime=5s ./...
# BenchmarkFibonacci-8    2000000    742 ns/op    0 B/op    0 allocs/op
```

---

### 5. How do you write subtests and setup/teardown?

**A:**

```go
func TestOrderService(t *testing.T) {
    // Setup shared for all subtests
    db := setupTestDB(t)
    svc := NewOrderService(db)

    t.Run("CreateOrder", func(t *testing.T) {
        order, err := svc.Create(ctx, req)
        require.NoError(t, err)
        assert.NotEmpty(t, order.ID)
    })

    t.Run("GetOrder", func(t *testing.T) {
        order, err := svc.Get(ctx, "order-1")
        require.NoError(t, err)
        assert.Equal(t, "order-1", order.ID)
    })

    t.Run("GetOrder/NotFound", func(t *testing.T) {
        _, err := svc.Get(ctx, "missing")
        assert.ErrorIs(t, err, ErrNotFound)
    })
}

// t.Cleanup — runs after test (or subtest) finishes, even on failure
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("postgres", testDSN)
    if err != nil {
        t.Fatal(err)
    }
    t.Cleanup(func() { db.Close() })
    return db
}
```

---

## 🟡 Mid Level

---

### 6. How do you use testify for assertions and mocking?

**A:**

```go
import (
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "github.com/stretchr/testify/suite"
)

func TestUser(t *testing.T) {
    user, err := CreateUser("Alice", "alice@example.com")

    // require — stops test immediately on failure (use for preconditions)
    require.NoError(t, err)
    require.NotNil(t, user)

    // assert — records failure but continues
    assert.Equal(t, "Alice", user.Name)
    assert.Equal(t, "alice@example.com", user.Email)
    assert.NotZero(t, user.ID)
    assert.True(t, user.IsActive)
    assert.WithinDuration(t, time.Now(), user.CreatedAt, time.Second)

    // Error assertions
    _, err = CreateUser("", "")
    assert.Error(t, err)
    assert.ErrorIs(t, err, ErrValidation)
    assert.ErrorContains(t, err, "name is required")

    // Slice/map assertions
    assert.ElementsMatch(t, []int{1, 2, 3}, []int{3, 1, 2}) // order-independent
    assert.Contains(t, user.Tags, "verified")
    assert.Len(t, user.Orders, 3)
}
```

---

### 7. How do you create mocks with `mockery` or `gomock`?

**A:**

```go
// Define your interface
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

// --- mockery approach ---
// go:generate mockery --name=UserRepository --output=mocks
// Auto-generates mocks/UserRepository.go

func TestUserService_GetUser(t *testing.T) {
    mockRepo := mocks.NewUserRepository(t) // auto-cleanup on test end

    // Set expectations
    mockRepo.On("GetByID", mock.Anything, "user-1").
        Return(&User{ID: "user-1", Name: "Alice"}, nil)

    svc := NewUserService(mockRepo)
    user, err := svc.GetUser(context.Background(), "user-1")

    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    mockRepo.AssertExpectations(t) // verify all expected calls were made
}

// Handle error case
mockRepo.On("GetByID", mock.Anything, "missing").
    Return(nil, ErrNotFound)

// Match any argument of a type
mockRepo.On("Save", mock.Anything, mock.AnythingOfType("*User")).
    Return(nil)

// Capture arguments
mockRepo.On("Save", mock.Anything, mock.MatchedBy(func(u *User) bool {
    return u.Name == "Alice"
})).Return(nil)
```

---

### 8. How do you use `testcontainers-go` for integration tests?

**A:**

```go
import (
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
    "github.com/testcontainers/testcontainers-go/modules/redis"
)

func TestWithRealDB(t *testing.T) {
    ctx := context.Background()

    // Start Postgres container
    pgContainer, err := postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready to accept connections").
                WithOccurrence(2)),
    )
    require.NoError(t, err)
    t.Cleanup(func() { pgContainer.Terminate(ctx) })

    connStr, _ := pgContainer.ConnectionString(ctx, "sslmode=disable")

    // Run migrations
    runMigrations(t, connStr)

    // Run test
    db, _ := sql.Open("postgres", connStr)
    repo := NewUserRepository(db)

    user, err := repo.Create(ctx, &User{Name: "Alice"})
    require.NoError(t, err)
    assert.NotZero(t, user.ID)
}

// Reuse container across tests in a package (TestMain)
var (
    testDB *sql.DB
)

func TestMain(m *testing.M) {
    ctx := context.Background()
    pgContainer, _ := postgres.Run(ctx, "postgres:16-alpine", ...)
    connStr, _ := pgContainer.ConnectionString(ctx)
    testDB, _ = sql.Open("postgres", connStr)
    runMigrations(connStr)

    code := m.Run()

    pgContainer.Terminate(ctx)
    os.Exit(code)
}
```

---

### 9. How do you test HTTP handlers without starting a server?

**A:**

```go
import "net/http/httptest"

func TestGetUserHandler(t *testing.T) {
    mockSvc := mocks.NewUserService(t)
    mockSvc.On("GetUser", mock.Anything, "42").
        Return(&User{ID: "42", Name: "Alice"}, nil)

    handler := NewUserHandler(mockSvc)
    router := setupRouter(handler)

    // Create request and recorder
    req := httptest.NewRequest(http.MethodGet, "/users/42", nil)
    req.Header.Set("Authorization", "Bearer "+validToken)
    w := httptest.NewRecorder()

    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    var resp UserResponse
    err := json.Unmarshal(w.Body.Bytes(), &resp)
    require.NoError(t, err)
    assert.Equal(t, "Alice", resp.Name)
}

func TestGetUserHandler_NotFound(t *testing.T) {
    mockSvc := mocks.NewUserService(t)
    mockSvc.On("GetUser", mock.Anything, "99").Return(nil, ErrNotFound)

    handler := NewUserHandler(mockSvc)
    router := setupRouter(handler)

    req := httptest.NewRequest(http.MethodGet, "/users/99", nil)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusNotFound, w.Code)
}
```

---

### 10. What is fuzzing in Go and how do you write a fuzz test?

**A:** Fuzz testing automatically generates random inputs to find crashes and panics:

```go
// func FuzzXxx(f *testing.F) — naming convention
func FuzzParseEmail(f *testing.F) {
    // Seed corpus — known interesting inputs
    f.Add("alice@example.com")
    f.Add("invalid-email")
    f.Add("")
    f.Add("@")
    f.Add("a@b.c")

    f.Fuzz(func(t *testing.T, email string) {
        // Must not panic for any input
        result, err := ParseEmail(email)
        if err != nil {
            return // invalid input is fine, panic is not
        }
        // Invariant: parsed email must re-parse identically
        result2, err2 := ParseEmail(result.String())
        if err2 != nil {
            t.Errorf("re-parse failed: %v", err2)
        }
        if result.String() != result2.String() {
            t.Errorf("not idempotent: %q vs %q", result, result2)
        }
    })
}
```

```bash
go test -fuzz=FuzzParseEmail -fuzztime=60s   # fuzz for 60 seconds
go test -fuzz=FuzzParseEmail -fuzztime=60s -parallel=8
go test ./... # regular mode — only runs seed corpus
```

---

### 11. How do you use build tags to separate unit and integration tests?

**A:**

```go
//go:build integration

package repository_test

import (
    "testing"
)

// Only compiled and run when -tags integration is passed
func TestUserRepository_Integration(t *testing.T) {
    db := connectToRealDB(t)
    repo := NewUserRepository(db)
    // ...
}
```

```bash
# Run only unit tests (default)
go test ./...

# Run integration tests
go test -tags integration ./...

# Run all
go test -tags integration,e2e ./...
```

Alternatively, use environment variable check:
```go
func TestIntegration(t *testing.T) {
    if os.Getenv("INTEGRATION") == "" {
        t.Skip("set INTEGRATION=1 to run")
    }
    // ...
}
```

---

## 🔴 Senior Level

---

### 12. How do you measure and improve test coverage meaningfully?

**A:**

```bash
# Generate coverage profile
go test -coverprofile=coverage.out -covermode=atomic ./...

# View in browser
go tool cover -html=coverage.out

# Coverage by function
go tool cover -func=coverage.out | sort -k3 -n

# CI threshold (fail if below 80%)
go test -coverprofile=coverage.out ./...
coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
if (( $(echo "$coverage < 80" | bc -l) )); then
  echo "Coverage $coverage% below threshold 80%"
  exit 1
fi
```

**Coverage modes:**
- `set` — was each statement reached? (default)
- `count` — how many times was each statement reached?
- `atomic` — like count, but safe for parallel tests

**Meaningful coverage:**
- Focus on critical paths and domain logic, not boilerplate
- 100% coverage on generated code is not useful
- Use `//nolint:exhaustruct` and `//nolint:unused` sparingly; prefer explicit
- Exclude generated files: `go test -coverprofile=coverage.out $(go list ./... | grep -v /gen/)`

---

### 13. How do you test concurrent code?

**A:**

```go
// Run with race detector
// go test -race ./...

func TestConcurrentCounter(t *testing.T) {
    c := NewCounter()
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            c.Increment()
        }()
    }
    wg.Wait()
    assert.Equal(t, int64(1000), c.Value())
}

// Stress test — run many times to expose flakiness
func TestConcurrentMap(t *testing.T) {
    if testing.Short() {
        t.Skip("stress test")
    }
    for i := 0; i < 10000; i++ {
        t.Run("", func(t *testing.T) {
            t.Parallel()
            m := NewSafeMap()
            m.Set("key", i)
            _ = m.Get("key")
        })
    }
}

// Deterministic testing with channels
func TestPipeline(t *testing.T) {
    in := make(chan int, 5)
    out := process(in)

    for _, v := range []int{1, 2, 3, 4, 5} {
        in <- v
    }
    close(in)

    var results []int
    for v := range out {
        results = append(results, v)
    }
    assert.ElementsMatch(t, []int{2, 4, 6, 8, 10}, results)
}
```

---

### 14. How do you implement a test suite with `testify/suite`?

**A:**

```go
import "github.com/stretchr/testify/suite"

type OrderServiceSuite struct {
    suite.Suite
    db      *sql.DB
    service *OrderService
    ctx     context.Context
}

// SetupSuite — runs once before all tests in the suite
func (s *OrderServiceSuite) SetupSuite() {
    s.ctx = context.Background()
    s.db = startTestDB(s.T())
    runMigrations(s.db)
}

// TearDownSuite — runs once after all tests
func (s *OrderServiceSuite) TearDownSuite() {
    s.db.Close()
}

// SetupTest — runs before each test method
func (s *OrderServiceSuite) SetupTest() {
    s.service = NewOrderService(s.db)
    s.db.Exec("TRUNCATE orders, order_items CASCADE")
}

func (s *OrderServiceSuite) TestCreateOrder() {
    order, err := s.service.Create(s.ctx, &CreateOrderInput{CustomerID: "c1"})
    s.Require().NoError(err)
    s.NotEmpty(order.ID)
}

func (s *OrderServiceSuite) TestGetOrder_NotFound() {
    _, err := s.service.Get(s.ctx, "missing")
    s.ErrorIs(err, ErrNotFound)
}

// Run the suite
func TestOrderServiceSuite(t *testing.T) {
    suite.Run(t, new(OrderServiceSuite))
}
```

---

### 15. How do you test with golden files?

**A:** Golden files store expected output — useful for complex structs, HTML, JSON, SQL:

```go
var update = flag.Bool("update", false, "update golden files")

func TestFormatReport(t *testing.T) {
    input := &Report{Title: "Q4 Results", Data: testData}
    got := FormatReport(input)

    goldenFile := filepath.Join("testdata", t.Name()+".golden")

    if *update {
        // Run with -update to regenerate golden files
        os.MkdirAll(filepath.Dir(goldenFile), 0755)
        os.WriteFile(goldenFile, []byte(got), 0644)
    }

    want, err := os.ReadFile(goldenFile)
    require.NoError(t, err, "golden file missing — run with -update to create")
    assert.Equal(t, string(want), got)
}
```

```bash
# Regenerate golden files when output intentionally changes
go test ./... -update
# Then review the diff and commit
```

---

## 🏛️ Architect Level

---

### 16. How do you structure tests in a large Go codebase?

**A:**

```
myservice/
├── internal/
│   ├── domain/
│   │   ├── order.go
│   │   └── order_test.go          # unit tests — white-box
│   ├── service/
│   │   ├── order_service.go
│   │   └── order_service_test.go  # unit tests with mocks
│   ├── repository/
│   │   ├── order_repo.go
│   │   └── order_repo_test.go     # integration — uses testcontainers
│   └── handler/
│       ├── order_handler.go
│       └── order_handler_test.go  # handler tests with httptest
├── integration/                   # end-to-end tests (build tag: integration)
│   └── order_flow_test.go
└── testdata/                      # fixtures, golden files
    ├── fixtures/
    │   └── orders.json
    └── TestFormatReport/
        └── golden
```

**Test pyramid in Go:**
- **Unit** — pure functions, domain logic, no I/O; fast, many
- **Integration** — repository tests with real DB (testcontainers); medium speed
- **Handler** — HTTP handler tests with httptest + mocked service; fast
- **E2E** — full stack with Docker Compose; slow, few, CI only

**CI strategy:**
```yaml
test-unit:
  run: go test -race -count=1 ./...

test-integration:
  run: go test -race -tags integration -count=1 ./...
  services: [postgres, redis]
```

---

### 17. How do you test code that depends on time?

**A:**

```go
// Inject a clock interface — don't use time.Now() directly
type Clock interface {
    Now() time.Time
    After(d time.Duration) <-chan time.Time
}

type RealClock struct{}
func (RealClock) Now() time.Time                         { return time.Now() }
func (RealClock) After(d time.Duration) <-chan time.Time { return time.After(d) }

// Production
svc := NewOrderService(RealClock{})

// Test with a fake clock (quartz or manual)
type FixedClock struct{ t time.Time }
func (f FixedClock) Now() time.Time                         { return f.t }
func (f FixedClock) After(d time.Duration) <-chan time.Time {
    ch := make(chan time.Time, 1)
    ch <- f.t.Add(d)
    return ch
}

func TestOrderExpiry(t *testing.T) {
    fixedTime := time.Date(2024, 1, 15, 12, 0, 0, 0, time.UTC)
    svc := NewOrderService(FixedClock{t: fixedTime})

    order := svc.CreateOrder(ctx, req)
    assert.Equal(t, fixedTime, order.CreatedAt)
    assert.Equal(t, fixedTime.Add(24*time.Hour), order.ExpiresAt)
}

// Or use quartz library for advanced time control
import "github.com/jonboulle/clockwork"
fakeClock := clockwork.NewFakeClock()
fakeClock.Advance(1 * time.Hour)
```
