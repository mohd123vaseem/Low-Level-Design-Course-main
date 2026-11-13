# Strategy Design Pattern: Notes

## 1. Overview

This file covers two connected topics:

1. **Composition over Inheritance**: _why_ putting every behaviour into a class hierarchy breaks down.
2. **Strategy Design Pattern**: the standard fix, where each behaviour becomes a swappable object.

---

## 2. Composition over Inheritance

### Definition

> **"Get behaviour by HAVING objects that do the work (has-a), instead of INHERITING it from a parent (is-a)."**

- **Inheritance (is-a):** behaviour is fixed in the class at compile time. `WorkerRobot` _is-a_ `Robot` and its `fly()` is baked in.
- **Composition (has-a):** the class holds a pointer to a behaviour object and **delegates** to it. `Robot` _has-a_ `FlyBehavior` and calls `flyBehavior->fly()`.

### What problem it solves (why we study it)

Imagine robots that can **walk, talk and fly** in different ways, and every robot type picks its own mix. With inheritance alone:

- **Code duplication:** `WorkerRobot` and `DeliveryRobot` both fly the same way, so the same `fly()` code is **copy-pasted** in both.
- **Class explosion:** 3 abilities × 2 variants each = **8 combinations**, so up to 8 subclasses. Add one more ability and it doubles to 16.
- **Can't change at runtime:** a robot can't switch from "NormalFly" to "NoFly" (for example, low battery), because behaviour is fixed by its class.
- **Bug fixes in many places:** fix the flying logic and you must edit every subclass that copied it.

```
------------------------------------------------------------------------------------------------
| Problem with inheritance only                 | Benefit with composition                     |
------------------------------------------------------------------------------------------------
| Same behaviour copy-pasted in many subclasses | Each behaviour written ONCE in its own class |
------------------------------------------------------------------------------------------------
| Class explosion: one subclass per combination | Mix and match behaviours, no new subclasses  |
------------------------------------------------------------------------------------------------
| Behaviour fixed at compile time               | Swap behaviour at runtime                    |
------------------------------------------------------------------------------------------------
| Fix a bug in many places                      | Fix it in one behaviour class                |
------------------------------------------------------------------------------------------------
```

**Key idea:** When behaviours **vary independently** and get **mixed and matched**, don't inherit them. **Hold them as objects.**

**Analogy 📱:** a phone doesn't come with one fixed camera app baked in forever. It **has** apps; you install, remove or swap them. The phone stays the same.

### Examples

#### ❌ Bad: every combination as a subclass

```
                     +----------------------+
                     |  <<abstract>> Robot  |
                     +----------------------+
                     | + walk()             |
                     | + talk()             |
                     | + fly()              |
                     | + projection() = 0   |
                     +----------------------+
                                 ^
                                 | is-a
          +----------------------+------------------------+
          |                      |                        |
+------------------+  +---------------------+  +---------------------+
|  CompanionRobot  |  |     WorkerRobot     |  |    DeliveryRobot    |
+------------------+  +---------------------+  +---------------------+
| walk: NORMAL     |  | walk: NO            |  | walk: NO            |
| talk: NORMAL     |  | talk: NO            |  | talk: NO            |
| fly : NO         |  | fly : NORMAL (COPY) |  | fly : NORMAL (COPY) |
+------------------+  +---------------------+  +---------------------+
```

Two classes, identical flying code. Every new combination means another subclass.

#### ✅ Good: hold the behaviour as an object

```
+---------------------------------+  has-a   +--------------------------+
|              Robot              |--------->| <<abstract>> FlyBehavior |
+---------------------------------+          +--------------------------+
| - flyBehavior : FlyBehavior*    |          | + fly() = 0              |
+---------------------------------+          +--------------------------+
| + fly()  -> flyBehavior->fly()  |                        ^
+---------------------------------+                        | is-a
                                                   +-------+-------+
                                                   |               |
                                            +------------+  +------------+
                                            | NormalFly  |  |   NoFly    |
                                            +------------+  +------------+
                                            | + fly()    |  | + fly()    |
                                            +------------+  +------------+
```

"Flying normally" is written **once**, and any robot can use it. This idea, done properly for every behaviour, **is the Strategy Pattern**.

### How to spot the problem

- Sibling subclasses with **copy-pasted method bodies**.
- Subclass names that list combinations (`FlyingTalkingRobot`, `WalkingNonTalkingRobot`).
- A need to **change behaviour while the program runs**.

### How to apply it

1. Find the behaviours that **vary** between subclasses.
2. Move each one into its **own small class hierarchy** (interface + variants).
3. Give the main class a **pointer** to that interface and **delegate** to it.

---

## 3. Strategy Design Pattern

### Definition

> **"Define a family of algorithms, put each one in its own class, and make them interchangeable. Strategy lets the algorithm vary independently from the clients that use it."** (Gang of Four)

- **Strategy (interface):** an abstract class declaring the behaviour (`WalkableRobot::walk() = 0`).
- **Concrete Strategies:** the different ways to do it (`NormalWalk`, `NoWalk`).
- **Context (Client):** the class that **has-a** strategy pointer and **delegates** to it (`Robot`).
- It's a **behavioural** design pattern: it is about how objects do things.

