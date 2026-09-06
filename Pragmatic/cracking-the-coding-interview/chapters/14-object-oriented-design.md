# Chapter 7 — Object-Oriented Design

> *"OOD interviews are about demonstrating that you can build a system that is flexible, maintainable, and logically sound."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

OOD questions ask you to model a real-world system using classes, interfaces, and relationships. The goal is to show you can **identify the right entities, define their responsibilities, and make them interact cleanly**.

---

## 🔢 The 5-Step OOD Process

```
STEP 1: CLARIFY USE CASES
  → Who uses this? What actions can they perform?
  → "Parking lot" — multiple levels? payment? vehicle types?

STEP 2: DEFINE CORE OBJECTS (the nouns)
  → ParkingLot, Level, Spot, Vehicle, Ticket, Payment

STEP 3: IDENTIFY RELATIONSHIPS
  → Is-a (inheritance): Car IS-A Vehicle
  → Has-a (composition): ParkingLot HAS-A List<Level>
  → Uses-a (dependency): Attendant USES-A Ticket

STEP 4: DEFINE ACTIONS (the verbs → methods)
  → ParkingLot.parkVehicle(), Spot.isAvailable()

STEP 5: APPLY DESIGN PATTERNS
  → Singleton, Factory, Strategy, Observer...
```

---

## 🎮 Example: Design a Deck of Cards

```java
public enum Suit { CLUB, DIAMOND, HEART, SPADE }

public class Card {
    private final Suit suit;
    private final int value; // 1=Ace, 11=J, 12=Q, 13=K
    public Card(Suit suit, int value) {
        this.suit = suit; this.value = value;
    }
}

public class Deck {
    private List<Card> cards = new ArrayList<>();

    public Deck() {
        for (Suit s : Suit.values())
            for (int v = 1; v <= 13; v++)
                cards.add(new Card(s, v));
    }

    public void shuffle() { Collections.shuffle(cards); }

    public Card deal() {
        if (cards.isEmpty()) throw new IllegalStateException();
        return cards.remove(cards.size() - 1);
    }
}

// Strategy pattern for game-specific scoring:
public abstract class Hand {
    protected List<Card> cards = new ArrayList<>();
    public void addCard(Card c) { cards.add(c); }
    public abstract int score(); // blackjack vs. poker differ!
}

public class BlackjackHand extends Hand {
    @Override public int score() {
        int total = 0, aces = 0;
        for (Card c : cards) {
            if (c.getValue() == 1) { aces++; total += 11; }
            else total += Math.min(c.getValue(), 10);
        }
        while (total > 21 && aces > 0) { total -= 10; aces--; }
        return total;
    }
}
```

---

## 🅿️ Example: Design a Parking Lot

```java
// Singleton — only ONE parking lot exists
public class ParkingLot {
    private static ParkingLot instance;
    private Level[] levels;

    private ParkingLot() {}
    public static ParkingLot getInstance() {
        if (instance == null) instance = new ParkingLot();
        return instance;
    }

    public boolean parkVehicle(Vehicle v) {
        for (Level l : levels) {
            ParkingSpot spot = l.findAvailableSpot(v);
            if (spot != null) { spot.park(v); return true; }
        }
        return false; // full
    }
}

public class ParkingSpot {
    private Vehicle vehicle; // null = available
    private VehicleSize spotSize;

    public boolean canFitVehicle(Vehicle v) {
        return vehicle == null && v.canFitInSpot(this);
    }
    public void park(Vehicle v) { vehicle = v; }
    public void free()           { vehicle = null; }
}
```

---

## 🏗️ Key Design Patterns in OOD Interviews

```
SINGLETON     Only one instance. Private constructor +
              static getInstance(). Use for: ParkingLot.

FACTORY       Create objects without specifying class.
              CardGame.create("blackjack") → BlackjackGame.

STRATEGY      Swap algorithms at runtime via interface.
              Hand.score() differs per game — inject scorer.

OBSERVER      Notify many observers on state change.
              Subject.addObserver(o); Subject.notifyAll().

DECORATOR     Add behavior without subclassing.
              Coffee + Milk + Sugar = decorated Coffee.
```

---

## 💡 Key Takeaways

| Principle | Application |
|-----------|-------------|
| Clarify first | Ask edge-case questions before drawing anything |
| Nouns → classes | Real-world nouns map to objects |
| Verbs → methods | Real-world actions map to methods |
| Is-a vs Has-a | Inherit for "is-a"; compose for "has-a" |
| Singleton | One instance makes logical sense (ParkingLot) |
| Strategy | Behavior varies by context (scoring rules) |
| Open/Closed | Add new game types by extending, not modifying |

---

*[← Chapter 6](13-math-and-logic-puzzles.md) | [Back to Index](../README.md) | [Chapter 8 — Recursion & DP →](15-recursion-and-dynamic-programming.md)*
