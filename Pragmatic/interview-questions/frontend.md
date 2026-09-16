# 🌐 Frontend — Interview Questions

Core concepts, React, and Angular — all in one file.

---

## 🧱 Core Frontend Concepts

---

### 1. How does the browser render a page? What is the critical rendering path?

**A:**

```
1. Parse HTML → DOM (Document Object Model)
2. Parse CSS → CSSOM (CSS Object Model)
3. DOM + CSSOM → Render Tree (visible nodes only)
4. Layout (Reflow) — compute position and size of each node
5. Paint — fill in pixels (color, borders, shadows)
6. Composite — combine layers, send to GPU
```

**Critical Rendering Path** — the sequence of steps the browser must complete before showing the first pixel. Minimizing it = faster First Contentful Paint (FCP).

**Blocking resources:**
- `<script>` without `defer`/`async` → pauses HTML parsing
- `<link rel="stylesheet">` → blocks rendering until CSS parsed
- Large images → don't block rendering but delay Largest Contentful Paint (LCP)

```html
<!-- Non-blocking scripts -->
<script defer src="app.js"></script>    <!-- runs after HTML parsed, in order -->
<script async src="analytics.js"></script> <!-- runs as soon as downloaded, any order -->

<!-- Preload critical resources -->
<link rel="preload" href="hero.jpg" as="image">
<link rel="preload" href="font.woff2" as="font" crossorigin>
```

---

### 2. What is the DOM and how is it different from HTML?

**A:** The DOM (Document Object Model) is a live, in-memory tree representation of the parsed HTML document. HTML is static text; the DOM is the browser's interpretation of it — a live API that JavaScript can read and modify.

```javascript
// HTML: <p id="msg">Hello</p>

// DOM: a tree of node objects
document.getElementById("msg");          // Element node
document.getElementById("msg").childNodes[0]; // Text node "Hello"

// DOM can differ from HTML:
// - Browser auto-corrects malformed HTML
// - JavaScript modifies DOM after parse
// - template tags, shadow DOM

// Key DOM APIs
document.querySelector(".card");
document.querySelectorAll("input[type=text]");
element.textContent = "new text";         // safe (no XSS)
element.innerHTML = "<b>bold</b>";         // careful — XSS risk
element.setAttribute("aria-label", "...");
element.classList.add("active");
element.classList.toggle("open");
element.addEventListener("click", handler);
parent.appendChild(child);
parent.removeChild(child);
element.insertAdjacentElement("afterend", newEl);
```

---

### 3. What is the event loop? How does JavaScript handle async?

**A:** JavaScript is single-threaded. The event loop allows it to handle async operations without blocking.

```
Call Stack      Web APIs           Task Queue (Macro)   Microtask Queue
──────────      ────────           ──────────────────   ───────────────
main()      →   setTimeout(fn,0)  → fn() queued         Promise.then() queued
                fetch(url)         → callback queued     queueMicrotask()
                addEventListener   → event callback

Event loop algorithm:
1. Execute everything in Call Stack until empty
2. Drain entire Microtask Queue (Promises, queueMicrotask, MutationObserver)
3. Pick ONE task from Task Queue (setTimeout, setInterval, I/O)
4. Render (if needed)
5. Repeat
```

```javascript
console.log("1");

setTimeout(() => console.log("2"), 0);    // macro task

Promise.resolve().then(() => console.log("3")); // microtask

console.log("4");

// Output: 1, 4, 3, 2
// Microtasks (3) run before macro tasks (2) — even with setTimeout 0
```

---

### 4. What is the difference between `==` and `===` in JavaScript?

**A:**
- `===` (strict equality) — checks value AND type. No coercion.
- `==` (loose equality) — type coercion before comparison. Confusing rules.

```javascript
// === (always use this)
1 === 1       // true
1 === "1"     // false — different types
null === undefined  // false

// == (avoid)
1 == "1"      // true  — string "1" coerced to number
0 == false    // true  — false coerced to 0
null == undefined // true  — special case
null == 0     // false — another special case
[] == false   // true  — [] → "" → 0, false → 0

// Falsy values: false, 0, "", null, undefined, NaN
// Truthy: everything else (including [], {}, "0")
```

---

### 5. What is closure in JavaScript?

**A:** A closure is a function that retains access to its outer scope's variables even after the outer function has returned.

```javascript
function createCounter() {
    let count = 0;  // lives in closure

    return {
        increment() { count++; },
        decrement() { count--; },
        get() { return count; }
    };
}

const counter = createCounter();
counter.increment();
counter.increment();
counter.get(); // 2
// count is not accessible from outside — private via closure

// Common pitfall: closure over loop variable
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100); // prints 3, 3, 3 (captures same i)
}

// Fix: use let (block-scoped) or IIFE
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100); // 0, 1, 2
}
```

---

### 6. What is the prototype chain?

**A:** Every JavaScript object has a hidden `[[Prototype]]` link to another object. Property lookup traverses the chain upward until found or `null` reached.

```javascript
const animal = { breathe() { return "breathing"; } };
const dog = Object.create(animal);  // dog's prototype = animal
dog.bark = function() { return "woof"; };

dog.bark();    // found on dog
dog.breathe(); // not on dog → lookup prototype → found on animal
dog.fly;       // not on dog → not on animal → not on Object.prototype → undefined

// Constructor function / class
class Vehicle {
    start() { return "starting"; }
}
class Car extends Vehicle {
    horn() { return "beep"; }
}

const car = new Car();
// car → Car.prototype → Vehicle.prototype → Object.prototype → null

// instanceof checks the chain
car instanceof Car;     // true
car instanceof Vehicle; // true
car instanceof Object;  // true
```

