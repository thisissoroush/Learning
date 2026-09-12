# 🏗️ ASP.NET Core — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is ASP.NET Core and what is Kestrel?

**A:** ASP.NET Core is Microsoft's cross-platform, high-performance web framework. **Kestrel** is its built-in HTTP server:

- Kestrel is the default web server — fast, async, cross-platform
- In production it typically sits behind a reverse proxy (Nginx, Azure App Gateway)
- Supports HTTP/1.1, HTTP/2, HTTP/3 (QUIC), WebSockets, Unix sockets

```
[Browser] → Nginx (TLS termination, load balancing) → Kestrel → ASP.NET Core pipeline
```

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(o =>
{
    o.ListenAnyIP(8080);
    o.ListenAnyIP(8443, l => l.UseHttps());
    o.Limits.MaxConcurrentConnections = 1000;
    o.Limits.RequestBodySize = 10 * 1024 * 1024; // 10MB
});
```

---

### 2. What is the middleware pipeline in ASP.NET Core?

**A:** Requests flow through a sequential chain of middleware — each can process the request before/after calling `next`:

```csharp
var app = builder.Build();

// Order matters!
app.UseExceptionHandler("/error"); // must be first to catch all exceptions
app.UseHsts();
app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseCors();
app.UseAuthentication();  // who are you?
app.UseAuthorization();   // are you allowed?
app.UseRateLimiter();
app.MapControllers();

app.Run();
```

Each `Use*` call adds a middleware. Request flows top → bottom; response flows bottom → top.

---

### 3. What is the difference between `app.Use`, `app.Run`, and `app.Map`?

**A:**

```csharp
// Use — adds middleware that calls next
app.Use(async (context, next) =>
{
    // Before
    await next(context);
    // After
});

// Run — terminal middleware (doesn't call next)
app.Run(async context =>
{
    await context.Response.WriteAsync("Hello World");
    // No next — pipeline ends here
});

// Map — branches pipeline based on path
app.Map("/health", branch =>
{
    branch.Run(async context =>
        await context.Response.WriteAsync("OK"));
});

// MapWhen — branches based on condition
app.MapWhen(ctx => ctx.Request.Query.ContainsKey("debug"), branch =>
{
    branch.Use(debugMiddleware);
});
```

---

### 4. What is dependency injection in ASP.NET Core and what are service lifetimes?

**A:**

```csharp
// Registration
builder.Services.AddSingleton<ICache, RedisCache>();    // one instance for app lifetime
builder.Services.AddScoped<IOrderService, OrderService>(); // one per HTTP request
builder.Services.AddTransient<IEmailSender, SmtpSender>(); // new instance every time

// Constructor injection
public class OrderController : ControllerBase
{
    private readonly IOrderService _orders;
    private readonly ILogger<OrderController> _logger;

    public OrderController(IOrderService orders, ILogger<OrderController> logger)
    {
        _orders = orders;
        _logger = logger;
    }
}

// Avoid captive dependency: never inject Scoped into Singleton!
// Runtime will throw unless you explicitly request a scope
```

---

### 5. What is the difference between Minimal API and Controller-based API?

**A:**

```csharp
// Minimal API — less ceremony, functional
var app = WebApplication.Create();

app.MapGet("/orders/{id}", async (int id, IOrderService svc) =>
{
    var order = await svc.GetAsync(id);
    return order is null ? Results.NotFound() : Results.Ok(order);
})
.WithName("GetOrder")
.RequireAuthorization();

