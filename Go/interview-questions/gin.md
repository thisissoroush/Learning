# 🌐 Gin — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is Gin and why is it popular for Go web development?

**A:** Gin is the most popular HTTP web framework for Go. It wraps `net/http` with:

- **Fast routing** via httprouter (radix tree — much faster than `http.ServeMux` for large route sets)
- **Middleware chain** — easy to compose request/response handlers
- **Binding & validation** — auto-parses JSON, form, query params into structs
- **Built-in rendering** — JSON, XML, HTML templates
- **Zero allocation router** — minimal GC pressure on hot paths

```go
import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default() // logger + recovery middleware included
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    r.Run(":8080")
}
```

---

### 2. What is `gin.Context` and what can you do with it?

**A:** `*gin.Context` is the core object carrying the request and response:

```go
func handler(c *gin.Context) {
    // Path params
    id := c.Param("id")

    // Query params
    page := c.DefaultQuery("page", "1")
    q, exists := c.GetQuery("q")

    // Headers
    auth := c.GetHeader("Authorization")

    // Request info
    c.Request.Method
    c.ClientIP()
    c.FullPath()    // "/users/:id"
    c.Request.Context() // standard context.Context

    // Response
    c.JSON(200, gin.H{"id": id})
    c.String(200, "hello %s", name)
    c.HTML(200, "index.html", gin.H{})
    c.Status(204)
    c.Header("X-Custom", "value")
    c.Redirect(302, "/new-path")
    c.Abort()       // stop middleware chain
    c.AbortWithStatus(403)
}
```

---

### 3. How does routing work in Gin?

**A:**

```go
r := gin.Default()

// HTTP methods
r.GET("/users", listUsers)
r.POST("/users", createUser)
r.PUT("/users/:id", updateUser)
r.PATCH("/users/:id", patchUser)
r.DELETE("/users/:id", deleteUser)
r.OPTIONS("/users", optionsHandler)
r.Any("/catch-all", anyHandler) // all methods

// Path parameters
r.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")  // "/users/42" → "42"
})

// Wildcard parameters
r.GET("/files/*filepath", func(c *gin.Context) {
    path := c.Param("filepath") // "/files/a/b/c" → "/a/b/c"
})

// Route groups
v1 := r.Group("/v1")
{
    v1.GET("/users", listUsers)
    v1.POST("/users", createUser)
}
```

---

### 4. How do you bind request data to a struct?

**A:**

```go
type CreateUserRequest struct {
    Name  string `json:"name"  binding:"required,min=1,max=100"`
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age"   binding:"gte=0,lte=150"`
}

func createUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    // req.Name, req.Email, req.Age are populated and validated
}

// Other binding methods
c.ShouldBindQuery(&req)       // query string: ?name=Alice&age=30
c.ShouldBindUri(&req)         // path params
c.ShouldBindHeader(&req)      // headers
c.ShouldBind(&req)            // auto-detects from Content-Type
c.ShouldBindWith(&req, binding.Form) // multipart form
```

Validation uses `go-playground/validator` under the hood — same tags as JSON struct tags.

---

### 5. What is the difference between `ShouldBind` and `MustBind`?

**A:**

- `ShouldBindJSON` / `ShouldBind` — returns an error; you handle it
- `MustBindWith` / `Bind` — calls `c.AbortWithStatus(400)` automatically on failure

```go
// ShouldBind — preferred: you control the response
if err := c.ShouldBindJSON(&req); err != nil {
    c.JSON(422, gin.H{"error": err.Error()})
    return
}

// MustBind — auto-aborts with 400; less control over error format
c.MustBindWith(&req, binding.JSON) // writes 400 and returns; don't write again after this
```

Use `ShouldBind*` everywhere — it gives you full control over the error response format.

---

### 6. How does middleware work in Gin?

**A:** Middleware is just a `gin.HandlerFunc` that calls `c.Next()` to pass control forward:

```go
func Logger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path

        c.Next() // execute all downstream handlers

        latency := time.Since(start)
        status := c.Writer.Status()
        log.Printf("%s %s %d %v", c.Request.Method, path, status, latency)
    }
}

