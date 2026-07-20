# Chapter 5 — Component-Based Decomposition Patterns

> *"Build services from components, not individual classes."*

---

## 🎯 Core Concept

Six sequential patterns guide you from a monolithic codebase to a distributed architecture in a structured, controlled way. Each pattern addresses a specific problem in preparing code for service extraction.

```
Pattern Flow
────────────
1. Identify & Size Components   → catalog and right-size the building blocks
2. Gather Common Domain         → consolidate duplicated domain logic
3. Flatten Components           → ensure all code lives in proper leaf-node namespaces
4. Determine Dependencies       → understand coupling to assess feasibility
5. Create Component Domains     → group components into logical domains
6. Create Domain Services       → physically extract domain groups into services
```

---

## 📦 Pattern 1: Identify and Size Components

**Goal:** Catalog all architectural components and ensure they are appropriately sized.

### Component = Leaf Node in a Namespace

```
ss.ticket.assign    ← Component (leaf node, contains source files)
ss.ticket           ← NOT a component if it's extended further (it's a subdomain)
```

### Sizing Metric: Total Statements Per Component

Count the total number of *statements* (not lines, not classes) in each component.

```
Component Size Analysis
───────────────────────
Component           Namespace                   %    Statements
─────────────       ─────────────────────────   ──   ──────────
Reporting           ss.reporting                33   27,765     ← TOO BIG!
Ticket Assign       ss.ticket.assign             9    7,845
Expert Profile      ss.expert.profile            6    5,099
Ticket              ss.ticket                    8    7,009
```

**Rule:** Components should fall within 1-2 standard deviations of the mean. Any outlier needs splitting.

### Fitness Functions for Component Size

```python
# Alert if any component exceeds 10% of codebase
def check_component_size(root_directory, threshold=0.10):
    components = identify_components(root_directory)
    total = accumulate_statements(root_directory)
    for component in components:
        pct = accumulate_statements(component) / total
        if pct > threshold:
            send_alert(component, pct)
```

### Sysops Squad: Splitting the Reporting Component

The Reporting component was 33% of the codebase — far too large. It was split into:
- `ss.reporting.shared` (7%) — common utilities
- `ss.reporting.tickets` (8%) — ticket reports
- `ss.reporting.experts` (9%) — expert reports  
- `ss.reporting.financial` (9%) — financial reports

---

## 🔗 Pattern 2: Gather Common Domain Components

**Goal:** Find and consolidate duplicated domain logic to prevent duplicate services.

### How to Spot Common Domain Functionality

```
Signal 1: Same leaf node name in multiple namespaces
  ss.ticket.notify
  ss.customer.notification  } → All about notification!
  ss.survey.notify

Signal 2: Common class files used across components
  SMTPConnection used by 5 different namespaces → common email logic

Signal 3: Components that do the same fundamental thing
  billing audit, ticket audit, survey audit → all write to audit table
```

### Warning: Consolidation Increases Coupling

Always measure incoming coupling (Ca) before and after:

```
Before consolidation:
  Customer Notification    Ca = 2  (Billing, Contract use it)
  Ticket Notify            Ca = 2  (Ticket, Ticket Route use it)
  Survey Notify            Ca = 1  (Survey uses it)

After consolidation to single Notification component:
  Notification             Ca = 5  (all 5 services use it)

Total coupling unchanged (5 = 5), but now ONE component to maintain ✓
```

### Fitness Functions

```python
# Alert on components with same leaf-node name
def find_common_leaf_nodes(components, exclusions):
    seen = {}
    for component in components:
        leaf = get_last_node(component)
        if leaf in seen and leaf not in exclusions:
            send_alert(component)
        seen[leaf] = True
```

---

## 📐 Pattern 3: Flatten Components

**Goal:** Remove "orphaned classes" — code that lives in a namespace that has been extended, making it belong to no defined component.

### The Problem: Orphaned Classes

```
Namespace hierarchy:
  ss.survey              ← ROOT NAMESPACE (extended further)
    → contains 5 class files  ← ORPHANED (no component!)
  ss.survey.templates    ← COMPONENT (leaf node)
    → contains 7 class files  ← belongs here ✓

ss.survey is now a "subdomain", not a component.
The 5 files in ss.survey are orphaned.
```

### Two Ways to Flatten

**Option A — Push up:** Move templates into `ss.survey` (combine)
```
ss.survey.templates removed
ss.survey now has 12 files → single component ✓
```

**Option B — Push down:** Break ss.survey's orphaned files into new leaf namespaces
```
ss.survey.create    ← orphaned files redistributed here
ss.survey.process   ← orphaned files redistributed here
ss.survey.templates ← unchanged
```

### Fitness Function

```python
# Alert if any source code lives in a non-leaf namespace
def check_for_orphaned_classes(root_directory):
    for component in identify_components(root_directory):
        for node in get_nodes(component):
            if contains_code(node) and not last_node(node):
                send_alert(component)
```

