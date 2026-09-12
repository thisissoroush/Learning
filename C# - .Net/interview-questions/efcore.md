# 🗄️ Entity Framework Core — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is EF Core and how does it differ from EF6?

**A:** EF Core is Microsoft's modern, cross-platform ORM for .NET. It maps C# classes to database tables and generates SQL automatically.

| | EF Core | EF6 |
|--|---------|-----|
| Platform | .NET Core / .NET 5+ | .NET Framework only |
| Performance | Faster, lighter | Heavier |
| Features | Compiled queries, raw SQL, interceptors, split queries | Mature but legacy |
| Providers | SQL Server, PostgreSQL, SQLite, MySQL, Cosmos DB | SQL Server, Oracle |
| Approach | Code-first focused | Code-first + DB-first + Model-first |

---

### 2. What is `DbContext` and `DbSet<T>`?

**A:**

```csharp
public class AppDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public DbSet<Customer> Customers { get; set; }

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder mb)
    {
        mb.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}

// Registration
services.AddDbContext<AppDbContext>(o =>
    o.UseNpgsql(connectionString)
     .EnableSensitiveDataLogging()   // dev only — logs param values
     .EnableDetailedErrors());       // dev only
```

`DbContext` is the unit of work. `DbSet<T>` is the repository for each entity. One `DbContext` per request (Scoped lifetime).

---

### 3. What are the basic CRUD operations in EF Core?

**A:**

```csharp
// Create
var order = new Order { CustomerId = 1, Total = 99.99m };
db.Orders.Add(order);
await db.SaveChangesAsync();

// Read
var order = await db.Orders.FindAsync(id);                  // by PK (cached)
var order = await db.Orders.FirstOrDefaultAsync(o => o.Id == id);
var orders = await db.Orders.Where(o => o.Total > 100).ToListAsync();

// Update
order.Status = "Shipped";
await db.SaveChangesAsync();  // change tracker detects the modification

// Delete
db.Orders.Remove(order);
await db.SaveChangesAsync();

// Bulk update / delete (EF Core 7+) — no entity load
await db.Orders.Where(o => o.Status == "Pending").ExecuteDeleteAsync();
await db.Orders.Where(o => o.Status == "Draft").ExecuteUpdateAsync(s =>
    s.SetProperty(o => o.Status, "Cancelled"));
```

---

### 4. What is the difference between `Add`, `Attach`, `Update`, and `Entry`?

**A:**

```csharp
// Add — marks entity as Added (will INSERT)
db.Orders.Add(newOrder);

// Attach — starts tracking an existing entity as Unchanged
db.Orders.Attach(existingOrder);

// Update — marks entity and all its properties as Modified (full UPDATE)
db.Orders.Update(existingOrder);

// Entry — gives fine-grained control over tracking state
var entry = db.Entry(order);
entry.State = EntityState.Modified;
entry.Property(o => o.Status).IsModified = true;  // only update Status column
entry.Property(o => o.Total).IsModified = false;
```

---

### 5. What is `AsNoTracking` and when should you use it?

**A:**

```csharp
// Default — tracked: change tracker watches every entity (overhead)
var users = await db.Users.ToListAsync();

// AsNoTracking — read-only: no tracking overhead (~20-40% faster for reads)
var users = await db.Users.AsNoTracking().ToListAsync();

// AsNoTrackingWithIdentityResolution — no tracking but deduplicates related entities
var posts = await db.Posts
    .AsNoTrackingWithIdentityResolution()
    .Include(p => p.Author)
    .ToListAsync();
```

**Rule:** Use `AsNoTracking()` for any query where you won't modify the result — list endpoints, reports, exports.

---

### 6. What is eager loading, lazy loading, and explicit loading?

**A:**

```csharp
// Eager loading — JOIN at query time
var orders = await db.Orders
    .Include(o => o.Customer)
    .Include(o => o.Items)
        .ThenInclude(i => i.Product)
    .ToListAsync();

// Lazy loading — loads on property access (requires proxies, causes N+1!)
// Opt-in: services.AddDbContext<AppDbContext>(o => o.UseLazyLoadingProxies())
var customer = await db.Customers.FindAsync(id);
var orders = customer.Orders; // SQL fires here

// Explicit loading — load on demand, manually
var customer = await db.Customers.FindAsync(id);
await db.Entry(customer).Collection(c => c.Orders).LoadAsync();
await db.Entry(customer).Reference(c => c.Address).LoadAsync();
```

