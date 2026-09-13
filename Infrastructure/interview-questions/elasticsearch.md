# 🔍 Elasticsearch — Interview Questions

---

### 1. What is Elasticsearch and what is it used for?

**A:** Elasticsearch is a distributed, RESTful search and analytics engine built on Apache Lucene. It stores data as JSON documents and makes them searchable in near real-time.

**Use cases:**
- **Full-text search** — product search, document search, log search
- **Log analytics** — ELK/EFK stack (with Logstash/Fluentd + Kibana)
- **Application performance monitoring** — Elastic APM
- **Metrics analytics** — time-series data
- **Vector search** — semantic search with embeddings (kNN)
- **Autocomplete/suggestions** — search-as-you-type

---

### 2. What are indices, documents, fields, and mappings?

**A:**

```
Database analogy (deprecated but helpful):
  Index    ≈ Database / Table
  Document ≈ Row
  Field    ≈ Column
  Mapping  ≈ Schema

Elasticsearch:
  Index: "products"
  Document: { "id": 1, "name": "iPhone 15", "price": 999.99, "tags": ["apple", "phone"] }
  Mapping: defines field types (text, keyword, integer, date, geo_point, etc.)
```

```bash
# Create index with mapping
curl -X PUT "localhost:9200/products" -H "Content-Type: application/json" -d '
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "custom_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id":          { "type": "integer" },
      "name":        { "type": "text",    "analyzer": "custom_analyzer",
                       "fields": { "keyword": { "type": "keyword" } } },
      "description": { "type": "text",    "analyzer": "english" },
      "price":       { "type": "float" },
      "category":    { "type": "keyword" },
      "tags":        { "type": "keyword" },
      "in_stock":    { "type": "boolean" },
      "created_at":  { "type": "date" },
      "location":    { "type": "geo_point" },
      "embedding":   { "type": "dense_vector", "dims": 768 }
    }
  }
}'
```

---

### 3. What is the difference between `text` and `keyword` field types?

**A:**

| | `text` | `keyword` |
|--|--------|----------|
| Analysis | Yes — tokenized, analyzed | No — stored as-is |
| Full-text search | Yes | No (exact match only) |
| Aggregations | No (high cardinality) | Yes |
| Sorting | No | Yes |
| Use for | Body text, descriptions | IDs, tags, status, email |

```bash
# text field — tokenized
# "iPhone 15 Pro" → ["iphone", "15", "pro"]
# Matches: "iphone", "iPhones", "15 Pro"

# keyword field — exact
# "iPhone 15 Pro" stored as "iPhone 15 Pro"
# Must match exactly: "iPhone 15 Pro"

# Multi-field (text + keyword)
"name": {
  "type": "text",
  "fields": {
    "keyword": { "type": "keyword", "ignore_above": 256 }
  }
}
# Search as text: name ("iphone 15")
# Filter/sort/aggregate as keyword: name.keyword ("iPhone 15 Pro")
```

---

### 4. How do you index, get, update, and delete documents?

**A:**

```bash
# Index (create or replace)
curl -X PUT "localhost:9200/products/_doc/1" -d '
{ "name": "iPhone 15", "price": 999.99, "category": "phones" }'

# Auto-generate ID
curl -X POST "localhost:9200/products/_doc" -d '{ "name": "iPad" }'

# Get
curl "localhost:9200/products/_doc/1"
curl "localhost:9200/products/_doc/1?_source=name,price"  # specific fields

# Check exists (HEAD request)
curl -I "localhost:9200/products/_doc/1"  # 200 = exists, 404 = not found

# Update (partial update)
curl -X POST "localhost:9200/products/_doc/1/_update" -d '
{ "doc": { "price": 899.99 } }'

# Update with script
curl -X POST "localhost:9200/products/_doc/1/_update" -d '
{ "script": { "source": "ctx._source.views += params.count", "params": { "count": 1 } } }'

# Delete
curl -X DELETE "localhost:9200/products/_doc/1"

# Bulk API — batch operations (much faster than individual requests)
curl -X POST "localhost:9200/_bulk" -d '
{ "index": { "_index": "products", "_id": "1" } }
{ "name": "iPhone 15", "price": 999.99 }
{ "index": { "_index": "products", "_id": "2" } }
{ "name": "iPad", "price": 799.99 }
{ "delete": { "_index": "products", "_id": "3" } }
{ "update": { "_index": "products", "_id": "4" } }
{ "doc": { "price": 499.99 } }
'
```

---

### 5. How do you write search queries?

