# 🏛️ C# / .NET — Architect-Level Interview Questions

---

## 1. How would you design the architecture of a large-scale .NET microservices system?

**A:**

**Service decomposition (Domain-Driven Design):**
- Define bounded contexts — each becomes a service with its own DB
- Prefer services aligned to business capabilities, not technical layers
- Anti-corruption layer between contexts to prevent tight coupling

**Communication:**
- **Synchronous:** gRPC (internal), REST (external/public API)
- **Asynchronous:** MassTransit + RabbitMQ/Azure Service Bus for domain events

**Per-service stack:**
```
ASP.NET Core (Minimal API) → MediatR (CQRS) → EF Core (Write) / Dapper (Read)
                          → Domain Events → MassTransit consumer
```

**Shared infrastructure:**
- API Gateway (YARP, Azure API Management) — routing, auth, rate limiting
- Identity server (Duende IdentityServer / Azure AD B2C) — OAuth 2.0, OIDC
- Service mesh (Linkerd) — mTLS, observability, retries

**Data:** Each service owns its schema. Cross-service reads via published projections (read models), not cross-DB joins.

---

## 2. How do you implement CQRS and Event Sourcing in .NET?

**A:**

**CQRS (Command Query Responsibility Segregation):**
```csharp
// Command — changes state
record CreateOrderCommand(Guid CustomerId, List<OrderLine> Lines) : ICommand;

// Handler — MediatR
class CreateOrderHandler : ICommandHandler<CreateOrderCommand>
{
    public async Task Handle(CreateOrderCommand cmd, CancellationToken ct)
    {
        var order = Order.Create(cmd.CustomerId, cmd.Lines);
        await _repo.SaveAsync(order, ct);
        await _bus.PublishAsync(new OrderCreated(order.Id), ct);
    }
}

// Query — reads from optimized read model
record GetOrderQuery(Guid Id) : IQuery<OrderDto>;
class GetOrderHandler : IQueryHandler<GetOrderQuery, OrderDto>
{
    // Hits read-optimized DB/view, no domain model
    public Task<OrderDto> Handle(GetOrderQuery q, CancellationToken ct)
        => _readDb.QuerySingleAsync<OrderDto>("SELECT...", new { q.Id });
}
```

**Event Sourcing:**
- Store sequence of domain events, not current state
- Replay events to rebuild aggregate state
- Snapshot for performance (every N events)
- Use EventStoreDB or Postgres-backed Marten for .NET

---

## 3. How do you approach database strategy in a .NET microservices architecture?

**A:**

**Database per service** — each service has its own DB/schema:
- Prevents tight coupling via shared DB
- Allows different DB engines per service (Postgres, MongoDB, Redis)

**Read/write split:**
- Write path: normalized relational DB (EF Core)
- Read path: denormalized read models, projections, or search index (Elasticsearch)

**Cross-service data access:**
- Event-driven projections — service B subscribes to events from A, builds its own read model
- API composition at the query service layer (no cross-DB joins)

**Schema evolution:**
- EF Core Migrations — always forward-only, backward-compatible (expand-contract pattern)
- Never drop/rename columns in the same deploy that removes their usage

**Multi-tenancy strategies:**
- Row-level (shared DB, `TenantId` column + global query filter in EF Core)
- Schema-per-tenant (Postgres schemas)
- DB-per-tenant (for strict isolation)

---

## 4. How do you handle distributed tracing and observability in .NET?

**A:** OpenTelemetry is the standard:

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddSource("MyApp")
        .AddOtlpExporter(o => o.Endpoint = new Uri("http://otel-collector:4317")))
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddRuntimeInstrumentation()
        .AddPrometheusExporter());

