# 🔌 Dapper — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is Dapper and how does it differ from EF Core?

**A:** Dapper is a lightweight "micro-ORM" — a thin extension over `IDbConnection` that handles SQL result mapping without generating SQL for you.

| | Dapper | EF Core |
|--|--------|---------|
| SQL | You write it | Generated |
| Mapping | Automatic | Automatic |
| Change tracking | ❌ None | ✅ Full |
| Migrations | ❌ None | ✅ Full |
| Learning curve | Low | Higher |
| Performance | Very high | High (with tuning) |
| Best for | Read-heavy, complex queries, reports | CRUD-heavy, domain modeling |

---

### 2. How do you execute a basic query with Dapper?

**A:**

```csharp
using Dapper;
using System.Data;
using Npgsql;

await using var conn = new NpgsqlConnection(connectionString);

// Query — returns IEnumerable<T>
var users = await conn.QueryAsync<User>("SELECT id, name, email FROM users");

// QueryFirst — throws if no rows
var user = await conn.QueryFirstAsync<User>(
    "SELECT * FROM users WHERE id = @Id", new { Id = 42 });

// QueryFirstOrDefault — returns default(T) if no rows
var user = await conn.QueryFirstOrDefaultAsync<User>(
    "SELECT * FROM users WHERE id = @Id", new { Id = 42 });

// QuerySingle — throws if not exactly one row
var count = await conn.QuerySingleAsync<int>("SELECT COUNT(*) FROM users");

// Execute — INSERT / UPDATE / DELETE, returns rows affected
int affected = await conn.ExecuteAsync(
    "UPDATE users SET name = @Name WHERE id = @Id",
    new { Name = "Alice", Id = 42 });
```

---

### 3. How does parameterization work in Dapper?

**A:** Always use parameters — never string interpolation (SQL injection risk):

```csharp
// Anonymous object — most common
await conn.QueryAsync<User>(
    "SELECT * FROM users WHERE status = @Status AND age >= @MinAge",
    new { Status = "active", MinAge = 18 });

// Dictionary
await conn.ExecuteAsync(
    "UPDATE users SET name = @name WHERE id = @id",
    new Dictionary<string, object> { ["name"] = "Bob", ["id"] = 1 });

// Strongly typed model as parameter
var cmd = new UpdateUserCommand { Name = "Alice", Id = 42 };
await conn.ExecuteAsync("UPDATE users SET name = @Name WHERE id = @Id", cmd);

// DynamicParameters — for output/return params
var p = new DynamicParameters();
p.Add("@Name", "Alice");
p.Add("@Id", dbType: DbType.Int32, direction: ParameterDirection.Output);
await conn.ExecuteAsync("INSERT INTO users (name) VALUES (@Name); SELECT @Id = SCOPE_IDENTITY()", p);
int newId = p.Get<int>("@Id");
```

---

### 4. How do you map query results to nested objects?

**A:** Using Dapper's multi-mapping feature:

```csharp
public class Order { public int Id; public Customer Customer; public List<OrderItem> Items; }
public class Customer { public int Id; public string Name; }

// splitOn tells Dapper where to split the result set into types
var orders = await conn.QueryAsync<Order, Customer, Order>(
    @"SELECT o.id, o.total, c.id, c.name
      FROM orders o
      JOIN customers c ON c.id = o.customer_id",
    (order, customer) =>
    {
        order.Customer = customer;
        return order;
    },
    splitOn: "id"  // second "id" column signals start of Customer
);
```

---

### 5. How do you handle multiple result sets?

**A:**

```csharp
var sql = @"
    SELECT * FROM orders WHERE customer_id = @Id;
    SELECT * FROM customers WHERE id = @Id;
";

using var multi = await conn.QueryMultipleAsync(sql, new { Id = customerId });

var orders   = (await multi.ReadAsync<Order>()).ToList();
var customer = await multi.ReadFirstAsync<Customer>();
```

Useful for loading a parent record and its children in one round-trip instead of two separate queries.

---

### 6. How do you execute stored procedures with Dapper?

**A:**

