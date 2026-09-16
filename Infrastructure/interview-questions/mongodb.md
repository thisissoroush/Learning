# 🍃 MongoDB — Interview Questions

---

### 1. What is MongoDB and what is its data model?

**A:** MongoDB is a document-oriented NoSQL database that stores data as BSON (Binary JSON) documents in collections.

```
Relational          MongoDB
─────────────────   ──────────────────
Database         →  Database
Table            →  Collection
Row              →  Document (BSON)
Column           →  Field
JOIN             →  Embedded document or $lookup
Primary key      →  _id (auto-generated ObjectId if not specified)
Schema           →  Flexible (schema-less, but schema validation available)

Example document:
{
  "_id": ObjectId("64f1a2b3c4d5e6f7a8b9c0d1"),
  "name": "Alice Smith",
  "email": "alice@example.com",
  "age": 30,
  "address": {              // embedded document
    "street": "123 Main St",
    "city": "New York",
    "zip": "10001"
  },
  "orders": [               // array of embedded documents
    { "id": "ord-1", "total": 99.99, "status": "shipped" },
    { "id": "ord-2", "total": 149.99, "status": "pending" }
  ],
  "tags": ["premium", "verified"],
  "created_at": ISODate("2024-01-15T10:30:00Z")
}
```

---

### 2. What is the difference between embedded documents and references?

**A:**

**Embedded (denormalized):** Related data stored inside the parent document.
```javascript
// Embed when:
// - Data is always accessed together (order + its items)
// - Data doesn't grow unboundedly (max N items)
// - No need to query embedded data independently
{
  "_id": ObjectId("..."),
  "order_id": "ord-123",
  "items": [
    { "product_id": "p1", "name": "Widget", "qty": 2, "price": 29.99 },
    { "product_id": "p2", "name": "Gadget", "qty": 1, "price": 49.99 }
  ]
}
// One read = full order with items — no joins
```

**References (normalized):** Store ID, look up separately.
```javascript
// Reference when:
// - Data is large or unbounded (all comments on a post)
// - Data is accessed independently
// - Data is shared between multiple documents
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("user-123"),  // reference to users collection
  "product_ids": [ObjectId("p1"), ObjectId("p2")]  // references
}
// Requires $lookup or application-level join
```

---

### 3. How do CRUD operations work in MongoDB?

**A:**

```javascript
// INSERT
db.orders.insertOne({ customer: "Alice", total: 99.99, status: "pending" });
db.orders.insertMany([
  { customer: "Bob", total: 49.99 },
  { customer: "Carol", total: 149.99 }
]);

// FIND
db.orders.findOne({ _id: ObjectId("...") });
db.orders.find({ status: "pending", total: { $gt: 50 } });
db.orders.find(
  { customer: "Alice" },                        // filter
  { total: 1, status: 1, _id: 0 }              // projection (1=include, 0=exclude)
).sort({ created_at: -1 }).limit(10).skip(20);

// UPDATE
db.orders.updateOne(
  { _id: ObjectId("...") },
  { $set: { status: "shipped" }, $currentDate: { updated_at: true } }
);
db.orders.updateMany(
  { status: "pending", created_at: { $lt: ISODate("2024-01-01") } },
  { $set: { status: "expired" } }
);

// Atomic update operators:
// $set, $unset, $inc, $mul, $min, $max, $push, $pull, $addToSet, $pop

// Replace vs Update
db.orders.replaceOne({ _id: id }, newDocument);  // replaces entire doc
db.orders.updateOne({ _id: id }, { $set: fields }); // partial update

// DELETE
db.orders.deleteOne({ _id: ObjectId("...") });
db.orders.deleteMany({ status: "expired", created_at: { $lt: cutoff } });

// Upsert — update if exists, insert if not
db.orders.updateOne(
  { order_id: "ord-123" },
  { $set: { status: "shipped" }, $setOnInsert: { created_at: new Date() } },
  { upsert: true }
);
```

---

### 4. How does the aggregation pipeline work?

**A:** The aggregation pipeline processes documents through a series of stages, each transforming the data.