**Standard UML (from the lecture):**

```
+------------------------+  has-a      +------------------------+
|   Client  (Context)    |------------>| <<abstract>> Strategy  |
+------------------------+             +------------------------+
| - strategy : Strategy* |             | + run() = 0            |
+------------------------+             +------------------------+
| + execute()            |                          ^
|   -> strategy->run()   |                          | is-a
+------------------------+   +----------------------+----------------------+
                             |                      |                      |
                   +-------------------+  +-------------------+  +-------------------+
                   | ConcreteStrategyA |  | ConcreteStrategyB |  | ConcreteStrategyC |
                   +-------------------+  +-------------------+  +-------------------+
                   | + run() { }       |  | + run() { }       |  | + run() { }       |
                   +-------------------+  +-------------------+  +-------------------+
```

The **Client** has-a **Strategy** and calls `strategy->run()` inside `execute()`. Each **ConcreteStrategy** gives its own `run()`. The client never knows _which_ one it holds.

### What problem it solves (why we study it)

- **Removes if-else / switch** on "type of algorithm" (`if (mode == "car") ... else if (mode == "bike")`).
- **Removes duplication and class explosion** (see Composition over Inheritance above).
- **Allows switching behaviour at runtime** (e.g. change route from car to walking mid-trip).
- **New behaviour = new class only.** The context stays unchanged (OCP).

```
-------------------------------------------------------------------------------------------
| Problem without Strategy                    | Benefit with Strategy                     |
-------------------------------------------------------------------------------------------
| Big if-else / switch choosing the algorithm | Each algorithm in its own class           |
-------------------------------------------------------------------------------------------
| Adding an algorithm edits the main class    | Add a new strategy class only (OCP)       |
-------------------------------------------------------------------------------------------
| Behaviour fixed per subclass                | Swap strategy at runtime                  |
-------------------------------------------------------------------------------------------
| Duplicated code across subclasses           | Write each behaviour once, reuse anywhere |
-------------------------------------------------------------------------------------------
| Hard to test algorithms separately          | Test each strategy on its own             |
-------------------------------------------------------------------------------------------
```

**Key idea:** **Separate WHAT the object is from HOW it does a task.** The "how" becomes a pluggable object.

**Cricket analogy 🏏:** the **captain (context)** has a **bowling strategy**. Spin on a dry pitch, pace on a green one. The captain doesn't change; he just **swaps the bowler** depending on conditions.

### Examples

#### Example 1: Robots (from the lecture code)

Each robot has **3 strategies** (walk, talk, fly), and each strategy has 2 variants:

```
+--------------------+  has-a (3 strategies)
| <<abstract>> Robot |------------------------+-------------------------------+-------------------------------+
+--------------------+                        v                               v                               v
| # walkBehavior     |         +----------------------------+  +----------------------------+  +----------------------------+
| # talkBehavior     |         | <<abstract>> WalkableRobot |  | <<abstract>> TalkableRobot |  | <<abstract>> FlyableRobot  |
| # flyBehavior      |         +----------------------------+  +----------------------------+  +----------------------------+
+--------------------+         | + walk() = 0               |  | + talk() = 0               |  | + fly() = 0                |
| + walk()           |         +----------------------------+  +----------------------------+  +----------------------------+
| + talk()           |                        ^                               ^                               ^
| + fly()            |                        | is-a                          | is-a                          | is-a
| + projection() = 0 |                +-------+-------+               +-------+-------+               +-------+-------+
+--------------------+                |               |               |               |               |               |
                               +------------+  +------------+  +------------+  +------------+  +------------+  +------------+
                               | NormalWalk |  |   NoWalk   |  | NormalTalk |  |   NoTalk   |  | NormalFly  |  |   NoFly    |
                               +------------+  +------------+  +------------+  +------------+  +------------+  +------------+
                               | + walk()   |  | + walk()   |  | + talk()   |  | + talk()   |  | + fly()    |  | + fly()    |
                               +------------+  +------------+  +------------+  +------------+  +------------+  +------------+
```

Robot **types** still use inheritance, but only for what truly differs per type (`projection()`):

```
          +----------------------+
          |  <<abstract>> Robot  |
          +----------------------+
          | + projection() = 0   |
          +----------------------+
                      ^
                      | is-a
          +-----------+-----------+
          |                       |
+------------------+    +------------------+
|  CompanionRobot  |    |   WorkerRobot    |
+------------------+    +------------------+
| + projection()   |    | + projection()   |
+------------------+    +------------------+
```

> Code: `StrategyDesignPattern.cpp`: the 3 strategy interfaces with Normal/No versions, `Robot` delegating `walk()/talk()/fly()`, `CompanionRobot` / `WorkerRobot`, and `main()` passing different strategy objects into the constructor.

Any mix of walk/talk/fly is just a **different set of objects passed in**. No new subclasses are needed.

**Bonus: change behaviour at runtime.**

A setter `setFlyBehavior(FlyableRobot* f)` lets the same robot switch from `NoFly` to `NormalFly` while the program runs (not in the lecture file).

