# Hibernate / JPA Interview Questions

> Covers JPA 3.x, Hibernate 6.x, Spring Data JPA 3.x · Junior → Architect

---

## 🟢 Junior

### 1. What is JPA, and how does it differ from Hibernate?

**A:** JPA (Jakarta Persistence API) is a **specification** — a set of interfaces and annotations defined in `jakarta.persistence.*` that standardises ORM for Java. It defines no implementation itself.

Hibernate is the most popular **implementation** of that specification. It ships extra features (HQL filters, multi-tenancy, batch fetching, etc.) on top of what JPA mandates.

| Aspect | JPA | Hibernate |
|---|---|---|
| Type | Specification (JSR-338) | Implementation |
| Package | `jakarta.persistence` | `org.hibernate` |
| Portability | Switch providers freely | Vendor-specific |
| Extra features | None beyond spec | HQL, filters, interceptors, … |

```java
// JPA-only code — portable across providers
EntityManagerFactory emf =
    Persistence.createEntityManagerFactory("myPU");
EntityManager em = emf.createEntityManager();

// Hibernate-specific unwrap
Session session = em.unwrap(Session.class);
```

---

### 2. What annotations are required to map a simple entity?

**A:** At minimum you need `@Entity` and `@Id`. Everything else has sensible defaults.

```java
import jakarta.persistence.*;

@Entity                          // marks this class as a JPA entity
@Table(name = "employees")       // optional — defaults to class name
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "full_name", nullable = false, length = 120)
    private String name;

    @Column(unique = true)
    private String email;

    // JPA requires a no-arg constructor (can be protected)
    protected Employee() {}

    public Employee(String name, String email) {
        this.name  = name;
        this.email = email;
    }
    // getters / setters …
}
```

Key rules:
- The class must **not** be `final` (Hibernate proxies need to subclass it).
- Fields or properties — pick one access strategy and be consistent.
- `@Column` is optional; omitting it maps to a column with the same name as the field.

---

### 3. What are the four entity states in JPA?

**A:**

| State | Description | In persistence context? | In DB? |
|---|---|---|---|
| **Transient** | `new` object, JPA knows nothing about it | ✗ | ✗ |
| **Managed** | Tracked by the current `EntityManager` | ✓ | ✓ (or pending insert) |
| **Detached** | Was managed; context closed or explicitly detached | ✗ | ✓ |
| **Removed** | Scheduled for DELETE at flush | ✓ (marked) | ✓ (until flush) |

```java
Employee e = new Employee("Alice", "a@x.com"); // TRANSIENT

em.getTransaction().begin();
em.persist(e);                                  // MANAGED

em.getTransaction().commit();
em.close();                                     // DETACHED (context closed)

em2.getTransaction().begin();
Employee managed = em2.merge(e);               // MANAGED again (new context)
em2.remove(managed);                           // REMOVED
em2.getTransaction().commit();                 // DELETE executed
```

---

### 4. What are the `@GeneratedValue` strategies?

**A:**

| Strategy | Behaviour | Best for |
|---|---|---|
| `AUTO` | Provider picks the best strategy | Quick prototyping |
| `IDENTITY` | DB auto-increment column (`SERIAL`, `AUTO_INCREMENT`) | MySQL, PostgreSQL |
| `SEQUENCE` | DB sequence object; batches allocation | PostgreSQL, Oracle |
| `TABLE` | Simulates a sequence in a table (slow, avoid) | Legacy DBs |
| `UUID` | Generates a UUID (Hibernate 6+) | Distributed systems |

```java
// SEQUENCE with custom allocation size (batch of 50 — fewer DB round-trips)
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE,
                generator  = "emp_seq")
@SequenceGenerator(name           = "emp_seq",
                   sequenceName   = "employee_seq",
                   allocationSize = 50)
private Long id;

// UUID (Hibernate 6)
@Id
@GeneratedValue(strategy = GenerationType.UUID)
private UUID id;
```

---

### 5. What is the persistence context, and what is its default scope in Spring?

**A:** The **persistence context** is the first-level cache managed by an `EntityManager`. It tracks all managed entities within a transaction — identical loads return the same Java object (identity guarantee).

In a Spring application the default scope is **transaction-scoped**: a new `EntityManager` (and therefore a new persistence context) is created per `@Transactional` method and closed when the transaction commits or rolls back.

```
Transaction starts
│
├─ em.find(Employee.class, 1L)  → hits DB, stores in 1st-level cache
├─ em.find(Employee.class, 1L)  → cache hit, NO second DB query
│
Transaction commits / rollback → persistence context destroyed
```

Extended persistence contexts (rare outside Java EE conversations) survive multiple transactions.

---

### 6. How do `@OneToMany` and `@ManyToOne` work? Show a bidirectional example.

**A:** In a bidirectional relationship one side is the **owner** (holds the FK column) and the other uses `mappedBy`.

```java
@Entity
public class Department {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    // inverse side — mappedBy points to the field in Employee that owns the FK
    @OneToMany(mappedBy = "department",
               cascade  = CascadeType.ALL,
               fetch    = FetchType.LAZY,
               orphanRemoval = true)
    private List<Employee> employees = new ArrayList<>();

    // always synchronise BOTH sides
    public void addEmployee(Employee e) {
        employees.add(e);
        e.setDepartment(this);
    }

    public void removeEmployee(Employee e) {
        employees.remove(e);
        e.setDepartment(null);
    }
}

@Entity
public class Employee {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    // owning side — holds the FK column
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;
}
```

> **Rule:** Always keep both sides in sync in your domain model, not just in DB.

---

### 7. What is `FetchType.LAZY` vs `FetchType.EAGER`?

**A:**

| | LAZY | EAGER |
|---|---|---|
| When loaded | On first access (proxy) | Immediately with the parent |
| Default for `@ManyToOne` / `@OneToOne` | ✗ (EAGER by default) | ✓ |
| Default for `@OneToMany` / `@ManyToMany` | ✓ | ✗ |
| Recommendation | **Prefer LAZY everywhere** | Avoid — causes over-fetching |

```java
// Bad — EAGER causes a JOIN on every Employee load even when you don't need orders
@OneToMany(fetch = FetchType.EAGER)
private List<Order> orders;

// Good — load orders only when accessed
@OneToMany(fetch = FetchType.LAZY)
private List<Order> orders;
```

> **Trap:** Accessing a LAZY collection outside a transaction throws `LazyInitializationException`. Fix: open a transaction, use a JOIN FETCH query, or use a DTO projection.

---

### 8. What is JPQL and how does it differ from SQL?

