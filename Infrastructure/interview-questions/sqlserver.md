# 🪟 SQL Server — Interview Questions

---

### 1. What makes SQL Server distinct from other relational databases?

**A:** Microsoft SQL Server is an enterprise RDBMS with tight Windows/Azure integration and some unique features:

- **T-SQL:** Transact-SQL — SQL Server's proprietary SQL dialect with procedural extensions
- **Always On Availability Groups:** Enterprise HA with automatic failover and readable secondaries
- **Columnstore indexes:** In-memory columnar storage for analytics (OLAP on OLTP data)
- **In-Memory OLTP (Hekaton):** Lock-free, latch-free memory-optimized tables
- **Query Store:** Built-in plan history and regression detection (first RDBMS to have it)
- **Temporal tables:** System-versioned tables with automatic history tracking
- **SSRS/SSAS/SSIS:** Reporting, Analysis Services, Integration Services as part of the ecosystem
- **Azure SQL Database:** PaaS version — managed, auto-tuning, hyperscale

---

### 2. What are the SQL Server transaction isolation levels?

**A:**

```sql
-- Standard isolation levels
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;  -- dirty reads allowed
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;    -- default (locks released after each statement)
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;   -- range locks prevent phantom reads partially
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;      -- strictest, range locks on all reads

-- SQL Server-specific: Snapshot isolation (MVCC-based)
-- Enable at database level:
ALTER DATABASE MyDB SET ALLOW_SNAPSHOT_ISOLATION ON;
ALTER DATABASE MyDB SET READ_COMMITTED_SNAPSHOT ON;  -- makes READ COMMITTED use MVCC

SET TRANSACTION ISOLATION LEVEL SNAPSHOT;  -- now uses row versions, not locks

-- RCSI (Read Committed Snapshot Isolation) — most important for modern apps:
-- Readers don't block writers, writers don't block readers
-- Enabled via READ_COMMITTED_SNAPSHOT ON
-- Used by default in Azure SQL Database
```

```sql
-- Check current isolation level
SELECT CASE transaction_isolation_level
    WHEN 0 THEN 'Unspecified'
    WHEN 1 THEN 'Read Uncommitted'
    WHEN 2 THEN 'Read Committed'
    WHEN 3 THEN 'Repeatable Read'
    WHEN 4 THEN 'Serializable'
    WHEN 5 THEN 'Snapshot'
END AS isolation_level
FROM sys.dm_exec_sessions
WHERE session_id = @@SPID;
```

---

### 3. What are execution plans and how do you read them?

**A:**

```sql
-- View estimated execution plan (no execution)
SET SHOWPLAN_XML ON;
SELECT * FROM orders WHERE customer_id = 42;
SET SHOWPLAN_XML OFF;

-- View actual execution plan (executes the query)
SET STATISTICS PROFILE ON;
SELECT * FROM orders WHERE customer_id = 42;
SET STATISTICS PROFILE OFF;

-- In SSMS: Ctrl+M (actual plan) or Ctrl+L (estimated plan)

-- Key operators to understand:
-- Index Seek   → specific rows via index (good)
-- Index Scan   → scans entire index (may be ok for small tables, bad for large)
-- Table Scan   → no usable index (heap scan - bad)
-- Key Lookup   → extra lookup to heap after index seek (cover the index)
-- Nested Loop  → good for small result sets
-- Hash Match   → good for large unsorted sets (high memory)
-- Merge Join   → good for pre-sorted sets

-- Warning signs:
-- Implicit conversions (orange warning icon) → index can't be used
-- Spills to TempDB → insufficient memory for sort/hash
-- Missing index recommendation → SQL Server is suggesting an index

-- Statistics I/O and TIME
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
SELECT * FROM orders WHERE customer_id = 42;
SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
-- Output: "Table 'orders'. Scan count 0, logical reads 3, physical reads 0"
-- logical reads >> 1000 for a simple query → missing index or bad plan
```

---

### 4. What is the Query Store?

**A:** Query Store captures query text, execution plans, and runtime statistics — automatically detects and allows fixing plan regressions.

