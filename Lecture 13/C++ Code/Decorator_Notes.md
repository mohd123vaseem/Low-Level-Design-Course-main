# Decorator Design Pattern: Notes

## 1. Decorator Design Pattern

### Definition
> **"Attach additional responsibilities to an object DYNAMICALLY. Decorators provide a flexible alternative to subclassing for extending functionality."** (GoF, a structural pattern)

- A **decorator wraps an object** and adds something on top (Mario + HeightUp + Gun...).
- The decorator **is-a** `Character` (same interface, so it can be used anywhere a `Character*` is expected) and **has-a** `Character*` (the object it wraps).
- Because a decorator is itself a `Character`, decorators can be **stacked** in any order, any number of times, at **runtime**.

### What problem it solves (why we study it)
Mario can get power-ups: HeightUp, Gun, Star, and any **combination** of them. With inheritance only:
- **Class explosion:** one subclass per combination. 3 power-ups = 2^3 - 1 = **7 subclasses**, and a 4th power-up makes it 15.
- **Duplicate code:** "add Gun" is written again in every class that includes Gun.
- **Fixed at compile time:** a `MarioWithGun` object can't pick up a Star while the game is running. You'd need to create an object of yet another class.

```
----------------------------------------------------------------------------------------
| Problem with inheritance only               | Benefit with Decorator                 |
----------------------------------------------------------------------------------------
| One subclass per combination (7, 15, 31...) | One class per power-up (3)             |
----------------------------------------------------------------------------------------
| Same power-up code copied in many classes   | Each power-up written ONCE             |
----------------------------------------------------------------------------------------
| Combination fixed at compile time           | Wrap / stack at runtime                |
----------------------------------------------------------------------------------------
| New power-up = many new combo classes       | New power-up = ONE new decorator (OCP) |
----------------------------------------------------------------------------------------
```

**Key idea:** **Don't create a subclass for every combination. Wrap the object in layers, each layer adding one thing and passing the call inward.**

### Standard UML (from `Standard UML.jpeg`)
```
               +--------------------------+
               | <<abstract>> IComponent  |
               +--------------------------+
               | + methodA() = 0          |<-----------------------+
               | + methodB() = 0          |                        |
               +--------------------------+                        |
                             ^                                     |
                             | is-a                                | has-a
          +------------------+------------------+                  |
          |                                     |                  |
+-------------------+             +---------------------------+    |
| ConcreteComponent |             |   <<abstract>> Decorator  |----+
+-------------------+             +---------------------------+
| + methodA()       |             | # component : IComponent* |
| + methodB()       |             +---------------------------+
+-------------------+                           ^
                                                | is-a
                                    +-----------+-----------+
                                    |                       |
                         +--------------------+  +--------------------+
                         | ConcreteDecoratorA |  | ConcreteDecoratorB |
                         +--------------------+  +--------------------+
                         | + methodA()        |  | + methodA()        |
                         | + methodB()        |  | + methodB()        |
                         +--------------------+  +--------------------+
```

- **IComponent** (abstract): the common interface (`methodA()`, `methodB()`).
- **ConcreteComponent** is-a IComponent: the plain object being decorated. There can be several (drawn stacked in the image).
- **Decorator** (abstract) **is-a** IComponent **and has-a** `IComponent* component`. Both arrows point to the same class: that's the heart of the pattern.
- **ConcreteDecoratorA / B** is-a Decorator: each one calls `component->methodA()` and adds its own work.

### Example: Mario power-ups (lecture code)

Mapping to the UML:

```
---------------------------------------------------------------------------------------------
| Standard UML                            | Lecture code                                    |
---------------------------------------------------------------------------------------------
| IComponent                              | Character (getAbilities() = 0)                  |
---------------------------------------------------------------------------------------------
| ConcreteComponent                       | Mario                                           |
---------------------------------------------------------------------------------------------
| Decorator (has-a IComponent* component) | CharacterDecorator (has-a Character* character) |
---------------------------------------------------------------------------------------------
| ConcreteDecoratorA / B                  | HeightUp, GunPowerUp, StarPowerUp               |
---------------------------------------------------------------------------------------------
```

#### ❌ Bad: a subclass for every combination
```
                                  +------------------+
                                  |      Mario       |
                                  +------------------+
                                  | + getAbilities() |
                                  +------------------+
                                            ^
                                            | is-a (one subclass per COMBINATION)
          +--------------------+------------+---------+-----------------------+
          |                    |                      |                       |
+-------------------+  +--------------+  +-------------------------+  +---------------+
| MarioWithHeightUp |  | MarioWithGun |  | MarioWithHeightUpAndGun |  | ... 7 classes |
+-------------------+  +--------------+  +-------------------------+  +---------------+
```

MarioWithHeightUp, MarioWithGun, MarioWithStar, MarioWithHeightUpAndGun, MarioWithHeightUpAndStar, MarioWithGunAndStar, MarioWithAll: 7 classes for just 3 power-ups, with the same "with Gun" logic copied into 4 of them.