**Use eager loading** as the default. Avoid lazy loading in production (N+1 risk). Explicit loading for conditional loads.

---

### 7. How do you configure models with Fluent API vs Data Annotations?

**A:**

```csharp
// Data Annotations — on the model class
public class Product
{
    [Key]
    public int Id { get; set; }

    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = "";

    [Column("unit_price", TypeName = "decimal(10,2)")]
    public decimal Price { get; set; }

    [Index(nameof(Sku), IsUnique = true)]
    public string Sku { get; set; } = "";
}

// Fluent API — in IEntityTypeConfiguration<T> (preferred for complex config)
public class ProductConfiguration : IEntityTypeConfiguration<Product>
{
    public void Configure(EntityTypeBuilder<Product> b)
    {
        b.ToTable("products");
        b.HasKey(p => p.Id);
        b.Property(p => p.Name).IsRequired().HasMaxLength(200);
        b.Property(p => p.Price).HasColumnType("decimal(10,2)");
        b.HasIndex(p => p.Sku).IsUnique();
        b.HasQueryFilter(p => !p.IsDeleted); // global soft-delete filter
    }
}
```

---

### 8. How do you configure relationships in EF Core?

**A:**

```csharp
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        // One-to-Many: Order → Customer
        b.HasOne(o => o.Customer)
         .WithMany(c => c.Orders)
         .HasForeignKey(o => o.CustomerId)
         .OnDelete(DeleteBehavior.Restrict);

        // One-to-One: Order → Invoice
        b.HasOne(o => o.Invoice)
         .WithOne(i => i.Order)
         .HasForeignKey<Invoice>(i => i.OrderId);

        // Many-to-Many: Order → Tags (EF Core 5+ — no join entity needed)
        b.HasMany(o => o.Tags)
         .WithMany(t => t.Orders);

        // Many-to-Many with explicit join entity
        b.HasMany(o => o.Tags)
         .WithMany(t => t.Orders)
         .UsingEntity<OrderTag>(
             j => j.HasOne(ot => ot.Tag).WithMany(),
             j => j.HasOne(ot => ot.Order).WithMany());
    }
}
```

---

### 9. What are EF Core migrations and how do you use them?

**A:**

```bash
# Add a migration
dotnet ef migrations add AddOrderStatusIndex

# Apply migrations
dotnet ef database update

# Generate SQL script (for CI/CD review)
dotnet ef migrations script --idempotent -o migrations.sql

# Revert last migration
dotnet ef migrations remove       # remove unapplied
dotnet ef database update PreviousMigration  # roll back applied

# List migrations
dotnet ef migrations list
```

```csharp
// Apply programmatically at startup
await db.Database.MigrateAsync();
```

---

### 10. What is the difference between `SaveChanges` and `SaveChangesAsync`?

**A:** They do the same thing — flush all tracked changes to the database as a single transaction — but:

- `SaveChanges()` — synchronous, blocks the thread
- `SaveChangesAsync()` — async, releases the thread during the DB round-trip

Always use `SaveChangesAsync` in web applications. Both wrap all pending changes in a single implicit transaction. If any operation fails, all changes are rolled back.

```csharp
// Returns number of rows affected
int affected = await db.SaveChangesAsync(cancellationToken);
```

---

## 🟡 Mid Level

---

### 11. How does EF Core's change tracker work?

**A:** The change tracker monitors every entity loaded through a tracked query, comparing current values against their snapshot:

```csharp
var order = await db.Orders.FindAsync(id); // Snapshot taken

order.Status = "Shipped"; // Detected as Modified

db.ChangeTracker.Entries<Order>().Where(e => e.State == EntityState.Modified);
// → prints the Order entry

await db.SaveChangesAsync();
// Generates: UPDATE orders SET status = 'Shipped' WHERE id = @id
```

**States:** `Added`, `Unchanged`, `Modified`, `Deleted`, `Detached`

**Performance tip:** Disable auto-detection for batch operations:
```csharp
db.ChangeTracker.AutoDetectChangesEnabled = false;
// ... bulk operations ...
db.ChangeTracker.DetectChanges();
await db.SaveChangesAsync();
```

---

### 12. How do you use raw SQL in EF Core?

**A:**