// Custom span
using var activity = ActivitySource.StartActivity("ProcessOrder");
activity?.SetTag("order.id", orderId);
activity?.SetStatus(ActivityStatusCode.Ok);
```

**Pillars:**
- **Traces** → Jaeger / Tempo
- **Metrics** → Prometheus + Grafana
- **Logs** → Serilog → Elasticsearch / Loki

**Alerting:** SLO-based (error rate < 0.1%, p99 latency < 500ms) via Grafana or PagerDuty.

---

## 5. How do you design for resilience in a .NET distributed system?

**A:**

**Polly — resilience policies:**
```csharp
var pipeline = new ResiliencePipelineBuilder<HttpResponseMessage>()
    .AddRetry(new RetryStrategyOptions<HttpResponseMessage>
    {
        MaxRetryAttempts = 3,
        Delay = TimeSpan.FromSeconds(1),
        BackoffType = DelayBackoffType.Exponential,
        ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
            .Handle<HttpRequestException>()
            .HandleResult(r => r.StatusCode >= HttpStatusCode.InternalServerError)
    })
    .AddCircuitBreaker(new CircuitBreakerStrategyOptions<HttpResponseMessage>
    {
        FailureRatio = 0.5,
        SamplingDuration = TimeSpan.FromSeconds(10),
        BreakDuration = TimeSpan.FromSeconds(30)
    })
    .AddTimeout(TimeSpan.FromSeconds(5))
    .Build();
```

**Bulkhead isolation:** `SemaphoreSlim` or `AddBulkhead` — cap concurrent calls to a dependency so one slow service doesn't exhaust all threads.

**Health checks:**
```csharp
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>()
    .AddRedis(redisConnStr)
    .AddCheck<DependencyHealthCheck>("dependency");

app.MapHealthChecks("/readyz", new() { ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse });
```

---

## 6. How do you approach zero-downtime deployments in a .NET/Kubernetes environment?

**A:**

**Application:**
- Implement `IHostApplicationLifetime.ApplicationStopping` to drain in-flight requests
- `/healthz` (liveness) and `/readyz` (readiness) endpoints — Kubernetes uses readiness to gate traffic
- Graceful shutdown timeout: `webApplication.Lifetime.ApplicationStopping` + `builder.WebHost.UseShutdownTimeout(TimeSpan.FromSeconds(30))`

**Kubernetes:**
```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "5"]  # wait for LB to deregister pod before SIGTERM
readinessProbe:
  httpGet:
    path: /readyz
  initialDelaySeconds: 5
  periodSeconds: 5
```

**Database migrations:**
- Run migrations as a separate Kubernetes Job before rolling out the new Deployment
- Migrations must be backward-compatible (expand-contract)

**Feature flags:** LaunchDarkly / Unleash — ship code off, enable per segment, roll back instantly without a deploy.

---

## 7. How do you design API contracts and versioning in .NET?

**A:**

**REST versioning (ASP.NET Core API Versioning):**
```csharp
builder.Services.AddApiVersioning(o =>
{
    o.DefaultApiVersion = new ApiVersion(1, 0);
    o.AssumeDefaultVersionWhenUnspecified = true;
    o.ReportApiVersions = true;
    o.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new HeaderApiVersionReader("X-API-Version"));
});