```sql
-- Enable Query Store
ALTER DATABASE MyDB SET QUERY_STORE = ON;
ALTER DATABASE MyDB SET QUERY_STORE (
    OPERATION_MODE = READ_WRITE,
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30),
    DATA_FLUSH_INTERVAL_SECONDS = 900,
    INTERVAL_LENGTH_MINUTES = 60,
    MAX_STORAGE_SIZE_MB = 1000,
    QUERY_CAPTURE_MODE = AUTO  -- only captures significant queries
);

-- Find regressed queries (plans that got slower)
SELECT TOP 10
    qt.query_sql_text,
    qsp.plan_id,
    rs.avg_duration / 1000 AS avg_duration_ms,
    rs.execution_count,
    rs.avg_logical_io_reads
FROM sys.query_store_query_text qt
JOIN sys.query_store_query q ON q.query_text_id = qt.query_text_id
JOIN sys.query_store_plan qsp ON qsp.query_id = q.query_id
JOIN sys.query_store_runtime_stats rs ON rs.plan_id = qsp.plan_id
ORDER BY rs.avg_duration DESC;

-- Force a specific plan (fix regressions)
EXEC sp_query_store_force_plan @query_id = 42, @plan_id = 7;

-- Unforce a plan
EXEC sp_query_store_unforce_plan @query_id = 42, @plan_id = 7;

-- Automatic plan correction (SQL Server 2017+)
ALTER DATABASE MyDB SET AUTOMATIC_TUNING (FORCE_LAST_GOOD_PLAN = ON);
```

---

### 5. What are columnstore indexes?

**A:** Columnstore indexes store data by column rather than row — dramatically faster for analytics (OLAP) queries on OLTP tables.

```sql
-- Nonclustered columnstore index (on existing heap/rowstore table)
-- Doesn't change primary storage — adds a columnar copy
CREATE NONCLUSTERED COLUMNSTORE INDEX NCI_Orders_Analytics
ON orders (customer_id, product_id, total, created_at, region);

-- Clustered columnstore index (replaces heap — primary storage is columnar)
-- Cannot have other clustered index — table IS the columnstore
CREATE CLUSTERED COLUMNSTORE INDEX CCI_Orders
ON orders;

-- Why columnstore is fast for analytics:
-- 1. Batch mode execution: processes ~900 rows at a time vs one row at a time
-- 2. Column compression: similar values compress 10x (only read needed columns)
-- 3. Segment elimination: each segment stores min/max — skip non-matching segments
-- 4. SIMD vectorized processing on modern CPUs

-- Real-world speedup for analytical queries: 10x-100x vs rowstore

-- Updateable columnstore (SQL Server 2014+):
-- Delta store: INSERTs go to rowstore delta store
-- Background tuple mover: compresses delta store into columnstore segments

-- Check columnstore health
SELECT object_name(object_id) AS table_name,
       state_description, row_count, size_in_bytes
FROM sys.column_store_row_groups
WHERE object_id = OBJECT_ID('orders');
```

---

### 6. What are SQL Server locking and blocking concepts?

**A:**

```sql
-- Lock types
-- Shared (S): SELECT — compatible with other S locks
-- Exclusive (X): INSERT/UPDATE/DELETE — incompatible with all others
-- Update (U): before modifying — compatible with S, exclusive with U and X
-- Intent locks: IS, IX, SIX — indicate intent at higher granularity
-- Schema locks: Sch-S (schema stability), Sch-M (schema modification)

-- Lock granularity: row → page → extent → table → database

-- View current locks and blocking
SELECT
    r.session_id,
    r.blocking_session_id,
    r.wait_type,
    r.wait_time / 1000.0 AS wait_sec,
    r.logical_reads,
    LEFT(t.text, 100) AS query_text,
    r.status
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.blocking_session_id > 0;

-- Deadlock detection
-- SQL Server auto-detects and kills the cheapest victim
-- Trace flag 1222 or Extended Events for deadlock graph

-- Deadlock info from system health session
SELECT
    xdr.value('@timestamp', 'datetime2') AS deadlock_time,
    xdr.query('.') AS deadlock_graph
FROM (
    SELECT CAST(target_data AS XML) AS target_data
    FROM sys.dm_xe_session_targets t
    JOIN sys.dm_xe_sessions s ON s.address = t.event_session_address
    WHERE s.name = 'system_health' AND t.target_name = 'ring_buffer'
) AS data
CROSS APPLY target_data.nodes('//RingBufferTarget/event[@name="xml_deadlock_report"]') AS XEventData(xdr);

-- Minimize locking
-- Use RCSI (READ_COMMITTED_SNAPSHOT)
-- Keep transactions short
-- Access tables in consistent order
-- Use appropriate isolation level
-- Index foreign keys (prevent table locks on parent)
```