```csharp
// FromSqlRaw — returns tracked entities (must select all columns)
var orders = await db.Orders
    .FromSqlRaw("SELECT * FROM orders WHERE total > {0}", threshold)
    .Include(o => o.Customer)
    .Where(o => o.Status == "Active")   // can compose LINQ on top
    .ToListAsync();

// FromSqlInterpolated — safe parameterization (no SQL injection)
var orders = await db.Orders
    .FromSqlInterpolated($"SELECT * FROM orders WHERE total > {threshold}")
    .ToListAsync();

// ExecuteSqlRaw — non-query (INSERT/UPDATE/DELETE/DDL)
await db.Database.ExecuteSqlRawAsync(
    "UPDATE orders SET status = {0} WHERE created_at < {1}",
    "Archived", cutoffDate);

// SqlQuery — arbitrary types (EF Core 7+)
var stats = await db.Database
    .SqlQuery<OrderStats>($"SELECT COUNT(*) as Count, SUM(total) as Revenue FROM orders")
    .ToListAsync();
```

---

### 13. How do you handle transactions in EF Core?

**A:**

```csharp
// Implicit transaction — SaveChanges wraps all changes automatically
db.Orders.Add(order);
db.Inventory.Update(item);
await db.SaveChangesAsync(); // one transaction

// Explicit transaction — for multiple SaveChanges calls or raw SQL
await using var tx = await db.Database.BeginTransactionAsync();
try
{
    db.Orders.Add(order);
    await db.SaveChangesAsync();

    db.Invoices.Add(invoice);
    await db.SaveChangesAsync();

    await tx.CommitAsync();
}
catch
{
    await tx.RollbackAsync();
    throw;
}

// Savepoints (EF Core 5+)
await tx.CreateSavepointAsync("before_inventory");
// ... if something fails:
await tx.RollbackToSavepointAsync("before_inventory");
```

---

### 14. What are compiled queries and when do you use them?

**A:** Compiled queries cache the LINQ → SQL translation, eliminating the per-call overhead:

```csharp
private static readonly Func<AppDbContext, int, Task<Order?>> GetOrderById =
    EF.CompileAsyncQuery((AppDbContext db, int id) =>
        db.Orders
          .Include(o => o.Items)
          .FirstOrDefault(o => o.Id == id));

// In handler — no translation overhead
var order = await GetOrderById(db, orderId);
```

**When to use:** High-frequency queries (per-request hot path) with fixed structure. Improves throughput by ~10-30% for complex queries.

---

### 15. What is `IEntityTypeConfiguration<T>` and why is it preferred over `OnModelCreating`?

**A:**

```csharp
// Avoid — everything in OnModelCreating becomes a huge method
protected override void OnModelCreating(ModelBuilder mb)
{
    mb.Entity<Order>().HasKey(o => o.Id);
    mb.Entity<Order>().Property(o => o.Total)...
    mb.Entity<Customer>()...
    // hundreds of lines
}

// Preferred — one class per entity, clean separation
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.ToTable("orders");
        b.HasKey(o => o.Id);
        b.Property(o => o.Total).HasColumnType("decimal(10,2)");
    }
}

// Register all configurations in the assembly at once
protected override void OnModelCreating(ModelBuilder mb) =>
    mb.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
```

---

### 16. What are owned entities and value objects?

**A:** Owned entities have no identity of their own — they belong to another entity and share its table:

```csharp
public class Address  // value object — no Id
{
    public string Street { get; init; } = "";
    public string City { get; init; } = "";
    public string PostalCode { get; init; } = "";
}

public class Customer
{
    public int Id { get; set; }
    public Address ShippingAddress { get; set; } = null!;
    public Address BillingAddress { get; set; } = null!;
}

// Configuration
b.OwnsOne(c => c.ShippingAddress, a =>
{
    a.Property(x => x.Street).HasColumnName("shipping_street");
    a.Property(x => x.City).HasColumnName("shipping_city");
});
b.OwnsOne(c => c.BillingAddress, a => { ... });
// Stored in the same customers table — no JOIN needed
```

---

### 17. What is a global query filter and how do you implement soft delete?

**A:**