---

### 7. What is `this` in JavaScript?

**A:** `this` is determined by **how** a function is called, not where it's defined (except for arrow functions).

```javascript
// Regular function: this = caller context
const obj = {
    name: "Alice",
    greet() { return this.name; }
};
obj.greet();  // "Alice" — this = obj
const fn = obj.greet;
fn();          // undefined (strict) or window.name (sloppy) — this = undefined/global

// Arrow function: this = lexical (enclosing scope)
class Timer {
    constructor() { this.seconds = 0; }
    start() {
        setInterval(() => {
            this.seconds++;  // arrow: this = Timer instance
        }, 1000);
    }
}

// Explicit binding
const greet = function(greeting) { return `${greeting}, ${this.name}`; };
greet.call({ name: "Bob" }, "Hi");    // "Hi, Bob"
greet.apply({ name: "Carol" }, ["Hey"]); // "Hey, Carol"
const greetAlice = greet.bind({ name: "Alice" }); // returns bound function
greetAlice("Hello"); // "Hello, Alice"
```

---

### 8. What is event delegation?

**A:** Attach a single event listener to a parent element to handle events from many child elements, using event bubbling.

```javascript
// Without delegation — attach to each item (expensive, breaks on dynamic content)
document.querySelectorAll(".item").forEach(item => {
    item.addEventListener("click", handleClick);
});

// With delegation — one listener on parent
document.querySelector("#list").addEventListener("click", (event) => {
    const item = event.target.closest(".item");
    if (!item) return;  // click was not on an item

    const id = item.dataset.id;
    handleItemClick(id);
});

// Works for dynamically added items — they bubble to #list automatically
// event.target  — the element that was clicked
// event.currentTarget — the element with the listener (#list)
// event.stopPropagation() — prevent bubbling up
// event.preventDefault() — prevent default action (form submit, link navigate)
```

---

### 9. What are Promises and async/await?

**A:**

```javascript
// Promise — represents a value that may be available now, later, or never
fetch("/api/users")
    .then(res => res.json())
    .then(users => console.log(users))
    .catch(err => console.error(err))
    .finally(() => setLoading(false));

// Promise.all — run concurrently, fail if any fails
const [user, orders] = await Promise.all([
    fetch("/api/user/1").then(r => r.json()),
    fetch("/api/orders?userId=1").then(r => r.json()),
]);

// Promise.allSettled — run all, get all results regardless of failure
const results = await Promise.allSettled([p1, p2, p3]);
results.forEach(r => {
    if (r.status === "fulfilled") use(r.value);
    else console.error(r.reason);
});

// Promise.race — first to settle wins
const result = await Promise.race([
    fetch("/api/data"),
    new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), 5000))
]);

// async/await — syntactic sugar over Promises
async function fetchUser(id) {
    try {
        const res = await fetch(`/api/users/${id}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error("Failed:", err);
        throw err;
    }
}
```

---

### 10. What are Web Storage options and when do you use each?

**A:**

| | `localStorage` | `sessionStorage` | Cookie | IndexedDB |
|--|--------------|----------------|--------|-----------|
| Capacity | ~5-10MB | ~5MB | 4KB | GBs |
| Expiry | Never | Tab close | Configurable | Never |
| Server access | No | No | Yes (header) | No |
| Sync | Sync | Sync | Sync | Async |
| Use for | Preferences, theme | Temp form data | Auth tokens (HttpOnly), sessions | Large offline data |

```javascript
// localStorage
localStorage.setItem("theme", "dark");
const theme = localStorage.getItem("theme");
localStorage.removeItem("theme");
localStorage.clear();

// sessionStorage — same API, cleared when tab closes

// IndexedDB — for structured data, offline apps
const db = await new Promise((resolve, reject) => {
    const req = indexedDB.open("mydb", 1);
    req.onupgradeneeded = e => e.target.result.createObjectStore("users", { keyPath: "id" });
    req.onsuccess = e => resolve(e.target.result);
});
```

---

### 11. What is CORS and how does it work?

**A:** Cross-Origin Resource Sharing — browser security mechanism that restricts HTTP requests to different origins (scheme + host + port).

```
Origin: https://myapp.com
Request to: https://api.myapp.com   → cross-origin (different subdomain)
Request to: https://myapp.com:8080  → cross-origin (different port)
Request to: http://myapp.com        → cross-origin (different scheme)
```

```javascript
// Browser adds Origin header automatically for cross-origin requests
// Server must respond with appropriate CORS headers

// Simple request (GET, POST with plain text/form)
// Server response:
// Access-Control-Allow-Origin: https://myapp.com
// Access-Control-Allow-Credentials: true

// Preflight (OPTIONS) — for complex requests (PUT, DELETE, custom headers)
// Browser sends OPTIONS first:
// OPTIONS /api/orders HTTP/1.1
// Origin: https://myapp.com
// Access-Control-Request-Method: DELETE
// Access-Control-Request-Headers: Content-Type, Authorization

// Server must respond:
// Access-Control-Allow-Origin: https://myapp.com
// Access-Control-Allow-Methods: GET, POST, PUT, DELETE
// Access-Control-Allow-Headers: Content-Type, Authorization
// Access-Control-Max-Age: 86400  ← cache preflight for 1 day