---

### 7. What are Temporal Tables?

**A:** System-versioned temporal tables automatically maintain full history of data changes.

```sql
-- Create temporal table
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name NVARCHAR(100),
    salary DECIMAL(10,2),
    department NVARCHAR(50),
    -- System-maintained period columns
    valid_from DATETIME2 GENERATED ALWAYS AS ROW START NOT NULL,
    valid_to   DATETIME2 GENERATED ALWAYS AS ROW END   NOT NULL,
    PERIOD FOR SYSTEM_TIME (valid_from, valid_to)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.employees_history));

-- Normal DML — history recorded automatically
UPDATE employees SET salary = 95000 WHERE id = 1;
DELETE FROM employees WHERE id = 5;

-- Query as of a specific point in time
SELECT * FROM employees
FOR SYSTEM_TIME AS OF '2024-01-15 09:00:00';

-- Query changes in a period
SELECT * FROM employees
FOR SYSTEM_TIME BETWEEN '2024-01-01' AND '2024-06-30';

-- All versions of a row
SELECT * FROM employees
FOR SYSTEM_TIME ALL
WHERE id = 1
ORDER BY valid_from;

-- Use cases:
-- Audit trail (who changed what, when)
-- Point-in-time recovery of specific rows
-- SCD (Slowly Changing Dimensions) in data warehouses
-- Debugging data corruption issues
```

---

### 8. What are Always On Availability Groups?

**A:**

```sql
-- Always On AG: enterprise HA and DR solution
-- Replica set of SQL Server instances sharing a group of databases

-- Components:
-- Primary replica: read-write
-- Secondary replicas: readable (optional), synchronous or asynchronous

-- Create Availability Group
CREATE AVAILABILITY GROUP [MyAG]
WITH (
    AUTOMATED_BACKUP_PREFERENCE = SECONDARY,  -- offload backups to secondary
    DB_FAILOVER = ON,                         -- failover if any DB goes offline
    REQUIRED_SYNCHRONIZED_SECONDARIES_TO_COMMIT = 1  -- synchronous commit count
)
FOR DATABASE [MyDB]
REPLICA ON
    N'SQL01' WITH (
        ENDPOINT_URL = N'TCP://sql01.domain.com:5022',
        AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,  -- no data loss failover
        FAILOVER_MODE = AUTOMATIC,
        READABLE_SECONDARY = NO
    ),
    N'SQL02' WITH (
        ENDPOINT_URL = N'TCP://sql02.domain.com:5022',
        AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
        FAILOVER_MODE = AUTOMATIC,
        READABLE_SECONDARY = YES              -- can offload reads here
    ),
    N'SQL03' WITH (
        ENDPOINT_URL = N'TCP://sql03.domain.com:5022',
        AVAILABILITY_MODE = ASYNCHRONOUS_COMMIT,  -- DR site, possible data loss
        FAILOVER_MODE = MANUAL,
        READABLE_SECONDARY = YES
    );

-- Connect via listener (transparent failover)
-- Connection string: Server=MyAGListener,1433;Database=MyDB;ApplicationIntent=ReadOnly
-- ApplicationIntent=ReadOnly → routes to readable secondary

-- Monitor AG health
SELECT ag.name, rs.role_desc, rs.operational_state_desc,
       rs.synchronization_health_desc, rs.last_commit_time
FROM sys.dm_hadr_availability_replica_states rs
JOIN sys.availability_groups ag ON ag.group_id = rs.group_id;
```

---

### 9. What are common T-SQL specific features?

**A:**

