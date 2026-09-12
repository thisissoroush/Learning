# 🌐 Echo & Chi — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level — Echo

---

### 1. What is Echo and how does it compare to Gin?

**A:** Echo is a high-performance, minimalist Go web framework. Compared to Gin:

| | Echo | Gin |
|--|------|-----|
| Router | Radix tree | Radix tree |
| Performance | Similar | Similar |
| Binding | Built-in + validator | Built-in + validator |
| Middleware | Composable | Composable |
| Context | Custom `echo.Context` interface | `*gin.Context` struct |
| Testability | Easy (interface makes mocking possible) | Easy |
| gRPC | No | No |

Echo is popular for its clean API, good documentation, and first-class WebSocket support.

---

### 2. How do you create a basic Echo server?

**A:**

```go
import "github.com/labstack/echo/v4"
import "github.com/labstack/echo/v4/middleware"

func main() {
    e := echo.New()

    // Built-in middleware
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Use(middleware.CORS())

    // Routes
    e.GET("/", func(c echo.Context) error {
        return c.JSON(http.StatusOK, echo.Map{"message": "hello"})
    })

    e.GET("/users/:id", getUser)
    e.POST("/users", createUser)
    e.PUT("/users/:id", updateUser)
    e.DELETE("/users/:id", deleteUser)

    // Start
    e.Logger.Fatal(e.Start(":8080"))

    // With TLS
    e.Logger.Fatal(e.StartTLS(":8443", "cert.pem", "key.pem"))
}
```

---

### 3. How do you read path params, query params, and body in Echo?

**A:**

```go
func getUser(c echo.Context) error {
    // Path param
    id := c.Param("id")

    // Query param
    page := c.QueryParam("page")
    limit, _ := strconv.Atoi(c.QueryParamOrDefault("limit", "20"))

    // Header
    auth := c.Request().Header.Get("Authorization")

    // Bind JSON body to struct
    var req CreateUserRequest
    if err := c.Bind(&req); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, err.Error())
    }

    // Bind + Validate in one step
    if err := c.Bind(&req); err != nil {
        return err
    }
    if err := c.Validate(&req); err != nil {
        return err
    }

    return c.JSON(http.StatusOK, echo.Map{"id": id})
}
```

---

### 4. How do you set up validation in Echo?

**A:** Echo has no built-in validator — you register one:

```go
import "github.com/go-playground/validator/v10"

type CustomValidator struct {
    validator *validator.Validate
}

func (cv *CustomValidator) Validate(i interface{}) error {
    if err := cv.validator.Struct(i); err != nil {
        return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
    }
    return nil
}

// Register at startup
e.Validator = &CustomValidator{validator: validator.New()}

// Usage in handler
type CreateUserRequest struct {
    Name  string `json:"name"  validate:"required,min=1,max=100"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age"   validate:"gte=0,lte=150"`
}

func createUser(c echo.Context) error {
    var req CreateUserRequest
    if err := c.Bind(&req); err != nil {
        return err
    }
    if err := c.Validate(req); err != nil {
        return err
    }
    // req is valid
    return c.JSON(http.StatusCreated, req)
}
```

---

### 5. How does Echo middleware work?

**A:**

```go
// Custom middleware
func RequestID() echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            id := c.Request().Header.Get("X-Request-ID")
            if id == "" {
                id = uuid.New().String()
            }
            c.Set("request_id", id)
            c.Response().Header().Set("X-Request-ID", id)
            return next(c)
        }
    }
}

func Auth() echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            token := c.Request().Header.Get("Authorization")
            if token == "" {
                return echo.NewHTTPError(http.StatusUnauthorized, "missing token")
            }
            userID, err := validateToken(token)
            if err != nil {
                return echo.NewHTTPError(http.StatusUnauthorized, "invalid token")
            }
            c.Set("user_id", userID)
            return next(c)
        }
    }
}

// Apply: global, group, or route level
e.Use(RequestID())
api := e.Group("/api", Auth())
api.GET("/me", getMe)
```

---

## 🟡 Mid Level — Echo

---

### 6. How do you implement route groups and versioning in Echo?

**A:**

```go
// API groups with middleware
v1 := e.Group("/v1")
v1.Use(middleware.JWT([]byte(secret)))

users := v1.Group("/users")
users.GET("", listUsers)
users.POST("", createUser)
users.GET("/:id", getUser)
users.PUT("/:id", updateUser)
users.DELETE("/:id", deleteUser)