// Common mistake: wildcard with credentials
// Access-Control-Allow-Origin: *     ← cannot use with credentials
// Must use specific origin when cookies/auth needed
```

---

### 12. What is the difference between `null` and `undefined`?

**A:**

```javascript
// undefined — variable declared but not assigned; missing property; missing function arg
let x;
console.log(x);          // undefined
console.log({}.foo);     // undefined
function f(a) { return a; }
f();                      // undefined

// null — intentional absence of value; explicitly assigned
let user = null;          // "no user" — deliberate
document.getElementById("missing");  // returns null (not undefined)

// Type difference
typeof undefined;  // "undefined"
typeof null;       // "object" — famous JavaScript bug (spec frozen for compatibility)

// Both are falsy
if (!undefined) // true
if (!null)      // true

// Equality
null == undefined;  // true  (loose)
null === undefined; // false (strict)

// Optional chaining — handles both
user?.profile?.name;  // undefined if user is null/undefined (no error)
```

---

### 13. What is `debounce` vs `throttle`?

**A:**

```javascript
// Debounce — delay execution until N ms after LAST call
// Use: search input, window resize handler, form validation
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

const search = debounce((query) => fetchResults(query), 300);
input.addEventListener("input", (e) => search(e.target.value));
// Only fires 300ms after user stops typing

// Throttle — execute at most once per N ms, regardless of call frequency
// Use: scroll events, mousemove, game loop, API rate limiting
function throttle(fn, interval) {
    let lastTime = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastTime >= interval) {
            lastTime = now;
            return fn.apply(this, args);
        }
    };
}

window.addEventListener("scroll", throttle(updateScrollProgress, 100));
// Fires at most every 100ms regardless of scroll speed
```

---

### 14. What are Web Workers?

**A:** Web Workers run JavaScript in a background thread — separate from the main UI thread, can't access DOM.

```javascript
// Main thread
const worker = new Worker("worker.js");

worker.postMessage({ type: "process", data: largeArray });

worker.onmessage = (e) => {
    console.log("Result:", e.data.result);
};

worker.onerror = (e) => console.error(e.message);

// worker.js (separate file)
self.onmessage = (e) => {
    if (e.data.type === "process") {
        const result = expensiveComputation(e.data.data); // runs off main thread
        self.postMessage({ result });
    }
};

// Communication: structured clone (copies data)
// SharedArrayBuffer: shared memory between threads (requires COOP/COEP headers)

// Use cases:
// - Image/video processing
// - Cryptography
// - Parsing large JSON/CSV
// - ML inference (TensorFlow.js)
// - WebAssembly execution
```

---

### 15. What is accessibility (a11y) and what are the basics?

**A:**

```html
<!-- Semantic HTML — free accessibility -->
<nav>, <main>, <header>, <footer>, <article>, <section>
<button> (not <div onclick>), <a href>, <label>

<!-- ARIA — when semantic HTML isn't enough -->
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
    <h2 id="dialog-title">Confirm deletion</h2>
    <button aria-label="Close dialog">×</button>
</div>

<!-- Images -->
<img src="chart.png" alt="Sales grew 20% in Q4">  <!-- descriptive -->
<img src="decorative.png" alt="">                   <!-- decorative: empty alt -->

<!-- Forms -->
<label for="email">Email address</label>
<input id="email" type="email" aria-describedby="email-hint" required>
<span id="email-hint">We'll never share your email</span>