#### ✅ Good: power-ups as decorators
```
                    +-------------------------+
                    |  <<abstract>> Character |
                    +-------------------------+
                    | + getAbilities() = 0    |<------------------------------+
                    +-------------------------+                               |
                                 ^                                            |
                                 | is-a                                       | has-a
          +----------------------+----------------------+                     |
          |                                             |                     |
+------------------+                  +----------------------------------+    |
|      Mario       |                  | <<abstract>> CharacterDecorator  |----+
+------------------+                  +----------------------------------+
| + getAbilities() |                  | # character : Character*         |
|   -> "Mario"     |                  +----------------------------------+
+------------------+                  | + CharacterDecorator(Character*) |
                                      | + ~CharacterDecorator()          |
                                      |     -> delete character          |
                                      +----------------------------------+
                                                        ^
                                                        | is-a
                                  +---------------------+---------------------+
                                  |                     |                     |
                        +------------------+  +------------------+  +------------------+
                        |     HeightUp     |  |    GunPowerUp    |  |   StarPowerUp    |
                        +------------------+  +------------------+  +------------------+
                        | + getAbilities() |  | + getAbilities() |  | + getAbilities() |
                        +------------------+  +------------------+  | + ~StarPowerUp() |
                                                                    +------------------+
```

> Code: `DecoratorPattern.cpp`: `Character`, `Mario`, `CharacterDecorator` (stores the wrapped `Character*` and deletes it in its destructor), `HeightUp`, `GunPowerUp`, `StarPowerUp`, and `main()`.

- Each power-up's `getAbilities()` = **inner object's `getAbilities()` + its own text** (`character->getAbilities() + " with Gun"`).
- `CharacterDecorator` is **abstract even with no `= 0` of its own**: it **inherits** the pure virtual `getAbilities()` from `Character` and never overrides it, so it's still pure there (`new CharacterDecorator(...)` gives a compile error). Only the power-ups that override it are concrete.
- Only 3 decorator classes, and they combine freely.

#### How the layers are built (`main()`)
Each `new X(mario)` wraps the **current outermost object**, then `mario` points to the new wrapper:
```
mario = new Mario();               mario --> [Mario]
mario = new HeightUp(mario);       mario --> [HeightUp] --> [Mario]
mario = new GunPowerUp(mario);     mario --> [Gun] --> [HeightUp] --> [Mario]
mario = new StarPowerUp(mario);    mario --> [Star] --> [Gun] --> [HeightUp] --> [Mario]
```
- Every `-->` is the `character` pointer stored in `CharacterDecorator`.
- A layer knows **only the one directly below it**, and only as a `Character*`. `GunPowerUp` doesn't know whether it wraps `HeightUp`, `Mario` or 10 more layers.

#### How a call travels (down once, built back up)
`mario->getAbilities()` on the outermost (Star) object:
```
Star::getAbilities()
  calls character->getAbilities()            --> Gun
     Gun::getAbilities()
       calls character->getAbilities()       --> HeightUp
          HeightUp::getAbilities()
            calls character->getAbilities()  --> Mario
               Mario::getAbilities() returns "Mario"             <-- end of chain (no pointer)
          HeightUp returns "Mario" + " with HeightUp"
     Gun returns "Mario with HeightUp" + " with Gun"
Star returns "Mario with HeightUp with Gun" + " with Star Power (Limited Time)"
```
- **Going down:** each layer delegates first, so the call reaches `Mario`.
- **Coming back up:** each layer appends its text, so the output reads innermost (Mario) to outermost (Star).
- **Each layer runs exactly once** per call. It works like recursion, but it's **virtual-function delegation through different objects**, and `Mario` is the "base case".

**`main()` output, step by step:**

```
-----------------------------------------------------------------------------------------------------------
| Step in main()         | Chain (outer -> inner)           | getAbilities() prints                       |
-----------------------------------------------------------------------------------------------------------
| new Mario()            | Mario                            | Mario                                       |
-----------------------------------------------------------------------------------------------------------
| new HeightUp(mario)    | HeightUp -> Mario                | Mario with HeightUp                         |
-----------------------------------------------------------------------------------------------------------
| new GunPowerUp(mario)  | Gun -> HeightUp -> Mario         | Mario with HeightUp with Gun                |
-----------------------------------------------------------------------------------------------------------
| new StarPowerUp(mario) | Star -> Gun -> HeightUp -> Mario | ... with Gun with Star Power (Limited Time) |
-----------------------------------------------------------------------------------------------------------
```