```csharp
// Simple stored procedure
var users = await conn.QueryAsync<User>(
    "sp_GetActiveUsers",
    commandType: CommandType.StoredProcedure);

// With parameters
var result = await conn.QueryAsync<Order>(
    "sp_GetOrdersByCustomer",
    new { CustomerId = 42, Status = "Active" },
    commandType: CommandType.StoredProcedure);

// With output parameters
var p = new DynamicParameters();
p.Add("@CustomerId", 42);
p.Add("@TotalRevenue", dbType: DbType.Decimal, direction: ParameterDirection.Output);
await conn.ExecuteAsync("sp_GetCustomerRevenue", p, commandType: CommandType.StoredProcedure);
decimal revenue = p.Get<decimal>("@TotalRevenue");
```

---

## 🟡 Mid Level

---

### 7. How do you handle transactions in Dapper?

**A:**

```csharp
await using var conn = new NpgsqlConnection(connectionString);
await conn.OpenAsync();
await using var tx = await conn.BeginTransactionAsync();

try
{
    await conn.ExecuteAsync(
        "INSERT INTO orders (customer_id, total) VALUES (@CustomerId, @Total)",
        new { CustomerId = 1, Total = 99.99 },
        transaction: tx); // pass the transaction!

    await conn.ExecuteAsync(
        "UPDATE inventory SET stock = stock - @Qty WHERE product_id = @ProductId",
        new { Qty = 1, ProductId = 5 },
        transaction: tx);

    await tx.CommitAsync();
}
catch
{
    await tx.RollbackAsync();
    throw;
}
```

Always pass `transaction:` to every Dapper call within a transaction.

---

### 8. How do you insert a list of records efficiently?

**A:**

```csharp
var orders = new List<Order> { ... };

// Dapper passes list as multiple parameter sets — one INSERT per row
await conn.ExecuteAsync(
    "INSERT INTO orders (customer_id, total, status) VALUES (@CustomerId, @Total, @Status)",
    orders);

// Better: use table-valued parameters (SQL Server) or unnest (PostgreSQL)
// PostgreSQL bulk insert with unnest
await conn.ExecuteAsync(@"
    INSERT INTO orders (customer_id, total)
    SELECT * FROM unnest(@CustomerIds::int[], @Totals::decimal[])",
    new
    {
        CustomerIds = orders.Select(o => o.CustomerId).ToArray(),
        Totals = orders.Select(o => o.Total).ToArray()
    });

// For very large datasets, use COPY (PostgreSQL) or SqlBulkCopy (SQL Server)
```

---

### 9. What are Dapper's `TypeHandler`s and when do you use them?

**A:** Type handlers convert between .NET types and database types that Dapper doesn't map natively:

```csharp
// Map Guid to/from PostgreSQL uuid
public class GuidTypeHandler : SqlMapper.TypeHandler<Guid>
{
    public override Guid Parse(object value) => new Guid((string)value);
    public override void SetValue(IDbDataParameter p, Guid value)
    {
        p.DbType = DbType.String;
        p.Value = value.ToString();
    }
}

// Map JSON column to a .NET object
public class JsonTypeHandler<T> : SqlMapper.TypeHandler<T>
{
    public override T Parse(object value) =>
        JsonSerializer.Deserialize<T>((string)value)!;

    public override void SetValue(IDbDataParameter p, T? value)
    {
        p.Value = JsonSerializer.Serialize(value);
        p.DbType = DbType.String;
    }
}

// Register at startup
SqlMapper.AddTypeHandler(new GuidTypeHandler());
SqlMapper.AddTypeHandler(new JsonTypeHandler<Dictionary<string, string>>());
```

---

### 10. How do you build dynamic queries safely with Dapper?

**A:**

```csharp
// BAD — string concatenation → SQL injection
var sql = $"SELECT * FROM users WHERE name = '{name}'";

// GOOD — use DynamicParameters for runtime-built queries
var where = new List<string>();
var p = new DynamicParameters();

if (!string.IsNullOrEmpty(name))
{
    where.Add("name ILIKE @Name");
    p.Add("Name", $"%{name}%");
}
if (status.HasValue)
{
    where.Add("status = @Status");
    p.Add("Status", status.Value);
}

var sql = "SELECT * FROM users";
if (where.Count > 0)
    sql += " WHERE " + string.Join(" AND ", where);

var users = await conn.QueryAsync<User>(sql, p);
```

---

### 11. How do you handle nullable types and NULL values?

**A:**

