# 🟢 C# — Junior Interview Questions

---

## 1. What is the difference between value types and reference types?

**A:**
- **Value types** (`int`, `bool`, `struct`, `enum`, `float`) — stored on the stack, copied on assignment
- **Reference types** (`class`, `string`, `array`, `delegate`) — stored on the heap, assignment copies the reference

```csharp
int a = 5;
int b = a; // b is a copy
b = 10;
Console.WriteLine(a); // 5 — unaffected

var p1 = new Person { Name = "Alice" };
var p2 = p1; // same reference
p2.Name = "Bob";
Console.WriteLine(p1.Name); // "Bob" — shared reference
```

---

## 2. What is the difference between `==` and `.Equals()`?

**A:**
- `==` for value types compares values
- `==` for reference types compares references (unless overloaded, like `string`)
- `.Equals()` compares values by default for value types; can be overridden for reference types

```csharp
string s1 = "hello";
string s2 = "hello";
Console.WriteLine(s1 == s2);       // true (string overloads ==)
Console.WriteLine(s1.Equals(s2));  // true

object o1 = new object();
object o2 = new object();
Console.WriteLine(o1 == o2);       // false (different references)
```

---

## 3. What are `const` vs `readonly`?

**A:**
- `const` — compile-time constant, must be initialized at declaration, implicitly static, only primitive types
- `readonly` — runtime constant, can be set in constructor, works with any type

```csharp
const double PI = 3.14159;        // compile-time
readonly DateTime Created;         // set in constructor only

public MyClass() {
    Created = DateTime.Now;        // allowed
}
```

---

## 4. What is a `nullable` type?

**A:** Value types can't normally be `null`. The `?` suffix makes them nullable:

```csharp
int? age = null;

if (age.HasValue)
    Console.WriteLine(age.Value);

// Null-coalescing
int result = age ?? 0;

// Null-conditional
string? name = null;
int? len = name?.Length; // null, not exception
```

---

## 5. What is the difference between `abstract class` and `interface`?

**A:**

| | Abstract Class | Interface |
|--|---------------|-----------|
| Multiple inheritance | No | Yes |
| Fields | Yes | No (only properties) |
| Access modifiers | Yes | Public by default |
| Constructors | Yes | No |
| Default implementations | Yes | Yes (C# 8+) |
| Use when | Shared base behavior + partial impl | Contract for unrelated types |

---

## 6. What is the difference between `IEnumerable`, `ICollection`, and `IList`?

**A:**
- `IEnumerable<T>` — iterate only, forward-only (`foreach`)
- `ICollection<T>` — adds Count, Add, Remove, Contains
- `IList<T>` — adds indexer (`list[0]`), Insert, RemoveAt

```csharp
IEnumerable<int> e = new List<int> { 1, 2, 3 };
IList<int> l = new List<int> { 1, 2, 3 };
l[0] = 99; // only available on IList
```

---

## 7. What is LINQ? Give a basic example.

**A:** Language Integrated Query — a declarative way to query collections (and databases via EF):

```csharp
var numbers = new List<int> { 1, 2, 3, 4, 5, 6 };

// Method syntax
var evens = numbers.Where(n => n % 2 == 0).ToList();

// Query syntax
var evens2 = (from n in numbers where n % 2 == 0 select n).ToList();

// Common operators
numbers.Select(n => n * 2)           // transform
numbers.OrderByDescending(n => n)    // sort
numbers.GroupBy(n => n % 2)          // group
numbers.FirstOrDefault(n => n > 4)   // 5
numbers.Sum()                        // 21
```

---

## 8. What is `using` in C#?

**A:** Two meanings:
1. **Namespace import:** `using System;`
2. **Resource management:** ensures `Dispose()` is called on `IDisposable` objects:

```csharp
using (var conn = new SqlConnection(connStr))
{
    conn.Open();
    // conn.Dispose() called automatically, even on exception
}

// Modern using statement (C# 8+)
using var conn = new SqlConnection(connStr); // disposed at end of scope
```

---

## 9. What is the difference between `String` and `StringBuilder`?

**A:**
- `string` is **immutable** — every concatenation creates a new string object
- `StringBuilder` is **mutable** — appends in-place, much faster for many concatenations

```csharp
// Bad for many iterations
string s = "";
for (int i = 0; i < 1000; i++) s += i; // 1000 allocations

// Good
var sb = new StringBuilder();
for (int i = 0; i < 1000; i++) sb.Append(i);
string result = sb.ToString(); // one allocation
```

---

## 10. What is `try-catch-finally`?

**A:**
```csharp
try {
    int result = int.Parse("bad input"); // throws FormatException
}
catch (FormatException ex) {
    Console.WriteLine($"Format error: {ex.Message}");
}
catch (Exception ex) {
    Console.WriteLine($"General error: {ex.Message}");
}
finally {
    Console.WriteLine("Always runs — cleanup here");
}
```

`finally` runs regardless of whether an exception was thrown or caught. Use it for cleanup (though `using` is preferred for `IDisposable`).

---

## 11. What is the difference between `override` and `new` in method declarations?

**A:**
- `override` — replaces the base class virtual method; polymorphism works correctly
- `new` — hides the base method; polymorphism uses the declared type

```csharp
class Base { public virtual void Print() => Console.WriteLine("Base"); }
class Child : Base { public override void Print() => Console.WriteLine("Child"); }
class Shadow : Base { public new void Print() => Console.WriteLine("Shadow"); }

Base b = new Child();
b.Print(); // "Child" — override: runtime type wins

Base s = new Shadow();
s.Print(); // "Base" — new: declared type (Base) wins
```

---

## 12. What are properties in C#?

**A:** Properties are members that expose fields with controlled access via `get`/`set`:

```csharp
class Person {
    private string _name;

    public string Name {
        get => _name;
        set => _name = value ?? throw new ArgumentNullException();
    }

    // Auto-property
    public int Age { get; set; }

    // Read-only auto-property
    public Guid Id { get; } = Guid.NewGuid();
}
```

---

## 13. What is the difference between `Stack` and `Queue`?

**A:**
- `Stack<T>` — LIFO (Last In First Out): `Push`, `Pop`, `Peek`
- `Queue<T>` — FIFO (First In First Out): `Enqueue`, `Dequeue`, `Peek`

```csharp
var stack = new Stack<int>();
stack.Push(1); stack.Push(2);
stack.Pop(); // 2

var queue = new Queue<int>();
queue.Enqueue(1); queue.Enqueue(2);
queue.Dequeue(); // 1
```

---

## 14. What is boxing and unboxing?

**A:** Converting a value type to `object` (boxing) and back (unboxing):

```csharp
int i = 42;
object boxed = i;        // boxing — heap allocation
int unboxed = (int)boxed; // unboxing — cast required
```

**Performance impact:** Boxing causes heap allocation. Avoid in hot paths — use generics (`List<int>` instead of `ArrayList`) to prevent boxing.

---

## 15. What is `params` keyword?

**A:** Allows passing a variable number of arguments:

```csharp
int Sum(params int[] numbers) {
    return numbers.Sum();
}

Sum(1, 2, 3);           // 6
Sum(new int[] {1, 2});  // also valid
```