func Auth() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if !isValidToken(token) {
            c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
            return // c.Abort() stops the chain; don't call c.Next()
        }
        c.Set("user_id", extractUserID(token))
        c.Next()
    }
}

// Apply globally
r := gin.New()
r.Use(Logger(), gin.Recovery())

// Apply to a group
auth := r.Group("/api", Auth())
auth.GET("/profile", getProfile)
```

---

### 7. What is `gin.H` and when do you use it?

**A:** `gin.H` is simply `map[string]any` — a convenience alias for building JSON responses inline:

```go
c.JSON(200, gin.H{
    "message": "success",
    "user_id": 42,
    "data":    someStruct,
})

// Equivalent to:
c.JSON(200, map[string]any{
    "message": "success",
})

// For structured responses, prefer a typed struct
type Response struct {
    Message string `json:"message"`
    UserID  int    `json:"user_id"`
}
c.JSON(200, Response{Message: "success", UserID: 42})
```

---

### 8. How do you handle errors in Gin?

**A:**

```go
// Pattern 1: return early with error response
func getUser(c *gin.Context) {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        c.JSON(400, gin.H{"error": "invalid id"})
        return
    }
    user, err := db.GetUser(id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            c.JSON(404, gin.H{"error": "user not found"})
            return
        }
        c.JSON(500, gin.H{"error": "internal error"})
        return
    }
    c.JSON(200, user)
}

// Pattern 2: c.Error() + global error handler middleware
func getUser(c *gin.Context) {
    user, err := db.GetUser(id)
    if err != nil {
        _ = c.Error(err) // attach error to context
        return
    }
    c.JSON(200, user)
}

func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        if len(c.Errors) > 0 {
            c.JSON(500, gin.H{"error": c.Errors.Last().Error()})
        }
    }
}
```

---

### 9. How do you set and get values from the context?

**A:**

```go
// In middleware — set
c.Set("user_id", 42)
c.Set("user", &User{ID: 42, Name: "Alice"})

// In handler — get
userID, exists := c.Get("user_id")
if !exists {
    c.AbortWithStatus(401)
    return
}

// Type-safe helpers
c.GetString("key")
c.GetInt("key")
c.GetBool("key")

// For structs, cast manually
user := c.MustGet("user").(*User) // panics if not set
```

---

### 10. What is `gin.Default()` vs `gin.New()`?

**A:**

- `gin.Default()` — creates router with `Logger` and `Recovery` middleware pre-attached
- `gin.New()` — bare router with no middleware

```go
// Default
r := gin.Default()
// Logger: logs method, path, status, latency
// Recovery: catches panics, returns 500

// New — add your own middleware
r := gin.New()
r.Use(
    myStructuredLogger(),  // your logger
    gin.Recovery(),        // still want panic recovery
    requestID(),
)
```

In production, you usually use `gin.New()` and attach your own structured logger instead of Gin's default.

---

## 🟡 Mid Level

---

### 11. How do you implement route groups with shared middleware?

**A:**

```go
r := gin.New()
r.Use(RequestID(), Logger())

// Public routes — no auth
public := r.Group("/")
{
    public.POST("/auth/login", login)
    public.POST("/auth/register", register)
    public.GET("/health", healthCheck)
}

// Authenticated routes
api := r.Group("/api", JWTAuth())
{
    api.GET("/me", getProfile)

    // Nested group with additional middleware
    admin := api.Group("/admin", RequireRole("admin"))
    {
        admin.GET("/users", listAllUsers)
        admin.DELETE("/users/:id", deleteUser)
    }
}
```

---

### 12. How do you implement JWT authentication in Gin?

**A:**

```go
import "github.com/golang-jwt/jwt/v5"

type Claims struct {
    UserID int `json:"user_id"`
    jwt.RegisteredClaims
}