<!-- Focus management -->
/* Visible focus ring — never remove without alternative */
:focus-visible { outline: 2px solid #0066cc; outline-offset: 2px; }

<!-- Keyboard navigation -->
<!-- Tab order follows DOM order -->
<!-- tabindex="0": include in tab order -->
<!-- tabindex="-1": focus programmatically only -->
<!-- tabindex="1+": avoid — breaks natural order -->

<!-- Color contrast -->
<!-- WCAG AA: 4.5:1 for normal text, 3:1 for large text -->
<!-- WCAG AAA: 7:1 for normal text -->
```

**WCAG levels:** A (minimum), AA (standard target), AAA (enhanced)
**POUR principles:** Perceivable, Operable, Understandable, Robust

---

### 16. What is Critical CSS and how do you optimize page load?

**A:**

```html
<!-- Critical CSS: inline styles needed for above-the-fold content -->
<head>
    <style>/* hero section, nav, fonts — critical */</style>
    <link rel="preload" href="full.css" as="style" onload="this.rel='stylesheet'">
</head>

<!-- Resource hints -->
<link rel="preconnect" href="https://api.example.com">     <!-- early TCP/TLS -->
<link rel="dns-prefetch" href="https://cdn.example.com">   <!-- DNS only -->
<link rel="prefetch" href="/next-page.js">                  <!-- low-priority future page -->
<link rel="preload" href="hero.webp" as="image" fetchpriority="high"> <!-- current page, high -->

<!-- Images -->
<img loading="lazy" src="below-fold.jpg" alt="...">   <!-- lazy load -->
<img loading="eager" src="hero.jpg" alt="...">         <!-- above fold: eager -->
<picture>
    <source srcset="hero.avif" type="image/avif">
    <source srcset="hero.webp" type="image/webp">
    <img src="hero.jpg" alt="Hero image">
</picture>
```

```javascript
// Code splitting — only load what's needed
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

// Bundle analysis
// webpack-bundle-analyzer, source-map-explorer

// Performance metrics (Core Web Vitals)
// LCP (Largest Contentful Paint) — < 2.5s — loading performance
// FID (First Input Delay) / INP — < 100ms — interactivity
// CLS (Cumulative Layout Shift) — < 0.1 — visual stability
```

---

## ⚛️ React

---

### 17. What is the Virtual DOM and how does React use it?

**A:** React maintains a lightweight in-memory copy of the real DOM. On state change, it creates a new virtual DOM, diffs it against the previous (reconciliation), and applies only the minimal real DOM changes.

```
State changes → Re-render (new VDOM) → Diff (reconciliation) → Patch real DOM

Diffing algorithm:
  - Two elements of different types → rebuild entire subtree
  - Same type → update attributes only
  - Lists: use key prop to identify elements (avoid index as key for reorderable lists)
```

**React 18 Fiber:** The reconciler is asynchronous — can pause, prioritize, and resume rendering work. Enables concurrent features (Suspense, transitions).

---

### 18. What are React hooks and what are the rules?

**A:**

```jsx
// Core hooks
useState   — local component state
useEffect  — side effects (fetch, subscriptions, DOM manipulation)
useContext — consume Context without prop drilling
useRef     — mutable ref (DOM access, persisting value without re-render)
useMemo    — memoize expensive computation
useCallback — memoize function reference (stable reference for child props)
useReducer — complex state logic (Redux-like)
useId      — stable unique ID for accessibility

// Rules of Hooks:
// 1. Only call hooks at the TOP LEVEL (not inside loops, conditions, nested functions)
// 2. Only call hooks from React function components or custom hooks

// WHY: React tracks hooks by call order — conditional calls break the order
// BAD:
if (condition) {
    const [val, setVal] = useState(0); // may not be called — breaks order!
}

// GOOD:
const [val, setVal] = useState(0);
if (condition) {
    // use val here
}
```

---

### 19. How does `useEffect` work and what are common pitfalls?

**A:**

```jsx
// Dependency array controls when effect runs
useEffect(() => { /* runs after every render */ });
useEffect(() => { /* runs once on mount */ }, []);
useEffect(() => { /* runs when a or b changes */ }, [a, b]);

// Cleanup function — runs before next effect and on unmount
useEffect(() => {
    const subscription = subscribe(userId);
    return () => subscription.unsubscribe();  // cleanup
}, [userId]);

// PITFALL 1: missing dependencies → stale closure
const [count, setCount] = useState(0);

useEffect(() => {
    const timer = setInterval(() => {
        console.log(count); // always logs 0! — captured at mount
        setCount(count + 1); // WRONG: uses stale count
    }, 1000);
    return () => clearInterval(timer);
}, []); // empty deps: count never updates

// FIX: use functional updater or add count to deps
setCount(prev => prev + 1); // always has latest value

// PITFALL 2: object/function deps cause infinite loop
useEffect(() => {
    fetch(options); // runs every render!
}, [options]); // options is new object reference every render

// FIX: useMemo or put object inside effect
const options = useMemo(() => ({ method: "GET" }), []);

// PITFALL 3: async in useEffect
useEffect(() => {
    async function load() {  // define inside, call inside
        const data = await fetchData();
        setData(data);
    }
    load();
}, []);
// DON'T: useEffect(async () => ...) — async returns a Promise, not a cleanup fn
```

---

### 20. What is `useMemo` vs `useCallback`?

**A:**

```jsx
// useMemo — memoize a computed VALUE
const expensiveValue = useMemo(() => {
    return items.filter(i => i.active).reduce((sum, i) => sum + i.price, 0);
}, [items]); // only recomputes when items changes

// useCallback — memoize a FUNCTION (stable reference)
const handleClick = useCallback((id) => {
    setSelected(id);
}, []);  // same function reference across renders

// WHY useCallback: prevents child re-renders when passing functions as props
const ChildComponent = React.memo(({ onClick }) => {
    // only re-renders if onClick reference changes
    return <button onClick={onClick}>Click</button>;
});

// Without useCallback:
function Parent() {
    const handleClick = () => doSomething(); // NEW reference every render
    return <ChildComponent onClick={handleClick} />; // Child always re-renders!
}

// With useCallback:
const handleClick = useCallback(() => doSomething(), []); // stable reference
// Child only re-renders when handleClick changes

// DON'T over-use: memoization has overhead. Profile first.
// Use when: expensive computation OR passing stable callbacks to memoized children
```

---

### 21. What is Context and when should you NOT use it?

**A:**

```jsx
// Create context
const ThemeContext = createContext("light");

// Provide value
function App() {
    const [theme, setTheme] = useState("dark");
    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            <Layout />
        </ThemeContext.Provider>
    );
}

// Consume anywhere in the tree
function Button() {
    const { theme } = useContext(ThemeContext);
    return <button className={theme}>Click</button>;
}

// WHEN NOT TO USE Context:
// 1. High-frequency updates (every keystroke, scroll position)
//    → Every consumer re-renders on context change
//    → Use Zustand, Jotai, or Redux for high-frequency state

// 2. When props suffice (only 1-2 levels deep)
//    → Context adds complexity without benefit

// 3. Server state (API data, cache)
//    → Use React Query, SWR — they handle caching, refetching, deduplication

// Context is good for: theme, locale, auth user, feature flags — low-frequency, global
```

---

### 22. What is React.memo and when does it help?

**A:**

```jsx
// React.memo — skip re-render if props haven't changed (shallow comparison)
const UserCard = React.memo(function UserCard({ user, onDelete }) {
    console.log("Rendering UserCard for", user.name);
    return (
        <div>
            <h3>{user.name}</h3>
            <button onClick={() => onDelete(user.id)}>Delete</button>
        </div>
    );
});

