# 🏗️ Infrastructure — Interview Questions

Interview questions for core infrastructure and DevOps topics, covering containers, orchestration, messaging, caching, and search.

---

## 📂 Contents

| Topic | File | Questions |
|-------|------|-----------|
| 🐳 Docker | [docker.md](./docker.md) | Images, containers, Dockerfile, multi-stage, networking, volumes, security, CI/CD |
| ⚓ Kubernetes | [kubernetes.md](./kubernetes.md) | Pods, Deployments, Services, Ingress, HPA, RBAC, Helm, zero-downtime, operators |
| 🐇 RabbitMQ | [rabbitmq.md](./rabbitmq.md) | Exchanges, queues, DLX, clustering, quorum queues, retry, outbox pattern |
| 📨 Apache Kafka | [kafka.md](./kafka.md) | Topics, partitions, consumer groups, exactly-once, Streams, Connect, Schema Registry |
| 🔴 Redis | [redis.md](./redis.md) | Data types, persistence, replication, Sentinel, Cluster, distributed locks, Streams |
| 🔍 Elasticsearch | [elasticsearch.md](./elasticsearch.md) | Indexing, search queries, aggregations, ILM, ELK stack, vector search |

## Databases

| Topic | File | Questions |
|-------|------|-----------|
| 🐘 PostgreSQL | [postgresql.md](./postgresql.md) | MVCC, VACUUM, indexes (all types), EXPLAIN ANALYZE, partitioning, replication, PgBouncer |
| 🍃 MongoDB | [mongodb.md](./mongodb.md) | Documents, aggregation pipeline, indexes, schema patterns, replication, sharding, transactions |
| 🪟 SQL Server | [sqlserver.md](./sqlserver.md) | Execution plans, Query Store, columnstore, Temporal tables, Always On AG, In-Memory OLTP, DMVs |

---

## 🔑 Key Themes

- **Containers first** — Docker images are immutable, layered, and reproducible
- **Declarative configuration** — Kubernetes YAML describes desired state; the control loop reconciles reality
- **At-least-once by default** — most messaging systems require idempotent consumers
- **Partition = unit of parallelism** — Kafka partitions and Redis Cluster slots both determine scalability
- **Near real-time** — Elasticsearch indexes within ~1s by default (configurable)
- **Memory is the bottleneck** — Redis eviction policies, JVM heap, ES heap all need careful tuning