// Controller-based — full MVC pipeline, filters, conventions
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class OrdersController : ControllerBase
{
    [HttpGet("{id}")]
    [ProducesResponseType<OrderDto>(200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Get(int id)
    {
        var order = await _service.GetAsync(id);
        return order is null ? NotFound() : Ok(order);
    }
}
```

Both compile to the same pipeline. Minimal APIs are preferred for microservices; Controllers for large apps with complex filters.

---

### 6. What is model binding and validation in ASP.NET Core?

**A:**

```csharp
public record CreateOrderRequest(
    [Required] Guid CustomerId,
    [Required, MinLength(1)] List<OrderLineRequest> Lines
);

public record OrderLineRequest(
    [Required] Guid ProductId,
    [Range(1, 1000)] int Quantity
);

// [ApiController] handles validation automatically — returns 400 on failure
[HttpPost]
public async Task<IActionResult> Create([FromBody] CreateOrderRequest req)
{
    // Validation already done — req is valid here
    var order = await _service.CreateAsync(req);
    return CreatedAtAction(nameof(Get), new { id = order.Id }, order);
}

// Manual validation
if (!ModelState.IsValid)
    return BadRequest(ModelState);

// FluentValidation (popular alternative to DataAnnotations)
public class CreateOrderValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.CustomerId).NotEmpty();
        RuleFor(x => x.Lines).NotEmpty().ForEach(l => l.ChildRules(line =>
        {
            line.RuleFor(x => x.Quantity).GreaterThan(0).LessThanOrEqualTo(1000);
        }));
    }
}
```

---

### 7. What are action filters and how do they work?

**A:**

```csharp
// Action filter — runs before/after an action method
public class LogActionFilter : IActionFilter
{
    public void OnActionExecuting(ActionExecutingContext context)
    {
        // Runs before action
        var name = context.ActionDescriptor.DisplayName;
        Log.Information("Executing {Action}", name);
    }

    public void OnActionExecuted(ActionExecutedContext context)
    {
        // Runs after action
        if (context.Exception != null)
            Log.Error(context.Exception, "Action failed");
    }
}

// Register globally
builder.Services.AddControllers(o =>
    o.Filters.Add<LogActionFilter>());

// Or per controller/action
[ServiceFilter(typeof(LogActionFilter))]
public class OrdersController : ControllerBase { ... }
```

**Filter types:** `IActionFilter`, `IResultFilter`, `IExceptionFilter`, `IAuthorizationFilter`, `IResourceFilter`

---

### 8. How does routing work in ASP.NET Core?

**A:**

```csharp
// Attribute routing (Controllers)
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet]                    // GET api/v1/users
    [HttpGet("{id:int}")]        // GET api/v1/users/42
    [HttpGet("{id:guid}")]       // GET api/v1/users/550e8400...
    [HttpGet("search")]          // GET api/v1/users/search
    [HttpPost]                   // POST api/v1/users
    [HttpDelete("{id:int}")]     // DELETE api/v1/users/42
}

// Route constraints
[HttpGet("{id:int:min(1)}")]     // int, min value 1
[HttpGet("{name:alpha}")]        // letters only
[HttpGet("{date:datetime}")]     // datetime

// Minimal API routing
app.MapGet("/users/{id:int}", (int id) => ...);
app.MapGet("/files/{**path}", (string path) => ...); // wildcard
```

---

### 9. What is `IConfiguration` and how do you read settings?

**A:**

```csharp
// appsettings.json
{
  "Database": {
    "ConnectionString": "...",
    "MaxConnections": 25
  },
  "Feature": {
    "EnableExport": true
  }
}

// Read individual values
var connStr = configuration["Database:ConnectionString"];
var maxConn = configuration.GetValue<int>("Database:MaxConnections", defaultValue: 10);

// Bind to a typed class (preferred)
public class DatabaseSettings
{
    public string ConnectionString { get; set; } = "";
    public int MaxConnections { get; set; } = 10;
}

builder.Services.Configure<DatabaseSettings>(
    builder.Configuration.GetSection("Database"));

// Inject and use
public class MyService(IOptions<DatabaseSettings> settings)
{
    private readonly DatabaseSettings _settings = settings.Value;
}
```

---

### 10. What is `ILogger` and how do you use structured logging?

**A:**

```csharp
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public OrderService(ILogger<OrderService> logger)
    {
        _logger = logger;
    }

    public async Task<Order> CreateAsync(CreateOrderCommand cmd)
    {
        _logger.LogInformation("Creating order for customer {CustomerId}", cmd.CustomerId);

        try
        {
            var order = await _repo.CreateAsync(cmd);
            _logger.LogInformation("Order {OrderId} created successfully", order.Id);
            return order;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create order for customer {CustomerId}", cmd.CustomerId);
            throw;
        }
    }
}

// Use Serilog in production
builder.Host.UseSerilog((ctx, cfg) =>
    cfg.ReadFrom.Configuration(ctx.Configuration)
       .Enrich.FromLogContext()
       .WriteTo.Console(new JsonFormatter()));