**A:** JPQL (Jakarta Persistence Query Language) operates on **entity classes and their mapped fields**, not on tables and columns. The provider translates it to SQL at runtime.

```java
// SQL — talks to tables/columns
SELECT e.full_name, d.dept_name
FROM employees e JOIN departments d ON e.department_id = d.id
WHERE d.dept_name = 'Engineering';

// JPQL — talks to entities/fields (portable across DBs)
TypedQuery<Employee> q = em.createQuery(
    "SELECT e FROM Employee e " +
    "JOIN e.department d " +
    "WHERE d.name = :deptName", Employee.class);
q.setParameter("deptName", "Engineering");
List<Employee> result = q.getResultList();
```

Key differences:
- JPQL uses entity names (default: class name) and field names, not table/column names.
- Fully **database-agnostic** — works across MySQL, PostgreSQL, Oracle, etc.
- No `SELECT *` — use `SELECT e` to load the whole entity.

---

### 9. What is `CascadeType` and what options are available?

**A:** Cascade propagates an operation from the parent entity to associated children automatically.

| CascadeType | Propagated operation |
|---|---|
| `PERSIST` | `em.persist(parent)` also persists children |
| `MERGE` | `em.merge(parent)` also merges children |
| `REMOVE` | `em.remove(parent)` also removes children |
| `REFRESH` | `em.refresh(parent)` also refreshes children |
| `DETACH` | `em.detach(parent)` also detaches children |
| `ALL` | All of the above |

```java
@OneToMany(mappedBy = "order",
           cascade  = CascadeType.ALL,   // persist/merge/remove flow to items
           orphanRemoval = true)
private List<OrderItem> items = new ArrayList<>();

// Now saving the order also saves all items:
Order order = new Order();
order.addItem(new OrderItem("Widget", 2));
em.persist(order);  // INSERT order + INSERT order_item — no manual persist needed
```

> **Warning:** `CascadeType.REMOVE` on `@ManyToMany` is almost always wrong — it will delete shared entities.

---

### 10. What does `orphanRemoval = true` do?

**A:** When an entity is **removed from the parent's collection**, `orphanRemoval` automatically issues a `DELETE` for that child — without you calling `em.remove()` explicitly.

```java
// With orphanRemoval = true on Department.employees:
department.getEmployees().remove(employee);
// At flush: DELETE FROM employees WHERE id = ?  ← automatic

// Without orphanRemoval, the same line just clears the FK:
// UPDATE employees SET department_id = NULL WHERE id = ?
```

- Use it when children have no meaning without their parent (composition).
- Combines naturally with `CascadeType.ALL`.
- Functionally equivalent to `CascadeType.REMOVE` triggered by collection removal rather than `em.remove(parent)`.

---

## 🟡 Mid

### 11. Explain the N+1 query problem and how to solve it.

**A:** N+1 happens when you load N parent entities and then trigger **one extra query per parent** to load their lazy collection — resulting in 1 + N queries instead of 1.

```java
// N+1 scenario
List<Department> depts = em.createQuery(
    "SELECT d FROM Department d", Department.class).getResultList(); // 1 query

for (Department d : depts) {
    System.out.println(d.getEmployees().size()); // N queries — one per dept!
}
```

**Solution 1 — JOIN FETCH (JPQL)**
```java
List<Department> depts = em.createQuery(
    "SELECT DISTINCT d FROM Department d JOIN FETCH d.employees",
    Department.class).getResultList(); // 1 query with JOIN
```

**Solution 2 — `@EntityGraph`**
```java
@EntityGraph(attributePaths = {"employees"})
@Query("SELECT d FROM Department d")
List<Department> findAllWithEmployees();
```

**Solution 3 — `@BatchSize` (Hibernate)**
```java
@OneToMany(mappedBy = "department", fetch = FetchType.LAZY)
@BatchSize(size = 25)  // loads 25 collections in one IN-clause query
private List<Employee> employees;
```

**Solution 4 — DTO projection (avoids entity entirely)**
```java
@Query("SELECT new com.example.dto.DeptSummary(d.name, COUNT(e)) " +
       "FROM Department d LEFT JOIN d.employees e GROUP BY d.name")
List<DeptSummary> findDeptSummaries();
```

> **Rule of thumb:** `JOIN FETCH` for a known single collection; `@BatchSize` or `@EntityGraph` for dynamic/optional fetching; DTO projection when you only need a subset of fields.

---

### 12. What is `@NamedQuery` and when would you use it?

**A:** `@NamedQuery` pre-compiles a JPQL query at startup, validates it against the schema, and caches the compiled form — avoiding parse overhead on every execution.

```java
@Entity
@NamedQuery(
    name  = "Employee.findByDepartment",
    query = "SELECT e FROM Employee e WHERE e.department.name = :deptName"
)
@NamedQuery(
    name  = "Employee.findActive",
    query = "SELECT e FROM Employee e WHERE e.active = true ORDER BY e.name"
)
// Multiple: use @NamedQueries({…})
public class Employee { … }

// Usage
TypedQuery<Employee> q = em.createNamedQuery(
    "Employee.findByDepartment", Employee.class);
q.setParameter("deptName", "Engineering");
List<Employee> result = q.getResultList();
```

Benefits:
- **Parse-time validation** — startup fails if JPQL is wrong.
- **Slightly faster** execution (pre-parsed).
- Centralised query definitions on the entity.

Drawback: less flexible than `@Query` in Spring Data JPA; cannot be dynamically composed.

---

### 13. How does the Criteria API work? When would you prefer it over JPQL?

**A:** The Criteria API builds queries programmatically through a type-safe, object-oriented API. Use it when query structure is **dynamic** (optional filters, user-driven sorting).

```java
CriteriaBuilder  cb    = em.getCriteriaBuilder();
CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);
Root<Employee>   root  = cq.from(Employee.class);

// Dynamic predicate building
List<Predicate> predicates = new ArrayList<>();

if (deptName != null) {
    predicates.add(cb.equal(root.get("department").get("name"), deptName));
}
if (minSalary != null) {
    predicates.add(cb.greaterThanOrEqualTo(root.get("salary"), minSalary));
}

cq.select(root)
  .where(predicates.toArray(new Predicate[0]))
  .orderBy(cb.asc(root.get("name")));

List<Employee> result = em.createQuery(cq).getResultList();
```

| | JPQL | Criteria API |
|---|---|---|
| Readability | High (string-based) | Verbose |
| Type safety | None (strings) | Compile-time with metamodel |
| Dynamic queries | Awkward string concat | Natural |
| IDE refactoring | Breaks silently | Refactor-safe |

> For Spring Data JPA, the **Specification pattern** (see Q28) wraps the Criteria API in a composable, reusable abstraction.