---

## 🔗 Pattern 4: Determine Component Dependencies

**Goal:** Visualize and analyze coupling between components to assess migration feasibility.

### The Three-Tier Sizing Model

```
Golf Ball (Low coupling → easy migration):
  ┌─────┐   ┌─────┐   ┌─────┐
  │  A  │   │  B  │   │  C  │
  └─────┘   └─────┘   └──┬──┘
                          └──▶ D
  Very few dependencies → refactoring ✓

Basketball (Medium coupling → harder migration):
  Components with dense left-side coupling, sparse right-side
  → Combination of refactoring and some rewriting

Airliner (Very high coupling → consider rewrite):
  ╔═════╗══╗═══╗   Every component depends on every other
  ║░░░░░║░░║░░░║   → Full rewrite likely required
  ╚═════╝══╝═══╝
```

### Metrics Per Component

```
CT (Total) = Ca (incoming) + Ce (outgoing)

If a component has Ca = 20, maybe only 14 use one function:
  → Split into A1 (the 14-user part, Ca=14) and A2 (Ca=6)
  → Reduces coupling on the main component
```

### Fitness Function: Restrict Dependencies

```java
// ArchUnit: Ticket Maintenance cannot access Expert Profile
public void ticket_maintenance_cannot_access_expert_profile() {
    noClasses().that()
        .resideInAPackage("..ss.ticket.maintenance..")
        .should().accessClassesThat()
        .resideInAPackage("..ss.expert.profile..")
        .check(myClasses);
}
```

---

## 🏠 Pattern 5: Create Component Domains

**Goal:** Group related components into logical domains and align namespaces accordingly.

### Namespace = Domain Identity

```
Before domain alignment:
  ss.billing.payment       ← billing under billing namespace
  ss.billing.history       ← ok
  ss.customer.profile      ← customer under customer namespace
  ss.supportcontract       ← root level — where does this belong?

After domain alignment (Customer domain):
  ss.customer.billing.payment    ← billing is under customer
  ss.customer.billing.history
  ss.customer.profile            ← unchanged
  ss.customer.supportcontract    ← now clearly in customer domain
```

### Sysops Squad Domains

```
ss.ticket.*     → Ticketing Domain  (ticket processing, KB, survey)
ss.reporting.*  → Reporting Domain
ss.customer.*   → Customer Domain   (profile, billing, contracts)
ss.admin.*      → Admin Domain      (users, experts)
ss.shared.*     → Shared Domain     (login, notification)
```

### Fitness Function: Enforce Domain Boundaries

```java
// Only these domains may exist in the application
public void restrict_domains() {
    classes()
        .should().resideInAPackage("..ss.ticket..")
        .orShould().resideInAPackage("..ss.customer..")
        .orShould().resideInAPackage("..ss.admin..")
        .orShould().resideInAPackage("..ss.reporting..")
        .orShould().resideInAPackage("..ss.shared..")
        .check(myClasses);
}
```

---

## 🚀 Pattern 6: Create Domain Services

**Goal:** Physically extract each domain into a separately deployed service (service-based architecture).

### Don't Apply Until All Domains Are Defined

```
WRONG order:
  1. Extract Ticket service ✓
  2. Discover Survey should be in Ticket domain
  3. Must go back and modify already-extracted Ticket service ✗ (rework!)

RIGHT order:
  1. Apply all 5 previous patterns first
  2. All domain boundaries settled
  3. Extract ALL domains at once (or in a planned sequence)
```

### The Result: Service-Based Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer                                │
└──────────┬─────────────┬────────────┬────────────┬─────────────┘
           │             │            │            │
    ┌──────▼──────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
    │  Ticketing  │ │Reporting│ │Customer │ │  Admin  │
    │   Service   │ │ Service │ │ Service │ │ Service │
    └─────────────┘ └─────────┘ └─────────┘ └─────────┘
                                    │
                              ┌─────▼──────┐
                              │  Shared DB │  ← still shared at this stage
                              └────────────┘
```

### Fitness Function per Domain Service

```java
// All components in Ticket service must start with ss.ticket
public void restrict_domain_within_ticket_service() {
    classes().should().resideInAPackage("..ss.ticket..")
        .check(myClasses);
}
```

---

## 💡 Key Takeaways

| Pattern | What It Fixes |
|---------|---------------|
| Identify & Size | Oversized components that are too hard to move |
| Gather Common Domain | Duplicate domain logic that would produce duplicate services |
| Flatten Components | Orphaned code with no clear home |
| Determine Dependencies | Unknown coupling that makes migration infeasible |
| Create Component Domains | Missing domain structure that makes extraction unclear |
| Create Domain Services | The actual physical split into separate deployments |

> **Remember:** Apply all six patterns in sequence. Don't skip ahead to extracting services before the codebase is properly organized — you'll create a distributed mess instead of a distributed architecture.

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