```sql
-- TOP with TIES
SELECT TOP 10 WITH TIES customer_id, SUM(total) AS revenue
FROM orders GROUP BY customer_id
ORDER BY revenue DESC;
-- Returns more than 10 if there are ties at position 10

-- OUTPUT clause — return affected rows
DECLARE @deleted TABLE (id INT, email NVARCHAR(255));
DELETE FROM users
OUTPUT DELETED.id, DELETED.email INTO @deleted
WHERE last_login < DATEADD(YEAR, -2, GETDATE());

SELECT * FROM @deleted;  -- what was deleted

-- MERGE (upsert)
MERGE INTO orders AS target
USING new_orders AS source ON target.order_id = source.order_id
WHEN MATCHED THEN
    UPDATE SET target.status = source.status,
               target.updated_at = GETDATE()
WHEN NOT MATCHED BY TARGET THEN
    INSERT (order_id, customer_id, total, status)
    VALUES (source.order_id, source.customer_id, source.total, source.status)
WHEN NOT MATCHED BY SOURCE THEN
    DELETE;

-- TRY...CATCH error handling
BEGIN TRY
    BEGIN TRANSACTION;
        UPDATE accounts SET balance -= 100 WHERE id = 1;
        UPDATE accounts SET balance += 100 WHERE id = 2;
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    DECLARE @msg NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @sev INT = ERROR_SEVERITY();
    RAISERROR(@msg, @sev, 1);
END CATCH;

-- STRING_AGG (SQL Server 2017+)
SELECT customer_id, STRING_AGG(product_name, ', ') WITHIN GROUP (ORDER BY product_name) AS products
FROM order_items GROUP BY customer_id;

-- TRIM, CONCAT_WS, TRANSLATE (2017+)
SELECT TRIM('  hello  ');
SELECT CONCAT_WS(', ', street, city, state, zip);  -- null-safe concatenation
```

---

### 10. What is In-Memory OLTP (Hekaton)?

**A:**

```sql
-- Memory-optimized tables: stored in memory, lock-free, latch-free
-- Massive throughput for high-frequency insert/update workloads

-- Memory-optimized filegroup (required)
ALTER DATABASE MyDB ADD FILEGROUP InMemory CONTAINS MEMORY_OPTIMIZED_DATA;
ALTER DATABASE MyDB ADD FILE (NAME='InMemory', FILENAME='C:\data\inmem') TO FILEGROUP InMemory;

-- Create memory-optimized table
CREATE TABLE orders_inmem (
    id BIGINT IDENTITY PRIMARY KEY NONCLUSTERED,
    customer_id INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    status NVARCHAR(20) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    INDEX ix_customer NONCLUSTERED (customer_id),
    INDEX ix_status HASH (status) WITH (BUCKET_COUNT = 1024)  -- hash index
)
WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA);

-- DURABILITY options:
-- SCHEMA_AND_DATA: fully durable (survives restart)
-- SCHEMA_ONLY: data lost on restart (for staging, temp data — extreme speed)

-- Natively compiled stored procedures (compiled to machine code)
CREATE PROCEDURE usp_insert_order
    @customer_id INT, @total DECIMAL(10,2)
WITH NATIVE_COMPILATION, SCHEMABINDING
AS BEGIN ATOMIC WITH (TRANSACTION ISOLATION LEVEL = SNAPSHOT, LANGUAGE = N'English')
    INSERT INTO dbo.orders_inmem (customer_id, total, status)
    VALUES (@customer_id, @total, 'pending');
END;

-- Performance: 10x-30x faster than disk-based for high-contention workloads
-- Limitations: no ALTER TABLE, limited T-SQL subset, FOREIGN KEY references limited
```

---

### 11. What are SQL Server DMVs and how do you use them?

**A:** Dynamic Management Views (DMVs) expose internal state for monitoring and troubleshooting.