---

### 14. What is `@Embeddable` / `@Embedded` and when should you use it?

**A:** An `@Embeddable` class is a value type — its fields are stored **in the same table** as the owning entity but modelled as a separate Java class.

```java
@Embeddable
public class Address {
    private String street;
    private String city;

    @Column(name = "zip_code")
    private String zipCode;
    private String country;
}

@Entity
public class Employee {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "home_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "home_city"))
    })
    private Address homeAddress;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "work_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "work_city"))
    })
    private Address workAddress;
}
```

Use `@Embeddable` when:
- The type is a **value object** (no identity of its own).
- Reusing the same structure in multiple entities.
- You want a richer domain model without an extra table.

---

### 15. Describe the three `@Inheritance` mapping strategies.

**A:**

**1. `SINGLE_TABLE` (default)**  
All subclasses in one table; a discriminator column differentiates rows.
```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "vehicle_type")
public abstract class Vehicle { @Id … private Long id; private String model; }

@Entity
@DiscriminatorValue("CAR")
public class Car extends Vehicle { private int doors; }

@Entity
@DiscriminatorValue("TRUCK")
public class Truck extends Vehicle { private double payload; }
```
Pros: fast queries (no JOINs), polymorphic queries simple.  
Cons: nullable columns for subclass-only fields; can get wide.

**2. `JOINED`**  
One table per class; subclass rows JOINed to base table via PK/FK.
```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Vehicle { … }

@Entity
@PrimaryKeyJoinColumn(name = "vehicle_id")
public class Car extends Vehicle { private int doors; }
```
Pros: normalised, no nulls.  
Cons: JOIN on every query; slower for deep hierarchies.

**3. `TABLE_PER_CLASS`**  
Each concrete class gets its own complete table (no shared base table).
```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public abstract class Vehicle { … }

@Entity
public class Car extends Vehicle { … } // has ALL Vehicle + Car columns
```
Pros: no JOINs for single-type queries.  
Cons: polymorphic queries use UNION ALL (very slow); requires `GenerationType.SEQUENCE` or `UUID` (not `IDENTITY`).

---

### 16. How does optimistic locking work with `@Version`?

**A:** Optimistic locking assumes conflicts are rare and detects them at commit time by comparing a version stamp.

```java
@Entity
public class Product {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private int stock;

    @Version   // Hibernate manages this automatically
    private Long version;
}
```

What Hibernate does:
```sql
-- Load: version = 3
SELECT id, name, stock, version FROM product WHERE id = 1;

-- Update includes version check:
UPDATE product
SET stock = 99, version = 4        -- increments version
WHERE id = 1 AND version = 3;      -- if 0 rows updated → conflict!
```

If another transaction committed between the SELECT and the UPDATE, the WHERE matches 0 rows → Hibernate throws `OptimisticLockException` → caller retries or shows a conflict message to the user.

Supported version types: `int`, `Integer`, `long`, `Long`, `short`, `Short`, `Instant`, `LocalDateTime`.

---

### 17. What is pessimistic locking and when should you use it?

**A:** Pessimistic locking acquires a DB-level lock **immediately** on read, preventing concurrent modifications.

```java
// PESSIMISTIC_READ — shared lock, others can read but not write
Product p = em.find(Product.class, 1L,
                    LockModeType.PESSIMISTIC_READ);

// PESSIMISTIC_WRITE — exclusive lock (SELECT … FOR UPDATE)
Product p = em.find(Product.class, 1L,
                    LockModeType.PESSIMISTIC_WRITE);

// With timeout (PostgreSQL / Oracle)
Map<String, Object> hints = Map.of("jakarta.persistence.lock.timeout", 3000);
Product p = em.find(Product.class, 1L,
                    LockModeType.PESSIMISTIC_WRITE, hints);

// In JPQL
em.createQuery("SELECT p FROM Product p WHERE p.id = :id", Product.class)
  .setParameter("id", 1L)
  .setLockMode(LockModeType.PESSIMISTIC_WRITE)
  .getSingleResult();
```

Use pessimistic locking when:
- Conflicts are **frequent** (high contention on the same rows).
- The cost of retrying (optimistic) exceeds the cost of waiting (pessimistic).
- Strict serialisation is required (e.g., inventory reservation, seat booking).

---

### 18. Explain Hibernate's first-level and second-level cache.

**A:**

**First-level cache (L1)**  
- Scope: single `EntityManager` / `Session`.  
- Always enabled, cannot be disabled.  
- Guarantees identity: `em.find(E.class, 1)` twice returns the **same object**.  
- Flushed / closed with the transaction.

**Second-level cache (L2)**  
- Scope: `SessionFactory` / application-wide.  
- Opt-in per entity with `@Cache`.  
- Requires a cache provider (EhCache, Caffeine, Infinispan, Hazelcast).  
- Shared across all sessions; survives transaction boundaries.

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jcache</artifactId>
</dependency>
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>jcache</artifactId>
</dependency>
```

```java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)  // org.hibernate.annotations
public class Product { … }

// Collection cache
@OneToMany(mappedBy = "product")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
private List<Review> reviews;
```

```yaml
# application.yml
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: jcache
```

| | L1 | L2 |
|---|---|---|
| Scope | Transaction | Application |
| Enabled | Always | Opt-in |
| Invalidation | Transaction end | Configurable TTL / eviction |
| Hit ratio | High for repeated access | High for read-heavy data |

---

### 19. What are Spring Data JPA repository interfaces and when do you use each?

**A:**

```
Repository (marker)
  └─ CrudRepository<T, ID>          — save, findById, findAll, delete, count
       └─ PagingAndSortingRepository — + findAll(Pageable), findAll(Sort)
            └─ JpaRepository<T, ID>  — + flush, saveAndFlush, deleteInBatch, getReferenceById
```

```java
// Most common starting point — exposes all JPA-specific helpers
public interface EmployeeRepository extends JpaRepository<Employee, Long> { }

// Use PagingAndSortingRepository when you need pagination but not JPA extras
// (e.g., to keep the interface portable to non-JPA stores)
public interface ProductRepository
        extends PagingAndSortingRepository<Product, Long> { }