// Parent re-renders → UserCard only re-renders if user or onDelete changed

// GOTCHA: only shallow comparison
// If props are objects/arrays created inline → always new reference → memo useless
<UserCard user={{ name: "Alice" }} />  // NEW object every render → memo broken

// FIX: stable references from parent
const user = useMemo(() => ({ name: "Alice" }), []);
<UserCard user={user} onDelete={handleDelete} />  // stable → memo works

// Custom comparison
const UserCard = React.memo(UserCardFn, (prevProps, nextProps) => {
    return prevProps.user.id === nextProps.user.id;  // true = skip render
});

// DON'T memo everything — profiling first
// memo helps when: component is expensive to render + parent re-renders frequently + props are stable
```

---

### 23. What is the React component lifecycle and how do hooks map to it?

**A:**

```
Class lifecycle → Hook equivalent
────────────────────────────────
constructor        → useState initial value
componentDidMount  → useEffect(() => {...}, [])
componentDidUpdate → useEffect(() => {...}, [deps])
componentWillUnmount → useEffect cleanup function
shouldComponentUpdate → React.memo
getDerivedStateFromProps → useState + useMemo
getSnapshotBeforeUpdate → useRef
componentDidCatch  → Error Boundary (still class-only)

// Mount → Update → Unmount

useEffect(() => {
    // componentDidMount equivalent: runs after first render
    const sub = subscribe();

    return () => {
        // componentWillUnmount equivalent: cleanup
        sub.unsubscribe();
    };
}, []); // empty array = mount/unmount only

useEffect(() => {
    // componentDidUpdate equivalent: runs when userId changes
    fetchUser(userId).then(setUser);
}, [userId]);
```

---

### 24. What is React Suspense and Concurrent Mode?

**A:**

```jsx
// Suspense — declarative loading states
import { Suspense, lazy } from "react";

const HeavyChart = lazy(() => import("./HeavyChart"));

function Dashboard() {
    return (
        <Suspense fallback={<Skeleton />}>
            <HeavyChart />  {/* renders fallback while loading */}
        </Suspense>
    );
}

// Suspense with data (React 18 + React Query / SWR)
// Component "suspends" (throws a Promise) → Suspense boundary shows fallback

// useTransition — mark state update as non-urgent
const [isPending, startTransition] = useTransition();

function handleSearch(query) {
    startTransition(() => {
        setSearchResults(expensiveFilter(query)); // can be interrupted
    });
    setInputValue(query); // urgent — updates immediately
}
// UI stays responsive during expensive state update

// useDeferredValue — defer a value update
const deferredQuery = useDeferredValue(searchQuery);
// searchQuery updates immediately (UI stays fast)
// deferredQuery lags behind — expensive filtering uses old value while new one processes
```

---

### 25. What is React state management? When do you need Redux vs Context vs Zustand?

**A:**

```
Local state (useState)     → component-specific, no sharing needed
Lifted state               → share between siblings (lift to parent)
Context                    → global, low-frequency (theme, auth, locale)
URL state                  → shareable, bookmarkable (filters, page)
Server state (React Query) → async data, caching, refetch
Global client state        → Zustand, Jotai, Redux

// Zustand — minimal, no boilerplate
import { create } from "zustand";

const useStore = create((set) => ({
    cart: [],
    addItem: (item) => set((state) => ({ cart: [...state.cart, item] })),
    removeItem: (id) => set((state) => ({ cart: state.cart.filter(i => i.id !== id) })),
    total: 0,
}));

function CartButton() {
    const { cart, addItem } = useStore();  // only re-renders when cart changes
    return <button onClick={() => addItem(product)}>{cart.length} items</button>;
}

// Redux Toolkit — when: large team, complex state, time-travel debugging, middleware
// React Query / SWR — server state: caching, refetch on focus, optimistic updates
// Jotai / Recoil — atomic state: fine-grained subscriptions, no over-render
```

---

### 26. What are React performance patterns?

**A:**

```jsx
// 1. Virtualization — only render visible rows (large lists)
import { FixedSizeList } from "react-window";

<FixedSizeList height={600} itemCount={100000} itemSize={50} width="100%">
    {({ index, style }) => <Row index={index} style={style} />}
</FixedSizeList>

// 2. Code splitting — lazy load routes
const OrdersPage = lazy(() => import("./OrdersPage"));

// 3. Avoid anonymous functions as props
// BAD: new function reference every render
<Button onClick={() => handleClick(id)} />

// GOOD: stable reference
const handler = useCallback(() => handleClick(id), [id]);
<Button onClick={handler} />

// 4. Key prop — help reconciler identify items
// BAD: index as key for reorderable lists
items.map((item, i) => <Item key={i} ... />)

// GOOD: stable unique ID
items.map(item => <Item key={item.id} ... />)

// 5. Avoid unnecessary renders with state structure
// BAD: one object → any change re-renders all consumers
const [state, setState] = useState({ count: 0, name: "", list: [] });

// GOOD: separate state for unrelated data
const [count, setCount] = useState(0);
const [name, setName] = useState("");