**A:**

```bash
# Match query — full-text search
curl -X GET "localhost:9200/products/_search" -d '
{
  "query": {
    "match": {
      "name": "iphone pro"    # tokenized, analyzed
    }
  }
}'

# Term query — exact match on keyword field
{
  "query": { "term": { "category": "phones" } }
}

# Range query
{
  "query": {
    "range": {
      "price": { "gte": 500, "lte": 1000 },
      "created_at": { "gte": "2024-01-01", "lt": "2025-01-01" }
    }
  }
}

# Bool query — combine multiple queries
{
  "query": {
    "bool": {
      "must": [                           # AND — affects score
        { "match": { "name": "iphone" } }
      ],
      "filter": [                         # AND — no score, cacheable
        { "term": { "in_stock": true } },
        { "range": { "price": { "lte": 1000 } } }
      ],
      "should": [                         # OR — boosts score
        { "term": { "tags": "apple" } },
        { "term": { "tags": "featured" } }
      ],
      "must_not": [                       # NOT
        { "term": { "category": "accessories" } }
      ],
      "minimum_should_match": 1
    }
  }
}
```

---

### 6. How does Elasticsearch scoring work?

**A:** Elasticsearch uses BM25 (Best Match 25) algorithm to score document relevance:

```
Score factors:
1. TF (Term Frequency)  — how often term appears in document
2. IDF (Inverse Document Frequency) — how rare the term is across all docs
3. Field length — shorter fields score higher

BM25 formula:
score(q, d) = IDF(t) * TF(t,d) * (k1 + 1) / (TF(t,d) + k1 * (1 - b + b * |d|/avgdl))
  k1 = 1.2 (term frequency saturation)
  b = 0.75 (field length normalization)
```

```bash
# Explain scoring
curl "localhost:9200/products/_explain/1" -d '{ "query": { "match": { "name": "iphone" } } }'

# Boost fields
{
  "query": {
    "multi_match": {
      "query": "iphone",
      "fields": ["name^3", "description^1", "tags^2"]  # ^ = boost multiplier
    }
  }
}

# Function score — custom scoring
{
  "query": {
    "function_score": {
      "query": { "match": { "name": "iphone" } },
      "functions": [
        { "field_value_factor": { "field": "rating", "factor": 1.5 } },
        { "gauss": { "created_at": { "origin": "now", "scale": "30d" } } }
      ],
      "score_mode": "multiply",
      "boost_mode": "multiply"
    }
  }
}
```

---

### 7. What are aggregations?

**A:**

```bash
# Aggregations — analytics on indexed data

# Terms aggregation — group by field value (SQL: GROUP BY)
{
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 10 }
    }
  }
}
# Result: { buckets: [{ key: "phones", doc_count: 150 }, ...] }

# Metrics aggregations
{
  "aggs": {
    "avg_price":  { "avg":   { "field": "price" } },
    "max_price":  { "max":   { "field": "price" } },
    "min_price":  { "min":   { "field": "price" } },
    "total_sales":{ "sum":   { "field": "price" } },
    "price_stats":{ "stats": { "field": "price" } },
    "percentiles":{ "percentiles": { "field": "price", "percents": [50, 95, 99] } }
  }
}

# Date histogram — time-series bucketing
{
  "aggs": {
    "sales_over_time": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "day"
      },
      "aggs": {
        "daily_revenue": { "sum": { "field": "price" } }
      }
    }
  }
}

# Nested aggregation — faceted search
{
  "query": { "match": { "name": "iphone" } },
  "aggs": {
    "categories": {
      "terms": { "field": "category" },
      "aggs": {
        "avg_price": { "avg": { "field": "price" } }
      }
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [{ "to": 500 }, { "from": 500, "to": 1000 }, { "from": 1000 }]
      }
    }
  }
}
```

---

### 8. What are shards and replicas?

**A:**

```
Index "products" with 3 shards, 1 replica:

Node 1: P0, R1, R2     P=Primary shard
Node 2: P1, R0, R2     R=Replica shard
Node 3: P2, R0, R1

- 3 primary shards → data distributed across 3 shards
- 1 replica of each → 6 total shards, each primary has 1 backup
- Indexing goes to primary, replicated to replicas
- Search can use primaries AND replicas (load balancing)
- If Node 2 fails → Node 1 or 3 promotes R1 to primary
```