```

Key differences:
- `CrudRepository` is Spring Data generic — also implemented by MongoDB, Redis, etc.
- `JpaRepository` adds `flush()`, batch delete, and `getReferenceById()` (proxy, no SELECT).
- `PagingAndSortingRepository` sits in between; useful for cross-store portability.

---

### 20. How do derived query methods work in Spring Data JPA?

**A:** Spring Data parses the method name and generates the JPQL at startup.

```java
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // SELECT e FROM Employee e WHERE e.name = ?1
    List<Employee> findByName(String name);

    // SELECT e FROM Employee e WHERE e.department.name = ?1 AND e.salary > ?2
    List<Employee> findByDepartmentNameAndSalaryGreaterThan(
            String deptName, BigDecimal minSalary);

    // SELECT e FROM Employee e WHERE e.active = true ORDER BY e.name ASC
    List<Employee> findByActiveTrueOrderByNameAsc();

    // Pagination
    Page<Employee> findByDepartmentName(String deptName, Pageable pageable);

    // Existence check
    boolean existsByEmail(String email);

    // Count
    long countByDepartmentName(String deptName);

    // Delete
    void deleteByActiveFalse();
}
```

Supported keywords: `And`, `Or`, `Is`/`Equals`, `Between`, `LessThan`, `GreaterThan`, `Like`, `Containing`, `StartingWith`, `EndingWith`, `In`, `NotIn`, `True`, `False`, `IsNull`, `IsNotNull`, `IgnoreCase`, `OrderBy`, `Top`/`First`, …

> Use derived methods for simple, stable queries. Prefer `@Query` when the generated JPQL would be ambiguous or complex.

---

### 21. How does `@Query` work in Spring Data JPA?

**A:** `@Query` lets you write custom JPQL or native SQL directly on a repository method.

```java
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // JPQL
    @Query("SELECT e FROM Employee e WHERE e.department.name = :dept " +
           "AND e.salary BETWEEN :min AND :max")
    List<Employee> findByDeptAndSalaryRange(
            @Param("dept") String dept,
            @Param("min")  BigDecimal min,
            @Param("max")  BigDecimal max);

    // Native SQL — bypass JPQL limitations
    @Query(value = "SELECT * FROM employees WHERE MATCH(name) AGAINST (?1)",
           nativeQuery = true)
    List<Employee> fullTextSearch(String term);

    // Modifying query — requires @Modifying + @Transactional
    @Modifying
    @Transactional
    @Query("UPDATE Employee e SET e.active = false WHERE e.lastLogin < :cutoff")
    int deactivateInactiveUsers(@Param("cutoff") LocalDate cutoff);

    // Pagination with native query — must supply countQuery
    @Query(value     = "SELECT * FROM employees WHERE department_id = ?1",
           countQuery= "SELECT COUNT(*) FROM employees WHERE department_id = ?1",
           nativeQuery= true)
    Page<Employee> findByDepartmentId(Long deptId, Pageable pageable);
}
```

---

### 22. What are projections in Spring Data JPA?

**A:** Projections retrieve a **subset of fields** without loading the full entity — reducing data transfer and mapping overhead.

**Interface projection (closed)**
```java
public interface EmployeeSummary {
    String getName();
    String getEmail();
    // Nested projection
    DepartmentInfo getDepartment();

    interface DepartmentInfo {
        String getName();
    }
}

List<EmployeeSummary> findByActiveTrue(); // Spring generates a proxy
```

**DTO (class-based) projection**
```java
public record EmployeeDto(String name, String email) {}

@Query("SELECT new com.example.dto.EmployeeDto(e.name, e.email) " +
       "FROM Employee e WHERE e.department.name = :dept")
List<EmployeeDto> findDtoByDept(@Param("dept") String dept);
```

**Dynamic projection**
```java
<T> List<T> findByDepartmentName(String deptName, Class<T> type);

// Caller decides:
List<EmployeeSummary> summaries = repo.findByDepartmentName("Eng", EmployeeSummary.class);
List<Employee>        entities  = repo.findByDepartmentName("Eng", Employee.class);
```

DTO projections are fastest (no proxying), interface projections are convenient for ad-hoc views.

---

## 🔴 Senior

### 23. How does the `@EntityGraph` annotation work? Compare it to JOIN FETCH.

**A:** `@EntityGraph` defines a **fetch plan** that overrides the default `FetchType` for a specific query without rewriting JPQL.

```java
// Define on entity
@Entity
@NamedEntityGraph(
    name             = "Employee.withDepartmentAndSkills",
    attributeNodes   = {
        @NamedAttributeNode("department"),
        @NamedAttributeNode(value = "skills", subgraph = "skills-subgraph")
    },
    subgraphs = @NamedSubgraph(
        name  = "skills-subgraph",
        attributeNodes = @NamedAttributeNode("category")
    )
)
public class Employee { … }

// Use in repository
@EntityGraph(value = "Employee.withDepartmentAndSkills")
List<Employee> findByActiveTrue();

// Inline (ad-hoc, no @NamedEntityGraph needed)
@EntityGraph(attributePaths = {"department", "skills.category"})
List<Employee> findBySalaryGreaterThan(BigDecimal min);
```

**Comparison with JOIN FETCH:**

| | `JOIN FETCH` | `@EntityGraph` |
|---|---|---|
| JPQL change | Yes | No |
| Reusable | Per-query | Defined once, reused |
| Works with derived methods | ✗ | ✓ |
| Multiple collections | Cartesian explosion risk | Same risk — use separate queries |

> **Cartesian product warning:** fetching two collections (`orders` + `tags`) in a single query produces rows² results. Split into two queries or use `@BatchSize`.

---

### 24. Describe the Specification pattern in Spring Data JPA.

**A:** `Specification<T>` wraps a single Criteria API predicate. Multiple specifications compose with `and()`, `or()`, `not()` — enabling **dynamic, reusable, testable** query fragments.

```java
// 1. Define specifications as static factory methods
public class EmployeeSpecs {

    public static Specification<Employee> hasDepartment(String dept) {
        return (root, query, cb) ->
            dept == null ? null :
            cb.equal(root.get("department").get("name"), dept);
    }

    public static Specification<Employee> isActive() {
        return (root, query, cb) -> cb.isTrue(root.get("active"));
    }

    public static Specification<Employee> salaryAtLeast(BigDecimal min) {
        return (root, query, cb) ->
            min == null ? null :
            cb.greaterThanOrEqualTo(root.get("salary"), min);
    }
}

// 2. Repository extends JpaSpecificationExecutor
public interface EmployeeRepository
        extends JpaRepository<Employee, Long>,
                JpaSpecificationExecutor<Employee> { }

// 3. Compose at runtime
Specification<Employee> spec = Specification
    .where(EmployeeSpecs.isActive())
    .and(EmployeeSpecs.hasDepartment("Engineering"))
    .and(EmployeeSpecs.salaryAtLeast(new BigDecimal("80000")));

Page<Employee> page = repo.findAll(spec, PageRequest.of(0, 20,
                                        Sort.by("name")));