```csharp
// In entity configuration
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.HasQueryFilter(o => !o.IsDeleted); // automatically applied to every query
    }
}

// Soft delete instead of hard delete
public class Order
{
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
}

// Override Remove to soft-delete
public override Task<int> SaveChangesAsync(CancellationToken ct = default)
{
    foreach (var entry in ChangeTracker.Entries<Order>().Where(e => e.State == EntityState.Deleted))
    {
        entry.State = EntityState.Modified;
        entry.Entity.IsDeleted = true;
        entry.Entity.DeletedAt = DateTime.UtcNow;
    }
    return base.SaveChangesAsync(ct);
}

// Bypass the filter when needed
var allOrders = await db.Orders.IgnoreQueryFilters().ToListAsync();
```

---

### 18. How do you handle concurrency conflicts in EF Core?

**A:**

```csharp
public class Order
{
    public int Id { get; set; }
    [Timestamp]
    public byte[] RowVersion { get; set; } = null!; // SQL Server
    // For PostgreSQL: use xmin column
}

// EF generates: UPDATE orders SET ... WHERE id = @id AND row_version = @rv
// 0 rows affected → throws DbUpdateConcurrencyException

try
{
    await db.SaveChangesAsync();
}
catch (DbUpdateConcurrencyException ex)
{
    var entry = ex.Entries.Single();
    var dbValues = await entry.GetDatabaseValuesAsync();

    if (dbValues == null)
        throw new InvalidOperationException("Entity was deleted");

    // Last-write-wins
    entry.OriginalValues.SetValues(dbValues);
    await db.SaveChangesAsync();

    // Or: merge business logic here before retrying
}
```

---

### 19. What is split query and when do you use it?

**A:** By default, EF Core loads Include chains in one large JOIN. Split queries issue separate SQL statements per collection:

```csharp
// Default — one big JOIN (can produce a cartesian explosion)
var orders = await db.Orders
    .Include(o => o.Items)
    .Include(o => o.Tags)
    .ToListAsync();
// SQL: one query with JOIN → many duplicate rows

// Split query — separate SQL per collection
var orders = await db.Orders
    .Include(o => o.Items)
    .Include(o => o.Tags)
    .AsSplitQuery()
    .ToListAsync();
// SQL: SELECT * FROM orders; SELECT * FROM items WHERE order_id IN (...); SELECT * FROM tags WHERE ...

// Set globally
services.AddDbContext<AppDbContext>(o =>
    o.UseNpgsql(cs, x => x.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery)));
```

**Use when:** Multiple collection Includes cause row explosion (product of rows × rows × rows).

---

### 20. How do you use EF Core interceptors?

**A:** Interceptors hook into EF Core's pipeline for cross-cutting concerns:

```csharp
public class SlowQueryInterceptor : DbCommandInterceptor
{
    private readonly ILogger _logger;
    private Stopwatch _sw = new();

    public override DbDataReader ReaderExecuted(
        DbCommand command,
        CommandExecutedEventData eventData,
        DbDataReader result)
    {
        if (eventData.Duration > TimeSpan.FromMilliseconds(500))
            _logger.LogWarning("Slow query ({ms}ms): {sql}", eventData.Duration.TotalMilliseconds, command.CommandText);
        return result;
    }
}

// Register
services.AddDbContext<AppDbContext>(o =>
    o.UseNpgsql(cs)
     .AddInterceptors(new SlowQueryInterceptor(logger)));
```

Other uses: audit logging, soft-delete enforcement, tenant isolation, query tagging.

---

## 🔴 Senior Level

---

### 21. How do you implement the repository pattern with EF Core — and should you?

**A:**

**Arguments for:**
- Decouples domain from EF Core
- Easier to unit test (mock the interface)
- Enforces query discipline

**Arguments against:**
- `DbSet<T>` already is a repository; `DbContext` already is a unit of work
- Wrapping EF Core often re-implements its features poorly
- Leaky abstraction — most repos end up exposing `IQueryable<T>` anyway

**Pragmatic approach:**

```csharp
// Thin repository — wraps only non-trivial queries
public interface IOrderRepository
{
    Task<Order?> GetWithItemsAsync(int id, CancellationToken ct);
    Task<List<Order>> GetPendingAsync(CancellationToken ct);
}

public class OrderRepository : IOrderRepository
{
    private readonly AppDbContext _db;
    public OrderRepository(AppDbContext db) => _db = db;

    public Task<Order?> GetWithItemsAsync(int id, CancellationToken ct) =>
        _db.Orders
           .AsNoTracking()
           .Include(o => o.Items).ThenInclude(i => i.Product)
           .FirstOrDefaultAsync(o => o.Id == id, ct);
}
```

