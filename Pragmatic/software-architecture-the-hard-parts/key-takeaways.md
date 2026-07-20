# Key Takeaways — Software Architecture: The Hard Parts

> *Neal Ford, Mark Richards, Pramod Sadalage & Zhamak Dehghani — O'Reilly, 2022*

---

## 🧠 The Mindset Shift

| Old Thinking | New Thinking |
|-------------|-------------|
| "What is the best practice?" | "What are the trade-offs in my specific context?" |
| "Decouple everything" | "Apply coupling appropriately — it's a dosage problem" |
| "Microservices means small" | "Microservices means right-sized for the domain" |
| "One database per service" | "One data ownership boundary per service" |
| "Follow industry patterns" | "Understand why a pattern exists before applying it" |

---

## 🏗️ Part I: Pulling Things Apart

### Architecture Quantum
- An **architecture quantum** = independently deployable artifact with high functional cohesion + high static coupling + synchronous dynamic coupling
- Shared databases reduce quantum count — even distributed services sharing one DB = **one quantum**
- A shared UI can collapse a microservices architecture to a single quantum

### Coupling Types
- **Static coupling** = how things are *wired* (dependencies, frameworks, databases)
- **Dynamic coupling** = how things *communicate* at runtime (sync/async, orchestrated/choreographed)
- The three dimensions of dynamic coupling: **Communication × Consistency × Coordination**

### Architectural Modularity Drivers
Breaking apart a system is justified by 5 characteristics:
1. **Maintainability** — isolate change scope to a domain
2. **Testability** — reduce testing surface per deployment
3. **Deployability** — deploy independently, more frequently
4. **Scalability** — scale only the parts that need it
5. **Availability/Fault Tolerance** — isolate failures to deployment units

### Decomposition Approaches
- **Component-Based Decomposition** — for structured codebases with clear component boundaries
- **Tactical Forking** — for big balls of mud; clone and delete, rather than extract

### Component-Based Decomposition Patterns (in order)
1. **Identify & Size** — measure by statements, not lines of code
2. **Gather Common Domain Components** — consolidate duplicate domain logic
3. **Flatten Components** — source code only in leaf node namespaces
4. **Determine Component Dependencies** — visualize coupling; golfball/basketball/airliner
5. **Create Component Domains** — group into namespace-aligned domains
6. **Create Domain Services** — extract to service-based architecture first

### Data Decomposition
**Disintegrators** (reasons to split data):
- Change control (schema changes break multiple services)
- Connection management (shared DB saturates connection pool)
- Scalability (DB becomes bottleneck)
- Fault tolerance (shared DB = single point of failure)
- Architecture quantum requirements
- Database type optimization

**Integrators** (reasons to keep data together):
- Data relationships (foreign keys, views, triggers)
- Database transactions (ACID requirements)

**Five-step data decomposition process:**
1. Analyze DB and create data domains
2. Assign tables to data domains (schemas)
3. Separate DB connections per domain
4. Move schemas to separate servers
5. Switch over to independent databases

### Service Granularity

**Disintegrators** (split a service when...):
- Service scope is too broad (weak cohesion)
- Code volatility differs by function
- Scalability requirements differ
- Fault tolerance is needed per function
- Security boundaries differ
- Extensibility is expected

**Integrators** (keep/merge services when...):
- ACID transactions are required across functions
- Workflow creates too much inter-service communication
- Shared domain code creates versioning complexity
- Data relationships can't be separated

---

## 🔗 Part II: Putting Things Back Together

### Code Reuse Patterns (in order of coupling)

| Pattern | Coupling | Change Risk | Best For |
|---------|----------|-------------|----------|
| Code Replication | Lowest | Lowest | Truly independent diverging logic |
| Shared Library | Low | Medium | Stable utility/infrastructure code |
| Shared Service | Medium | High | Frequently-changing domain logic |
| Sidecar/Service Mesh | Lowest operational | Managed | Cross-cutting infrastructure concerns |

### Data Ownership

| Scenario | Technique |
|----------|-----------|
| One service writes | Single ownership — straightforward |
| Multiple services write same table | Table split, data domain, delegate, or consolidate |
| Joint ownership | Use the technique that minimizes coupling |

**Eventual consistency patterns:**
- Background Synchronization — periodic sync job
- Orchestrated Request-Based — orchestrator calls multiple services
- Event-Based — publish events, services react

### Distributed Data Access

| Pattern | When to Use |
|---------|-------------|
| Interservice Communication | Small data, low frequency, simple queries |
| Column Schema Replication | High-read, rarely-changing reference data |
| Replicated Caching | Frequently-read, medium-sized, low-latency needed |
| Data Domain | Services that are tightly coupled by data anyway |

### Workflow Management

| Style | Coupling | Visibility | Best For |
|-------|----------|------------|---------|
| Orchestration | Higher | High | Complex workflows, error handling, audit |
| Choreography | Lower | Low | Simple reactive workflows, independence |

### The 8 Transactional Saga Patterns

| Pattern | Code | Coupling | Consistency | Notes |
|---------|------|----------|-------------|-------|
| Epic Saga | `sao` | Very High | Strong | Avoid for complex workflows |
| Phone Tag | `sac` | High | Strong | Sequential strict workflows |
| Fairy Tale | `seo` | High | Eventual | Orchestrated + relaxed |
| Time Travel | `sec` | Medium | Eventual | Choreographed eventual |
| Fantasy Fiction | `aao` | High | Strong | Complex async + atomic |
| Horror Story | `aac` | Medium | Strong | Avoid |
| **Parallel Saga** | **`aeo`** | **Low** | **Eventual** | **Most practical** |
| Anthology Saga | `aec` | Very Low | Eventual | Most decoupled |

### Contracts

- **Strict contracts**: high safety, low flexibility, requires coordination for changes
- **Loose contracts**: lower safety, high flexibility, enables independent evolution
- **Tolerant Reader Pattern**: consume only what you need, ignore the rest
- **Stamp coupling**: passing full data structures when only a subset is needed — avoid it
- **Consumer-Driven Contract Testing**: consumers define what they need; providers verify compliance

### Analytical Data Approaches

| Approach | Ownership | Flexibility | Governance |
|---------|-----------|-------------|------------|
| Data Warehouse | Central team | Low | High (centralized) |
| Data Lake | Central team | Very High | Low (swamp risk) |
| **Data Mesh** | **Domain teams** | **High** | **Federated** |

**Data Mesh principles:**
1. Domain-oriented ownership
2. Data as a product (with SLAs)
3. Self-serve data infrastructure
4. Federated governance

---

## 🔬 The Trade-Off Analysis Framework

```
1. Find entangled dimensions — what forces are in play?
2. Analyze coupling — what is coupled to what, and why?
3. Assess impact of change — what breaks if this changes?
4. Use MECE lists — exhaustive and non-overlapping options
5. Avoid out-of-context advice — context makes advice valid
6. Model real domain cases — ground decisions in actual use cases
7. Lead with recommendations — bottom line over overwhelming evidence
8. Document in ADRs — future architects need the "why"
```

---

## ⚡ Most Important Principles

1. **There are no best practices in architecture — only trade-offs in context**
2. **Coupling is dosage — not inherently good or bad**
3. **Move to service-based architecture first, then microservices if needed**
4. **Data decomposition is harder than code decomposition — plan it carefully**
5. **Design compensating transactions before implementing forward paths**
6. **Async + eventual + orchestrated (Parallel Saga) is the most practical saga pattern**
7. **The goal is the least worst combination of trade-offs, not the best solution**