```

Benefits over `@Query`: composable, unit-testable, no string concatenation, no conditional JPQL logic.

---

### 25. How does Spring Data JPA auditing work?

**A:** Enable `@EnableJpaAuditing` and annotate fields with `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy`.

```java
// 1. Enable
@SpringBootApplication
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class App { … }

// 2. Provide current user (for @CreatedBy / @LastModifiedBy)
@Bean
public AuditorAware<String> auditorProvider() {
    return () -> Optional.ofNullable(
        SecurityContextHolder.getContext()
                             .getAuthentication()
                             .getName());
}

// 3. Base entity (or mix directly on entity)
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class Auditable {

    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;

    @CreatedBy
    @Column(updatable = false)
    private String createdBy;

    @LastModifiedBy
    private String updatedBy;
}

@Entity
public class Employee extends Auditable {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
}
```

---

### 26. How do you implement soft delete with Hibernate?

**A:** Use `@SQLDelete` to override the DELETE SQL and `@Where` (deprecated in 6.x; use `@SQLRestriction` in Hibernate 6.3+) to filter queries automatically.

```java
@Entity
@SQLDelete(sql = "UPDATE employees SET deleted_at = NOW() WHERE id = ?")
@SQLRestriction("deleted_at IS NULL")   // Hibernate 6.3+ (@Where in older versions)
public class Employee {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Column(name = "deleted_at")
    private Instant deletedAt;
}

// em.remove(employee) now issues:
// UPDATE employees SET deleted_at = NOW() WHERE id = ?
// instead of DELETE FROM employees WHERE id = ?

// All queries automatically append: AND deleted_at IS NULL
```

For Spring Data JPA repositories, calling `delete()` triggers `@SQLDelete`. `findAll()` and `findById()` automatically respect `@SQLRestriction`.

To occasionally query **including** deleted records, use native SQL or a separate DTO query without the restriction.

---

### 27. What are Hibernate Filters and how do they work?

**A:** Hibernate Filters are **session-scoped, parameterised WHERE clauses** attached to entities or collections. They are defined statically but enabled/disabled (and parameterised) at runtime.

```java
// 1. Define the filter
@FilterDef(
    name       = "tenantFilter",
    parameters = @ParamDef(name = "tenantId", type = Long.class)
)
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
@Entity
public class Invoice { … }

// 2. Enable per session
Session session = em.unwrap(Session.class);
session.enableFilter("tenantFilter")
       .setParameter("tenantId", currentTenantId);

// All Invoice queries in this session now include: AND tenant_id = ?
List<Invoice> invoices = em.createQuery(
    "SELECT i FROM Invoice i", Invoice.class).getResultList();

// 3. Disable when done
session.disableFilter("tenantFilter");
```

Unlike `@SQLRestriction`, filters are dynamic — you can enable/disable them per request. Common use cases: multi-tenancy, soft delete, locale filtering.

---

### 28. How does QueryDSL integrate with Spring Data JPA?

**A:** QueryDSL generates type-safe `Q`-classes from entities at compile time (via APT) and provides a fluent, IDE-friendly API for building queries.

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.querydsl</groupId>
    <artifactId>querydsl-jpa</artifactId>
    <classifier>jakarta</classifier>
</dependency>
<!-- APT plugin generates QEmployee, QDepartment, … -->
```

```java
// Repository extends QuerydslPredicateExecutor
public interface EmployeeRepository
        extends JpaRepository<Employee, Long>,
                QuerydslPredicateExecutor<Employee> { }

// Query using generated Q-class
QEmployee e    = QEmployee.employee;
QDepartment d  = QDepartment.department;

BooleanExpression predicate = e.active.isTrue()
    .and(e.department.name.eq("Engineering"))
    .and(e.salary.goe(new BigDecimal("70000")));

Iterable<Employee> result = employeeRepo.findAll(predicate,
    QSort.by(e.name.asc()));

// Complex join with JPAQueryFactory
JPAQueryFactory factory = new JPAQueryFactory(em);

List<EmployeeDto> dtos = factory
    .select(Projections.constructor(EmployeeDto.class,
                e.name, e.email, d.name))
    .from(e)
    .join(e.department, d)
    .where(predicate)
    .orderBy(e.name.asc())
    .fetch();
```

Advantages over Specification: more readable for complex queries; type-safe navigation (`e.department.name`); better IDE completion.

---

### 29. How does HikariCP integrate with Spring Boot and what are the key settings?

**A:** Spring Boot auto-configures HikariCP as the default JDBC connection pool since Boot 2.0. Zero explicit configuration needed for basic use — tune it for production.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: app
    password: secret
    hikari:
      # Pool sizing — start: (2 * CPU_CORES) + effective_spindle_count
      maximum-pool-size: 20       # max connections in pool
      minimum-idle: 5             # min idle connections maintained
      connection-timeout: 30000   # ms to wait for a connection before exception
      idle-timeout: 600000        # ms before idle connection is removed (10 min)
      max-lifetime: 1800000       # ms max connection lifetime (30 min, < DB timeout)
      keepalive-time: 60000       # ms to ping idle connections (prevents firewall drops)
      pool-name: MyAppPool
      # Validation
      connection-test-query: SELECT 1  # only needed for drivers lacking JDBC4 isValid()
```

```java
// Programmatic (rare — prefer YAML)
@Bean
public DataSource dataSource() {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:postgresql://localhost/mydb");
    config.setUsername("app");
    config.setPassword("secret");
    config.setMaximumPoolSize(20);
    config.addDataSourceProperty("cachePrepStmts", "true");
    config.addDataSourceProperty("prepStmtCacheSize", "250");
    return new HikariDataSource(config);
}
```

Key tuning insight: **pool size ≠ more connections = faster**. For CPU-bound work, `(2 × cores) + 1` is often optimal (HikariCP's own recommendation).

---

### 30. What is `spring.jpa.hibernate.ddl-auto` and which value suits which environment?

**A:**

| Value | Behaviour |
|---|---|
| `none` | No schema action — safest for production |
| `validate` | Validates schema against entities on startup; fails if mismatch |
| `update` | Adds new columns/tables; never drops — risky for production |
| `create` | Drops and recreates schema on every startup |
| `create-drop` | Like `create` but also drops on shutdown (ideal for tests) |

```yaml
# Dev
spring.jpa.hibernate.ddl-auto: update

# Test
spring.jpa.hibernate.ddl-auto: create-drop

