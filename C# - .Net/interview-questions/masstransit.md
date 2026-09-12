# 🚌 MassTransit — Interview Questions (Junior → Architect)

MassTransit is a free, open-source distributed application framework for .NET. It abstracts message brokers (RabbitMQ, Azure Service Bus, Kafka, Amazon SQS) behind a unified API.

---

## 🟢 Junior Level

---

### 1. What is MassTransit and why use it over using a broker SDK directly?

**A:** MassTransit is an abstraction layer over message brokers that adds:

- **Unified API** — same code works with RabbitMQ, Azure Service Bus, Kafka, SQS
- **Consumer pipeline** — middleware, retry, error queues
- **Saga/state machine** — long-running workflow orchestration
- **Request/response** — synchronous-feeling messaging
- **Scheduling** — delayed and recurring messages
- **OpenTelemetry** — built-in distributed tracing

```csharp
// Without MassTransit — tied to RabbitMQ SDK
var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = factory.CreateConnection();
using var channel = connection.CreateModel();
channel.BasicPublish(exchange: "", routingKey: "orders", basicProperties: null, body: body);

// With MassTransit — broker-agnostic
await publishEndpoint.Publish<OrderCreated>(new { OrderId = order.Id });
```

---

### 2. How do you configure MassTransit with RabbitMQ?

**A:**

```csharp
builder.Services.AddMassTransit(x =>
{
    // Register consumers
    x.AddConsumer<OrderCreatedConsumer>();
    x.AddConsumer<PaymentProcessedConsumer>();

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host("rabbitmq", "/", h =>
        {
            h.Username("guest");
            h.Password("guest");
        });

        // Configure consumers' receive endpoints (queues)
        cfg.ConfigureEndpoints(context);
        // Auto-generates queue name from consumer type: "order-created"
    });
});
```

---

### 3. What is the difference between `Publish` and `Send`?

**A:**

| | `Publish` | `Send` |
|--|-----------|--------|
| Routing | Exchange/topic — all subscribed consumers receive it | Point-to-point — specific queue |
| Receivers | All consumers subscribed to the message type | One specific consumer |
| Pattern | Event (something happened) | Command (do this specific thing) |
| Address needed | No | Yes (queue address) |

```csharp
// Publish — event, any consumer can handle it
await _publishEndpoint.Publish<OrderCreated>(new
{
    OrderId = order.Id,
    CustomerId = order.CustomerId,
    Total = order.Total
});

// Send — command to a specific service
var endpointUri = new Uri("rabbitmq://localhost/payment-service");
var endpoint = await _bus.GetSendEndpoint(endpointUri);
await endpoint.Send<ProcessPayment>(new
{
    OrderId = order.Id,
    Amount = order.Total
});
```

---

### 4. How do you write a consumer?

**A:**

```csharp
public class OrderCreatedConsumer : IConsumer<OrderCreated>
{
    private readonly ILogger<OrderCreatedConsumer> _logger;
    private readonly IInventoryService _inventory;

    public OrderCreatedConsumer(ILogger<OrderCreatedConsumer> logger, IInventoryService inventory)
    {
        _logger = logger;
        _inventory = inventory;
    }

    public async Task Consume(ConsumeContext<OrderCreated> context)
    {
        _logger.LogInformation("Processing order {OrderId}", context.Message.OrderId);

        await _inventory.ReserveAsync(
            context.Message.OrderId,
            context.Message.Items,
            context.CancellationToken);

        _logger.LogInformation("Order {OrderId} inventory reserved", context.Message.OrderId);
    }
}
```

---

### 5. What is a message contract and how should you define it?

**A:** Message contracts should be simple — interfaces or records with only properties:

```csharp
// Preferred: interface (MassTransit can proxy it)
public interface OrderCreated
{
    Guid OrderId { get; }
    Guid CustomerId { get; }
    decimal Total { get; }
    DateTime CreatedAt { get; }
    IReadOnlyList<OrderLine> Lines { get; }
}

public interface OrderLine
{
    Guid ProductId { get; }
    int Quantity { get; }
    decimal UnitPrice { get; }
}

// Also fine: record
public record OrderCreated(
    Guid OrderId,
    Guid CustomerId,
    decimal Total,
    DateTime CreatedAt);

// Avoid: class with no interface — harder to extend without breaking
```

---

### 6. What happens when a consumer throws an exception?

**A:** By default, MassTransit retries the message and then moves it to an error queue:

1. **Retry** — message redelivered immediately (default: no retries unless configured)
2. **Fault** — a `Fault<T>` message is published (other consumers can handle failures)
3. **Error queue** — if all retries fail, message moved to `{queue-name}_error` queue
4. **Dead letter** — broker-level dead letter queue

```csharp
cfg.ConfigureEndpoints(context);

// Configure retry globally
cfg.UseMessageRetry(r => r.Intervals(
    TimeSpan.FromSeconds(1),
    TimeSpan.FromSeconds(5),
    TimeSpan.FromSeconds(30)));

// Consume faults
public class OrderCreatedFaultConsumer : IConsumer<Fault<OrderCreated>>
{
    public async Task Consume(ConsumeContext<Fault<OrderCreated>> context)
    {
        var originalMessage = context.Message.Message;
        var exceptions = context.Message.Exceptions;
        // alert, log, notify ops
    }
}
```

---

### 7. What is `ConsumeContext<T>` and what can you access from it?

**A:**

```csharp
public async Task Consume(ConsumeContext<OrderCreated> context)
{
    // Message
    var order = context.Message;

    // Headers / metadata
    Guid? messageId = context.MessageId;
    Guid? correlationId = context.CorrelationId;
    DateTime? sentTime = context.SentTime;
    Uri? sourceAddress = context.SourceAddress;

    // Respond to a request
    await context.RespondAsync<OrderConfirmed>(new { order.OrderId });

    // Publish from within consumer
    await context.Publish<InventoryReserved>(new { order.OrderId });

    // Send to specific endpoint
    await context.Send<ProcessPayment>(endpointUri, new { order.OrderId, order.Total });

    // Cancellation
    context.CancellationToken.ThrowIfCancellationRequested();
}
```

---

## 🟡 Mid Level

---

### 8. How do you implement retry and circuit breaker policies?

**A:**

```csharp
x.UsingRabbitMq((context, cfg) =>
{
    // Immediate retry — for transient errors (e.g., DB deadlock)
    cfg.UseMessageRetry(r =>
    {
        r.Immediate(3);  // 3 immediate retries
        r.Ignore<ValidationException>();       // don't retry these
        r.Handle<SqlException>();              // only retry these
    });

    // Exponential backoff with jitter
    cfg.UseMessageRetry(r =>
        r.Exponential(retryLimit: 5,
                      minInterval: TimeSpan.FromSeconds(1),
                      maxInterval: TimeSpan.FromMinutes(5),
                      intervalDelta: TimeSpan.FromSeconds(2)));

    // Redelivery — moves to delayed queue, not in-memory
    cfg.UseScheduledRedelivery(r =>
        r.Intervals(TimeSpan.FromMinutes(1),
                    TimeSpan.FromMinutes(5),
                    TimeSpan.FromMinutes(30)));

    // Circuit breaker
    cfg.UseCircuitBreaker(cb =>
    {
        cb.TrackingPeriod = TimeSpan.FromMinutes(1);
        cb.TripThreshold = 15;     // 15% failure rate trips the breaker
        cb.ActiveThreshold = 10;   // minimum 10 messages to evaluate
        cb.ResetInterval = TimeSpan.FromMinutes(5);
    });

    cfg.ConfigureEndpoints(context);
});
```

---

### 9. How do you implement request/response messaging?

**A:** MassTransit supports synchronous-looking request/response over the message bus:

```csharp
// Define contracts
public interface GetOrderStatus { Guid OrderId { get; } }
public interface OrderStatusResponse { string Status { get; } bool IsFound { get; } }

// Consumer (server side)
public class GetOrderStatusConsumer : IConsumer<GetOrderStatus>
{
    public async Task Consume(ConsumeContext<GetOrderStatus> context)
    {
        var order = await _repo.GetAsync(context.Message.OrderId);
        await context.RespondAsync<OrderStatusResponse>(new
        {
            Status = order?.Status ?? "Unknown",
            IsFound = order != null
        });
    }
}

// Caller (client side)
public class OrderQueryService
{
    private readonly IRequestClient<GetOrderStatus> _client;

    public async Task<string> GetStatusAsync(Guid orderId, CancellationToken ct)
    {
        var response = await _client.GetResponse<OrderStatusResponse>(
            new { OrderId = orderId }, ct, timeout: RequestTimeout.After(s: 5));

        return response.Message.Status;
    }
}

// Register client
builder.Services.AddMassTransit(x =>
{
    x.AddRequestClient<GetOrderStatus>();
    // ...
});
```

---

### 10. What is a saga state machine in MassTransit?

**A:** A saga is a long-running process/workflow that reacts to events and maintains state:

```csharp
public class OrderState : SagaStateMachineInstance
{
    public Guid CorrelationId { get; set; }
    public string CurrentState { get; set; } = "";
    public Guid OrderId { get; set; }
    public decimal Total { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class OrderStateMachine : MassTransitStateMachine<OrderState>
{
    public State Submitted { get; private set; } = null!;
    public State PaymentPending { get; private set; } = null!;
    public State Completed { get; private set; } = null!;
    public State Cancelled { get; private set; } = null!;

    public Event<OrderCreated> OrderCreated { get; private set; } = null!;
    public Event<PaymentConfirmed> PaymentConfirmed { get; private set; } = null!;
    public Event<PaymentFailed> PaymentFailed { get; private set; } = null!;

    public OrderStateMachine()
    {
        InstanceState(x => x.CurrentState);
        Event(() => OrderCreated, x => x.CorrelateById(ctx => ctx.Message.OrderId));
        Event(() => PaymentConfirmed, x => x.CorrelateById(ctx => ctx.Message.OrderId));
        Event(() => PaymentFailed, x => x.CorrelateById(ctx => ctx.Message.OrderId));

        Initially(
            When(OrderCreated)
                .Then(ctx => {
                    ctx.Saga.OrderId = ctx.Message.OrderId;
                    ctx.Saga.Total = ctx.Message.Total;
                    ctx.Saga.CreatedAt = DateTime.UtcNow;
                })
                .PublishAsync(ctx => ctx.Init<ProcessPayment>(new { ctx.Saga.OrderId, ctx.Saga.Total }))
                .TransitionTo(PaymentPending));

        During(PaymentPending,
            When(PaymentConfirmed)
                .PublishAsync(ctx => ctx.Init<FulfillOrder>(new { ctx.Saga.OrderId }))
                .TransitionTo(Completed),
            When(PaymentFailed)
                .PublishAsync(ctx => ctx.Init<CancelOrder>(new { ctx.Saga.OrderId }))
                .TransitionTo(Cancelled));
    }
}
```

---

### 11. How do you configure saga persistence?

**A:**

```csharp
// Entity Framework Core persistence (most common)
builder.Services.AddMassTransit(x =>
{
    x.AddSagaStateMachine<OrderStateMachine, OrderState>()
     .EntityFrameworkRepository(r =>
     {
         r.ConcurrencyMode = ConcurrencyMode.Pessimistic; // or Optimistic
         r.AddDbContext<AppDbContext>((provider, options) =>
             options.UseNpgsql(connectionString));
         r.UsePostgres(); // Postgres-specific locking hints
     });
});

// EF Core migration for saga state
// OrderState maps to a database table
public class AppDbContext : SagaDbContext
{
    public AppDbContext(DbContextOptions options) : base(options) { }

    protected override IEnumerable<ISagaClassMap> Configurations =>
        [new OrderStateMap()];
}

public class OrderStateMap : SagaClassMap<OrderState>
{
    protected override void Configure(EntityTypeBuilder<OrderState> entity, ModelBuilder model)
    {
        entity.Property(x => x.CurrentState).HasMaxLength(64);
    }
}
```

---

### 12. How do you implement the outbox pattern with MassTransit?

**A:** MassTransit has a built-in transactional outbox — atomically saves messages to DB and delivers them:

```csharp
builder.Services.AddMassTransit(x =>
{
    x.AddEntityFrameworkOutbox<AppDbContext>(o =>
    {
        o.UsePostgres();          // Postgres-specific locking
        o.UseBusOutbox();         // enable outbox for all bus operations
        o.QueryDelay = TimeSpan.FromSeconds(1);
        o.QueryTimeout = TimeSpan.FromSeconds(30);
    });

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.UseMessageRetry(r => r.Intervals(1000, 5000, 30000));
        cfg.ConfigureEndpoints(context);
    });
});

// Usage — message is saved to DB atomically with your business data
// then delivered by the outbox relay
await using var tx = await db.Database.BeginTransactionAsync();
db.Orders.Add(order);
await publishEndpoint.Publish<OrderCreated>(new { order.Id }); // saved to outbox table
await db.SaveChangesAsync();
await tx.CommitAsync();
// Relay picks up from outbox and delivers to broker
```

---

### 13. How do you test MassTransit consumers?

**A:**