```sql
-- Most important DMVs:

-- Top resource-consuming queries
SELECT TOP 20
    qs.execution_count,
    qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
    qs.total_elapsed_time / qs.execution_count / 1000 AS avg_elapsed_ms,
    qs.total_worker_time / qs.execution_count / 1000 AS avg_cpu_ms,
    LEFT(qt.text, 200) AS query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY qs.total_logical_reads DESC;

-- Missing indexes
SELECT TOP 20
    ROUND(migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans), 0) AS score,
    mid.statement AS table_name,
    mid.equality_columns, mid.inequality_columns, mid.included_columns
FROM sys.dm_db_missing_index_groups mig
JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details mid ON mid.index_handle = mig.index_handle
ORDER BY score DESC;

-- Wait statistics (what is SQL Server waiting on)
SELECT TOP 20
    wait_type, waiting_tasks_count,
    wait_time_ms / 1000.0 AS wait_sec,
    max_wait_time_ms / 1000.0 AS max_wait_sec,
    signal_wait_time_ms / 1000.0 AS signal_wait_sec
FROM sys.dm_os_wait_stats
WHERE wait_type NOT IN ('SLEEP_TASK','BROKER_TO_FLUSH','BROKER_TASK_STOP',
                         'CLR_AUTO_EVENT','DISPATCHER_QUEUE_SEMAPHORE',
                         'FT_IFTS_SCHEDULER_IDLE_WAIT','HADR_WORK_QUEUE',
                         'SQLTRACE_BUFFER_FLUSH','REQUEST_FOR_DEADLOCK_SEARCH',
                         'RESOURCE_QUEUE','SERVER_IDLE_CHECK','SLEEP_DBSTARTUP',
                         'SLEEP_DBRECOVER','SLEEP_MASTERDBREADY','SLEEP_MASTERMDREADY',
                         'SLEEP_MASTERUPGRADED','SLEEP_MSDBSTARTUP','SLEEP_SYSTEMTASK',
                         'SLEEP_TEMPDBSTARTUP','SNI_HTTP_ACCEPT','SP_SERVER_DIAGNOSTICS_SLEEP',
                         'WAITFOR','XE_DISPATCHER_WAIT','XE_TIMER_EVENT')
ORDER BY wait_time_ms DESC;

-- Buffer pool usage (which tables are in cache)
SELECT
    OBJECT_NAME(i.object_id) AS table_name,
    i.name AS index_name,
    COUNT(*) * 8 / 1024 AS cached_mb
FROM sys.dm_os_buffer_descriptors bd
JOIN sys.allocation_units au ON au.allocation_unit_id = bd.allocation_unit_id
JOIN sys.partitions p ON p.partition_id = au.container_id
JOIN sys.indexes i ON i.object_id = p.object_id AND i.index_id = p.index_id
WHERE bd.database_id = DB_ID()
GROUP BY i.object_id, i.name
ORDER BY cached_mb DESC;
```

---

### 12. What are SQL Server indexing best practices?

**A:**

```sql
-- Clustered index: the table IS the index (B-tree ordered by key)
-- Every table should have a clustered index (otherwise: heap = unordered)
-- Best clustered index key: narrow, unique, static, ever-increasing (IDENTITY)
-- BAD clustered on GUID: random inserts cause page splits → fragmentation

-- Nonclustered index: separate B-tree, leaf contains row locator (RID or clustered key)
-- Include columns: avoid key lookups for common queries
CREATE NONCLUSTERED INDEX IX_Orders_Customer
ON orders (customer_id, created_at DESC)
INCLUDE (status, total);  -- cover the SELECT columns, no lookup needed

-- Filtered index: partial index for subsets
CREATE NONCLUSTERED INDEX IX_Orders_Active
ON orders (customer_id, created_at)
WHERE status IN ('pending', 'processing');

-- Index fragmentation
SELECT
    OBJECT_NAME(ips.object_id) AS table_name,
    i.name AS index_name,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
JOIN sys.indexes i ON i.object_id = ips.object_id AND i.index_id = ips.index_id
WHERE ips.avg_fragmentation_in_percent > 10
ORDER BY ips.avg_fragmentation_in_percent DESC;

-- Fix fragmentation
-- < 30% fragmented: REORGANIZE (online, page-level defrag)
ALTER INDEX IX_Orders_Customer ON orders REORGANIZE;

-- > 30% fragmented: REBUILD (offline by default, ONLINE=ON for Enterprise)
ALTER INDEX IX_Orders_Customer ON orders REBUILD WITH (ONLINE = ON);
ALTER INDEX ALL ON orders REBUILD;  -- rebuild all indexes on table
```