If using CQRS with MediatR, you often don't need a repo at all — query handlers access `DbContext` directly.

---

### 22. How do you optimize EF Core for high-throughput write scenarios?

**A:**

```csharp
// 1. Bulk insert (EF Core 7+ built-in)
await db.BulkInsertAsync(orders); // via EFCore.BulkExtensions

// 2. ExecuteUpdate / ExecuteDelete — no entity load, no tracking
await db.Orders
    .Where(o => o.CreatedAt < cutoff)
    .ExecuteDeleteAsync();

// 3. Disable change tracking and auto-detect
db.ChangeTracker.AutoDetectChangesEnabled = false;

// 4. AddRange + single SaveChanges (batches statements)
db.Orders.AddRange(orders); // 1000 orders
await db.SaveChangesAsync(); // EF batches into ~42 statements of 42 rows each

// 5. Disable identity resolution for inserts
db.ChangeTracker.LazyLoadingEnabled = false;

// 6. Use a fresh DbContext per batch (avoid tracking overhead accumulation)
await using var scope = services.CreateAsyncScope();
var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
```

---

### 23. What is `DbContextFactory` and when do you use it?

**A:** `IDbContextFactory<T>` creates `DbContext` instances on demand — essential for non-request scopes:

```csharp
services.AddDbContextFactory<AppDbContext>(o => o.UseNpgsql(cs));

// In a Singleton or BackgroundService (can't inject Scoped DbContext)
public class OutboxRelay : BackgroundService
{
    private readonly IDbContextFactory<AppDbContext> _factory;

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            await using var db = await _factory.CreateDbContextAsync(ct);
            var messages = await db.OutboxMessages
                .Where(m => !m.Processed)
                .Take(50)
                .ToListAsync(ct);
            // ... publish and mark processed
        }
    }
}
```

---

### 24. How do you configure connection resiliency in EF Core?

**A:**

```csharp
services.AddDbContext<AppDbContext>(o =>
    o.UseNpgsql(cs, npgsql =>
    {
        npgsql.EnableRetryOnFailure(
            maxRetryCount: 5,
            maxRetryDelay: TimeSpan.FromSeconds(30),
            errorCodesToAdd: null);

        npgsql.CommandTimeout(30); // seconds
    })
    .UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking) // default no-tracking
);
```

**Caveat:** Retry on failure requires idempotent operations. Wrap non-idempotent SaveChanges in an explicit `IExecutionStrategy`:

```csharp
var strategy = db.Database.CreateExecutionStrategy();
await strategy.ExecuteAsync(async () =>
{
    await using var tx = await db.Database.BeginTransactionAsync();
    // ... work ...
    await tx.CommitAsync();
});
```

---

### 25. How do you implement multi-tenancy in EF Core?

**A:**

```csharp
// Row-level: global query filter per entity
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    private readonly ITenantContext _tenant;
    public OrderConfiguration(ITenantContext tenant) => _tenant = tenant;

    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.HasQueryFilter(o => o.TenantId == _tenant.CurrentTenantId);
    }
}

// Schema-level: switch search_path on connection open (PostgreSQL)
public class TenantDbContext : AppDbContext
{
    private readonly ITenantContext _tenant;

    protected override void OnConfiguring(DbContextOptionsBuilder o)
    {
        o.UseNpgsql(cs, n =>
            n.UseAdminDatabase("postgres"));
    }

    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        await Database.ExecuteSqlRawAsync($"SET search_path = '{_tenant.Schema}'", ct);
        return await base.SaveChangesAsync(ct);
    }
}
```

---

### 26. What are value converters and how do you use them?

**A:** Value converters transform values between the CLR type and the database column:

```csharp
// Encrypt PII in the database
public class EncryptedConverter : ValueConverter<string, string>
{
    public EncryptedConverter(IDataProtector protector) : base(
        v => protector.Protect(v),       // CLR → DB
        v => protector.Unprotect(v))     // DB → CLR
    { }
}

// Store enum as string
b.Property(u => u.Status)
 .HasConversion<string>();

// Store JSON as column
b.Property(o => o.Metadata)
 .HasConversion(
     v => JsonSerializer.Serialize(v, null as JsonSerializerOptions),
     v => JsonSerializer.Deserialize<Dictionary<string, string>>(v, null as JsonSerializerOptions)!);

// Custom Money type
b.Property(o => o.Price)
 .HasConversion(
     m => m.Amount,
     v => new Money(v, "USD"));
```