// 6. useId for SSR-safe IDs
const id = useId();
return <><label htmlFor={id}>Name</label><input id={id} /></>;
```

---

## 🅰️ Angular

---

### 27. What is Angular's architecture and how is it organized?

**A:** Angular is a full opinionated framework (vs React's library). Key concepts:

```
NgModule (or Standalone) → Component → Template + Class + Styles
                         → Directive → extend HTML behavior
                         → Pipe → transform template values
                         → Service → business logic, DI-injectable
                         → Guard → route protection
                         → Resolver → pre-fetch data before route
                         → Interceptor → HTTP middleware

Module structure:
  BrowserModule → root module features
  FormsModule / ReactiveFormsModule → forms
  HttpClientModule → HTTP
  RouterModule → routing
  Feature modules → lazy-loaded domain areas

Standalone components (Angular 14+):
  // No NgModule needed — component declares its own imports
  @Component({
    standalone: true,
    imports: [CommonModule, RouterModule, UserCardComponent],
    template: `...`
  })
```

---

### 28. What is Angular's change detection and how does OnPush work?

**A:**

```typescript
// Default change detection: checks EVERY component on ANY event
// OnPush: only checks when:
//   - @Input() reference changes
//   - Event originated inside the component
//   - Observable marked with async pipe emits
//   - ChangeDetectorRef.markForCheck() called manually

@Component({
    selector: "app-user-card",
    template: `{{ user.name }}`,
    changeDetection: ChangeDetectionStrategy.OnPush  // opt-in
})
class UserCardComponent {
    @Input() user: User;  // only re-checks when reference changes

    // WRONG: mutating object — same reference, OnPush won't detect change
    this.user.name = "Bob";  // reference unchanged → no update!

    // RIGHT: new reference triggers OnPush
    this.user = { ...this.user, name: "Bob" };  // new object → re-check
}

// Use with immutable data or Observables + async pipe
@Component({
    template: `{{ user$ | async | json }}`,
    changeDetection: ChangeDetectionStrategy.OnPush
})
class UserComponent {
    user$ = this.userService.getUser(42);  // Observable
    // async pipe subscribes and calls markForCheck() on each emission
}

// Manual trigger
constructor(private cdr: ChangeDetectorRef) {}
this.cdr.markForCheck();    // schedule check for this component + ancestors
this.cdr.detectChanges();   // immediately run change detection on this subtree
```

---

### 29. What is Angular's Dependency Injection?

**A:**

```typescript
// Injectable service — registers itself with DI
@Injectable({ providedIn: "root" })  // singleton for entire app
export class UserService {
    constructor(private http: HttpClient) {}

    getUser(id: number): Observable<User> {
        return this.http.get<User>(`/api/users/${id}`);
    }
}

// Component injection — receives service
@Component({ selector: "app-profile" })
class ProfileComponent {
    constructor(private userService: UserService) {}
    // Angular's injector finds and injects UserService
}

// Scoping providers
@Component({
    providers: [UserService]  // new instance for this component + children
})

// Injection tokens — for non-class dependencies
export const API_URL = new InjectionToken<string>("api_url");

// Register
providers: [{ provide: API_URL, useValue: "https://api.example.com" }]

// Inject
constructor(@Inject(API_URL) private apiUrl: string) {}

// inject() function (Angular 14+ — no constructor needed)
class UserService {
    private http = inject(HttpClient);
    private config = inject(APP_CONFIG);
}

// Provider types
{ provide: UserService, useClass: MockUserService }   // substitute class
{ provide: UserService, useExisting: AdminService }   // alias
{ provide: UserService, useValue: mockService }       // static value
{ provide: UserService, useFactory: (http) => new UserService(http), deps: [HttpClient] }
```

---

### 30. What is RxJS and how is it used in Angular?

**A:**

```typescript
import { Observable, Subject, BehaviorSubject, combineLatest, forkJoin } from "rxjs";
import { map, filter, switchMap, debounceTime, distinctUntilChanged,
         catchError, takeUntil, shareReplay } from "rxjs/operators";

// Observable — lazy stream of values
const user$ = this.http.get<User>("/api/user");
user$.subscribe({
    next: user => this.user = user,
    error: err => this.error = err,
    complete: () => console.log("done")
});

// Operators — transform streams
this.searchControl.valueChanges.pipe(
    debounceTime(300),              // wait 300ms after last keystroke
    distinctUntilChanged(),         // only if value actually changed
    filter(q => q.length > 2),      // minimum 3 chars
    switchMap(q =>                  // cancel previous, switch to new request
        this.searchService.search(q).pipe(
            catchError(() => of([]))  // return empty on error
        )
    )
).subscribe(results => this.results = results);

// Subject — emit values imperatively
const notify$ = new Subject<string>();
notify$.next("user logged in");
notify$.subscribe(msg => console.log(msg));

// BehaviorSubject — has current value, replays to new subscribers
const currentUser$ = new BehaviorSubject<User | null>(null);
currentUser$.next(user);
currentUser$.getValue();  // get current value synchronously

// Avoiding memory leaks — unsubscribe
// Pattern 1: takeUntil
private destroy$ = new Subject<void>();
user$.pipe(takeUntil(this.destroy$)).subscribe(...);
ngOnDestroy() { this.destroy$.next(); this.destroy$.complete(); }

// Pattern 2: async pipe (auto-unsubscribes)
// template: {{ user$ | async }}

// Combining
combineLatest([user$, orders$]).pipe(
    map(([user, orders]) => ({ user, orders }))
);