# Production — let Flyway/Liquibase own the schema
spring.jpa.hibernate.ddl-auto: validate
```

> **Never** use `create` or `update` in production — they bypass migration tracking and can silently corrupt data. Use `validate` so startup fails fast if the schema drifts.

---

### 31. How do Flyway and Liquibase integrate with Spring Boot / JPA?

**A:** Both tools manage **versioned, repeatable schema migrations** as files checked into source control.

**Flyway:**
```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```
```
src/main/resources/db/migration/
  V1__create_employees.sql
  V2__add_salary_column.sql
  V3__create_index.sql
```
```sql
-- V2__add_salary_column.sql
ALTER TABLE employees ADD COLUMN salary NUMERIC(15,2) DEFAULT 0;
```
```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true   # for existing DB without Flyway history
  jpa:
    hibernate:
      ddl-auto: validate        # let Flyway own schema; JPA only validates
```

**Liquibase:**
```xml
<dependency>
    <groupId>org.liquibase</groupId>
    <artifactId>liquibase-core</artifactId>
</dependency>
```
```yaml
# src/main/resources/db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: soroush
      changes:
        - createTable:
            tableName: employees
            columns:
              - column: { name: id,   type: BIGINT, autoIncrement: true, constraints: { primaryKey: true } }
              - column: { name: name, type: VARCHAR(120), constraints: { nullable: false } }
```

| | Flyway | Liquibase |
|---|---|---|
| Format | SQL (or Java) | XML, YAML, JSON, SQL |
| Rollback | Manual (Pro for auto) | Built-in `rollback` |
| Complexity | Simpler, SQL-native | More powerful, DB-agnostic |

---

### 32. Explain `@OneToOne` mapping and the N+1 pitfall specific to it.

**A:**

```java
@Entity
public class Employee {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Owning side — holds the FK
    @OneToOne(fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    @JoinColumn(name = "passport_id", unique = true)
    private Passport passport;
}

@Entity
public class Passport {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Inverse side
    @OneToOne(mappedBy = "passport", fetch = FetchType.LAZY)
    private Employee employee;
    private String number;
}
```

**The N+1 trap unique to `@OneToOne` inverse side:**  
Hibernate **cannot proxy** the inverse side of a `@OneToOne` because it needs to check whether the association is null — which requires a query. Even with `LAZY`, accessing `passport.getEmployee()` fires a SELECT.

Fix: avoid the bidirectional `@OneToOne` inverse side, or use `@LazyToOne(LazyToOneOption.NO_PROXY)` with bytecode enhancement (Hibernate-specific).

---

### 33. What is `@ManyToMany` and how do you map it correctly?

**A:**

```java
@Entity
public class Student {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @ManyToMany
    @JoinTable(
        name               = "student_course",
        joinColumns        = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>(); // Set, not List — avoids duplicates
}

@Entity
public class Course {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;

    @ManyToMany(mappedBy = "courses")
    private Set<Student> students = new HashSet<>();
}
```

**When the join table needs extra columns:** promote it to an entity.

```java
@Entity
@Table(name = "student_course")
public class Enrollment {
    @EmbeddedId
    private EnrollmentId id;

    @ManyToOne @MapsId("studentId")
    private Student student;

    @ManyToOne @MapsId("courseId")
    private Course course;

    private LocalDate enrolledOn;
    private String grade;
}

@Embeddable
public class EnrollmentId implements Serializable {
    private Long studentId;
    private Long courseId;
}
```

> Always use `Set` (not `List`) for `@ManyToMany` — Hibernate deletes and re-inserts all rows when you remove from a `List`.

---

## 🏛️ Architect

### 34. How does multi-tenancy work in Hibernate? Compare the three strategies.

**A:** Multi-tenancy isolates data for multiple customers within the same application. Hibernate 6 supports three strategies configured via `MultiTenancyStrategy`.

**Strategy 1 — Separate Database**
```java
// Each tenant gets its own database
public class DatabaseTenantConnectionProvider
        implements MultiTenantConnectionProvider<String> {

    @Override
    public Connection getConnection(String tenantId) throws SQLException {
        DataSource ds = dataSources.get(tenantId); // lookup per tenant
        return ds.getConnection();
    }
}
```
Best isolation; highest ops cost.

**Strategy 2 — Separate Schema**
```java
public class SchemaTenantConnectionProvider
        implements MultiTenantConnectionProvider<String> {

    @Override
    public Connection getConnection(String tenantId) throws SQLException {
        Connection c = defaultDataSource.getConnection();
        c.createStatement().execute("SET search_path TO " + tenantId); // PostgreSQL
        return c;
    }
}
```
One DB; isolated schemas. Good balance.

**Strategy 3 — Discriminator Column (Shared Schema)**
```java
// Hibernate 6 introduces @TenantId for discriminator-based multi-tenancy
@Entity
public class Invoice {
    @Id @GeneratedValue
    private Long id;

    @TenantId   // Hibernate 6 — automatically filtered per tenant context
    private String tenantId;

    private BigDecimal amount;
}
```
Lowest isolation; simplest ops; highest data-leak risk if filter disabled.

**Wiring the current tenant:**
```java
public class CurrentTenantResolver implements CurrentTenantIdentifierResolver<String> {
    @Override
    public String resolveCurrentTenantIdentifier() {
        return TenantContext.getCurrentTenant(); // ThreadLocal set by filter/interceptor
    }
    @Override
    public boolean validateExistingCurrentSessions() { return true; }
}
```

```yaml
spring.jpa.properties:
  hibernate.multiTenancy: SCHEMA           # DATABASE | SCHEMA | DISCRIMINATOR
  hibernate.tenant_identifier_resolver: com.example.CurrentTenantResolver
  hibernate.multi_tenant_connection_provider: com.example.SchemaTenantConnectionProvider
```

---

### 35. How do you tune Hibernate for high-throughput batch processing?

**A:** The default entity-per-INSERT approach is unsuitable for bulk operations. Layer several optimisations:

```yaml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50              # send 50 INSERTs/UPDATEs per round-trip
          batch_versioned_data: true  # enable batching for versioned entities
        order_inserts: true           # group same-table INSERTs together
        order_updates: true
        generate_statistics: true     # monitor hit ratios in dev
```

```java
@Service
@Transactional
public class BulkEmployeeService {

    private static final int BATCH_SIZE = 50;

    @PersistenceContext private EntityManager em;