[ApiVersion("2.0")]
[Route("v{version:apiVersion}/users")]
public class UsersV2Controller : ControllerBase { ... }
```

**gRPC:** Package versioning (`package myservice.v2`) + backward-compatible field additions only.

**Contract testing (Pact):**
- Consumer defines expectations
- Provider verifies against them in CI
- Prevents breaking consumers without running the full integration suite

**Deprecation:** `Sunset` + `Deprecation` response headers; monitor usage with custom metrics before removal.

---

## 8. How do you implement multi-tenancy in ASP.NET Core + EF Core?

**A:**

**Tenant resolution:**
```csharp
public class TenantMiddleware
{
    public async Task InvokeAsync(HttpContext ctx, ITenantResolver resolver)
    {
        var tenantId = await resolver.ResolveAsync(ctx); // header, JWT, subdomain
        ctx.Items["TenantId"] = tenantId;
        await _next(ctx);
    }
}
```

**Row-level isolation (EF Core global query filter):**
```csharp
protected override void OnModelCreating(ModelBuilder mb)
{
    mb.Entity<Order>().HasQueryFilter(o => o.TenantId == _currentTenantId);
}
// All queries automatically include WHERE TenantId = @current
```

**Schema isolation (per tenant, Postgres):**
- Set `search_path` at connection open time
- Use EF Core's `UseSchema(tenantId)` in `OnModelCreating`

**Connection string per tenant:**
- Resolve connection string in `IDbContextFactory<T>` based on `ITenantContext`
- Pool connections per tenant to avoid connection explosion

---

## 9. How do you handle security at the architecture level in .NET?

**A:**

**Authentication/Authorization:**
- OAuth 2.0 + OIDC via Duende IdentityServer or Azure AD
- JWT validation in middleware: `AddJwtBearer`
- Policy-based authorization: `[Authorize(Policy = "OrderRead")]`
- Resource-based authorization: `IAuthorizationService.AuthorizeAsync(user, resource, policy)`

**Secrets management:**
- Azure Key Vault / AWS Secrets Manager — never store secrets in config files or env vars in source
- .NET secret manager for local dev: `dotnet user-secrets`

**Threat mitigation:**
- SQL injection → EF Core parameterized queries; never raw format strings
- XSS → Razor auto-encodes; use `HtmlEncoder` for manual output
- CSRF → ASP.NET Core's `ValidateAntiForgeryToken` (SPA: SameSite cookies)
- SSRF → whitelist outbound HTTP targets; validate `Uri` before `HttpClient` calls
- Supply chain → NuGet package lock files, `dotnet list package --vulnerable`

---

## 10. How do you evaluate and govern technical debt in a large .NET codebase?

**A:**

**Measurement:**
- Static analysis: Roslyn analyzers, SonarQube, NDepend (coupling, cohesion, cyclomatic complexity)
- Test coverage: Coverlet — but coverage ≠ quality; focus on critical path coverage
- Architecture fitness functions: `NetArchTest` for enforcing layer rules in CI:

```csharp
var result = Types.InAssembly(assembly)
    .That().ResideInNamespace("MyApp.Infrastructure")
    .ShouldNot().HaveDependencyOn("MyApp.Presentation")
    .GetResult();
Assert.True(result.IsSuccessful);
```

**Governance:**
- ADR (Architecture Decision Records) — document decisions and trade-offs
- RFC process for cross-team changes
- Tech debt backlog — treat as first-class work items with business justification
- "Boy Scout Rule" — leave code cleaner than you found it; enforce via PR review culture

**Refactoring strategies:**
- Strangler Fig — incrementally replace legacy with new behind a facade
- Branch by abstraction — swap implementations behind an interface
- Parallel run — run old + new simultaneously, compare outputs

---

## 11. How do you design a high-availability .NET service on Kubernetes?

**A:**

**Application-level:**
```csharp
// Health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("db", failureStatus: HealthStatus.Degraded)
    .AddRedis(redisConn, "redis")
    .AddCheck("self", () => HealthCheckResult.Healthy());

app.MapHealthChecks("/healthz", new() { Predicate = _ => false }); // liveness
app.MapHealthChecks("/readyz");                                     // readiness
```

**Kubernetes:**
```yaml
spec:
  replicas: 3
  strategy:
    rollingUpdate:
      maxUnavailable: 0     # never take a pod down before replacement is ready
      maxSurge: 1
  template:
    spec:
      containers:
        livenessProbe:
          httpGet: { path: /healthz, port: 8080 }
          initialDelaySeconds: 10
        readinessProbe:
          httpGet: { path: /readyz, port: 8080 }
          initialDelaySeconds: 5
        lifecycle:
          preStop:
            exec:
              command: ["sleep", "10"]  # drain connections before SIGTERM
```

**PodDisruptionBudget:**
```yaml
spec:
  minAvailable: 2
  selector:
    matchLabels: { app: order-service }
```

---

## 12. How do you implement the Saga pattern in .NET with MassTransit?

**A:**

```csharp
// State machine saga with MassTransit
public class OrderSaga : MassTransitStateMachine<OrderSagaData>
{
    public State AwaitingPayment { get; private set; } = null!;
    public State AwaitingShipment { get; private set; } = null!;
    public State Completed { get; private set; } = null!;

