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

---

## 16. What is the difference between `struct` and `class` in C#?

**A:**

| | `struct` | `class` |
|--|---------|---------|
| Type | Value type | Reference type |
| Storage | Stack (usually) | Heap |
| Default | Cannot be null | Can be null |
| Inheritance | No | Yes |
| Copy | By value | By reference |

```csharp
struct Point { public int X, Y; }
class Person { public string Name; }

Point p1 = new Point { X = 1, Y = 2 };
Point p2 = p1;   // copy
p2.X = 99;
Console.WriteLine(p1.X); // 1 — unaffected

Person a = new Person { Name = "Alice" };
Person b = a;    // reference copy
b.Name = "Bob";
Console.WriteLine(a.Name); // "Bob" — shared
```

---

## 17. What is the difference between `is` and `as` operators?

**A:**
```csharp
object obj = "hello";

// is — type check with pattern matching (C# 7+)
if (obj is string s)
    Console.WriteLine(s.ToUpper()); // HELLO

// as — safe cast (returns null if incompatible, no exception)
string? s2 = obj as string;
if (s2 != null) Console.WriteLine(s2);

// Direct cast — throws InvalidCastException if wrong type
string s3 = (string)obj;
```

---

## 18. What is `switch` expression (C# 8+)?

**A:**
```csharp
// Traditional switch statement
string result;
switch (day)
{
    case DayOfWeek.Saturday:
    case DayOfWeek.Sunday: result = "Weekend"; break;
    default: result = "Weekday"; break;
}

// Switch expression — concise, returns a value
string result2 = day switch
{
    DayOfWeek.Saturday or DayOfWeek.Sunday => "Weekend",
    _ => "Weekday"
};
```

---

## 19. What is string interpolation and what are raw string literals?

**A:**
```csharp
string name = "Alice";
int age = 30;

// Interpolation
string msg = $"Hello, {name}! You are {age} years old.";

// Format specifiers inside interpolation
decimal price = 9.99m;
string formatted = $"Price: {price:C2}"; // Price: $9.99

// Raw string literals (C# 11+) — no escaping needed
string json = """
    {
        "name": "Alice",
        "age": 30
    }
    """;
```

---

## 20. What are null coalescing and null-conditional operators?

**A:**
```csharp
string? name = null;

// ?? — use right side if left is null
string display = name ?? "Anonymous";

// ??= — assign only if null
name ??= "Default";

// ?. — null conditional: short-circuits to null if left is null
int? len = name?.Length;

// Chaining
string? city = user?.Address?.City;

// With method call
user?.SendEmail();
```

---

## 21. What is pattern matching in C#?

**A:**
```csharp
object shape = new Circle { Radius = 5 };

// Type pattern
if (shape is Circle c)
    Console.WriteLine($"Circle radius: {c.Radius}");

// Switch expression with patterns
double area = shape switch
{
    Circle { Radius: var r }                   => Math.PI * r * r,
    Rectangle { Width: var w, Height: var h }  => w * h,
    _ => throw new ArgumentException("Unknown shape")
};

// Relational patterns
string category = score switch
{
    >= 90 => "A",
    >= 80 => "B",
    >= 70 => "C",
    _     => "F"
};
```

---

## 22. What is `yield return` in C#?

**A:** `yield return` creates an iterator — produces values lazily without building a full collection:

```csharp
IEnumerable<int> EvenNumbers(int max)
{
    for (int i = 0; i <= max; i += 2)
        yield return i; // suspends, resumes on next MoveNext()
}

foreach (var n in EvenNumbers(10))
    Console.WriteLine(n); // 0, 2, 4, 6, 8, 10
```

The method body doesn't execute until iterated. `yield break` ends the sequence early.

---

## 23. What are anonymous types and tuples?

