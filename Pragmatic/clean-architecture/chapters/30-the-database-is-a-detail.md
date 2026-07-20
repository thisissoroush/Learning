# Chapter 30 — The Database Is a Detail

> *"The database is not the data model. The database is a piece of software — a utility that provides access to the data."*

---

## 🎯 Core Concept

From an architectural perspective, the **database is a detail** — not an architectural element. Your business rules should not know or care which database technology you use.

---

## 🗄️ Why Databases Became So Dominant

Databases exist because **disks are slow**. To work around disk latency, we need indexes, caches, and query schemes. That's it. It's a mechanical problem, not an architectural one.

```
Business Rules ──→ need data ──→ data lives in RAM
                                     ↑
                              loaded from disk via DB
                                  (a detail!)
```

---

## 🔑 The Key Distinction

| Architecturally Significant | Not Architecturally Significant |
|---|---|
| **Data model** (how data is structured) | **Database system** (SQL, NoSQL, files) |
| **Business rules that operate on data** | **Which database vendor you use** |
| **Relationships between entities** | **Query language (SQL, etc.)** |

---

## 🏗️ What Good Architecture Looks Like

```
┌──────────────────────────┐
│     Business Rules       │  ← no mention of SQL, tables, or DBs
└────────────┬─────────────┘
             │ uses interface
┌────────────▼─────────────┐
│   Data Access Interface  │  ← save(), find(), delete()
└────────────┬─────────────┘
             │ implemented by
┌────────────▼─────────────┐
│   Database Component     │  ← MySQL, Postgres, flat files — a plugin
└──────────────────────────┘
```

---

## 💡 Key Takeaways

- The database is a **detail** — treat it like a plugin to your business rules
- Your use cases should neither know nor care about rows, tables, or SQL
- Passing database rows through the system is an architectural error
- The data model is significant; the database system is not
- As RAM grows and disks fade away, this principle becomes even more obvious

---

*← [Back to Clean Architecture](../README.md)*
