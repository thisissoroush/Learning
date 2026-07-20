# Chapter 14 — Managing Analytical Data

> *"Operational data runs the business today. Analytical data shapes decisions about tomorrow."*

---

## 🎯 Core Concept

**Operational data** (OLTP) is what your services read and write to run the business right now. **Analytical data** (OLAP) is used by data scientists and business analysts to understand trends, make predictions, and guide strategy. As distributed architectures scale, keeping these two concerns separate — and managing the analytical side properly — becomes a major architectural concern.

---

## 📊 Operational vs. Analytical Data

```
Operational Data (OLTP):               Analytical Data (OLAP):
─────────────────────────              ─────────────────────────
Current state of the business          Historical trends and patterns
Transactional (insert/update/delete)   Read-heavy (SELECT, aggregations)
Millisecond latency required           Minutes/hours acceptable
Normalized (3NF relational)            Denormalized (star/snowflake schema)
Owned by microservices                 Aggregated from many services
Small record sets accessed             Large datasets scanned

Examples: orders, inventory,           Examples: sales trends, customer
payments, user profiles                behavior analysis, forecasting
```

---

## 🏛️ Evolution of Analytical Data Approaches

### Approach 1: The Data Warehouse

```
Multiple source systems → ETL → Centralized Data Warehouse → BI Reports

Source Systems:
  CRM, ERP, Order Management, Inventory...
         ↓ (ETL: Extract, Transform, Load)
  ┌─────────────────────────┐
  │      Data Warehouse     │ ← analysts query here
  │  (Star schema, denorm.) │
  └─────────────────────────┘
```

**Benefits:**
- Single source of truth for analytics
- Optimized for complex analytical queries
- Well-understood technology (decades of tooling)

**Shortcomings:**
- ETL pipelines are brittle and slow (often batch, not real-time)
- Data warehouse teams become bottlenecks
- Schema changes in source systems break ETL pipelines
- Centralized — all analytics depends on one team maintaining it

---

### Approach 2: The Data Lake

```
All raw data dumped into a central repository (often S3/HDFS):

Source Systems → Raw Data Lake (all formats) → Analytics/ML
                 (JSON, CSV, Parquet, logs...)

"Store first, figure out later"
```

**Benefits:**
- Extremely flexible — accept any data format
- Cheap storage (object storage)
- Great for ML/AI workloads
- No ETL required upfront

**Shortcomings:**
- Can become a **"Data Swamp"** — raw data with no governance
- Without catalog/schema management, data becomes unusable
- No clear ownership — who is responsible for data quality?
- Complex to query without significant transformation work

---

### Approach 3: The Data Mesh

The **Data Mesh** is the modern approach that aligns with distributed architectures.

**Core Idea:** Treat analytical data as a product, owned by the domain team that produces it.

```
Traditional approach:
  Domain Teams produce data → Central Data Team manages analytics

Data Mesh approach:
  Domain Teams produce AND manage their own analytical data products
  Central platform provides infrastructure (but not the data itself)
```

---

## 🕸️ Data Mesh Principles

### 1. Domain-Oriented Ownership

```
Order Domain:         Owns "Order Analytics" data product
Customer Domain:      Owns "Customer Behavior" data product
Inventory Domain:     Owns "Inventory Trends" data product

Each domain team is responsible for:
  - Quality of their analytical data
  - Schema and documentation
  - SLAs for data freshness
  - Access control
```

### 2. Data as a Product

```
Each domain produces a well-defined data product:
  ✓ Documented schema
  ✓ Defined quality SLAs (freshness, completeness, accuracy)
  ✓ Discoverable (in a data catalog)
  ✓ Versioned (consumers aren't broken by changes)
  ✓ Accessible (self-service via query or API)
```

### 3. Self-Serve Data Infrastructure

```
Central Platform Team provides:
  ✓ Storage infrastructure (data lake/warehouse)
  ✓ Data catalog (discovery and lineage)
  ✓ Query engines (Spark, Presto, etc.)
  ✓ Pipeline tooling
  ✓ Access control framework

Domain teams USE this platform — they don't build it.
```

### 4. Federated Governance

```
Standards are set centrally, applied locally:
  Central: data format standards, PII handling rules, retention policies
  Domain: applies standards to their own data products
  
  Not "central team enforces everything"
  Not "every domain does whatever they want"
```

---

## 📦 Data Product Quantum

A **Data Product Quantum (DPQ)** is the architecture quantum for analytical data — the independently deployable unit of analytical data:

```
Data Product Quantum:
  ┌─────────────────────────────────────────────┐
  │  Order Analytics Data Product               │
  │  ┌────────────────────────────────────────┐ │
  │  │ Source: Order Service (operational DB) │ │
  │  │ Transform: aggregation pipeline        │ │
  │  │ Store: Parquet files in data lake      │ │
  │  │ Serve: SQL endpoint + REST API         │ │
  │  │ Quality: SLA: 99% fresh within 1 hour  │ │
  │  └────────────────────────────────────────┘ │
  └─────────────────────────────────────────────┘
```

---

## 🔗 Data Mesh and Architecture Quantum

Each domain's data product forms its own quantum — independently:
- Owned by the domain team
- Deployed on its own schedule
- Versioned separately from operational services
- Consumed independently by analytical consumers

```
Operational Quanta:        Analytical Quanta (DPQs):
  Order Service       →      Order Analytics DPQ
  Customer Service    →      Customer Behavior DPQ
  Inventory Service   →      Inventory Trends DPQ
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Operational and analytical data have fundamentally different needs | Don't use your operational DB for analytics — separate them |
| Data warehouses centralize control; data meshes decentralize it | Data mesh aligns with microservices philosophy of domain ownership |
| Data lakes without governance become data swamps | Always pair a data lake with a data catalog and ownership model |
| Treat analytical data as a product with SLAs | Domain teams must own quality, not just production, of their data |
| Data Product Quanta mirror service quanta | Apply the same independent-deployability thinking to analytics |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