admin := v1.Group("/admin", requireAdmin())
admin.GET("/stats", getStats)
admin.GET("/users", adminListUsers)

// Deprecation middleware for v1
v1.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        c.Response().Header().Set("Deprecation", "true")
        c.Response().Header().Set("Sunset", "Sat, 01 Jan 2026 00:00:00 GMT")
        return next(c)
    }
})

v2 := e.Group("/v2")
// v2 routes...
```

---

### 7. How do you handle errors globally in Echo?

**A:**

```go
// Custom error handler
e.HTTPErrorHandler = func(err error, c echo.Context) {
    var (
        code    = http.StatusInternalServerError
        message any = "internal server error"
    )

    var he *echo.HTTPError
    if errors.As(err, &he) {
        code = he.Code
        message = he.Message
    } else if errors.Is(err, ErrNotFound) {
        code = http.StatusNotFound
        message = "resource not found"
    } else if errors.Is(err, ErrUnauthorized) {
        code = http.StatusUnauthorized
        message = "unauthorized"
    }

    // Log unexpected errors
    if code == http.StatusInternalServerError {
        c.Logger().Errorf("unhandled error: %v", err)
    }

    if !c.Response().Committed {
        c.JSON(code, echo.Map{
            "error":      message,
            "request_id": c.Get("request_id"),
        })
    }
}

// In handlers — use typed errors
func getUser(c echo.Context) error {
    user, err := svc.GetUser(c.Param("id"))
    if errors.Is(err, ErrNotFound) {
        return echo.NewHTTPError(http.StatusNotFound, "user not found")
    }
    if err != nil {
        return err // caught by global handler
    }
    return c.JSON(http.StatusOK, user)
}
```

---

### 8. How do you implement WebSockets in Echo?

**A:**

```go
import "github.com/gorilla/websocket"

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true }, // configure properly in prod
}

func wsHandler(c echo.Context) error {
    ws, err := upgrader.Upgrade(c.Response(), c.Request(), nil)
    if err != nil {
        return err
    }
    defer ws.Close()

    for {
        msgType, msg, err := ws.ReadMessage()
        if err != nil {
            if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway) {
                c.Logger().Error(err)
            }
            break
        }

        // Echo back
        if err := ws.WriteMessage(msgType, msg); err != nil {
            break
        }
    }
    return nil
}

e.GET("/ws", wsHandler)
```

---

## 🟢 Junior Level — Chi

---

### 9. What is Chi and how does it differ from Gin and Echo?

**A:** Chi is an extremely lightweight, idiomatic HTTP router for Go that works directly with the standard `net/http` interfaces:

| | Chi | Gin | Echo |
|--|-----|-----|------|
| Uses stdlib `http.Handler` | ✅ Yes | ❌ No (own context) | ❌ No (own context) |
| Composability | High (plain Handler) | Medium | Medium |
| Middleware ecosystem | Any `net/http` middleware | Gin-specific | Echo-specific |
| Performance | Very high | Very high | Very high |
| Bundle size | Minimal | Medium | Medium |
| Learning curve | Very low | Low | Low |

**Key advantage:** Any middleware that wraps `http.Handler` works with Chi — Alice, Gorilla, etc.

---

### 10. How do you create a Chi router?

**A:**

```go
import "github.com/go-chi/chi/v5"
import "github.com/go-chi/chi/v5/middleware"

func main() {
    r := chi.NewRouter()

    // Built-in middleware
    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(30 * time.Second))
    r.Use(middleware.Compress(5))

    // Routes
    r.Get("/", homeHandler)
    r.Get("/health", healthHandler)

    // Route group
    r.Route("/api/v1", func(r chi.Router) {
        r.Use(jwtAuth)

        r.Route("/users", func(r chi.Router) {
            r.Get("/", listUsers)
            r.Post("/", createUser)

            r.Route("/{userID}", func(r chi.Router) {
                r.Use(userCtx) // load user into context
                r.Get("/", getUser)
                r.Put("/", updateUser)
                r.Delete("/", deleteUser)

                r.Get("/orders", getUserOrders) // nested resource
            })
        })
    })

    http.ListenAndServe(":8080", r)
}
```

---

### 11. How do you read URL params and context values in Chi?

**A:**

```go
import "github.com/go-chi/chi/v5"