```csharp
public class User
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string? Bio { get; set; }      // nullable string
    public DateTime? DeletedAt { get; set; } // nullable DateTime
    public int? ManagerId { get; set; }   // nullable FK
}

// Dapper maps NULL → null for nullable types automatically
var users = await conn.QueryAsync<User>("SELECT id, name, bio, deleted_at, manager_id FROM users");
// bio = null if DB value is NULL
// DeletedAt = null if DB value is NULL

// Null parameters
await conn.ExecuteAsync(
    "UPDATE users SET manager_id = @ManagerId WHERE id = @Id",
    new { ManagerId = (int?)null, Id = 42 }); // sends NULL to DB
```

---

### 12. How do you map to non-default column names?

**A:** Dapper maps by matching property names to column names (case-insensitive). For mismatches:

```csharp
// Option 1: use SQL aliases
var users = await conn.QueryAsync<User>(
    "SELECT user_id AS Id, user_name AS Name FROM users");

// Option 2: use ColumnAttribute with Dapper.Contrib or a custom mapper
[Table("users")]
public class User
{
    [Key]
    [Column("user_id")]
    public int Id { get; set; }

    [Column("user_name")]
    public string Name { get; set; } = "";
}

// Option 3: custom type map
var mapper = new CustomPropertyTypeMap(typeof(User), (type, column) =>
    type.GetProperties().FirstOrDefault(prop =>
        prop.GetCustomAttributes<ColumnAttribute>()
            .Any(a => a.Name == column)));
SqlMapper.SetTypeMap(typeof(User), mapper);
```

---

## 🔴 Senior Level

---

### 13. How do you implement a repository pattern with Dapper?

**A:**

```csharp
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(int id, CancellationToken ct);
    Task<List<Order>> GetByCustomerAsync(int customerId, CancellationToken ct);
    Task<int> CreateAsync(Order order, IDbTransaction? tx = null, CancellationToken ct = default);
}

public class OrderRepository : IOrderRepository
{
    private readonly IDbConnection _conn;

    public OrderRepository(IDbConnection conn) => _conn = conn;

    public Task<Order?> GetByIdAsync(int id, CancellationToken ct) =>
        _conn.QueryFirstOrDefaultAsync<Order>(new CommandDefinition(
            "SELECT * FROM orders WHERE id = @Id",
            new { Id = id },
            cancellationToken: ct));

    public async Task<int> CreateAsync(Order order, IDbTransaction? tx = null, CancellationToken ct = default)
    {
        return await _conn.ExecuteScalarAsync<int>(new CommandDefinition(
            "INSERT INTO orders (customer_id, total) VALUES (@CustomerId, @Total) RETURNING id",
            order,
            transaction: tx,
            cancellationToken: ct));
    }
}

// Register connection as Scoped — one per request
services.AddScoped<IDbConnection>(_ => new NpgsqlConnection(connectionString));
services.AddScoped<IOrderRepository, OrderRepository>();
```

---

### 14. How do you combine Dapper and EF Core in the same application?

**A:** A common pattern — EF Core for writes, Dapper for complex reads (CQRS):

```csharp
// Write side: EF Core — handles domain model, change tracking, migrations
public class CreateOrderHandler
{
    private readonly AppDbContext _db;
    public async Task Handle(CreateOrderCommand cmd, CancellationToken ct)
    {
        var order = Order.Create(cmd.CustomerId, cmd.Items);
        _db.Orders.Add(order);
        await _db.SaveChangesAsync(ct);
    }
}

// Read side: Dapper — raw SQL, optimized DTOs, complex joins
public class GetOrderSummaryHandler
{
    private readonly IDbConnection _conn;
    public async Task<OrderSummaryDto> Handle(GetOrderSummaryQuery q, CancellationToken ct)
    {
        return await _conn.QueryFirstAsync<OrderSummaryDto>(new CommandDefinition(@"
            SELECT o.id, o.total, o.status,
                   c.name AS customer_name,
                   COUNT(i.id) AS item_count,
                   SUM(i.quantity * p.price) AS line_total
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            JOIN order_items i ON i.order_id = o.id
            JOIN products p ON p.id = i.product_id
            WHERE o.id = @Id
            GROUP BY o.id, o.total, o.status, c.name",
            new { q.Id }, cancellationToken: ct));
    }
}
```

---

### 15. How do you handle connection management and pooling with Dapper?

**A:** Dapper doesn't manage connections — you do. ADO.NET connection pooling handles the actual connections:

```csharp
// Open/close for every call — pooling re-uses physical connections
public async Task<User?> GetUserAsync(int id)
{
    await using var conn = new NpgsqlConnection(_connectionString);
    // conn.OpenAsync() is optional — Dapper opens if needed
    return await conn.QueryFirstOrDefaultAsync<User>(
        "SELECT * FROM users WHERE id = @Id", new { Id = id });
    // conn disposed → returned to pool
}

// Connection pool tuning in connection string
var csb = new NpgsqlConnectionStringBuilder(connectionString)
{
    MaxPoolSize = 50,
    MinPoolSize = 5,
    ConnectionIdleLifetime = 300,  // seconds
    ConnectionPruningInterval = 10
};

// Reuse connection for multiple calls in a unit of work
await using var conn = new NpgsqlConnection(connectionString);
await conn.OpenAsync();
// ... multiple Dapper calls on the same connection
```

---

### 16. What is `CommandDefinition` and why use it?

**A:** `CommandDefinition` bundles all call parameters including `CancellationToken` — makes async queries properly cancellable:

```csharp
var cmd = new CommandDefinition(
    commandText: "SELECT * FROM orders WHERE status = @Status",
    parameters: new { Status = "pending" },
    transaction: currentTransaction,
    commandTimeout: 30,
    commandType: CommandType.Text,
    cancellationToken: cancellationToken
);

var orders = await conn.QueryAsync<Order>(cmd);
```

Without `CommandDefinition`, Dapper's `QueryAsync` overloads don't accept `CancellationToken` directly — always use it in production code.

---

## 🏛️ Architect Level

---

### 17. When should you choose Dapper over EF Core in a system design?

**A:**

**Choose Dapper when:**
- Your read queries are complex (multi-table reports, window functions, CTEs)
- You need maximum query control (EXPLAIN ANALYZE driven optimization)
- Performance is critical and you can't afford ORM overhead
- Working with a legacy schema that doesn't map cleanly to an ORM
- CQRS read side — queries never change domain state

**Choose EF Core when:**
- You need migrations and schema management
- Domain model is complex (aggregates, value objects, relationships)
- Team is less comfortable with raw SQL
- Write path requires change tracking and concurrency handling

**Hybrid (most production systems):**
```
EF Core → writes (INSERT, UPDATE, DELETE), migrations
Dapper  → reads (reports, dashboards, search, exports)
```

---

### 18. How do you implement the query object pattern with Dapper?

**A:**

```csharp
// Each query is a self-contained class
public class GetOrdersQuery
{
    public int? CustomerId { get; init; }
    public string? Status { get; init; }
    public DateOnly? From { get; init; }
    public DateOnly? To { get; init; }
    public int Page { get; init; } = 1;
    public int PageSize { get; init; } = 20;
}

public class GetOrdersQueryHandler
{
    private readonly IDbConnection _conn;

    public async Task<(List<OrderDto> Items, int Total)> HandleAsync(GetOrdersQuery q, CancellationToken ct)
    {
        var where = new List<string>();
        var p = new DynamicParameters();

        if (q.CustomerId.HasValue) { where.Add("o.customer_id = @CustomerId"); p.Add("CustomerId", q.CustomerId); }
        if (!string.IsNullOrEmpty(q.Status)) { where.Add("o.status = @Status"); p.Add("Status", q.Status); }
        if (q.From.HasValue) { where.Add("o.created_at::date >= @From"); p.Add("From", q.From); }
        if (q.To.HasValue)   { where.Add("o.created_at::date <= @To");   p.Add("To",   q.To); }

        var whereClause = where.Count > 0 ? "WHERE " + string.Join(" AND ", where) : "";
        p.Add("Offset", (q.Page - 1) * q.PageSize);
        p.Add("Limit",  q.PageSize);

        var sql = $@"
            SELECT COUNT(*) OVER() AS Total, o.id, o.total, o.status, c.name AS CustomerName
            FROM orders o JOIN customers c ON c.id = o.customer_id
            {whereClause}
            ORDER BY o.created_at DESC
            OFFSET @Offset LIMIT @Limit";

        var rows = (await _conn.QueryAsync<(int Total, OrderDto Order)>(sql, p)).ToList();
        return (rows.Select(r => r.Order).ToList(), rows.FirstOrDefault().Total);
    }
}
```
