# Chapter 14 — Databases

> *"You don't need to be a DBA, but every engineer should understand SQL, normalization, and when to reach for NoSQL."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Database questions appear in both technical interviews and system design rounds. Key topics: **SQL queries, normalization, indexing, and SQL vs. NoSQL trade-offs**.

---

## 🗄️ SQL Fundamentals

```sql
-- Core query structure:
SELECT columns FROM table
  JOIN other ON condition
  WHERE row_filter
  GROUP BY column
  HAVING group_filter
  ORDER BY column LIMIT n;

-- Users with more than 3 orders:
SELECT u.name, COUNT(o.id) AS cnt
FROM Users u JOIN Orders o ON u.id = o.user_id
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 3
ORDER BY cnt DESC;

-- Students with NO exam scores (LEFT JOIN anti-pattern):
SELECT s.name FROM Students s
LEFT JOIN Exams e ON s.id = e.student_id
WHERE e.id IS NULL;

-- Second highest salary:
SELECT MAX(salary) FROM Employees
WHERE salary < (SELECT MAX(salary) FROM Employees);
```

---

## 🔗 JOIN Types

```
INNER JOIN:   Rows matching in BOTH tables (intersection)
LEFT JOIN:    All left rows + matched right (null if no match)
FULL OUTER:   All rows from both sides (null where no match)
CROSS JOIN:   Cartesian product — dangerous on large tables!
SELF JOIN:    Table joined to itself (find manager vs. employee)

-- Employees earning more than their manager:
SELECT e.name FROM Employees e
JOIN Employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

---

## 📐 Normalization

```
1NF: Atomic values, no repeating groups
  ❌ items column: "apple, banana"
  ✅ Separate row per item

2NF: No partial dependencies on composite primary key
  ❌ (order_id, product_id) → product_name
     (product_name depends only on product_id)
  ✅ Separate Products table

3NF: No transitive dependencies (non-key → non-key)
  ❌ employee_id → dept_id → dept_name
  ✅ Separate Departments table

DENORMALIZATION: Intentional 3NF violation for READ speed.
  Store dept_name on employee row to skip the JOIN.
  Used in data warehouses, high-traffic read systems.
```

---

## ⚡ Indexing

```
Index = B-tree data structure for fast column lookups.
CREATE INDEX idx_users_email ON Users(email);
→ WHERE email = 'x' goes from O(n) to O(log n).

WHEN INDEX HELPS:     Frequent WHERE/JOIN/ORDER BY columns
WHEN INDEX HURTS:     Write-heavy tables, low-cardinality columns

COMPOSITE INDEX (last_name, first_name):
  ✅ WHERE last_name = 'Smith'
  ✅ WHERE last_name = 'Smith' AND first_name = 'John'
  ❌ WHERE first_name = 'John'  ← violates leftmost prefix rule
```

---

## 🆚 SQL vs. NoSQL

```
SQL:                              NoSQL:
  Structured, schema-enforced       Flexible, schema-free
  ACID transactions                 BASE (eventually consistent)
  Complex JOINs and queries         Simple key-based lookups
  Vertical scaling                  Horizontal scaling built-in
  PostgreSQL, MySQL                 Cassandra, MongoDB, Redis

CHOOSE SQL:  Relational data, ACID, complex reporting
CHOOSE NoSQL: Massive scale, flexible schema, key-value patterns

NoSQL types:
  Key-Value:  Redis, DynamoDB   → caching, sessions
  Document:   MongoDB            → flexible JSON records
  Column:     Cassandra          → time-series, IoT
  Graph:      Neo4j              → social networks, fraud
```

---

## 💡 Key Takeaways

| Concept | Key Rule |
|---------|---------|
| JOIN types | INNER = intersection; LEFT = left + nullable right |
| WHERE vs. HAVING | WHERE filters rows; HAVING filters groups |
| 3NF | Eliminate partial + transitive dependencies |
| Denormalization | Trade integrity for read speed; use deliberately |
| Indexing | Speeds reads, slows writes; high-cardinality columns only |
| Composite index | Leftmost prefix rule: must start from first column |
| SQL vs NoSQL | ACID + relations → SQL; scale + flexibility → NoSQL |

---

*[← Chapter 13](20-java.md) | [Back to Index](../README.md) | [Chapter 15 — Threads & Locks →](22-threads-and-locks.md)*