    public void importEmployees(List<EmployeeDto> dtos) {
        for (int i = 0; i < dtos.size(); i++) {
            Employee e = mapper.toEntity(dtos.get(i));
            em.persist(e);

            if (i % BATCH_SIZE == 0 && i > 0) {
                em.flush();   // execute the batch
                em.clear();   // evict from 1st-level cache — prevents OOM
            }
        }
    }
}
```

**Bulk UPDATE/DELETE — bypass entity lifecycle entirely:**
```java
// JPQL bulk update (no entity loading, no dirty checking)
int updated = em.createQuery(
    "UPDATE Employee e SET e.active = false WHERE e.lastLogin < :cutoff")
    .setParameter("cutoff", LocalDate.now().minusYears(2))
    .executeUpdate();

// Spring Data JPA
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("DELETE FROM Employee e WHERE e.active = false")
int deleteInactiveEmployees();
```

**StatelessSession (Hibernate-specific) — zero overhead:**
```java
StatelessSession ss = sessionFactory.openStatelessSession();
Transaction tx = ss.beginTransaction();
// No 1st-level cache, no dirty checking, no interceptors
ss.insert(employee);
tx.commit();
ss.close();
```

Checklist for batch tuning:
1. `SEQUENCE` generator with large `allocationSize` (avoids per-row sequence calls).
2. `batch_size` ≥ 50 with `order_inserts/order_updates = true`.
3. `flush()` + `clear()` every batch to keep heap stable.
4. Use `StatelessSession` for pure write-only ETL.
5. Profile with `generate_statistics: true` or Datasource Proxy.

---

### 36. How does Hibernate's dirty-checking mechanism work, and how can you optimise it?

**A:** At flush time Hibernate compares each managed entity's current state against its **snapshot** (taken at load/persist time) field-by-field. Any difference triggers an UPDATE.

**Default mechanism (reflection-based):**
```
flush() called
  │
  ├─ for each managed entity:
  │    compare current fields vs. snapshot
  │    if dirty: add to UPDATE queue
  │
  └─ execute batched SQL
```

**Problem:** With thousands of managed entities, snapshot comparison is O(N × fields).

**Optimisation 1 — Bytecode enhancement (compile-time instrumentation)**
```xml
<plugin>
    <groupId>org.hibernate.orm.tooling</groupId>
    <artifactId>hibernate-enhance-maven-plugin</artifactId>
    <configuration>
        <enableDirtyTracking>true</enableDirtyTracking>
        <enableLazyInitialization>true</enableLazyInitialization>
    </configuration>
</plugin>
```
Entities track their own dirty fields — no snapshot scan needed.

**Optimisation 2 — `@DynamicUpdate`**
```java
@Entity
@DynamicUpdate  // generates UPDATE with only changed columns, not all columns
public class Employee { … }
```
Reduces payload and allows partial DB-level updates (better index usage, fewer lock conflicts).

**Optimisation 3 — `@SelectBeforeUpdate`**
```java
@Entity
@SelectBeforeUpdate  // only update if state actually changed — prevents spurious UPDATEs
public class Employee { … }
```
Useful for detached entities re-merged when most are unmodified.

**Optimisation 4 — Keep persistence context small**
```java
em.clear(); // evict all — nothing to dirty-check
em.detach(entity); // evict one entity
```

---

### 37. Describe Hibernate interceptors and event listeners — when and how would you use them?

**A:** Both provide hooks into the entity lifecycle; they differ in granularity and use-case.

**Interceptors** (Hibernate-level, session or factory scope):
```java
public class AuditInterceptor extends EmptyInterceptor {

    @Override
    public boolean onFlushDirty(Object entity, Serializable id,
                                Object[] currentState, Object[] previousState,
                                String[] propertyNames, Type[] types) {
        for (int i = 0; i < propertyNames.length; i++) {
            if ("updatedAt".equals(propertyNames[i])) {
                currentState[i] = Instant.now();
                return true; // state modified
            }
        }
        return false;
    }

    @Override
    public boolean onSave(Object entity, Serializable id,
                          Object[] state, String[] propertyNames, Type[] types) {
        for (int i = 0; i < propertyNames.length; i++) {
            if ("createdAt".equals(propertyNames[i])) {
                state[i] = Instant.now();
                return true;
            }
        }
        return false;
    }
}

// Register on SessionFactory
sessionFactory.withOptions().interceptor(new AuditInterceptor()).openSession();
```

**Event Listeners** (finer-grained, replaces interceptors in modern Hibernate):
```java
public class SoftDeleteEventListener implements DeleteEventListener {

    @Override
    public void onDelete(DeleteEvent event) {
        Object entity = event.getObject();
        if (entity instanceof SoftDeletable sd) {
            sd.setDeletedAt(Instant.now());
            // Cancel the actual DELETE — just mark the entity dirty
            event.getSession().merge(entity);
            throw new HibernateException("soft delete intercepted"); // or handle differently
        }
    }
}

// Registration via Integrator SPI (Boot auto-detects if @Component + correct interface)
```

**JPA Entity Listeners** (portable, simpler):
```java
@Entity
@EntityListeners(AuditEntityListener.class)
public class Invoice { … }

public class AuditEntityListener {
    @PrePersist  void onPrePersist(Object o) { /* set createdAt */ }
    @PreUpdate   void onPreUpdate(Object o)  { /* set updatedAt */ }
    @PostRemove  void onPostRemove(Object o) { /* emit audit event */ }
}
```

Use JPA listeners for portable audit/event use-cases; Hibernate interceptors/event listeners for deeper hooks (state mutation, custom flush logic, schema-level cross-cutting concerns).

---

### 38. How would you design a read-scalable JPA layer with CQRS?

**A:** Separate the **command model** (JPA entities, full lifecycle) from the **query model** (lightweight read projections, possibly read replicas).

```
                   ┌──────────────────────────┐
Write Path         │  Command Service          │
(transactional)    │  EmployeeCommandService   │──► JpaRepository (primary DB)
                   │  @Transactional           │    entity lifecycle, validation
                   └──────────────────────────┘

                   ┌──────────────────────────┐
Read Path          │  Query Service            │
(read-only, fast)  │  EmployeeQueryService     │──► Read replica DataSource
                   │  @Transactional(readOnly) │    DTO projections / native SQL
                   └──────────────────────────┘
```

```java
// Read-only transaction — Hibernate skips dirty checking, flush mode = NEVER
@Transactional(readOnly = true)
public List<EmployeeSummaryDto> getEngineeringDashboard() {
    return employeeRepository.findDashboardData("Engineering");
}

// Direct JDBC for complex reporting — bypass ORM entirely
@Repository
public class EmployeeReportRepository {

    private final JdbcTemplate jdbc;

