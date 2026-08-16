# Chapter 9 — Design a Web Crawler

> *"A web crawler is the internet's librarian — it reads everything, indexes it, and makes it searchable. Building one that's polite, scalable, and thorough is an engineering art."*

---

## 🎯 Core Concept

A **Web Crawler** (also called a spider or bot) systematically browses the World Wide Web, downloading web pages and following links to discover new ones. Crawlers power search engines (Google, Bing), price comparators, SEO tools, and research datasets.

The core challenges: **politeness** (don't overload servers), **deduplication** (don't visit the same page twice), and **scale** (billions of URLs exist on the web).

---

## 📋 Requirements

### Functional
- Start from a set of seed URLs
- Download HTML content of each URL
- Extract all links from downloaded pages
- Add new links to the crawl queue
- Store downloaded content (for indexing)
- Avoid revisiting the same URL
- Respect robots.txt

### Non-Functional
- Scale: crawl 1 billion pages in 1 month
- Politeness: max 1 request per domain per second
- Resilience: recover from server failures/timeouts
- Extensible: support future content types (images, PDFs)

### Scale (Back-of-Envelope)
```
Target: 1 billion pages in 4 weeks = 29 days
Pages/day: 1B / 29 = 34.5M pages/day
Pages/sec: 34.5M / 86,400 = 400 pages/sec

Average page size: 100KB
Total download: 1B × 100KB = 100TB
Storage with 5-year retention: 500TB

Bandwidth: 400 pages/sec × 100KB = 40MB/sec = 320 Mbps (one network port)
→ Need multiple machines for sufficient bandwidth
```

---

## 🏗️ High-Level Architecture

![Web Crawler Architecture](../images/09-web-crawler.png)

### Component Breakdown

```
Seed URLs → URL Frontier → HTML Downloader → Content Parser
                                              → Content Store
                                              → URL Extractor → Bloom Filter → URL Frontier
```

---

## 🔑 Core Components

### 1. URL Frontier (The Queue)

The **URL Frontier** is a priority queue of URLs to crawl. It's not a simple FIFO — it has two important properties:

```
Priority Queue:
  High-priority URLs crawled first:
    - High PageRank pages
    - Recently updated pages (based on historical data)
    - News sites (updated frequently)
    - "Important" domains (google.com, wikipedia.org)

Politeness Queue:
  One queue per domain:
    Queue 0: ["https://amazon.com/page1", "https://amazon.com/page2"]
    Queue 1: ["https://google.com/index", ...]
    Queue 2: ["https://wikipedia.org/..."]
  
  Politeness rule: only one request to a domain at a time (1 req/sec)
  Router: pick one URL from each domain queue in round-robin
```

**Why separate queues per domain?**
```
Without politeness: crawler sends 400 requests/sec to amazon.com
→ amazon.com blocks your IP (rightfully!)

With politeness: crawler sends 1 request/second to amazon.com
→ amazon.com happy, crawler happy
```

### 2. HTML Downloader

```
For each URL from frontier:
  1. DNS lookup: "amazon.com" → 1.2.3.4
     (cache DNS results for 30 minutes to reduce lookups)
  
  2. HTTP GET request with headers:
     User-Agent: MyBot/1.0 (+https://mycompany.com/bot)
     ← Always identify yourself — sites may allow bots with valid UA
  
  3. Handle redirects:
     301/302 → follow redirect
     Track redirect chain to detect loops
  
  4. Handle errors:
     404: page gone → skip
     429: rate limited → back off and retry
     500: server error → retry after delay
  
  5. Timeout: 30 seconds max per page
```

### 3. Content Parser

```
Downloaded HTML needs validation:
  - Valid HTML? (malformed HTML still common)
  - Is it actually text/html? (not binary, not image)
  - Language filter (if only crawling English content)
  - Content-length check (skip very large pages)

Separate parser service for robustness:
  If parser crashes (bad HTML), downloader keeps running
  Parser runs in isolated process (sandboxed for security)
```

### 4. Duplicate Detection

**Problem:** The web has enormous duplication.
- Same article syndicated across 100 sites
- Multiple URLs pointing to same content (URL parameters)
- Near-duplicate content with minor differences