func JWTAuth() gin.HandlerFunc {
    return func(c *gin.Context) {
        header := c.GetHeader("Authorization")
        if !strings.HasPrefix(header, "Bearer ") {
            c.AbortWithStatusJSON(401, gin.H{"error": "missing token"})
            return
        }
        tokenStr := strings.TrimPrefix(header, "Bearer ")

        claims := &Claims{}
        token, err := jwt.ParseWithClaims(tokenStr, claims, func(t *jwt.Token) (any, error) {
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("unexpected signing method")
            }
            return []byte(os.Getenv("JWT_SECRET")), nil
        })

        if err != nil || !token.Valid {
            c.AbortWithStatusJSON(401, gin.H{"error": "invalid token"})
            return
        }

        c.Set("claims", claims)
        c.Next()
    }
}
```

---

### 13. How do you validate request data with custom validators?

**A:**

```go
import "github.com/go-playground/validator/v10"

// Register custom validator
if v, ok := binding.Validator.Engine().(*validator.Validate); ok {
    v.RegisterValidation("slug", func(fl validator.FieldLevel) bool {
        return regexp.MustCompile(`^[a-z0-9-]+$`).MatchString(fl.Field().String())
    })
}

type CreatePostRequest struct {
    Title string `json:"title" binding:"required,min=3,max=200"`
    Slug  string `json:"slug"  binding:"required,slug"`
}

// Custom error messages from validation errors
func formatValidationErrors(err error) []string {
    var ve validator.ValidationErrors
    if errors.As(err, &ve) {
        out := make([]string, len(ve))
        for i, fe := range ve {
            out[i] = fmt.Sprintf("%s: %s", fe.Field(), fe.Tag())
        }
        return out
    }
    return []string{err.Error()}
}
```

---

### 14. How do you handle file uploads in Gin?

**A:**

```go
func uploadFile(c *gin.Context) {
    // Single file
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(400, gin.H{"error": "file required"})
        return
    }

    // Validate size (set globally or check manually)
    if file.Size > 10<<20 { // 10MB
        c.JSON(400, gin.H{"error": "file too large"})
        return
    }

    // Validate MIME type by reading magic bytes
    src, _ := file.Open()
    defer src.Close()
    buf := make([]byte, 512)
    src.Read(buf)
    contentType := http.DetectContentType(buf)

    // Save
    dst := filepath.Join("uploads", filepath.Base(file.Filename))
    c.SaveUploadedFile(file, dst) // convenience wrapper

    c.JSON(200, gin.H{"filename": file.Filename, "size": file.Size})
}

// Multiple files
func uploadMultiple(c *gin.Context) {
    form, _ := c.MultipartForm()
    files := form.File["files"]
    for _, file := range files {
        c.SaveUploadedFile(file, "./uploads/"+file.Filename)
    }
}

// Set max multipart memory (default 32MB)
r.MaxMultipartMemory = 8 << 20 // 8MB
```

---

### 15. How do you stream responses in Gin?

**A:**

```go
// Server-Sent Events (SSE)
func events(c *gin.Context) {
    c.Header("Content-Type", "text/event-stream")
    c.Header("Cache-Control", "no-cache")
    c.Header("Connection", "keep-alive")

    clientCh := make(chan string, 10)
    // register client...

    c.Stream(func(w io.Writer) bool {
        select {
        case msg := <-clientCh:
            c.SSEvent("message", msg)
            return true // keep streaming
        case <-c.Request.Context().Done():
            return false // client disconnected
        }
    })
}

// Stream large file download
func download(c *gin.Context) {
    c.Header("Content-Disposition", "attachment; filename=export.csv")
    c.Header("Content-Type", "text/csv")

    c.Stream(func(w io.Writer) bool {
        // write rows in chunks
        return writeNextChunk(w) // return false when done
    })
}
```

---

### 16. How do you write tests for Gin handlers?

**A:**

```go
import (
    "net/http"
    "net/http/httptest"
    "testing"
    "github.com/gin-gonic/gin"
)