---

### 13. What is SQL Server Agent and how is it used?

**A:**

```sql
-- SQL Server Agent: job scheduler for automating DBA and ETL tasks

-- Create a job
EXEC msdb.dbo.sp_add_job @job_name = N'Nightly_Maintenance';

-- Add job step
EXEC msdb.dbo.sp_add_jobstep
    @job_name = N'Nightly_Maintenance',
    @step_name = N'Rebuild Indexes',
    @command = N'
        EXEC dbo.IndexOptimize
            @Databases = ''ALL_DATABASES'',
            @FragmentationLow = NULL,
            @FragmentationMedium = ''INDEX_REORGANIZE,INDEX_REBUILD_ONLINE'',
            @FragmentationHigh = ''INDEX_REBUILD_ONLINE,INDEX_REBUILD_OFFLINE'',
            @FragmentationLevel1 = 5,
            @FragmentationLevel2 = 30';

-- Schedule
EXEC msdb.dbo.sp_add_schedule
    @schedule_name = N'Daily_2AM',
    @freq_type = 4,           -- daily
    @freq_interval = 1,
    @active_start_time = 020000;  -- 2:00 AM

EXEC msdb.dbo.sp_attach_schedule
    @job_name = N'Nightly_Maintenance',
    @schedule_name = N'Daily_2AM';

-- Monitor job history
SELECT j.name, jh.step_name, jh.run_status,
       msdb.dbo.agent_datetime(jh.run_date, jh.run_time) AS run_datetime,
       jh.message
FROM msdb.dbo.sysjobhistory jh
JOIN msdb.dbo.sysjobs j ON j.job_id = jh.job_id
ORDER BY run_datetime DESC;
```

---

### 14. What are SQL Server security best practices?

**A:**

```sql
-- 1. Principle of least privilege
CREATE LOGIN app_login WITH PASSWORD = 'StrongPass123!';
CREATE USER app_user FOR LOGIN app_login;

-- Grant only what's needed (not db_owner!)
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT EXECUTE ON usp_process_order TO app_user;

-- 2. Avoid SA and Windows admin logins for applications
-- Use dedicated service accounts with minimal permissions

-- 3. Transparent Data Encryption (TDE) — encrypt data at rest
USE master;
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'MasterKeyPass!';
CREATE CERTIFICATE TDECert WITH SUBJECT = 'TDE Certificate';

USE MyDB;
CREATE DATABASE ENCRYPTION KEY
    WITH ALGORITHM = AES_256
    ENCRYPTION BY SERVER CERTIFICATE TDECert;
ALTER DATABASE MyDB SET ENCRYPTION ON;

-- 4. Always Encrypted — encrypt sensitive columns (app-level, DB never sees plaintext)
-- Client drivers handle encryption/decryption
-- Column master key stored in Windows Certificate Store, Azure Key Vault, etc.

-- 5. Row-Level Security
CREATE FUNCTION dbo.fn_tenant_predicate(@tenant_id INT)
RETURNS TABLE WITH SCHEMABINDING
AS RETURN (SELECT 1 AS result WHERE @tenant_id = CAST(SESSION_CONTEXT(N'tenant_id') AS INT));

CREATE SECURITY POLICY TenantPolicy
ADD FILTER PREDICATE dbo.fn_tenant_predicate(tenant_id) ON dbo.orders;
-- Now: SELECT * FROM orders automatically filtered by tenant_id in SESSION_CONTEXT

-- 6. Audit
CREATE SERVER AUDIT MyAudit TO FILE (FILEPATH = 'C:\Audit\');
CREATE DATABASE AUDIT SPECIFICATION MyDbAudit
FOR SERVER AUDIT MyAudit
ADD (SELECT, INSERT, UPDATE, DELETE ON dbo.orders BY public);
ALTER DATABASE AUDIT SPECIFICATION MyDbAudit WITH (STATE = ON);
```