```
Method 1: URL deduplication (fast)
  Before downloading: check if URL seen before
  Use Bloom Filter:
    bloom_filter.add(url)
    if url in bloom_filter: skip (already seen)
    
  Bloom filter: 1 billion URLs × 10 bits/URL = 10Gb = 1.25GB in RAM
  False positive rate: ~1% (acceptable — skip 1% of new URLs)

Method 2: Content hash deduplication (slower but more accurate)
  After downloading: hash the HTML content
  SHA-256(content) → 32 bytes
  Store in "seen_hashes" set
  If hash seen before: skip (duplicate content, different URL)
  
  Eliminates syndicated duplicates
```

---

## 🤖 Robots.txt: Respecting Website Rules

```
Websites publish rules at: https://domain.com/robots.txt

Example robots.txt:
  User-agent: *
  Disallow: /private/
  Disallow: /admin/
  Crawl-delay: 10
  
  User-agent: Googlebot
  Allow: /
  Crawl-delay: 1

Rules:
  - Never crawl /private/ or /admin/ URLs
  - 10-second delay between requests (this domain)
  - Googlebot has special access and 1s delay

Crawler behavior:
  1. Fetch and cache robots.txt per domain (TTL: 24h)
  2. Before crawling any URL: check robots.txt rules
  3. If disallowed: skip URL, don't add to frontier
```

---

## 🔄 URL Normalization

The same page can be reached through many different URLs:

```
These are all the same page:
  https://example.com/page
  https://example.com/page/
  https://example.com/page?
  https://example.com/page?utm_source=twitter&utm_campaign=summer
  https://EXAMPLE.COM/page
  https://example.com/PAGE  (some servers are case-insensitive)

Normalization steps:
  1. Lowercase the domain: EXAMPLE.COM → example.com
  2. Remove trailing slash: /page/ → /page
  3. Remove tracking parameters: remove utm_*, ref=*, etc.
  4. Decode percent-encoding: /caf%C3%A9 → /café
  5. Sort query parameters: ?z=1&a=2 → ?a=2&z=1

Normalized URL → hash → deduplication check
```

---

## 📊 Distributed Architecture

```
Single machine can download ~100 pages/sec.
Target: 400 pages/sec → need 4+ machines.

Distributed design:
  URL Frontier: distributed queue (Kafka or Redis Streams)
  Each downloader claims URLs from the frontier
  Content Store: shared storage (S3 or HDFS)
  Seen URLs: shared Bloom filter (Redis SETBIT)
  
  Coordinator: assigns domain queues to downloader machines
    Machine 1: handles amazon.com, ebay.com, walmart.com
    Machine 2: handles wikipedia.org, reddit.com, twitter.com
    Machine 3: handles news sites
    Machine 4: overflow + unknown domains

  Why domain assignment?
    Politeness: only one machine per domain → easy to enforce 1 req/sec
    DNS caching: all amazon.com requests go to same machine → same DNS cache
```

---

## ⚖️ Design Decisions & Trade-offs

### BFS vs. DFS Traversal

```
BFS (Breadth-First Search):
  Crawl links closest to seed URLs first
  → Gets to important, well-linked pages sooner
  → More uniform coverage
  ✅ Better for web crawling (seeds are usually important)

DFS (Depth-First Search):
  Follow each link as deep as possible first
  → Could get trapped in "link farms" (spam sites)
  ❌ Bad for web crawling

Use BFS with priority queue (high-PageRank first)
```

### Handling Infinite Crawl Traps

```
Adversarial sites may generate infinite unique URLs:
  https://evil.com/page?seed=1
  https://evil.com/page?seed=2
  ... (infinite URLs, all same content)

Defenses:
  1. Max URL depth limit: don't go more than N links from seed
  2. Max URLs per domain: stop after K URLs from evil.com
  3. Content hash dedup: same content → same hash → skip
  4. Domain blacklist: known spam/trap domains
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Politeness queues** | One queue per domain + 1 req/sec per domain = be a good citizen |
| **Bloom filter** | O(1) URL deduplication with 1.25GB RAM for 1 billion URLs |
| **robots.txt** | Always respect — cache per domain with 24h TTL |
| **URL normalization** | Remove tracking params, normalize case — deduplicate before fetching |
| **BFS with priority** | Crawl high-PageRank pages first — more valuable data sooner |
| **Domain-to-machine assignment** | Route all requests for a domain to one machine — clean politeness enforcement |

---

*← [Back to System Design Interview](../README.md)*