```csharp
// Unit test with InMemoryTestHarness
using MassTransit.Testing;

public class OrderCreatedConsumerTests
{
    [Fact]
    public async Task Should_Reserve_Inventory_On_OrderCreated()
    {
        await using var provider = new ServiceCollection()
            .AddMassTransitTestHarness(x =>
            {
                x.AddConsumer<OrderCreatedConsumer>();
            })
            .AddScoped<IInventoryService, MockInventoryService>()
            .BuildServiceProvider(true);

        var harness = provider.GetRequiredService<ITestHarness>();
        await harness.Start();

        await harness.Bus.Publish<OrderCreated>(new
        {
            OrderId = NewId.NextGuid(),
            CustomerId = NewId.NextGuid(),
            Total = 99.99m
        });

        // Assert consumer was invoked
        Assert.True(await harness.Consumed.Any<OrderCreated>());

        var consumerHarness = harness.GetConsumerHarness<OrderCreatedConsumer>();
        Assert.True(await consumerHarness.Consumed.Any<OrderCreated>());

        // Assert no faults
        Assert.False(await harness.Published.Any<Fault<OrderCreated>>());
    }
}
```

---

## 🔴 Senior Level

---

### 14. How do you configure MassTransit with Azure Service Bus?

**A:**

```csharp
builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<OrderCreatedConsumer>();

    x.UsingAzureServiceBus((context, cfg) =>
    {
        cfg.Host(new Uri("sb://mynamespace.servicebus.windows.net"), h =>
        {
            // Managed Identity (preferred in Azure)
            h.TokenCredential = new DefaultAzureCredential();
            // Or connection string
            // h.ConnectionString = connectionString;
        });

        cfg.Message<OrderCreated>(m => m.SetEntityName("order-created")); // topic name

        cfg.SubscriptionEndpoint<OrderCreated>(
            subscriptionName: "order-service",
            configureEndpoint: e =>
            {
                e.ConfigureConsumer<OrderCreatedConsumer>(context);
                e.PrefetchCount = 32;
                e.MaxAutoLockRenewalDuration = TimeSpan.FromMinutes(5);
            });
    });
});
```

---

### 15. How do you implement message routing and filtering?

**A:**

```csharp
// Header-based routing
cfg.Send<ProcessPayment>(x =>
    x.UseRoutingKey(m => m.Message.Currency == "USD" ? "usd-payments" : "intl-payments"));

// Topology — configure exchanges and bindings
cfg.Message<OrderCreated>(m => m.SetEntityName("orders"));

cfg.Publish<OrderCreated>(p =>
{
    p.ExchangeType = "topic";  // RabbitMQ topic exchange
    p.Durable = true;
});

// Consumer filter — only consume messages matching a condition
cfg.ReceiveEndpoint("high-value-orders", e =>
{
    e.ConfigureConsumer<HighValueOrderConsumer>(context);
    e.Bind("orders", b =>
    {
        b.ExchangeType = "topic";
        b.RoutingKey = "high-value.*";
    });
});
```

---

### 16. How do you handle idempotency in MassTransit consumers?

**A:**

```csharp
public class OrderCreatedConsumer : IConsumer<OrderCreated>
{
    private readonly AppDbContext _db;

    public async Task Consume(ConsumeContext<OrderCreated> context)
    {
        var messageId = context.MessageId ?? throw new InvalidOperationException("MessageId required");

        // Check if already processed (inbox pattern)
        var alreadyProcessed = await _db.ProcessedMessages
            .AnyAsync(m => m.MessageId == messageId, context.CancellationToken);

        if (alreadyProcessed)
        {
            // Idempotent — skip but don't fail
            return;
        }

        await using var tx = await _db.Database.BeginTransactionAsync(context.CancellationToken);

        // Business logic
        await _inventoryService.ReserveAsync(context.Message.OrderId, context.CancellationToken);

        // Record as processed
        _db.ProcessedMessages.Add(new ProcessedMessage
        {
            MessageId = messageId,
            ProcessedAt = DateTime.UtcNow,
            MessageType = typeof(OrderCreated).Name
        });

        await _db.SaveChangesAsync(context.CancellationToken);
        await tx.CommitAsync(context.CancellationToken);
    }
}
```

---

## 🏛️ Architect Level

---

### 17. How do you design a saga for a complex order fulfillment workflow?

**A:**

