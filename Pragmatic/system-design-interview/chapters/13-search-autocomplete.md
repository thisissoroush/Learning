# Chapter 13 — Design a Search Autocomplete System

> *"As you type 'sys' into Google, it's already predicting 'system design' — querying a Trie data structure across millions of historical searches in under 100ms."*

---

## 🎯 Core Concept

**Search Autocomplete** (also called "search-as-you-type" or "typeahead") predicts what a user is searching for based on their partial input, surfacing the most popular completions. The challenge is serving these suggestions from a prefix index that's built from billions of historical queries — and doing it in under 100ms per keystroke.

---

## 📋 Requirements

### Functional
- As user types, return top 5 matching search suggestions
- Suggestions are ranked by popularity (search frequency)
- Suggestions update with each additional character typed
- Support Unicode (not just ASCII)

### Non-Functional
- Fast: results in < 100ms (human perception threshold for "instant")
- Fresh: autocomplete updated within 1 week of new trending terms
- Highly available: search autocomplete is important for UX
- Scalable: 10 million DAU, each typing ~10 queries → 100M queries/day

### Scale (Back-of-Envelope)
```
DAU:              10M
Searches/user/day: 10
Characters per search avg: 20
Total keystrokes:  10M × 10 × 20 = 2B keystrokes/day
                   = 23,000 keystrokes/sec

With debouncing (query every 300ms vs every keypress):
  Actual API calls: much less
  ~5 API calls per search query
  10M × 10 × 5 = 500M API calls/day = 5,800/sec
```

---

## 🏗️ High-Level Architecture

![Search Autocomplete](../images/13-search-autocomplete.png)

---

## 🔑 The Trie Data Structure

A **Trie** (prefix tree) is the perfect data structure for autocomplete. It stores strings in a tree where each node represents one character, and common prefixes share the same path.

```
Words: ["apple", "app", "application", "apply", "apt"]

Trie structure:
        root
          |
          a
          |
          p
         / \
        p   t
       /|    \
      ● l     ●(apt)
     app e
          |
          ●(apple)
         / \
        i   y
        c   ●(apply)
        a
        t
        i
        o
        n
        ●(application)
```

**Prefix query:** Find all words starting with "app"
```
1. Traverse: root → a → p → p (depth 3)
2. DFS from this node: find all leaf descendants
3. Returns: "app", "apple", "apply", "application"
```

**Time complexity:**
```
Build trie: O(N × W) where N = num words, W = avg word length
Query trie: O(P + Q) where P = prefix length, Q = number of results
```

---

## 🏆 Top-K Suggestions: Caching in Each Node

**Problem:** After reaching the prefix node, DFS to find all words is O(N) in the worst case (if millions of words start with "a"). Too slow!

**Solution:** Cache top-K suggestions at each node.

```
Trie node structure with cached top-5:
  Node for "app" → {
    children: {l: ..., t: ..., ...},
    top5: [
      ("application", 1,234,567),  ← most searched
      ("apple",       987,654),
      ("apply",       456,789),
      ("app",         345,678),
      ("apps",        234,567),
    ]
  }

Query "app":
  1. Traverse: root → a → p → p (O(prefix_length))
  2. Return cached top5 directly (O(1))!
  
No DFS needed! O(P) total time.
```

**Cost of this optimization:**
```
Memory increase: each node stores top-5 (5 × ~50 bytes) = 250 bytes extra
For a trie with 1M nodes: 1M × 250B = 250MB extra (acceptable)
```

---

## 🔄 Building and Updating the Trie

### Data Source: Query Logs

```
Every search query is logged:
  2024-01-15 10:30:01 user_id=alice query="apple"
  2024-01-15 10:30:02 user_id=bob   query="app store"
  2024-01-15 10:30:03 user_id=carol query="application"
  ...

Weekly batch job:
  1. Aggregate query logs → (query, count) pairs
     SELECT query, COUNT(*) as count FROM search_logs
     WHERE timestamp >= now() - 7 days
     GROUP BY query ORDER BY count DESC LIMIT 1000000
  
  2. Build new trie from top 1M queries
  3. Serialize trie to binary format
  4. Upload to S3
  5. Query service loads new trie (hot swap — no downtime)
```