```

---

## 🟡 Mid Level

---

### 11. How do you implement JWT authentication in ASP.NET Core?

**A:**

```csharp
// Registration
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = configuration["Jwt:Issuer"],
            ValidAudience = configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(configuration["Jwt:Secret"]!))
        };

        // Extract token from cookie instead of header
        o.Events = new JwtBearerEvents
        {
            OnMessageReceived = ctx =>
            {
                ctx.Token = ctx.Request.Cookies["access_token"];
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddAuthorization(o =>
{
    o.AddPolicy("AdminOnly", p => p.RequireRole("admin"));
    o.AddPolicy("MinimumAge", p => p.Requirements.Add(new MinAgeRequirement(18)));
});

// Usage
app.UseAuthentication();
app.UseAuthorization();

[Authorize(Policy = "AdminOnly")]
[HttpDelete("{id}")]
public async Task<IActionResult> Delete(int id) { ... }
```

---

### 12. How do you implement output caching in ASP.NET Core 7+?

**A:**

```csharp
builder.Services.AddOutputCache(o =>
{
    o.DefaultExpirationTimeSpan = TimeSpan.FromSeconds(60);

    o.AddPolicy("ProductsPolicy", p =>
        p.Expire(TimeSpan.FromMinutes(5))
         .Tag("products")
         .VaryByQuery("category", "page"));
});

app.UseOutputCache();

// On endpoint
app.MapGet("/products", GetProducts).CacheOutput("ProductsPolicy");

// Invalidate by tag (after update)
await outputCacheStore.EvictByTagAsync("products", cancellationToken);

// [OutputCache] attribute on controllers
[OutputCache(Duration = 300, VaryByQueryKeys = ["page"])]
[HttpGet]
public async Task<IActionResult> GetProducts() { ... }
```

---

### 13. How do you implement rate limiting in ASP.NET Core 7+?

**A:**

```csharp
builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = 429;

    // Fixed window — 100 requests per minute
    o.AddFixedWindowLimiter("fixed", opt =>
    {
        opt.PermitLimit = 100;
        opt.Window = TimeSpan.FromMinutes(1);
        opt.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opt.QueueLimit = 5;
    });

    // Sliding window
    o.AddSlidingWindowLimiter("sliding", opt =>
    {
        opt.PermitLimit = 20;
        opt.Window = TimeSpan.FromSeconds(10);
        opt.SegmentsPerWindow = 5;
    });

    // Token bucket — allows bursts
    o.AddTokenBucketLimiter("token", opt =>
    {
        opt.TokenLimit = 100;
        opt.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
        opt.TokensPerPeriod = 20;
    });

    // Per-user partitioned limiter
    o.AddPolicy("perUser", httpContext =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: httpContext.User.Identity?.Name ?? httpContext.Connection.RemoteIpAddress?.ToString() ?? "anonymous",
            factory: _ => new FixedWindowRateLimiterOptions { PermitLimit = 30, Window = TimeSpan.FromMinutes(1) }));
});

app.UseRateLimiter();
app.MapGet("/api/data", Handler).RequireRateLimiting("fixed");
```

---

### 14. How does `IHostedService` and `BackgroundService` work?

**A:**

```csharp
public class OutboxProcessor : BackgroundService
{
    private readonly IServiceProvider _services;
    private readonly ILogger<OutboxProcessor> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("OutboxProcessor starting");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await using var scope = _services.CreateAsyncScope();
                var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

                var messages = await db.OutboxMessages
                    .Where(m => !m.Processed)
                    .OrderBy(m => m.CreatedAt)
                    .Take(50)
                    .ToListAsync(stoppingToken);

                foreach (var msg in messages)
                {
                    await PublishAsync(msg, stoppingToken);
                    msg.Processed = true;
                }

                await db.SaveChangesAsync(stoppingToken);
            }
            catch (Exception ex) when (!stoppingToken.IsCancellationRequested)
            {
                _logger.LogError(ex, "Outbox processing failed");
            }

            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
        }
    }
}

builder.Services.AddHostedService<OutboxProcessor>();
```

---

### 15. What is `IExceptionHandler` and Problem Details?

**A:**

```csharp
// Global exception handler (ASP.NET Core 8+)
public class GlobalExceptionHandler : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext ctx, Exception ex, CancellationToken ct)
    {
        var (status, title) = ex switch
        {
            NotFoundException      => (404, "Resource Not Found"),
            ValidationException    => (422, "Validation Error"),
            UnauthorizedAccessException => (403, "Forbidden"),
            _                      => (500, "Internal Server Error")
        };

        ctx.Response.StatusCode = status;
        await ctx.Response.WriteAsJsonAsync(new ProblemDetails
        {
            Status = status,
            Title = title,
            Detail = ex.Message,
            Extensions = { ["traceId"] = Activity.Current?.Id }
        }, ct);

        return true;
    }
}

builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();
app.UseExceptionHandler();
```

---

### 16. How do you implement health checks in ASP.NET Core?

**A:**

```csharp
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("database")
    .AddRedis(redisConnectionString, "redis")
    .AddUrlGroup(new Uri("https://payment-service/health"), "payment-service")
    .AddCheck("custom", () =>
    {
        if (IsReady())
            return HealthCheckResult.Healthy("All good");
        return HealthCheckResult.Degraded("Warming up");
    });

// Liveness — is the process alive?
app.MapHealthChecks("/healthz", new HealthCheckOptions
{
    Predicate = _ => false // no checks, just returns 200
});

// Readiness — is it ready to serve traffic?
app.MapHealthChecks("/readyz", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

// UI dashboard
builder.Services.AddHealthChecksUI().AddInMemoryStorage();
app.MapHealthChecksUI(o => o.UIPath = "/health-ui");
```

---

### 17. What is `HttpClientFactory` and why should you use it?

**A:**

```csharp
// Problem: manually creating HttpClient leaks sockets (no connection reuse)
// HttpClientFactory manages HttpClient lifetimes and connection pooling

// Named client
builder.Services.AddHttpClient("payment", c =>
{
    c.BaseAddress = new Uri("https://payment-service");
    c.DefaultRequestHeaders.Add("X-Api-Key", apiKey);
    c.Timeout = TimeSpan.FromSeconds(10);
});

// Typed client
public class PaymentClient
{
    private readonly HttpClient _http;
    public PaymentClient(HttpClient http) => _http = http;

    public async Task<PaymentResult> ChargeAsync(ChargeRequest req, CancellationToken ct)
        => await _http.PostAsJsonAsync("/charge", req, ct)
                      .ReadFromJsonAsync<PaymentResult>(ct);
}

builder.Services.AddHttpClient<PaymentClient>(c =>
    c.BaseAddress = new Uri("https://payment-service"))
    .AddPolicyHandler(retryPolicy)         // Polly integration
    .AddPolicyHandler(circuitBreakerPolicy);

// Inject and use
public class OrderService(PaymentClient payment) { ... }
```

---

## 🔴 Senior Level

---

### 18. How does Kestrel handle HTTP/2 and HTTP/3?

**A:**

```csharp
builder.WebHost.ConfigureKestrel(o =>
{
    // HTTP/1.1 and HTTP/2 on port 8080 (TLS required for HTTP/2 in production)
    o.ListenAnyIP(8443, listen =>
    {
        listen.UseHttps("cert.pfx", "password");
        listen.Protocols = HttpProtocols.Http1AndHttp2;
    });

    // HTTP/3 (QUIC) — requires TLS
    o.ListenAnyIP(8443, listen =>
    {
        listen.UseHttps();
        listen.Protocols = HttpProtocols.Http1AndHttp2AndHttp3;
    });
});
```

**HTTP/2 features used by ASP.NET Core:**
- Header compression (HPACK)
- Request multiplexing — multiple requests over one connection
- Server push (limited support)
- Binary framing

**HTTP/3 (QUIC):** Eliminates TCP head-of-line blocking; better for high-latency or lossy networks.

---

### 19. How do you implement request decompression and response compression?

**A:**

```csharp
// Response compression
builder.Services.AddResponseCompression(o =>
{
    o.EnableForHttps = true; // only enable if you understand BREACH attack
    o.Providers.Add<BrotliCompressionProvider>();
    o.Providers.Add<GzipCompressionProvider>();
    o.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(
        ["application/json", "text/csv"]);
});

builder.Services.Configure<BrotliCompressionProviderOptions>(o =>
    o.Level = CompressionLevel.Fastest);

app.UseResponseCompression(); // add early in pipeline

// Request decompression (ASP.NET Core 7+)
builder.Services.AddRequestDecompression();
app.UseRequestDecompression();

// Now clients can POST with Content-Encoding: gzip/br
```

---

### 20. How do you implement API versioning in ASP.NET Core?

**A:**

```csharp
builder.Services.AddApiVersioning(o =>
{
    o.DefaultApiVersion = new ApiVersion(1, 0);
    o.AssumeDefaultVersionWhenUnspecified = true;
    o.ReportApiVersions = true; // adds api-supported-versions header
    o.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),        // /v1/users
        new HeaderApiVersionReader("X-API-Version"), // header
        new QueryStringApiVersionReader("api-version")); // ?api-version=1.0
})
.AddApiExplorer(o =>
{
    o.GroupNameFormat = "'v'VVV";
    o.SubstituteApiVersionInUrl = true;
});