```javascript
// Revenue by category with top products
db.orders.aggregate([
  // Stage 1: Filter
  { $match: {
    status: "completed",
    created_at: { $gte: ISODate("2024-01-01") }
  }},

  // Stage 2: Unwind array into separate documents
  { $unwind: "$items" },

  // Stage 3: Group and aggregate
  { $group: {
    _id: "$items.category",
    total_revenue: { $sum: { $multiply: ["$items.price", "$items.qty"] } },
    order_count: { $sum: 1 },
    avg_item_price: { $avg: "$items.price" },
    products: { $addToSet: "$items.product_id" }
  }},

  // Stage 4: Add computed field
  { $addFields: {
    product_count: { $size: "$products" }
  }},

  // Stage 5: Sort
  { $sort: { total_revenue: -1 } },

  // Stage 6: Limit
  { $limit: 10 },

  // Stage 7: Reshape output
  { $project: {
    category: "$_id",
    total_revenue: { $round: ["$total_revenue", 2] },
    order_count: 1,
    product_count: 1,
    _id: 0
  }}
]);

// $lookup — left outer join (like SQL JOIN)
db.orders.aggregate([
  { $lookup: {
    from: "customers",
    localField: "customer_id",
    foreignField: "_id",
    as: "customer"
  }},
  { $unwind: "$customer" },
  { $project: { total: 1, "customer.name": 1, "customer.email": 1 }}
]);
```

---

### 5. What are MongoDB indexes and how do you use them?

**A:**

```javascript
// Single field index
db.orders.createIndex({ customer_id: 1 });      // ascending
db.orders.createIndex({ created_at: -1 });       // descending

// Compound index — field order matters
db.orders.createIndex({ customer_id: 1, status: 1, created_at: -1 });
// Supports queries on: (customer_id), (customer_id, status), (customer_id, status, created_at)

// Unique index
db.users.createIndex({ email: 1 }, { unique: true });

// Sparse index — only indexes documents that have the field
db.users.createIndex({ phone: 1 }, { sparse: true });

// Partial index — only indexes documents matching a filter
db.orders.createIndex(
  { customer_id: 1, created_at: -1 },
  { partialFilterExpression: { status: "active" } }
);
// Only indexes active orders — smaller, faster

// TTL index — auto-delete documents after a time
db.sessions.createIndex({ created_at: 1 }, { expireAfterSeconds: 3600 });
// Documents deleted 1 hour after created_at

// Text index — full-text search
db.products.createIndex({ name: "text", description: "text" });
db.products.find({ $text: { $search: "iphone camera" } },
                 { score: { $meta: "textScore" } })
           .sort({ score: { $meta: "textScore" } });

// Wildcard index — index all fields in a document
db.products.createIndex({ "attributes.$**": 1 });

// Check index usage
db.orders.find({ customer_id: 42 }).explain("executionStats");
// Look for: IXSCAN (good) vs COLLSCAN (bad/missing index)

// List indexes
db.orders.getIndexes();

// Drop index
db.orders.dropIndex("customer_id_1");
```

---

### 6. What is the MongoDB query optimizer and how do you analyze queries?

**A:**

```javascript
// explain() — analyze query execution
db.orders.find({ customer_id: 42, status: "pending" })
         .explain("executionStats");

// Key fields in output:
// queryPlanner.winningPlan.stage: IXSCAN (good) | COLLSCAN (bad)
// executionStats.nReturned: docs returned
// executionStats.totalDocsExamined: docs scanned (high vs nReturned = missing index)
// executionStats.executionTimeMillis: total time
// executionStats.indexesUsed: which indexes used

// Examples of what to look for:
// nReturned: 5, totalDocsExamined: 5 → perfect (index covers exactly)
// nReturned: 5, totalDocsExamined: 100000 → bad (full scan, add index)

// Profile slow queries
db.setProfilingLevel(1, { slowms: 100 });  // profile queries > 100ms
db.system.profile.find().sort({ ts: -1 }).limit(10);

// db.currentOp() — see currently running operations
db.currentOp({ active: true, secs_running: { $gt: 5 } });

// Kill long-running operation
db.killOp(opId);
```

---

### 7. How does MongoDB replication work?

**A:**

