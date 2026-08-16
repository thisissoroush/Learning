# Chapter 2 — Back-of-Envelope Estimation

> *"A rough estimate that takes 5 minutes is worth more than a precise calculation that takes 5 hours. Learn to think in orders of magnitude."*

---

## 🎯 Core Concept

**Back-of-envelope estimation** is the skill of quickly approximating system scale requirements to guide design decisions. Engineers who master this can instantly evaluate whether a design will work at the required scale, without writing a single line of code.

In a system design interview, the interviewer wants to see your *reasoning process*, not just the final number.

---

## 🔑 The Essential Number Table

You must know these by heart:

### Powers of 2 (Data Sizes)

```
2^10  =  1,024           ≈  1 thousand     = 1 KB
2^20  =  1,048,576       ≈  1 million      = 1 MB
2^30  =  1,073,741,824   ≈  1 billion      = 1 GB
2^40  =                  ≈  1 trillion     = 1 TB
2^50  =                  ≈  1 quadrillion  = 1 PB

Memory hint: each power of 10 adds one digit.
  1 KB = 1,000 bytes (roughly)
  1 GB = 1,000 MB = 1,000,000 KB = 1,000,000,000 bytes
```

### Latency Numbers Every Engineer Should Know

```
                        Actual      "Round number" to use
L1 cache reference       0.5 ns     1 ns
L2 cache reference       7 ns       10 ns
Main memory access       100 ns     100 ns
SSD random read          150 μs     0.1 ms
1 Gbps network (DC)      ~0.5 ms    1 ms
SSD sequential read      1 GB/s     1 ms/MB
HDD seek                 10 ms      10 ms
Round trip (same DC)     0.5 ms     1 ms
Round trip (US-Europe)   150 ms     200 ms
```

**Key ratios to remember:**
```
Memory is 10,000× faster than disk
SSD is 100× faster than HDD  
Datacenter round trip is 1ms (fast)
Cross-continent is 150ms (slow)
```

### Availability Numbers

```
Availability    Downtime/year    Downtime/month    Downtime/day
99%             3.65 days        7.2 hours         14.4 min
99.9%  (3 9s)   8.77 hours       43.8 min          1.44 min
99.99% (4 9s)   52.6 min         4.38 min          8.64 sec
99.999%(5 9s)   5.26 min         26.3 sec          0.86 sec
```

**Typical SLAs by service type:**
- E-commerce checkout: 99.99%
- Social media feed: 99.9%
- Internal admin tools: 99%

---

## 📊 Estimation Reference Diagram

![Estimation Cheat Sheet](../images/02-estimation-cheatsheet.png)

---

## 🔢 The Estimation Framework

### Step 1: Identify the Critical Metrics

```
For any system, estimate:
  DAU      = Daily Active Users
  QPS      = Queries Per Second (reads and writes separately)
  Storage  = How much data is stored and for how long
  Bandwidth = How much data flows in/out per second
  Servers  = How many machines are needed
```

### Step 2: Calculate QPS

```
Twitter Example:
  DAU = 300 million
  Each user sends 2 tweets/day + views 50 tweets/day
  
  Write QPS = 300M × 2 / 86,400 sec/day
            = 600M / 86,400
            ≈ 7,000 writes/sec (peak: ×2 = 14,000)
  
  Read QPS  = 300M × 50 / 86,400
            = 15B / 86,400
            ≈ 174,000 reads/sec (peak: ×2 = 350,000)

  Read/Write ratio = 174,000 / 7,000 ≈ 25:1 (reads dominate!)
  → Design for heavy caching and read replicas
```

### Step 3: Calculate Storage

```
Twitter Example (continued):
  Tweet size = 140 chars × 2 bytes/char = 280 bytes ≈ 300 bytes
  Media per tweet = 0.1 (1 in 10 tweets has image, avg 1MB)
  
  Daily write volume:
    Text: 300M × 2 × 300 bytes = 180GB/day
    Media: 300M × 2 × 0.1 × 1MB = 60TB/day
  
  5-year retention:
    Text: 180GB × 365 × 5 = 329TB ← relational DB, manageable
    Media: 60TB × 365 × 5 = 109PB ← blob storage, massive
```