func getUser(w http.ResponseWriter, r *http.Request) {
    // URL parameters
    userID := chi.URLParam(r, "userID")

    // Query params (stdlib)
    page := r.URL.Query().Get("page")

    // Context values (set by middleware)
    user, _ := r.Context().Value(userKey).(*User)

    // Response
    json.NewEncoder(w).Encode(map[string]any{"id": userID, "user": user})
}

// Middleware that loads user and stores in context
func userCtx(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        userID := chi.URLParam(r, "userID")
        user, err := userRepo.GetByID(r.Context(), userID)
        if err != nil {
            http.Error(w, "user not found", http.StatusNotFound)
            return
        }
        ctx := context.WithValue(r.Context(), userKey, user)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

---

### 12. How do you write middleware in Chi?

**A:** Chi middleware is a plain `func(http.Handler) http.Handler` — works with any `net/http` compatible code:

```go
// Logging middleware
func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)

        defer func() {
            log.Printf(
                "method=%s path=%s status=%d duration=%v bytes=%d",
                r.Method, r.URL.Path,
                ww.Status(), time.Since(start), ww.BytesWritten(),
            )
        }()

        next.ServeHTTP(ww, r)
    })
}

// Auth middleware
func JWTAuth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        claims, err := validateToken(token)
        if err != nil {
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return
        }
        ctx := context.WithValue(r.Context(), claimsKey, claims)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Apply to router
r.Use(Logger, JWTAuth)
```

---

## 🔴 Senior Level

---

### 13. How do you structure a large Chi application?

**A:**

```go
// handler/users.go — plain http.Handler methods
type UserHandler struct {
    service UserService
}

func (h *UserHandler) Routes() chi.Router {
    r := chi.NewRouter()
    r.Get("/", h.List)
    r.Post("/", h.Create)
    r.Route("/{id}", func(r chi.Router) {
        r.Use(h.userCtx)
        r.Get("/", h.Get)
        r.Put("/", h.Update)
        r.Delete("/", h.Delete)
    })
    return r
}

func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
    users, err := h.service.List(r.Context())
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    render.JSON(w, r, users)
}

// main router assembly
func NewRouter(userHandler *UserHandler, orderHandler *OrderHandler) chi.Router {
    r := chi.NewRouter()
    r.Use(middleware.RequestID, middleware.Logger, middleware.Recoverer)

    r.Mount("/api/v1/users", userHandler.Routes())
    r.Mount("/api/v1/orders", orderHandler.Routes())
    r.Mount("/health", healthRouter())

    return r
}
```

---

### 14. When should you choose Chi over Gin or Echo?

**A:**

**Choose Chi when:**
- You want to stay close to `net/http` — no custom context type, existing middleware works
- Library authors — Chi handlers are `http.Handler`, usable anywhere
- Team already knows `net/http` patterns
- You want to mix and match middleware from different ecosystems

**Choose Gin when:**
- Team is familiar with it
- You want the largest ecosystem and community
- Binding and validation out of the box

**Choose Echo when:**
- You want Gin-like API with a slightly cleaner interface
- First-class WebSocket support matters
- You prefer `echo.Context` as an interface (testable via mock)

**All three are production-ready and have similar performance.** The choice is mostly about team familiarity and ecosystem preference.

---

## 🏛️ Architect Level

---

### 15. How do you design a framework-agnostic handler layer?

**A:** Keep business logic in framework-independent service/domain layers. HTTP handlers are thin adapters:

```go
// Domain — no framework dependency
type UserService interface {
    Create(ctx context.Context, cmd CreateUserCommand) (*User, error)
    Get(ctx context.Context, id string) (*User, error)
    List(ctx context.Context, filter UserFilter) ([]User, int, error)
}

// HTTP adapter — can be Gin, Echo, Chi, or stdlib
// For Chi (stdlib-compatible):
type UserHandler struct{ svc UserService }

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var cmd CreateUserCommand
    if err := json.NewDecoder(r.Body).Decode(&cmd); err != nil {
        writeError(w, http.StatusBadRequest, err)
        return
    }
    user, err := h.svc.Create(r.Context(), cmd)
    if err != nil {
        writeError(w, http.StatusInternalServerError, err)
        return
    }
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}

// Same UserService — different framework adapter
// For Gin:
func (h *UserHandler) GinCreate(c *gin.Context) {
    var cmd CreateUserCommand
    if err := c.ShouldBindJSON(&cmd); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    user, err := h.svc.Create(c.Request.Context(), cmd)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    c.JSON(201, user)
}
```

The service layer is completely framework-agnostic — you can switch from Gin to Chi or Echo without touching business logic.