```
Replica Set — group of mongod instances maintaining same dataset:
  - Primary: accepts all writes
  - Secondaries (N): replicate from primary via oplog (operation log)
  - Arbiter (optional): votes in elections but holds no data

Election process (Raft-based):
  Primary fails → secondaries detect heartbeat timeout
  → Election → majority vote → new primary
  → Requires: 3+ nodes (or 2 data + 1 arbiter)

Read preferences:
  primary:            reads only from primary (default — consistent)
  primaryPreferred:   primary if available, else secondary
  secondary:          only from secondaries (possibly stale)
  secondaryPreferred: secondary if available, else primary
  nearest:            lowest network latency
```

```javascript
// Write concern — how many nodes must acknowledge write
db.orders.insertOne(
  { customer_id: 1, total: 99.99 },
  { writeConcern: { w: "majority", j: true, wtimeout: 5000 } }
  // w: "majority" — majority of nodes must acknowledge
  // j: true — must be written to journal (durable)
  // wtimeout: 5000ms — timeout if nodes don't ack
);

// Read concern — data consistency for reads
db.orders.find({ status: "pending" })
         .readConcern("majority");  // reads only majority-committed data
         // "local" = default, may read uncommitted data
         // "linearizable" = strongest, reads most recent majority-committed

// Oplog — capped collection that records all write operations
use local
db.oplog.rs.find().sort({ $natural: -1 }).limit(5);
// ts: timestamp, op: "i"nsert/"u"pdate/"d"elete, ns: namespace, o: document
```

---

### 8. What is MongoDB sharding?

**A:**

```
Sharded cluster components:
  mongos (router): client connects here, routes to correct shard
  Config servers:  store cluster metadata (3 config servers)
  Shards:          each shard is a replica set

Shard key selection (critical decision):
  Once set, VERY difficult to change
  Must provide:
    ✅ High cardinality (many distinct values)
    ✅ Even distribution (no hotspots)
    ✅ Queries include shard key (targeted queries, not scatter-gather)
```

```javascript
// Enable sharding
sh.enableSharding("mydb");

// Shard a collection
sh.shardCollection("mydb.orders", { customer_id: "hashed" });  // hashed = even distribution
sh.shardCollection("mydb.orders", { region: 1, customer_id: 1 }); // range = good for range queries

// Check shard distribution
sh.status();
db.orders.getShardDistribution();

// Targeted vs scatter-gather queries
// Targeted (includes shard key) — goes to ONE shard
db.orders.find({ customer_id: 42, status: "pending" });

// Scatter-gather (no shard key) — goes to ALL shards — expensive!
db.orders.find({ status: "pending" });

// Zone sharding — pin data to specific shards (geo, compliance)
sh.addShardTag("shard-eu", "EU");
sh.addTagRange("mydb.orders",
  { region: "EU", customer_id: MinKey },
  { region: "EU", customer_id: MaxKey },
  "EU"
);
```

---

### 9. What are MongoDB transactions?

**A:**

```javascript
// Multi-document ACID transactions (requires replica set, MongoDB 4.0+)
// Sharded transactions: MongoDB 4.2+

const session = client.startSession();

try {
  session.startTransaction({
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority" }
  });

  // Both operations either succeed or both fail
  await db.collection("accounts").updateOne(
    { _id: fromAccountId },
    { $inc: { balance: -amount } },
    { session }
  );

  await db.collection("accounts").updateOne(
    { _id: toAccountId },
    { $inc: { balance: amount } },
    { session }
  );

  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}

// When NOT to use transactions:
// - Single document operations are atomic by default (no transaction needed)
// - Embedded documents handle many "transaction" needs
// - Transactions have performance overhead — design schema to avoid them
```

---

### 10. What is schema design in MongoDB and what are the patterns?

**A:**