**A:**
```csharp
// Anonymous type — compiler-generated, read-only properties
var person = new { Name = "Alice", Age = 30 };
Console.WriteLine(person.Name); // Alice

// Tuple — lightweight grouping without a class
var point = (X: 1, Y: 2);
Console.WriteLine(point.X); // 1

// Return multiple values
(string Name, int Age) GetInfo() => ("Alice", 30);
var (name, age) = GetInfo(); // deconstruction
```

---

## 24. What is the difference between `Func<>`, `Action<>`, and `Predicate<>`?

**A:**
```csharp
// Func<TInput, TOutput> — returns a value
Func<int, int, int> add = (a, b) => a + b;
int result = add(2, 3); // 5

// Action<T> — returns void
Action<string> log = msg => Console.WriteLine(msg);
log("hello");

// Predicate<T> — returns bool (shorthand for Func<T, bool>)
Predicate<int> isEven = n => n % 2 == 0;
bool even = isEven(4); // true
```

---

## 25. What is object initializer syntax?

**A:**
```csharp
// With object initializer
var p = new Person { Name = "Alice", Age = 30 };

// Collection initializer
var list = new List<int> { 1, 2, 3, 4, 5 };

// Dictionary initializer
var dict = new Dictionary<string, int>
{
    ["a"] = 1,
    ["b"] = 2
};
```

---

## 26. What is the difference between `IEnumerable<T>` and `List<T>`?

**A:**
- `IEnumerable<T>` — read-only, forward-only iteration; can be lazy
- `List<T>` — concrete, in-memory, random access, add/remove, implements `IEnumerable<T>`

```csharp
IEnumerable<int> lazy = GetNumbersFromDB(); // not executed yet
List<int> eager = lazy.ToList();            // executes, loads all into memory

list.Add(42);
list.Remove(1);
list.Sort();
int first = list[0]; // random access
```

Prefer `IEnumerable<T>` in method signatures to keep callers flexible.

---

## 27. What is `checked` and `unchecked` arithmetic?

**A:**
```csharp
int max = int.MaxValue; // 2,147,483,647

// Unchecked (default) — silently overflows/wraps
int overflow = max + 1; // -2,147,483,648

// Checked — throws OverflowException
checked
{
    int overflow2 = max + 1; // throws!
}
```

---

## 28. What is the `nameof` operator?

**A:** Returns a member name as a string — refactor-safe (renames propagate automatically):

```csharp
public void SetName(string name)
{
    if (name == null)
        throw new ArgumentNullException(nameof(name)); // "name" not a magic string
}

// INotifyPropertyChanged
OnPropertyChanged(nameof(FirstName));
```

---

## 29. What are local functions?

**A:** Functions defined inside another function — scoped, can capture locals, no delegate allocation:

```csharp
public int Factorial(int n)
{
    if (n < 0) throw new ArgumentException("Must be >= 0");
    return Calculate(n);

    int Calculate(int x) => x <= 1 ? 1 : x * Calculate(x - 1); // local
}
```

Unlike lambdas, local functions can be recursive and don't allocate a delegate object on the heap.

---

## 30. What is `Enumerable.Range`, `Repeat`, and `Empty`?

**A:**
```csharp
// Range — sequence of integers
var nums = Enumerable.Range(1, 5).ToList(); // [1, 2, 3, 4, 5]

// Repeat — repeat a value N times
var zeros = Enumerable.Repeat(0, 3).ToList(); // [0, 0, 0]

// Empty — empty typed sequence (avoids null)
IEnumerable<string> empty = Enumerable.Empty<string>();
```

---

## 31. What are `ref`, `out`, and `in` parameters?

**A:**
```csharp
// ref — pass by reference, must be initialized before passing
void Increment(ref int n) => n++;
int x = 5;
Increment(ref x); // x = 6

// out — pass by reference, assigned inside the method (no pre-init required)
bool TryParse(string s, out int result) {
    return int.TryParse(s, out result);
}
if (TryParse("42", out int val)) Console.WriteLine(val);

// in — read-only reference (avoids copying large structs)
void Print(in LargeStruct s) => Console.WriteLine(s.Value); // no copy
```
