# Chapter 10 — Sorting & Searching

> *"You should know the major sorting algorithms cold. The trick is recognizing which one fits the problem — or when to invent a custom approach."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Sorting and searching are foundational. In interviews, you rarely implement a sorting algorithm from scratch — but you MUST know their trade-offs to choose correctly, and binary search variants appear constantly in "medium" and "hard" problems.

---

## 📊 Sorting Algorithms — Comparison

```
ALGORITHM       TIME (avg)    TIME (worst)  SPACE   STABLE?
────────────────────────────────────────────────────────────
Bubble Sort     O(n²)         O(n²)         O(1)    ✅ Yes
Selection Sort  O(n²)         O(n²)         O(1)    ❌ No
Insertion Sort  O(n²)         O(n²)         O(1)    ✅ Yes
                              (O(n) if nearly sorted!)
Merge Sort      O(n log n)    O(n log n)    O(n)    ✅ Yes
Quick Sort      O(n log n)    O(n²)         O(log n)❌ No
Heap Sort       O(n log n)    O(n log n)    O(1)    ❌ No
Counting Sort   O(n + k)      O(n + k)      O(k)    ✅ Yes
                (k = range of input values)
────────────────────────────────────────────────────────────
Java Arrays.sort(): TimSort (Merge+Insertion), O(n log n)
Java Collections.sort(): same
```

---

## 🔀 Merge Sort — The Reliable Choice

Guaranteed O(n log n). Preferred when stability matters or for linked lists.

```java
void mergeSort(int[] arr, int left, int right) {
    if (left >= right) return;           // base case
    int mid = left + (right - left) / 2;
    mergeSort(arr, left, mid);           // sort left half
    mergeSort(arr, mid + 1, right);      // sort right half
    merge(arr, left, mid, right);        // merge sorted halves
}

void merge(int[] arr, int left, int mid, int right) {
    int[] tmp = Arrays.copyOfRange(arr, left, right + 1);
    int i = 0, j = mid - left + 1, k = left;
    while (i <= mid - left && j <= right - left)
        arr[k++] = tmp[i] <= tmp[j] ? tmp[i++] : tmp[j++];
    while (i <= mid - left) arr[k++] = tmp[i++];
    while (j <= right - left) arr[k++] = tmp[j++];
}
// Time: O(n log n) guaranteed, Space: O(n) for temp array
```

---

## ⚡ Quick Sort — The Fast Choice in Practice

O(n log n) average; O(n²) worst case (avoided with random pivot).

```java
void quickSort(int[] arr, int low, int high) {
    if (low < high) {
        int pivot = partition(arr, low, high);
        quickSort(arr, low, pivot - 1);
        quickSort(arr, pivot + 1, high);
    }
}

int partition(int[] arr, int low, int high) {
    int pivot = arr[high]; // pick last element as pivot
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(arr, i, j);  // move smaller elements left
        }
    }
    swap(arr, i + 1, high); // place pivot in correct position
    return i + 1;
}
// Average O(n log n), Worst O(n²) — use random pivot to avoid
```

---

## 🔍 Binary Search — The Essential Pattern

O(log n) search on a **sorted** array. Appears in dozens of interview problems.

```java
// Classic binary search
int binarySearch(int[] arr, int target) {
    int lo = 0, hi = arr.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;   // prevents overflow!
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1; // not found
}
```

### Binary Search Variants

```java
// Find LEFTMOST position of target (first occurrence)
int lowerBound(int[] arr, int target) {
    int lo = 0, hi = arr.length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return lo; // insertion point for target
}

// Find RIGHTMOST position (last occurrence + 1)
int upperBound(int[] arr, int target) {
    int lo = 0, hi = arr.length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] <= target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

// Search in ROTATED sorted array [4,5,6,7,0,1,2], target=0
int searchRotated(int[] arr, int target) {
    int lo = 0, hi = arr.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) return mid;
        if (arr[lo] <= arr[mid]) {           // left half is sorted
            if (arr[lo] <= target && target < arr[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {                             // right half is sorted
            if (arr[mid] < target && target <= arr[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return -1;
}
```

---

## 🏆 When to Use Which Sort?

```
PROBLEM CONTEXT                         BEST CHOICE
─────────────────────────────────────────────────────
General purpose, stability needed       Merge Sort
General purpose, in-memory speed        Quick Sort (random pivot)
Memory is tight, stability not needed   Heap Sort
Nearly sorted data                      Insertion Sort
Small integers, bounded range           Counting Sort / Radix Sort
Linked list (no random access)          Merge Sort
External sort (data doesn't fit in RAM) Merge Sort
```

---

## 💡 Key Takeaways

| Algorithm | Best For | Watch Out For |
|-----------|----------|---------------|
| Merge Sort | Stable sort, linked lists, guaranteed O(n log n) | O(n) extra space |
| Quick Sort | In-memory speed, general use | O(n²) worst case — use random pivot |
| Heap Sort | O(1) space + O(n log n) — but not stable | Cache-unfriendly in practice |
| Counting Sort | Small integer ranges (k is small) | Only works on integers |
| Binary Search | Anything on a sorted structure | Must be sorted first! |
| lower/upper bound | Finding ranges, insertion points | `hi = arr.length` not `arr.length-1` |

---

*[← Chapter 9](16-system-design-and-scalability.md) | [Back to Index](../README.md) | [Chapter 11 — Testing →](18-testing.md)*