```javascript
// Pattern 1: Attribute pattern — variable attributes without sparse indexes
// Instead of: { color: "red", size: "L", material: "cotton" } (3 sparse indexes)
{
  attributes: [
    { key: "color",    value: "red" },
    { key: "size",     value: "L" },
    { key: "material", value: "cotton" }
  ]
}
// One index on { "attributes.key": 1, "attributes.value": 1 }

// Pattern 2: Bucket pattern — time-series data
// Instead of one document per measurement (millions of docs):
{
  sensor_id: "sensor-1",
  date: ISODate("2024-01-15"),
  readings: [                     // 24 hourly readings in one document
    { hour: 0, temp: 22.5 },
    { hour: 1, temp: 22.1 },
    // ...
    { hour: 23, temp: 23.0 }
  ],
  min_temp: 21.8, max_temp: 24.2, avg_temp: 22.5  // pre-computed
}

// Pattern 3: Computed pattern — pre-compute expensive aggregations
// Instead of computing average on every read:
{
  product_id: "p1",
  total_reviews: 1523,
  total_rating: 6854,
  avg_rating: 4.5           // pre-computed: update on each new review
}

// Pattern 4: Outlier pattern — handle documents with unusually large arrays
{
  movie_id: "avengers",
  fans: [...],              // first 1000 fans embedded
  has_extras: true          // flag
}
// fans_overflow collection for the rest

// Pattern 5: Extended reference — embed frequently accessed fields
// Instead of joining every time to get customer name:
{
  order_id: "ord-1",
  customer_id: ObjectId("..."),  // reference for full customer data
  customer_name: "Alice Smith",  // denormalized for display (snapshot at order time)
  customer_email: "alice@x.com"  // accepts that this may become stale
}
```

---

### 11. What are common MongoDB gotchas and anti-patterns?

**A:**

```javascript
// 1. Growing arrays — NEVER store unbounded arrays in a document
// BAD: store all comments in a post document (grows forever → 16MB doc limit)
{ post_id: 1, comments: [{...}, {...}, ...] }  // anti-pattern!
// GOOD: comments as a separate collection with post_id reference

// 2. $where and JavaScript evaluation (never in production)
db.orders.find({ $where: "this.total > 100" });  // scans every doc, slow, injection risk

// 3. Not using indexes for sort
db.orders.find().sort({ created_at: -1 });
// Without index on created_at: loads ALL docs into memory to sort → slow/OOM

// 4. Using _id as ObjectId but querying with string
db.orders.findOne({ _id: "64f1a2b3..." });  // WRONG — returns null
db.orders.findOne({ _id: ObjectId("64f1a2b3...") });  // CORRECT

// 5. count() vs countDocuments()
db.orders.count({ status: "pending" });          // may use metadata, can be inaccurate
db.orders.countDocuments({ status: "pending" }); // always accurate

// 6. Unbounded $in queries
db.orders.find({ customer_id: { $in: allCustomerIds } });  // 100k IDs = very slow

// 7. Not projecting fields (over-fetching)
db.orders.find({ status: "pending" });  // returns ALL fields including large ones
db.orders.find({ status: "pending" }, { total: 1, created_at: 1 });  // project needed fields only

// 8. Schema-less ≠ Schema-free — validate your schema
db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customer_id", "total", "status"],
      properties: {
        total: { bsonType: "double", minimum: 0 },
        status: { enum: ["pending", "confirmed", "shipped", "delivered"] }
      }
    }
  },
  validationAction: "error"  // reject invalid documents
});
```

---

### 12. How do you monitor MongoDB?

**A:**

```javascript
// Server status — overall health
db.serverStatus();
db.serverStatus().connections;  // current, available, totalCreated
db.serverStatus().opcounters;   // insert, query, update, delete, getmore, command
db.serverStatus().wiredTiger;   // cache hit rate, dirty bytes

// Collection stats
db.orders.stats();
// storageSize, totalIndexSize, count, avgObjSize

// Index usage stats
db.orders.aggregate([{ $indexStats: {} }]);
// Shows: which indexes are used, how many times

// Current operations
db.currentOp();
db.currentOp({ active: true, secs_running: { $gt: 10 } });

// Replica set lag
rs.printReplicationInfo();   // oplog window
rs.printSecondaryReplicationInfo();  // per-secondary lag

// Key metrics to monitor:
// connections.current         — alert near max (ulimit)
// opcounters.query            — queries per second trend
// repl.lag                    — replica lag (alert > 10s)
// wiredTiger.cache.bytes in cache / maximum bytes  — cache pressure
// globalLock.currentQueue.total — queued operations (alert > 0 sustained)
// asserts.regular             — assertion failures (alert > 0)
```