### Deleting the chain (fixed in the code)
- `delete mario;` deletes only the **outermost** object (Star).
- **Originally**, nothing deleted the inner layers, so `Gun`, `HeightUp` and `Mario` **leaked**.
- **Fix:** `~CharacterDecorator() { delete character; }`. Deleting a layer now deletes the layer it wraps, so the whole chain is freed, the same way calls travel:
```
delete mario (Star)
  ~StarPowerUp()         prints "Destroying StarPowerUp Decorator"
  ~CharacterDecorator()  delete character --> Gun
     ~CharacterDecorator()  delete character --> HeightUp
        ~CharacterDecorator()  delete character --> Mario
           ~Mario()   (end of chain)
```
- This works because `Character` has a **virtual destructor**: `delete` through a `Character*` runs the real (derived) destructor first, then the base ones.

### How to spot that you need it
- You're creating subclasses for **combinations** of features (`MarioWithGunAndStar`).
- Features should be **added or removed at runtime**, on one object.
- Every feature is "the same thing, plus a bit more".

### How to apply it
1. Make the **component interface** (`Character` with `getAbilities() = 0`, plus a virtual destructor).
2. Make the **concrete component** (`Mario`).
3. Make an **abstract decorator** that is-a component **and** has-a `Component*`, set in its constructor, and deletes it in its destructor (`CharacterDecorator`).
4. Make one **concrete decorator per feature**: call the wrapped object, then add its own part (`HeightUp`, `GunPowerUp`, `StarPowerUp`).
5. Build at runtime: `obj = new Decorator(obj);` for each feature.

### Where it is used (real world)
Wherever optional features are stacked on one object at runtime:

```
--------------------------------------------------------------------------------------------------
| Where                     | Base object               | Layers added (decorators)              |
--------------------------------------------------------------------------------------------------
| Java I/O streams          | FileInputStream           | Buffered, GZIP stream wrappers         |
--------------------------------------------------------------------------------------------------
| Coffee / pizza ordering   | Coffee, base pizza        | Milk, cheese, toppings (price + text)  |
--------------------------------------------------------------------------------------------------
| Services in a backend     | Real service / API client | Logging, caching, retry, auth wrappers |
--------------------------------------------------------------------------------------------------
| GUI windows (GoF classic) | Text view                 | Scrollbar, border                      |
--------------------------------------------------------------------------------------------------
| Games (lecture)           | Mario                     | HeightUp, Gun, Star power-ups          |
--------------------------------------------------------------------------------------------------
| Python @decorator         | A function                | Timing, caching, auth wrappers         |
--------------------------------------------------------------------------------------------------
```

---

## 2. Links to other principles
- **OCP:** a new power-up is a new decorator class; `Mario` and the other power-ups never change.
- **SRP:** each decorator handles exactly one feature.
- **Composition over inheritance (Lecture 08):** features are added by **wrapping (has-a)**, not by subclass combinations. The is-a here is only to keep the same interface.
- **LSP:** any decorator must be usable wherever a `Character*` is expected, which is what makes stacking possible.

---

## 3. Important interview questions

**Q1. What is the Decorator pattern?**
A structural pattern that adds behaviour to an object at runtime by wrapping it in decorator objects that share its interface.

**Q2. Why does the decorator both inherit from AND hold a `Character`?**
Is-a gives it the same interface, so a decorated object can be used (and wrapped again) anywhere a `Character*` is expected. Has-a gives it the inner object to delegate to.

**Q3. How does `getAbilities()` work on 3 stacked decorators?**
Each layer calls `character->getAbilities()` on the layer below until it reaches `Mario`, then each layer appends its text on the way back. Every layer runs once.

**Q4. Why not just use inheritance?**
Combinations cause a class explosion (2^n - 1 subclasses for n features), duplicate code, and can't change at runtime.

**Q5. Does the order of decorators matter?**
Yes. The outermost decorator's part comes last in `getAbilities()`, so `Gun(HeightUp(Mario))` and `HeightUp(Gun(Mario))` give different strings.

**Q6. What memory issue can decorators cause in C++, and how is it fixed?**
Deleting the outermost decorator doesn't free the inner ones unless the decorator's destructor deletes the wrapped object (`delete character;`). The component also needs a virtual destructor.

**Q7. `CharacterDecorator` has no `= 0` of its own. Why is it abstract?**
It inherits the pure virtual `getAbilities()` from `Character` and doesn't override it. In C++, a class with ANY un-overridden pure virtual (its own or inherited) is abstract, so it can't be created; only the concrete power-ups can.

**Q8. Real-world uses?**
Adding toppings to a pizza or coffee (price + description), stream wrappers (buffered + compressed + encrypted streams), and adding logging/caching around a service.

---

## 4. One-line revision
> **"A decorator is-a Component AND has-a Component: wrap the object, call the inner one, add your bit. Stack layers at runtime instead of subclassing every combination."**

Related code in this folder: `DecoratorPattern.cpp` (and `../Standard UML.jpeg`).
Previous: **Observer Pattern** (`../../Lecture 12/C++ Code/`). Next: **Lecture 14: Notification System** (`../../Lecture 14/C++ Code/`).