forkJoin([user$, orders$]);  // waits for all to complete (like Promise.all)
```

---

### 31. What is Angular routing and how do guards work?

**A:**

```typescript
// Route configuration
const routes: Routes = [
    { path: "", component: HomeComponent },
    { path: "login", component: LoginComponent },
    {
        path: "dashboard",
        canActivate: [AuthGuard],          // protect route
        canActivateChild: [RoleGuard],     // protect child routes
        component: DashboardComponent,
        children: [
            { path: "orders", component: OrdersComponent },
            { path: "orders/:id", component: OrderDetailComponent,
              resolve: { order: OrderResolver } }  // pre-fetch data
        ]
    },
    {
        path: "admin",
        loadChildren: () => import("./admin/admin.module").then(m => m.AdminModule),
        canLoad: [AdminGuard]              // prevent even loading the module
    },
    { path: "**", redirectTo: "/" }
];

// Guard (functional guards, Angular 14+)
export const authGuard: CanActivateFn = (route, state) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    if (auth.isLoggedIn()) return true;
    return router.createUrlTree(["/login"], { queryParams: { returnUrl: state.url } });
};

// Resolver — returns data before component activates
export const orderResolver: ResolveFn<Order> = (route) => {
    const orderService = inject(OrderService);
    return orderService.getOrder(route.paramMap.get("id")!);
};

// In component: receive resolved data
constructor(private route: ActivatedRoute) {
    this.order = this.route.snapshot.data["order"];
    // OR reactive:
    this.route.data.pipe(map(d => d["order"])).subscribe(order => this.order = order);
}

// Navigation
constructor(private router: Router) {}
this.router.navigate(["/orders", orderId]);
this.router.navigate(["/orders"], { queryParams: { status: "pending" } });
this.router.navigateByUrl("/dashboard");
```

---

### 32. What are Angular directives and what are the types?

**A:**

```typescript
// 1. Component — directive with a template
@Component({ selector: "app-button", template: `<button><ng-content></ng-content></button>` })

// 2. Structural directive — modifies DOM structure (prefix: *)
*ngIf="condition"           // add/remove element
*ngFor="let item of items"  // repeat element
*ngSwitch                   // switch/case

// Custom structural directive
@Directive({ selector: "[appRepeat]" })
class RepeatDirective {
    @Input() set appRepeat(times: number) {
        this.viewContainer.clear();
        for (let i = 0; i < times; i++) {
            this.viewContainer.createEmbeddedView(this.templateRef);
        }
    }
    constructor(private templateRef: TemplateRef<any>, private viewContainer: ViewContainerRef) {}
}
// Usage: <div *appRepeat="3">Hello</div>

// 3. Attribute directive — modifies element appearance/behavior
@Directive({ selector: "[appHighlight]", standalone: true })
class HighlightDirective {
    @Input() appHighlight = "yellow";
    @HostListener("mouseenter") onEnter() { this.el.nativeElement.style.background = this.appHighlight; }
    @HostListener("mouseleave") onLeave() { this.el.nativeElement.style.background = ""; }
    constructor(private el: ElementRef) {}
}
// Usage: <p appHighlight="lightblue">Hover me</p>

// Built-in attribute directives
[ngClass]="{ active: isActive, disabled: isDisabled }"
[ngStyle]="{ color: textColor, fontSize: fontSize + 'px' }"
[(ngModel)]="username"  // two-way binding (FormsModule)
```

---

### 33. What are Angular forms — Template-driven vs Reactive?

**A:**

```typescript
// Template-driven — simple, less code, async validation tricky
// FormsModule required
@Component({
    template: `
        <form #form="ngForm" (ngSubmit)="onSubmit(form)">
            <input name="email" [(ngModel)]="user.email"
                   required email #emailField="ngModel">
            <span *ngIf="emailField.invalid && emailField.touched">
                Invalid email
            </span>
            <button [disabled]="form.invalid">Submit</button>
        </form>
    `
})