### Why Weekly (Not Real-time)?

```
Real-time trie updates:
  - Complex: concurrent read/write requires locking or MVCC
  - Expensive: rebuild top-K for all ancestor nodes on each update
  - Risky: trending topics (Taylor Swift concert) cause update storms

Weekly batch:
  ✅ Simpler: rebuild entire trie once a week
  ✅ Safe: no concurrent modification issues
  ✅ Accurate: aggregate a full week's data for stable rankings
  ❌ Lag: new trending terms take up to a week to appear

Hybrid approach:
  Weekly: full trie rebuild (stable baseline)
  Hourly: hot-patch top trending terms (via separate "trending" overlay)
```

---

## 🌐 Serving Architecture

```
Client (user's browser/app)
  ↓ AJAX request on each keystroke (debounced 300ms)
  ↓ GET /autocomplete?q=syst&limit=5

Load Balancer
  ↓ route to one of N autocomplete servers

Autocomplete Server (stateless)
  ↓ serves requests from in-memory Trie
  ↓ Trie loaded at startup from S3 (~200MB)
  ↓ fits entirely in RAM

No database call needed → sub-millisecond query!

Cache (optional CDN):
  Prefix "sys" → same 5 results for everyone → CDN can cache!
  Cache key: "autocomplete:sys"
  TTL: 5 minutes
  Hit rate: ~80% (common prefixes queried frequently)
```

### AJAX Debouncing at Client

```javascript
// Don't query on every keypress — debounce to avoid excessive calls
const debounce = (fn, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const fetchSuggestions = debounce(async (query) => {
  if (query.length < 2) return;  // Don't query for 1 char
  const results = await fetch(`/autocomplete?q=${query}&limit=5`);
  displayResults(await results.json());
}, 300);  // 300ms after last keystroke

searchInput.addEventListener('input', (e) => {
  fetchSuggestions(e.target.value);
});
```

---

## ⚖️ Design Decisions & Trade-offs

### Trie vs. Prefix Hash Map

| Approach | Memory | Query Time | Update |
|---------|--------|-----------|--------|
| **Trie** | O(N×W) | O(P) with top-K cache | Complex |
| **Prefix hash map** | O(prefix_count × K) | O(1) | Simple |
| **Elasticsearch** | High | O(log N) | Real-time |

```
Prefix hash map example:
  {"s": [top5], "sy": [top5], "sys": [top5], "syst": [top5], ...}
  
  For 1M queries × avg 10 chars: 10M entries
  10M × 5 results × 50 bytes = 2.5GB ← larger than Trie
  
  O(1) lookup (hash map) vs O(P) lookup (Trie traversal)
  But hash map is larger and doesn't benefit from prefix sharing
  
  Trie is preferred for memory efficiency in most implementations
```

### Handling Scale: Trie Sharding

```
If trie doesn't fit in one server's RAM:
  Shard by first letter: 
    "a-f" → Shard 1
    "g-m" → Shard 2
    "n-t" → Shard 3
    "u-z" → Shard 4
    
  Router: "syst" → first char 's' → Shard 3
  
  Or: shard by first two characters (more fine-grained)
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Trie data structure** | O(P + K) prefix lookup where P = prefix length, K = top results |
| **Top-K caching in nodes** | Store top 5 results at each node — O(P) total, no DFS needed |
| **Weekly batch rebuild** | Build from aggregate logs — stable, simple, no concurrent modification |
| **AJAX debouncing** | Don't query on every keystroke — 300ms delay reduces API calls 10× |
| **CDN for common prefixes** | High-traffic prefixes ("the", "how", "sys") → cache at CDN |
| **In-memory serving** | Entire trie in RAM → sub-millisecond queries, no DB calls |

---

*← [Back to System Design Interview](../README.md)*