    public List<ReportRow> monthlyHires(YearMonth month) {
        return jdbc.query(
            """
            SELECT d.name dept, COUNT(*) hires
            FROM employees e JOIN departments d ON e.department_id = d.id
            WHERE DATE_TRUNC('month', e.hired_at) = ?
            GROUP BY d.name ORDER BY hires DESC
            """,
            (rs, i) -> new ReportRow(rs.getString("dept"), rs.getLong("hires")),
            month.atDay(1));
    }
}

// Route to read replica using AbstractRoutingDataSource
public class ReadWriteRoutingDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
               ? "READ" : "WRITE";
    }
}
```

Key architectural decisions:
1. `@Transactional(readOnly = true)` signals Spring to set flush mode NEVER and optionally route to replica.
2. Skip JPA entirely for complex aggregations — use `JdbcTemplate` or `jOOQ`.
3. Eventual consistency: if the replica lags, the read path may see stale data — design the UX accordingly.
4. Event-driven projection updates (Outbox pattern) decouple the write model completely from read views.

---

### 39. How do you handle the `LazyInitializationException` systematically in a layered architecture?

**A:** `LazyInitializationException` (LIE) is thrown when a lazy association is accessed outside a persistence context. The fix depends on the layer.

**Root causes:**
```
@Transactional method returns entity          ← persistence context closes here
    │
Controller / View receives entity
    │
entity.getLazyCollection().size()            ← BOOM: LazyInitializationException
```

**Fix 1 — Fetch everything needed inside the transaction (preferred)**
```java
@Transactional(readOnly = true)
public EmployeeDetailView getDetail(Long id) {
    Employee e = repo.findById(id).orElseThrow();
    Hibernate.initialize(e.getSkills());     // explicit initialise
    return mapper.toDetailView(e);           // map to DTO inside transaction
}
```

**Fix 2 — Return DTOs, not entities**
```java
@Query("SELECT new com.example.dto.EmployeeDetail(e.name, e.email, " +
       "e.department.name) FROM Employee e WHERE e.id = :id")
Optional<EmployeeDetail> findDetailById(@Param("id") Long id);
```
No lazy associations possible on a DTO — the safest approach.

**Fix 3 — Open Session In View (OSIV) — anti-pattern**
```yaml
spring.jpa.open-in-view: false   # DISABLE this — it's on by default in Spring Boot!
```
OSIV keeps the session open through the HTTP request, masking LIE but causing N+1 in the view layer and holding DB connections far too long.

**Fix 4 — `@EntityGraph` or `JOIN FETCH` per use-case**
```java
@EntityGraph(attributePaths = {"skills", "department"})
Optional<Employee> findWithSkillsById(Long id);
```

**Systematic rule:** the service layer owns transaction boundaries. Entities must never escape the transaction — return DTOs or view models to the presentation layer.

---

### 40. What strategies exist for handling large result sets in JPA without OOM?

**A:** Loading millions of rows into a `List` exhausts heap. Use streaming, scrollable results, or pagination.

**Strategy 1 — Stream (JPA / Spring Data)**
```java
// Spring Data — returns a Java Stream; cursor stays open until stream closed
@Query("SELECT e FROM Employee e WHERE e.department.name = :dept")
@QueryHints(@QueryHint(name = HINT_FETCH_SIZE, value = "50"))
Stream<Employee> streamByDepartment(@Param("dept") String dept);

// Must be used inside a transaction and closed
@Transactional(readOnly = true)
public void processAll(String dept) {
    try (Stream<Employee> stream = repo.streamByDepartment(dept)) {
        stream.forEach(this::process); // processes one at a time
    }
}
```

**Strategy 2 — Scrollable results (Hibernate StatelessSession)**
```java
StatelessSession ss = sessionFactory.openStatelessSession();
ScrollableResults<Employee> scroll = ss.createQuery(
    "FROM Employee e", Employee.class)
    .setFetchSize(100)
    .scroll(ScrollMode.FORWARD_ONLY);

while (scroll.next()) {
    process(scroll.get());
}
scroll.close();
ss.close();
```

**Strategy 3 — Keyset (seek) pagination**
```java
// Offset pagination degrades at high pages — use keyset instead
@Query("SELECT e FROM Employee e WHERE e.id > :lastSeenId " +
       "ORDER BY e.id ASC LIMIT :pageSize")
List<Employee> findNextPage(@Param("lastSeenId") Long lastSeenId,
                            @Param("pageSize")   int pageSize);
```

**Strategy 4 — Chunked processing with `Slice`**
```java
Pageable page = PageRequest.of(0, 500);
Slice<Employee> slice;
do {
    slice = repo.findByActiveTrue(page);
    slice.forEach(this::process);
    page = slice.nextPageable();
} while (slice.hasNext());
```

`Slice` avoids the `COUNT(*)` query that `Page` issues; use it when total count is not needed.

---

### 41. How do you prevent and diagnose performance issues in a JPA application?

**A:** Performance problems cluster around three root causes: too many queries, too much data, too many locks.

**Detection toolkit:**
```yaml
# Log slow / all SQL in development
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        generate_statistics: true
        session.events.log.LOG_QUERIES_SLOWER_THAN_MS: 25
logging.level.org.hibernate.SQL: DEBUG
logging.level.org.hibernate.orm.jdbc.bind: TRACE  # log bind parameters (Hibernate 6)
```

**Datasource Proxy (production-safe N+1 detection):**
```java
@Bean
public DataSource dataSource(DataSource original) {
    return ProxyDataSourceBuilder.create(original)
        .name("DS-Proxy")
        .logQueryBySlf4j(SLF4JLogLevel.INFO)
        .countQuery()
        .build();
}
```

**Checklist:**

| Problem | Symptom | Fix |
|---|---|---|
| N+1 | Many small SELECT on same table | JOIN FETCH / @EntityGraph / @BatchSize |
| Cartesian explosion | 1 query but huge ResultSet | Split into separate queries |
| OSIV | DB connections held for request lifetime | `open-in-view: false` |
| Missing index | Slow WHERE / ORDER BY | Analyse query plan, add `@Index` |
| Over-fetching | All columns loaded, only 2 used | DTO projection |
| Under-batching | 1000 individual INSERTs | `batch_size`, `order_inserts` |
| OptimisticLock storms | Frequent `OptimisticLockException` | @Version + retry; or pessimistic lock |
| L2 cache stale reads | Stale data after update | `CacheConcurrencyStrategy.READ_WRITE` |

**Integration test for N+1:**
```java
@Test
void shouldLoadDepartmentsWithoutNPlusOne() {
    // Using datasource-proxy or Hypersistence Utils:
    assertSelectCount(1, () -> {
        departmentService.findAllWithEmployees(); // must issue exactly 1 query
    });
}
```

---

*Generated for the Java interview-questions series · Hibernate 6.x / Spring Data JPA 3.x / Spring Boot 3.x*