```bash
# Shard sizing best practices:
# - Aim for 10-50GB per shard
# - Max 200M docs per shard
# - More shards = more parallelism but more overhead
# - Too many small shards = "oversharding" problem

# Cannot change primary shards after index creation!
# Use reindex or rollover for re-sharding

# Check shard health
curl "localhost:9200/_cat/shards?v"
curl "localhost:9200/_cluster/health?pretty"
```

---

### 9. How do you implement autocomplete / search-as-you-type?

**A:**

```bash
# Option 1: edge_ngram analyzer
{
  "settings": {
    "analysis": {
      "filter": {
        "autocomplete_filter": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 20
        }
      },
      "analyzer": {
        "autocomplete": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "autocomplete_filter"]
        },
        "autocomplete_search": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "autocomplete",        # index time: generates ngrams
        "search_analyzer": "autocomplete_search"  # search time: no ngrams
      }
    }
  }
}

# Option 2: search_as_you_type field type (ES 7.2+)
{
  "mappings": {
    "properties": {
      "name": {
        "type": "search_as_you_type"  # creates ngram sub-fields automatically
      }
    }
  }
}

# Query
{
  "query": {
    "multi_match": {
      "query": "ipho",
      "type": "bool_prefix",
      "fields": ["name", "name._2gram", "name._3gram"]
    }
  }
}

# Option 3: completion suggester (stored separately, very fast)
```

---

### 10. How do you handle index lifecycle management (ILM)?

**A:**

```bash
# ILM policy — manage time-series indices (logs, metrics)
curl -X PUT "localhost:9200/_ilm/policy/logs-policy" -d '
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d",
            "max_docs": 100000000
          },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {},
          "set_priority": { "priority": 0 }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": { "delete": {} }
      }
    }
  }
}'

# Index template with ILM
curl -X PUT "localhost:9200/_index_template/logs-template" -d '
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "index.lifecycle.name": "logs-policy",
      "index.lifecycle.rollover_alias": "logs"
    }
  }
}'
```

---

### 11. What is the ELK/EFK stack?

**A:**

```
ELK Stack:
  E = Elasticsearch  — store, search, analyze logs
  L = Logstash       — collect, parse, transform logs (heavy, uses Java)
  K = Kibana         — visualize, dashboard, alerts

EFK Stack (lighter):
  E = Elasticsearch
  F = Fluentd/Fluent Bit  — lightweight log shipper (Go, low resource)
  K = Kibana

Data flow:
  App Logs → Fluent Bit (per node) → Kafka (optional buffer) → Elasticsearch → Kibana
  Metrics  → Metricbeat → Elasticsearch → Kibana
  APM      → APM Agent  → APM Server    → Elasticsearch → Kibana
```

```yaml
# Fluent Bit config
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Refresh_Interval  5

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_URL            https://kubernetes.default.svc:443
    Merge_Log           On

[OUTPUT]
    Name            es
    Match           *
    Host            elasticsearch
    Port            9200
    Index           logs-%Y.%m.%d
    Type            _doc
    Logstash_Format On
    Logstash_Prefix logs
```

---

### 12. How do you optimize Elasticsearch performance?

**A:**

```bash
# 1. Bulk indexing — batch documents
# Single doc: 500 docs/s per shard
# Bulk (1000 docs): 50,000 docs/s per shard

# 2. Refresh interval — reduce for high-throughput indexing
curl -X PUT "localhost:9200/products/_settings" -d '
{ "index": { "refresh_interval": "30s" } }'  # default: 1s
# During bulk import:
{ "refresh_interval": "-1" }  # disable, then enable after

# 3. Replicas — disable during bulk import, re-enable after
{ "number_of_replicas": 0 }  # then restore to 1+

# 4. Mapping optimizations
{
  "_source": { "enabled": false },  # saves disk (can't return source)
  "properties": {
    "id": { "type": "keyword", "doc_values": false },  # no aggregation
    "log_message": { "type": "text", "norms": false }  # no scoring
  }
}

# 5. Filter vs query context
# Use filter (cached, no scoring) whenever relevance scoring not needed
{
  "query": {
    "bool": {
      "filter": [  # ← filter context, cached, fast
        { "term": { "status": "active" } },
        { "range": { "price": { "gte": 100 } } }
      ],
      "must": [    # ← query context, scored, not cached
        { "match": { "name": "iphone" } }
      ]
    }
  }
}

# 6. Avoid wildcard at start (prefix is ok)
# BAD:  { "wildcard": { "name": "*phone" } }
# GOOD: { "wildcard": { "name": "phone*" } }

# 7. doc_values for sorting/aggregations (enabled by default on keyword/numeric)
# 8. fielddata for sorting on text fields (expensive — avoid)
```