// Reactive forms — explicit, testable, synchronous, complex validation
// ReactiveFormsModule required
@Component({ template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
        <input formControlName="email">
        <span *ngIf="form.get('email')?.errors?.['email']">Invalid email</span>
        <input formControlName="password">
    </form>
`})
class LoginComponent implements OnInit {
    form = this.fb.group({
        email: ["", [Validators.required, Validators.email]],
        password: ["", [Validators.required, Validators.minLength(8)]],
        address: this.fb.group({   // nested group
            street: [""],
            city: ["", Validators.required]
        })
    });

    constructor(private fb: FormBuilder) {}

    ngOnInit() {
        // React to value changes
        this.form.get("email")!.valueChanges
            .pipe(debounceTime(300))
            .subscribe(email => this.checkEmailAvailability(email));
    }

    onSubmit() {
        if (this.form.valid) {
            console.log(this.form.value);
        }
    }
}

// Custom validator
function passwordStrength(control: AbstractControl): ValidationErrors | null {
    const value = control.value as string;
    if (!value || value.length < 8 || !/[A-Z]/.test(value)) {
        return { passwordStrength: { message: "Must be 8+ chars with uppercase" } };
    }
    return null;
}

// Async validator (check server)
function emailAvailable(userService: UserService): AsyncValidatorFn {
    return (control) => userService.checkEmail(control.value).pipe(
        map(taken => taken ? { emailTaken: true } : null),
        catchError(() => of(null))
    );
}
```

---

### 34. What is Angular's HttpClient and interceptors?

**A:**

```typescript
// HttpClient — type-safe HTTP
@Injectable({ providedIn: "root" })
class UserService {
    constructor(private http: HttpClient) {}

    getUsers(): Observable<User[]> {
        return this.http.get<User[]>("/api/users", {
            params: { page: "1", size: "20" },
            headers: { "X-Custom": "header" }
        });
    }

    createUser(user: Partial<User>): Observable<User> {
        return this.http.post<User>("/api/users", user);
    }

    // Full response (headers, status)
    getWithMeta(): Observable<HttpResponse<User[]>> {
        return this.http.get<User[]>("/api/users", { observe: "response" });
    }

    // Upload progress
    uploadFile(file: File): Observable<HttpEvent<any>> {
        const formData = new FormData();
        formData.append("file", file);
        return this.http.post("/api/upload", formData, {
            reportProgress: true,
            observe: "events"
        });
    }
}

// Interceptor — middleware for all HTTP requests
@Injectable()
class AuthInterceptor implements HttpInterceptor {
    constructor(private auth: AuthService) {}

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const token = this.auth.getToken();
        const authReq = req.clone({
            headers: req.headers.set("Authorization", `Bearer ${token}`)
        });
        return next.handle(authReq).pipe(
            catchError(err => {
                if (err.status === 401) this.auth.logout();
                return throwError(() => err);
            })
        );
    }
}

// Register (provide in provideHttpClient with functional interceptors in Angular 15+)
providers: [
    provideHttpClient(withInterceptors([authInterceptor, loggingInterceptor]))
]
```

---

### 35. What are Angular Signals (Angular 16+)?

**A:** Signals are a new reactive primitive — fine-grained reactivity without Zone.js, similar to Vue's ref or SolidJS signals.

```typescript
import { signal, computed, effect } from "@angular/core";

// signal() — writable reactive value
const count = signal(0);
count();           // read: 0
count.set(5);      // write
count.update(v => v + 1);  // update based on current

// computed() — derived value, auto-updates
const doubled = computed(() => count() * 2);
doubled();         // 10 (auto-tracks count dependency)

// effect() — side effects when signals change
effect(() => {
    console.log("Count changed:", count());  // runs when count changes
    // auto-cleanup on destroy
});

// In templates — no | async pipe needed
@Component({
    template: `
        <p>Count: {{ count() }}</p>
        <p>Double: {{ doubled() }}</p>
        <button (click)="count.update(v => v + 1)">+</button>
    `
})
class CounterComponent {
    count = signal(0);
    doubled = computed(() => this.count() * 2);
}

// Interop with RxJS
import { toSignal, toObservable } from "@angular/core/rxjs-interop";

const user = toSignal(this.userService.user$, { initialValue: null });
// OR
const user$ = toObservable(this.userSignal);

// Why Signals matter:
// - No Zone.js patching needed (zoneless apps possible)
// - Fine-grained: only components that read changed signals re-render
// - Synchronous: no async pipe needed for sync state
// - Replaces much of RxJS for local state
```

---

### 36. What is Angular's standalone component architecture?

**A:**

```typescript
// Before standalone: everything declared in NgModule
@NgModule({
    declarations: [AppComponent, UserCardComponent, DatePipe],
    imports: [BrowserModule, HttpClientModule, RouterModule],
    bootstrap: [AppComponent]
})
class AppModule {}

// Standalone (Angular 14+): components self-contained, no NgModule needed
@Component({
    standalone: true,
    selector: "app-user-card",
    imports: [
        CommonModule,       // ngIf, ngFor, etc.
        RouterLink,         // router directives
        DatePipe,           // built-in pipe
        UserAvatarComponent // another standalone component
    ],
    template: `
        <img [routerLink]="['/users', user.id]" [src]="user.avatar">
        <h3>{{ user.name }}</h3>
        <p>Joined: {{ user.createdAt | date }}</p>
    `
})
export class UserCardComponent {
    @Input() user!: User;
}

// Bootstrap without NgModule
bootstrapApplication(AppComponent, {
    providers: [
        provideRouter(routes),
        provideHttpClient(withInterceptors([authInterceptor])),
        provideAnimations(),
        importProvidersFrom(StoreModule.forRoot(reducers))
    ]
});

// Lazy loading standalone routes
const routes: Routes = [
    {
        path: "admin",
        loadComponent: () => import("./admin.component").then(m => m.AdminComponent)
    }
];
```

---

### 37. What are the key differences between React and Angular?

**A:**

| | React | Angular |
|--|-------|---------|
| Type | UI library | Full framework |
| Language | JavaScript / JSX | TypeScript (enforced) |
| Data binding | One-way (explicit) | Two-way (`[(ngModel)]`) + one-way |
| State | useState, external libs | Services + Signals + RxJS |
| Rendering | Virtual DOM | Zone.js + Signals (new) |
| Forms | Uncontrolled / Controlled | Template-driven / Reactive |
| HTTP | fetch / axios | HttpClient (built-in) |
| DI | Manual / Context | Built-in hierarchical DI |
| Routing | React Router (third-party) | Angular Router (built-in) |
| Testing | Jest + React Testing Library | Jasmine/Jest + TestBed |
| Learning curve | Lower (library only) | Higher (full framework) |
| Bundle size | Smaller (tree-shakeable) | Larger base |
| Mobile | React Native | Ionic / NativeScript |
| Best for | Flexibility, varied stack | Enterprise, opinionated teams |

**When Angular:** Large enterprise teams, strict TypeScript, need full framework conventions, long-lived projects with many developers.

**When React:** Smaller teams, flexibility, existing JS ecosystem, smaller apps, React Native mobile.