    public OrderSaga()
    {
        InstanceState(x => x.CurrentState);

        Event(() => OrderCreated, x => x.CorrelateById(ctx => ctx.Message.OrderId));
        Event(() => PaymentConfirmed, x => x.CorrelateById(ctx => ctx.Message.OrderId));
        Event(() => PaymentFailed, x => x.CorrelateById(ctx => ctx.Message.OrderId));

        Initially(
            When(OrderCreated)
                .PublishAsync(ctx => ctx.Init<ReserveInventory>(new { ctx.Message.OrderId }))
                .TransitionTo(AwaitingPayment));

        During(AwaitingPayment,
            When(PaymentConfirmed)
                .PublishAsync(ctx => ctx.Init<ShipOrder>(new { ctx.Message.OrderId }))
                .TransitionTo(AwaitingShipment),
            When(PaymentFailed)
                .PublishAsync(ctx => ctx.Init<ReleaseInventory>(new { ctx.Message.OrderId }))
                .Finalize());
    }
}
```

---

## 13. How do you implement eventual consistency with the Outbox + Inbox pattern?

**A:**

**Outbox (producer side):** Atomically write domain event + business data in same transaction.

**Inbox (consumer side):** Deduplicate received messages by tracking processed message IDs:

```csharp
// Consumer with inbox deduplication
public async Task Consume(ConsumeContext<OrderCreated> ctx)
{
    var messageId = ctx.MessageId ?? throw new InvalidOperationException();

    await using var tx = await _db.BeginTransactionAsync();

    // Check if already processed (idempotency)
    if (await _db.InboxMessages.AnyAsync(m => m.Id == messageId))
    {
        await tx.RollbackAsync();
        return; // duplicate — skip
    }

    // Process
    await _orderService.HandleOrderCreatedAsync(ctx.Message);

    // Record as processed
    _db.InboxMessages.Add(new InboxMessage { Id = messageId, ProcessedAt = DateTime.UtcNow });
    await _db.SaveChangesAsync();
    await tx.CommitAsync();
}
```

---

## 14. How do you design a .NET system for PCI DSS or HIPAA compliance?

**A:**

**Data protection:**
```csharp
// ASP.NET Core Data Protection API
builder.Services.AddDataProtection()
    .PersistKeysToAzureKeyVault(keyVaultUri, credential)
    .ProtectKeysWithAzureKeyVault(keyIdentifier, credential)
    .SetApplicationName("MyApp");

// Encrypt sensitive fields in EF Core
[Encrypted]  // custom converter
public string CardNumberHash { get; set; }
```

**Architecture:**
- Dedicated VPC/VNet — no public access to data tier
- All data encrypted at rest (AES-256) and in transit (TLS 1.2+)
- Audit log for every data access: who, what, when — immutable (append-only Cosmos DB or Postgres + WAL shipping)
- Secrets in Key Vault — no secrets in config or environment
- Column-level encryption for PII (EF Core value converters with `IDataProtector`)
- Regular penetration testing, vulnerability scanning in CI (`dotnet-retire`, Snyk)

**Access control:**
- RBAC + ABAC (Attribute-based) for fine-grained access
- Short-lived tokens (15 min) with refresh token rotation
- MFA for admin access

---

## 15. How would you architect real-time features (live dashboards, notifications) in .NET?

**A:**

**SignalR (WebSocket / long-polling fallback):**
```csharp
// Hub
public class DashboardHub : Hub
{
    public async Task JoinGroup(string tenantId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, tenantId);
    }
}

// Push from background service
public class MetricsPublisher : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var metrics = await _metricsService.GetLatestAsync(ct);
            await _hubContext.Clients.Group(metrics.TenantId)
                .SendAsync("MetricsUpdated", metrics, ct);
            await Task.Delay(5000, ct);
        }
    }
}
```

**Scale-out (multiple server instances):**
```csharp
// Redis backplane — routes messages to the correct server
builder.Services.AddSignalR().AddStackExchangeRedis("redis:6379");
```

**Alternative for event streaming:** Server-Sent Events (SSE) for one-way push — simpler, works through HTTP/2, no WebSocket upgrade needed:
```csharp
app.MapGet("/events", async (HttpResponse resp, CancellationToken ct) =>
{
    resp.Headers["Content-Type"] = "text/event-stream";
    await foreach (var evt in GetEventsAsync(ct))
        await resp.WriteAsync($"data: {JsonSerializer.Serialize(evt)}\n\n", ct);
});
```