```csharp
// Full order lifecycle saga
public class OrderFulfillmentStateMachine : MassTransitStateMachine<OrderFulfillmentState>
{
    // States
    public State AwaitingInventory { get; private set; } = null!;
    public State AwaitingPayment { get; private set; } = null!;
    public State AwaitingShipment { get; private set; } = null!;
    public State Completed { get; private set; } = null!;
    public State Cancelled { get; private set; } = null!;

    // Timeouts
    public Schedule<OrderFulfillmentState, PaymentTimeout> PaymentTimeoutSchedule { get; private set; } = null!;

    public OrderFulfillmentStateMachine()
    {
        InstanceState(x => x.CurrentState);

        Schedule(() => PaymentTimeoutSchedule, state => state.PaymentTimeoutTokenId,
            s =>
            {
                s.Received = r => r.CorrelateById(ctx => ctx.Message.OrderId);
                s.Delay = TimeSpan.FromMinutes(15);
            });

        Initially(
            When(OrderCreated)
                .Then(Initialize)
                .PublishAsync(ctx => ctx.Init<CheckInventory>(new { ctx.Saga.OrderId }))
                .TransitionTo(AwaitingInventory));

        During(AwaitingInventory,
            When(InventoryReserved)
                .Schedule(PaymentTimeoutSchedule, ctx => ctx.Init<PaymentTimeout>(new { ctx.Saga.OrderId }))
                .PublishAsync(ctx => ctx.Init<ProcessPayment>(new { ctx.Saga.OrderId, ctx.Saga.Total }))
                .TransitionTo(AwaitingPayment),
            When(InventoryInsufficient)
                .PublishAsync(ctx => ctx.Init<NotifyCustomer>(new { ctx.Saga.OrderId, Reason = "Out of stock" }))
                .TransitionTo(Cancelled));

        During(AwaitingPayment,
            When(PaymentConfirmed)
                .Unschedule(PaymentTimeoutSchedule)
                .PublishAsync(ctx => ctx.Init<ShipOrder>(new { ctx.Saga.OrderId }))
                .TransitionTo(AwaitingShipment),
            When(PaymentTimeoutSchedule.Received)
                .PublishAsync(ctx => ctx.Init<ReleaseInventory>(new { ctx.Saga.OrderId }))
                .PublishAsync(ctx => ctx.Init<NotifyCustomer>(new { ctx.Saga.OrderId, Reason = "Payment timeout" }))
                .TransitionTo(Cancelled));

        During(AwaitingShipment,
            When(OrderShipped)
                .PublishAsync(ctx => ctx.Init<NotifyCustomer>(new { ctx.Saga.OrderId, Reason = "Shipped!" }))
                .TransitionTo(Completed));
    }
}
```

---

### 18. How do you monitor and operate MassTransit in production?

**A:**

**Observability:**
```csharp
// OpenTelemetry — auto-instruments publish/consume/saga transitions
builder.Services.AddOpenTelemetry()
    .WithTracing(b => b
        .AddSource("MassTransit")  // traces all MT operations
        .AddOtlpExporter());

// Prometheus metrics
cfg.UsePrometheusMetrics();
// Exposes: mt_receive_total, mt_publish_total, mt_consumer_duration, etc.
```

**Dead letter queue processing:**
- Monitor `{queue}_error` queues for failed messages
- Use MassTransit's Conductor or a custom dashboard
- Implement automated requeue for transient errors, alert for persistent ones

**Broker monitoring:**
- RabbitMQ Management Plugin — queue depths, delivery rates, consumer counts
- Azure Service Bus — dead letter counts, active message counts in Azure Monitor

**Key metrics to alert on:**
- Error queue depth > 0
- Consumer lag (queue depth growing)
- Consumer exception rate > threshold
- Saga instance count growing (stuck sagas)

---

### 19. How do you handle schema evolution in MassTransit messages?

**A:**

**Backward-compatible changes (safe):**
- Add new optional properties
- Add new message types
- Never remove or rename properties

```csharp
// V1 consumer still handles V2 messages safely (extra fields ignored)
public interface OrderCreated  // V1
{
    Guid OrderId { get; }
    decimal Total { get; }
}

public interface OrderCreated  // V2 — added fields
{
    Guid OrderId { get; }
    decimal Total { get; }
    string Currency { get; }    // new — V1 consumers ignore this
    Guid? PromoCodeId { get; }  // new nullable — safe
}
```

**Breaking changes — versioned message types:**
```csharp
// Run both versions in parallel during migration
public interface OrderCreatedV2 : OrderCreated  // extends V1
{
    string Currency { get; }
}

// Translator consumer converts V1 → V2 for new consumers
public class OrderCreatedTranslator : IConsumer<OrderCreated>
{
    public async Task Consume(ConsumeContext<OrderCreated> context)
    {
        await context.Publish<OrderCreatedV2>(new
        {
            context.Message.OrderId,
            context.Message.Total,
            Currency = "USD"  // default
        });
    }
}
```