### Step 4: Calculate Bandwidth

```
Twitter media bandwidth:
  If 50 tweets viewed/day and 1 in 5 has image:
  Outbound: 300M × 50 × 0.2 × 1MB / 86,400
          = 300M × 10MB / 86,400
          ≈ 34,700 GB/sec
          ≈ 34.7 TB/sec ← massive CDN required
```

### Step 5: Estimate Server Count

```
Rule of thumb: 1 server handles ~1,000 QPS (for typical web apps)

For 174,000 reads/sec:
  Servers = 174,000 / 1,000 = 174 web servers
  
  With caching (80% cache hit rate):
  Actual DB queries = 174,000 × 0.2 = 34,800/sec
  DB servers = 34,800 / 1,000 = 35 DB servers (with connection pooling)
```

---

## 💡 A Real Estimation Example: Instagram Stories

**Assumptions:**
- 1 billion DAU
- 10% of users post 1 story/day → 100M stories/day
- Average story size: 2MB (photo) or 15MB (video)
- Stories expire after 24 hours

```
WRITE QPS:
  100M stories/day / 86,400 sec = 1,157 stories/sec ≈ 1,200/sec
  Peak (1.5× average) = 1,800/sec

STORAGE:
  Mix: 70% photos (2MB), 30% videos (15MB)
  Per day:
    Photos: 100M × 0.7 × 2MB = 140TB
    Videos: 100M × 0.3 × 15MB = 450TB
    Total: 590TB/day
  
  After 24h expiry, total stored = 1 day's worth ≈ 590TB

BANDWIDTH (outbound for views):
  If each story viewed 50 times on average:
  100M × 50 × (0.7×2MB + 0.3×15MB) / 86,400
  = 100M × 50 × 5.9MB / 86,400
  ≈ 341 TB/sec (→ needs massive CDN)
```

---

## ⚡ Interview Tips for Estimation

### 1. Round Aggressively

```
Don't say: "86,400 seconds per day"
Do say:    "About 100,000 seconds per day (10^5)"

Don't say: "1,048,576 bytes = 1MB"  
Do say:    "1 million bytes = 1MB"

The goal is order-of-magnitude reasoning, not precision
```

### 2. Clarify Assumptions Out Loud

```
"I'll assume 10% of users are DAU" — state it
"I'll assume average tweet size is 300 bytes" — state it
"I'll assume 80% cache hit rate" — state it

The interviewer may correct your assumptions → better answer
```

### 3. Write Numbers Clearly

```
Use scientific notation or explicit units:
  "3 × 10^8 bytes = 300MB"  ← clear
  "300000000 bytes"          ← confusing
  
Always label units: MB/s, QPS, GB/day — not just numbers
```

### 4. The "Order of Magnitude" Mental Model

```
Estimating 150,000 or 200,000 requests/sec?
  → These are the same order of magnitude → same design decision
  
The number matters for:
  "Do we need 1 server or 100?" (order of magnitude matters)
  "Do we need 1TB or 1PB?" (order of magnitude matters)
  
Precise numbers matter less than getting the right tier:
  KB, MB, GB, TB, PB
  1, 10, 100, 1K, 10K, 100K, 1M, 10M, 100M
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Powers of 2** | 10 bits = KB, 20 = MB, 30 = GB, 40 = TB, 50 = PB |
| **Latency hierarchy** | Memory < SSD < Network(DC) < Disk < Cross-continent |
| **100K sec/day rule** | 86,400 ≈ 10^5 — use this for QPS calculations |
| **Read dominates** | Typical systems: reads are 10-100× more than writes |
| **Peak = 2× average** | Always estimate peak as double your average calculation |
| **State assumptions** | Always say your assumptions out loud — interviewer can guide you |

---

*← [Back to System Design Interview](../README.md)*