// Controller
[ApiController]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[Route("v{version:apiVersion}/users")]
public class UsersController : ControllerBase
{
    [HttpGet]
    [MapToApiVersion("1.0")]
    public IActionResult GetV1() => Ok("v1 response");

    [HttpGet]
    [MapToApiVersion("2.0")]
    public IActionResult GetV2() => Ok("v2 response");

    [HttpGet]
    [MapToApiVersion("1.0")]
    [Obsolete]
    public IActionResult DeprecatedEndpoint() => Ok();
}
```

---

### 21. How do you configure Kestrel for high performance?

**A:**

```csharp
builder.WebHost.ConfigureKestrel(o =>
{
    // Connection limits
    o.Limits.MaxConcurrentConnections = 10_000;
    o.Limits.MaxConcurrentUpgradedConnections = 1_000;

    // Request limits
    o.Limits.MaxRequestBodySize = 10 * 1024 * 1024; // 10MB
    o.Limits.MaxRequestHeadersTotalSize = 32_768;    // 32KB

    // Timeouts
    o.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(30);
    o.Limits.KeepAliveTimeout = TimeSpan.FromMinutes(2);
    o.Limits.MinRequestBodyDataRate = new MinDataRate(bytesPerSecond: 240, gracePeriod: TimeSpan.FromSeconds(5));

    // Thread pool
    o.AddServerHeader = false; // don't expose server info
});

// Enable System.IO.Pipelines (default in Kestrel — don't disable)
// Use SocketsHttpHandler for outbound connections
builder.Services.ConfigureHttpClientDefaults(c =>
    c.ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
    {
        PooledConnectionLifetime = TimeSpan.FromMinutes(2),
        MaxConnectionsPerServer = 50
    }));
```

---

## 🏛️ Architect Level

---

### 22. How do you design the middleware pipeline for a production ASP.NET Core service?

**A:**

```csharp
var app = builder.Build();

// 1. Exception handling — must be outermost
app.UseExceptionHandler();

// 2. Security headers
app.UseHsts();
app.UseHttpsRedirection();

// 3. Request ID — before logging
app.Use(async (ctx, next) =>
{
    ctx.TraceIdentifier = ctx.Request.Headers["X-Request-ID"].FirstOrDefault()
                          ?? Activity.Current?.Id
                          ?? Guid.NewGuid().ToString();
    ctx.Response.Headers["X-Request-ID"] = ctx.TraceIdentifier;
    await next();
});

// 4. Logging (Serilog enrichment)
app.UseSerilogRequestLogging();

// 5. Rate limiting
app.UseRateLimiter();

// 6. Response compression
app.UseResponseCompression();

// 7. Output caching
app.UseOutputCache();

// 8. Routing
app.UseRouting();

// 9. CORS
app.UseCors();

// 10. Auth
app.UseAuthentication();
app.UseAuthorization();

// 11. Endpoints
app.MapControllers();
app.MapHealthChecks("/healthz");
app.MapHealthChecks("/readyz");
```

---

### 23. How do you implement zero-downtime deployments for an ASP.NET Core service?

**A:**

**Graceful shutdown:**
```csharp
builder.Services.Configure<HostOptions>(o =>
    o.ShutdownTimeout = TimeSpan.FromSeconds(30));

// Kestrel drains in-flight requests on SIGTERM automatically
// BackgroundService should check stoppingToken
```

**Kubernetes:**
```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sleep", "10"] # wait for LB to deregister

readinessProbe:
  httpGet: { path: /readyz, port: 8080 }
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3

strategy:
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

**Database migrations:** Run `dotnet ef database update` in an `initContainer` before the main container starts. Migrations must be backward-compatible.

**Feature flags:** Deploy new code disabled; enable gradually without redeployment.