#### Example 2: Navigation app (classic interview one)

##### ❌ Bad: if-else inside the context

`Navigator::navigate()` has `if (mode == "car") ... else if (mode == "bike") ... else if (mode == "walk")`. Every new mode means editing this class (breaks OCP).

##### ✅ Good: each route algorithm is a strategy

```
+----------------------------+  has-a   +----------------------------+
|    Navigator  (Context)    |--------->| <<abstract>> RouteStrategy |
+----------------------------+          +----------------------------+
| - route : RouteStrategy*   |          | + buildRoute(a, b) = 0     |
+----------------------------+          +----------------------------+
| + setRoute(RouteStrategy*) |                         ^
| + navigate(a, b)           |                         | is-a
+----------------------------+    +--------------------+--------------------+
                                  |                    |                    |
                         +-----------------+  +-----------------+  +-----------------+
                         |     CarRoute    |  |    BikeRoute    |  |    WalkRoute    |
                         +-----------------+  +-----------------+  +-----------------+
                         | + buildRoute()  |  | + buildRoute()  |  | + buildRoute()  |
                         +-----------------+  +-----------------+  +-----------------+
```

Switch mode mid-trip with `setRoute(new BikeRoute())`. Adding a `TrainRoute` needs no change to `Navigator`.

### When to use it (how to spot the need)

- A class has a **big if-else / switch** that picks _how_ to do something.
- **Several subclasses differ only in one behaviour**, and that code gets copy-pasted.
- You need to **change the algorithm at runtime** (payment method, route, sorting, compression, discount).
- You want to **add new variants without editing** existing code.

### How to apply it

1. Find the behaviour that **varies** (walk, route, payment...).
2. Create a **Strategy interface** with a pure virtual method (`walk() = 0`).
3. Write one **Concrete Strategy** class per variant (`NormalWalk`, `NoWalk`).
4. Give the **Context** a `Strategy*` member and **delegate** to it.
5. **Inject** the strategy via the constructor (and a setter if it must change at runtime).

---

## 4. Links to other principles

- **OCP:** new behaviour = new strategy class, and the context is never edited.
- **DIP:** the context depends on the strategy **abstraction** (`WalkableRobot*`), not on `NormalWalk`. Strategies are **injected** through the constructor.
- **SRP:** each strategy class does exactly one job (one way of walking).
- **ISP:** walk, talk and fly are **separate small interfaces**, not one fat `RobotBehavior`.
- **LSP:** every concrete strategy must work wherever its interface is expected.

## 5. Comparison / summary

```
---------------------------------------------------------------------------------------------------
|                      | Inheritance (is-a)                | Composition / Strategy (has-a)       |
---------------------------------------------------------------------------------------------------
| Behaviour decided    | At compile time, by the class     | At runtime, by the object passed in  |
---------------------------------------------------------------------------------------------------
| Reusing a behaviour  | Copy-paste into each subclass     | Reuse the same strategy object/class |
---------------------------------------------------------------------------------------------------
| New combination      | New subclass                      | Pass a different set of strategies   |
---------------------------------------------------------------------------------------------------
| Change while running | Not possible                      | Yes, with a setter                   |
---------------------------------------------------------------------------------------------------
| Coupling             | Tight (child tied to parent code) | Loose (via interface)                |
---------------------------------------------------------------------------------------------------
```

---

## 6. Important interview questions

**Q1. What is the Strategy Design Pattern?**
A behavioural pattern that puts each algorithm/behaviour in its own class behind a common interface, so the context can use and swap them interchangeably.

**Q2. What are the parts of the Strategy pattern?**
Strategy (interface), Concrete Strategies (implementations), and Context/Client (holds a strategy pointer and delegates to it).

**Q3. Why "composition over inheritance"?**
Inheritance fixes behaviour at compile time and causes duplication and class explosion when behaviours combine. Composition lets you reuse and swap behaviours freely.

**Q4. How do you change the strategy at runtime?**
Give the context a setter (`setFlyBehavior(FlyableRobot*)`) that replaces the strategy pointer.

**Q5. Which SOLID principles does Strategy follow?**
Mainly OCP (add strategies without editing the context) and DIP (the context depends on the strategy abstraction). Also SRP and ISP.

**Q6. Real-world uses of Strategy?**
Payment methods, navigation routes, sorting algorithms, compression formats, discount/pricing rules, authentication methods.

**Q7. Strategy vs simple inheritance/polymorphism: what's the difference?**
In plain polymorphism the object IS the variant (subclass). In Strategy the object HAS a variant (member pointer), so it can mix several behaviours and change them at runtime.

**Q8. Downside of Strategy?**
More classes, and the client must know which strategy to pick and pass in. It's overkill if there are only one or two fixed behaviours that never change.

---

## 7. One-line revision

> **"Don't inherit HOW to do something. HOLD it as a swappable strategy object."**

Related code in this folder: `StrategyDesignPattern.cpp`. Lecture UML: `../Standard UML.png`.
Previous: **Lecture 07**. Next: **Lecture 09** (Factory patterns).