func TestGetUser(t *testing.T) {
    gin.SetMode(gin.TestMode)

    r := gin.New()
    r.GET("/users/:id", getUser)

    w := httptest.NewRecorder()
    req := httptest.NewRequest("GET", "/users/42", nil)
    req.Header.Set("Authorization", "Bearer "+validToken)

    r.ServeHTTP(w, req)

    assert.Equal(t, 200, w.Code)
    var resp map[string]any
    json.Unmarshal(w.Body.Bytes(), &resp)
    assert.Equal(t, float64(42), resp["id"])
}

// Test with mock dependencies
func setupRouter(db *MockDB) *gin.Engine {
    gin.SetMode(gin.TestMode)
    r := gin.New()
    h := NewUserHandler(db)
    r.GET("/users/:id", h.GetUser)
    return r
}
```

---

### 17. How does Gin handle panics and what is `Recovery`?

**A:** `gin.Recovery()` is middleware that catches panics and returns a 500:

```go
r := gin.New()
r.Use(gin.CustomRecovery(func(c *gin.Context, err any) {
    // Log with stack trace
    buf := make([]byte, 4096)
    n := runtime.Stack(buf, false)
    log.Printf("panic: %v\n%s", err, buf[:n])

    // Custom error response
    c.AbortWithStatusJSON(500, gin.H{
        "error": "internal server error",
        "request_id": c.GetString("request_id"),
    })
}))
```

Without `Recovery`, a panicking handler crashes the goroutine and causes the HTTP response to be incomplete (or the whole server to crash if the panic escapes to `net/http`'s handler dispatcher).

---

### 18. How do you implement rate limiting in Gin?

**A:**

```go
import "golang.org/x/time/rate"

// Simple per-IP rate limiter
var limiters = sync.Map{}

func getLimiter(ip string) *rate.Limiter {
    v, loaded := limiters.LoadOrStore(ip, rate.NewLimiter(rate.Limit(10), 20))
    // 10 requests/second, burst of 20
    return v.(*rate.Limiter)
}

func RateLimiter() gin.HandlerFunc {
    return func(c *gin.Context) {
        limiter := getLimiter(c.ClientIP())
        if !limiter.Allow() {
            c.AbortWithStatusJSON(429, gin.H{
                "error": "rate limit exceeded",
                "retry_after": "1s",
            })
            return
        }
        c.Next()
    }
}

// Or use gin-contrib/limiter for Redis-backed distributed rate limiting
```

---

### 19. How do you handle CORS in Gin?

**A:**

```go
import "github.com/gin-contrib/cors"

r.Use(cors.New(cors.Config{
    AllowOrigins:     []string{"https://myfrontend.com"},
    AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
    AllowHeaders:     []string{"Authorization", "Content-Type", "X-Request-ID"},
    ExposeHeaders:    []string{"X-Total-Count"},
    AllowCredentials: true,
    MaxAge:           12 * time.Hour,
}))

// Or allow all origins in development
r.Use(cors.Default())
```

---

### 20. How do you serve static files and HTML templates in Gin?

**A:**

```go
// Static files
r.Static("/assets", "./static")           // directory
r.StaticFile("/favicon.ico", "./favicon.ico")
r.StaticFS("/files", http.Dir("./files")) // http.FileSystem interface

// HTML templates
r.LoadHTMLGlob("templates/**/*.html")
// or r.LoadHTMLFiles("templates/index.html", "templates/error.html")

r.GET("/", func(c *gin.Context) {
    c.HTML(200, "index.html", gin.H{
        "title": "Home",
        "user":  currentUser,
    })
})

// Custom template functions
r.SetFuncMap(template.FuncMap{
    "formatDate": func(t time.Time) string {
        return t.Format("2006-01-02")
    },
})
```

---

## 🔴 Senior Level

---

### 21. How do you implement graceful shutdown with Gin?

**A:**

```go
func main() {
    r := gin.Default()
    r.GET("/", handler)

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      r,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    log.Println("Shutting down...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Forced shutdown:", err)
    }
    log.Println("Server stopped")
}
```

---

### 22. How do you structure a large Gin application?

**A:**

```
cmd/
└── server/main.go        # wire everything, start server