---

### 27. How do you implement table-per-hierarchy (TPH), table-per-type (TPT), and table-per-concrete-type (TPC)?

**A:**

```csharp
public abstract class Payment { public int Id { get; set; } }
public class CreditCardPayment : Payment { public string Last4 { get; set; } = ""; }
public class BankTransferPayment : Payment { public string IBAN { get; set; } = ""; }

// TPH (default) — all in one table with Discriminator column
b.UseTphMappingStrategy(); // single payments table

// TPT — one table per type, joined
b.UseTptMappingStrategy(); // payments + credit_card_payments + bank_transfer_payments

// TPC (EF Core 7+) — one table per concrete type, no joins
b.UseTpcMappingStrategy(); // credit_card_payments + bank_transfer_payments only
```

| Strategy | Tables | Join | Best for |
|----------|--------|------|----------|
| TPH | 1 | None | Sparse hierarchies, simple queries |
| TPT | N | JOIN per level | Normalized schema, few subtypes |
| TPC | N-1 | None | Many subtypes, many rows, polymorphic queries rare |

---

## 🏛️ Architect Level

---

### 28. How do you design EF Core for a CQRS architecture?

**A:**

```csharp
// Write side — uses full DbContext with tracking, domain model, events
public class CreateOrderHandler : ICommandHandler<CreateOrderCommand>
{
    private readonly AppDbContext _db;

    public async Task Handle(CreateOrderCommand cmd, CancellationToken ct)
    {
        var order = Order.Create(cmd.CustomerId, cmd.Lines);
        _db.Orders.Add(order);
        await _db.SaveChangesAsync(ct);
        // Raise domain events, publish to outbox, etc.
    }
}

// Read side — separate ReadDbContext: AsNoTracking, no domain model, optimized DTOs
public class ReadDbContext : DbContext
{
    public ReadDbContext(DbContextOptions<ReadDbContext> opts) : base(opts) { }

    protected override void OnConfiguring(DbContextOptionsBuilder o)
    {
        o.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTrackingWithIdentityResolution);
    }
}

public class GetOrdersHandler : IQueryHandler<GetOrdersQuery, List<OrderDto>>
{
    private readonly ReadDbContext _db;

    public Task<List<OrderDto>> Handle(GetOrdersQuery q, CancellationToken ct) =>
        _db.Database
           .SqlQuery<OrderDto>($"""
               SELECT o.id, o.total, c.name as customer_name
               FROM orders o
               JOIN customers c ON c.id = o.customer_id
               WHERE o.status = {q.Status}
               """)
           .ToListAsync(ct);
}
```

---

### 29. How do you implement the outbox pattern with EF Core?

**A:**

```csharp
public class OutboxMessage
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Type { get; set; } = "";
    public string Payload { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public bool Processed { get; set; }
}

// Atomically save business data + outbox message
public async Task Handle(CreateOrderCommand cmd, CancellationToken ct)
{
    var order = Order.Create(cmd.CustomerId, cmd.Lines);
    db.Orders.Add(order);
    db.OutboxMessages.Add(new OutboxMessage
    {
        Type = nameof(OrderCreated),
        Payload = JsonSerializer.Serialize(new OrderCreated(order.Id))
    });
    await db.SaveChangesAsync(ct); // atomic transaction
}

// BackgroundService polls outbox and publishes
// SELECT ... FOR UPDATE SKIP LOCKED → process and mark Processed = true
```

---

### 30. How do you handle EF Core in a microservices architecture?

**A:**

**Each service owns its schema:**
```csharp
// Order service DbContext — knows nothing about Inventory models
public class OrderDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public DbSet<OutboxMessage> OutboxMessages { get; set; }
    // No cross-service entities
}
```

**Cross-service data:** Never join across services. Maintain local read models (projections) updated via events:
```csharp
// Inventory service publishes ProductPriceChanged event
// Order service consumes it and updates its local ProductSnapshot table
public class ProductSnapshot
{
    public int ProductId { get; set; }   // FK exists only in this service
    public decimal Price { get; set; }   // local copy, updated via events
    public string Name { get; set; } = "";
}
```

**Migration strategy:** Run `dotnet ef database update` as a Kubernetes Job before rolling out new pods. Migrations must always be backward-compatible (expand-contract).