---

### 13. How do you handle multi-tenancy in Elasticsearch?

**A:**

```bash
# Option 1: Index per tenant (best isolation, more overhead)
logs-tenant-A-2024.01.15
logs-tenant-B-2024.01.15
# Pros: complete isolation, different retention per tenant
# Cons: thousands of indices if many tenants

# Option 2: tenant_id field (most scalable)
{
  "mappings": {
    "properties": {
      "tenant_id": { "type": "keyword" }
    }
  }
}
# Always include in filter:
{
  "query": {
    "bool": {
      "filter": [{ "term": { "tenant_id": "tenant-A" } }]
    }
  }
}
# Pros: single index, simple
# Cons: no isolation, one tenant's bulk load affects others

# Option 3: Routing per tenant (same index, same shard per tenant)
curl -X PUT "localhost:9200/products/_doc/1?routing=tenant-A" -d '{...}'
curl "localhost:9200/products/_search?routing=tenant-A" -d '{...}'
# Pros: queries only hit tenant's shards (efficient)
# Cons: potential hotspots if one tenant has all data
```

---

### 14. What is a search template and script?

**A:**

```bash
# Search template — parameterized search (avoid SQL injection-like issues)
curl -X PUT "localhost:9200/_scripts/product-search" -d '
{
  "script": {
    "lang": "mustache",
    "source": {
      "query": {
        "bool": {
          "must": [
            { "match": { "name": "{{query}}" } }
          ],
          "filter": [
            { "term": { "category": "{{category}}" } },
            { "range": { "price": { "gte": "{{min_price}}", "lte": "{{max_price}}" } } }
          ]
        }
      },
      "from": "{{from}}",
      "size": "{{size}}"
    }
  }
}'

# Use template
curl -X GET "localhost:9200/products/_search/template" -d '
{
  "id": "product-search",
  "params": {
    "query": "iphone",
    "category": "phones",
    "min_price": 500,
    "max_price": 1000,
    "from": 0,
    "size": 10
  }
}'
```

---

### 15. How do you handle reindexing without downtime?

**A:**

```bash
# Zero-downtime reindex pattern:
# 1. Create new index with new mapping
curl -X PUT "localhost:9200/products-v2" -d '{ "mappings": {...} }'

# 2. Create alias pointing to old index
curl -X PUT "localhost:9200/products-v1/_alias/products"

# 3. Application uses alias "products" (writes to v1)

# 4. Reindex from v1 to v2 (background)
curl -X POST "localhost:9200/_reindex?wait_for_completion=false" -d '
{
  "source": { "index": "products-v1" },
  "dest":   { "index": "products-v2" }
}'

# 5. After reindex — sync writes (reindex documents added during reindex)
curl -X POST "localhost:9200/_reindex" -d '
{
  "source": {
    "index": "products-v1",
    "query": { "range": { "updated_at": { "gte": "reindex_start_time" } } }
  },
  "dest": { "index": "products-v2", "op_type": "create" }
}'

# 6. Swap alias atomically — zero downtime
curl -X POST "localhost:9200/_aliases" -d '
{
  "actions": [
    { "remove": { "index": "products-v1", "alias": "products" } },
    { "add":    { "index": "products-v2", "alias": "products" } }
  ]
}'

# 7. Delete old index when safe
curl -X DELETE "localhost:9200/products-v1"
```

---

### 16. How do you implement vector search in Elasticsearch?

**A:**

```bash
# dense_vector field for semantic/neural search (ES 8.x)
{
  "mappings": {
    "properties": {
      "title":      { "type": "text" },
      "embedding":  { "type": "dense_vector", "dims": 768, "index": true, "similarity": "cosine" }
    }
  }
}

# Index document with embedding
{
  "title": "iPhone 15 Pro",
  "embedding": [0.1, 0.2, 0.3, ...768 floats...]
}

# kNN search — find semantically similar documents
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.15, 0.25, 0.35, ...],  # embed the query with same model
    "k": 10,                                    # return top 10 neighbors
    "num_candidates": 100                        # consider top 100 before filtering
  },
  "filter": [{ "term": { "category": "phones" } }]
}

# Hybrid search — combine kNN with BM25
{
  "query": { "match": { "title": "iphone camera" } },
  "knn": { "field": "embedding", "query_vector": [...], "k": 10 },
  "rank": { "rrf": {} }   # Reciprocal Rank Fusion to combine scores
}
```