internal/
├── handler/              # HTTP handlers (thin adapters)
│   ├── user.go
│   └── order.go
├── service/              # business logic
│   ├── user_service.go
│   └── order_service.go
├── repository/           # DB layer
│   ├── user_repo.go
│   └── order_repo.go
├── middleware/            # request middleware
│   ├── auth.go
│   ├── logger.go
│   └── recovery.go
├── model/                # domain structs
└── router/               # route definitions
    └── router.go
```

```go
// router/router.go
func Setup(h *handler.Handlers, middlewares ...gin.HandlerFunc) *gin.Engine {
    r := gin.New()
    r.Use(middlewares...)

    v1 := r.Group("/v1")
    v1.Use(middleware.Auth())

    users := v1.Group("/users")
    users.GET("", h.User.List)
    users.POST("", h.User.Create)
    users.GET("/:id", h.User.Get)

    return r
}
```

---

### 23. How do you implement request tracing in Gin?

**A:**

```go
import (
    "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
    "go.opentelemetry.io/otel"
)

// Auto-instrument all routes
r.Use(otelgin.Middleware("my-service"))

// Manual span inside handler
func createOrder(c *gin.Context) {
    ctx := c.Request.Context()
    tracer := otel.Tracer("order-handler")

    ctx, span := tracer.Start(ctx, "create_order")
    defer span.End()

    span.SetAttributes(attribute.String("customer.id", customerID))

    // Pass ctx down to DB calls, service calls
    order, err := orderService.Create(ctx, req)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        c.JSON(500, gin.H{"error": "internal error"})
        return
    }
    c.JSON(201, order)
}
```

---

### 24. How do you benchmark Gin and tune its performance?

**A:**

```bash
# wrk load test
wrk -t8 -c200 -d30s http://localhost:8080/api/endpoint

# go tool pprof via net/http/pprof
import _ "net/http/pprof"
go http.ListenAndServe(":6060", nil)

go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

**Gin performance tips:**
```go
// 1. Use gin.New() in production — no default logger overhead
r := gin.New()

// 2. Release mode — disables debug logs and some checks
gin.SetMode(gin.ReleaseMode)

// 3. Avoid allocations in hot handlers — reuse buffers
var bufPool = sync.Pool{New: func() any { return new(bytes.Buffer) }}

// 4. Use c.JSON only when needed — for static responses, write directly
c.Data(200, "application/json", precomputedJSON)

// 5. Tune http.Server settings
srv := &http.Server{
    ReadHeaderTimeout: 5 * time.Second,
    WriteTimeout:      10 * time.Second,
    IdleTimeout:       120 * time.Second,
}

// 6. HTTP/2 push for assets (if using TLS)
srv.ListenAndServeTLS(cert, key)
```

---

## 🏛️ Architect Level

---

### 25. How do you design a Gin service for high availability?

**A:**

**Health endpoints:**
```go
r.GET("/healthz", func(c *gin.Context) {
    c.JSON(200, gin.H{"status": "alive"})
})

r.GET("/readyz", func(c *gin.Context) {
    if err := db.PingContext(c.Request.Context()); err != nil {
        c.JSON(503, gin.H{"status": "not ready", "reason": "db"})
        return
    }
    c.JSON(200, gin.H{"status": "ready"})
})
```

**Zero-downtime shutdown:** Use the graceful shutdown pattern (Q22) with `preStop` sleep in Kubernetes.

**Connection pool tuning:**
```go
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(5 * time.Minute)
db.SetConnMaxIdleTime(1 * time.Minute)
```

**Middleware stack for production:**
```go
r.Use(
    RequestID(),           // trace ID on every request
    otelgin.Middleware("service"),  // tracing
    StructuredLogger(),    // structured JSON logs
    gin.CustomRecovery(panicHandler),
    RateLimiter(),
    cors.New(corsConfig),
)
```
