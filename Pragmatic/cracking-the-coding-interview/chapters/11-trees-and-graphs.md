# Chapter 4 — Trees & Graphs

> *"Trees and graphs are the backbone of technical interviews. If you can't traverse a tree, you can't pass a top-company interview."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Trees and graphs are the most commonly tested data structures. This chapter covers traversals (**BFS, DFS**), key variants (**BST, Trie, Heap**), and the graph algorithms that appear repeatedly in interviews.

---

## 🌳 Tree Fundamentals

```
VOCABULARY: Root (top node) | Leaf (no children) | Height (root→leaf)
Balanced: subtree heights differ by ≤ 1
Complete: every level filled except possibly the last
BST:      left < node < right (for every node)
```

```java
class TreeNode { int val; TreeNode left, right; }
```

---

## 🔍 The Four Tree Traversals

```java
// IN-ORDER (left → root → right) → produces sorted output on BST
void inOrder(TreeNode n) {
    if (n == null) return;
    inOrder(n.left); visit(n); inOrder(n.right);
}

// PRE-ORDER (root → left → right) → clone a tree
void preOrder(TreeNode n) {
    if (n == null) return;
    visit(n); preOrder(n.left); preOrder(n.right);
}

// POST-ORDER (left → right → root) → delete a tree safely
void postOrder(TreeNode n) {
    if (n == null) return;
    postOrder(n.left); postOrder(n.right); visit(n);
}

// LEVEL-ORDER / BFS → level by level using a queue
void levelOrder(TreeNode root) {
    Queue<TreeNode> q = new ArrayDeque<>();
    if (root != null) q.offer(root);
    while (!q.isEmpty()) {
        TreeNode n = q.poll();
        visit(n);
        if (n.left != null)  q.offer(n.left);
        if (n.right != null) q.offer(n.right);
    }
}
```

---

## 🔎 Binary Search Tree (BST)

```
       8
      / \        In-order: 2,4,6,8,10,20 (sorted!)
     4   10       Search 6: 8→4→6 ✓  (3 steps, not n)
    / \    \
   2   6    20

BST Search: O(log n) balanced, O(n) worst case (degenerate)
```

---

## 📊 Graph: BFS vs. DFS

```java
// BFS — shortest path, level-order (uses a QUEUE)
void bfs(Map<Integer, List<Integer>> g, int start) {
    Set<Integer> visited = new HashSet<>();
    Queue<Integer> q = new ArrayDeque<>();
    q.offer(start); visited.add(start);
    while (!q.isEmpty()) {
        int node = q.poll();
        for (int nb : g.getOrDefault(node, List.of()))
            if (visited.add(nb)) q.offer(nb);
    }
}

// DFS — cycle detection, topological sort (uses STACK/recursion)
void dfs(Map<Integer, List<Integer>> g, int node,
         Set<Integer> visited) {
    visited.add(node);
    for (int nb : g.getOrDefault(node, List.of()))
        if (!visited.contains(nb)) dfs(g, nb, visited);
}
// Both: Time O(V+E), Space O(V)
```

```
USE BFS WHEN:                  USE DFS WHEN:
  Shortest path (unweighted)     Cycle detection
  Level-by-level traversal       Topological sort
  Minimum depth of tree          Path existence
```

---

## 🔤 Trie — Prefix Tree

```java
class TrieNode { TrieNode[] ch = new TrieNode[26]; boolean end; }

class Trie {
    TrieNode root = new TrieNode();

    void insert(String w) {
        TrieNode n = root;
        for (char c : w.toCharArray()) {
            int i = c - 'a';
            if (n.ch[i] == null) n.ch[i] = new TrieNode();
            n = n.ch[i];
        }
        n.end = true;
    }

    boolean search(String w) {
        TrieNode n = root;
        for (char c : w.toCharArray()) {
            int i = c - 'a';
            if (n.ch[i] == null) return false;
            n = n.ch[i];
        }
        return n.end;
    }
}
// Time: O(m) per insert/search where m = word length
// Use for: autocomplete, spell check, IP routing
```

---

## ⛰️ Heap — Priority Queue

```java
// Java: PriorityQueue is a MIN-heap by default
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());

minHeap.offer(5); minHeap.offer(1); minHeap.offer(3);
minHeap.peek();  // → 1  O(1)
minHeap.poll();  // → 1, removes it  O(log n)

// Classic use: K largest elements
// Keep min-heap of size K. If new > peek, swap.
```

---

## 💡 Key Takeaways

| Structure | Best Use Case | Time Complexity |
|-----------|--------------|-----------------|
| BST | Sorted data, range queries | O(log n) balanced |
| Trie | Prefix search, autocomplete | O(m) per word |
| Heap/PQ | K-largest/smallest, Dijkstra | O(log n) insert/remove |
| BFS | Shortest path, level-order | O(V + E) |
| DFS | Cycles, topological sort, paths | O(V + E) |
| In-order | Get sorted output from BST | O(n) |

---

*[← Chapter 3](10-stacks-and-queues.md) | [Back to Index](../README.md) | [Chapter 5 — Bit Manipulation →](12-bit-manipulation.md)*
