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
