# Factory Design Patterns: Notes

## 1. Overview
This lecture covers **3 creational patterns**, each one fixing the limit of the previous one:
1. **Simple Factory**: one class decides *which* object to create.
2. **Factory Method**: an *abstract* factory with subclasses; each subclass decides which object to create.
3. **Abstract Factory**: a factory that creates a whole **family of related objects** (burger + garlic bread).

### The common idea: what is a "factory"?
> **"A factory is an object whose job is to CREATE other objects, so the client doesn't have to use `new ConcreteClass()` itself."**

- **Creational pattern:** a pattern about *how objects are created*.
- The client asks for **what** it wants (`"basic"`), and the factory decides **which class** to `new`.
- The client only knows the **abstract product** (`Burger*`), never `BasicBurger`.

**Analogy 🍔:** at a burger shop you say *"one basic burger"*. You don't go into the kitchen and assemble it. The **kitchen is the factory**, and you only get back a `Burger`.

### Reading the arrows: has-a vs creates
```
Client ---------> Factory          has-a   : Client KEEPS a Factory* as a member (lives with it)
Factory - - - - > BasicBurger      creates : Factory does `new BasicBurger()`, RETURNS it, keeps nothing
Burger  <-------- BasicBurger      is-a    : inheritance (drawn as ^ in the trees)
```
- A factory is **not has-a** with its products: `BurgerFactory` has **no `Burger*` member**. It builds a burger, hands it over and forgets it.
- So the link is a **dependency** ("creates", `<<create>>` in UML), drawn **dashed** `- - ->`. Solid `---->` is kept for has-a.
- The **concrete** factory creates the **concrete** product (`SinghBurger - - -> BasicBurger`). The abstract `BurgerFactory` creates nothing; it only promises to return a `Burger*`.

---

## 2. Simple Factory

### Definition
> **"One factory class with a single method that takes a type and returns the matching concrete object."**

- All the `if-else` / `switch` on the type lives **in one place** (the factory).
- The method returns the **abstract** type (`Burger*`).
- It's an **idiom/technique**, not one of the 23 official GoF patterns, but it's the first step towards them.

### What problem it solves (why we study it)
Without a factory, **every client** writes `new BasicBurger()` / `new PremiumBurger()` with its own if-else:
- **Creation logic is copy-pasted** in many places (order screen, delivery app, menu printer...).
- **Clients are tied to concrete classes**, which breaks DIP.
- **Adding a new burger** means finding and editing every if-else in the codebase.
- **Mixed responsibilities:** the client both *creates* and *uses* objects, which breaks SRP.

```
-----------------------------------------------------------------------------------------
| Problem without a factory                     | Benefit with Simple Factory           |
-----------------------------------------------------------------------------------------
| new ConcreteClass() scattered in every client | Creation in ONE class                 |
-----------------------------------------------------------------------------------------
| Same if-else copy-pasted everywhere           | One if-else, one place to change      |
-----------------------------------------------------------------------------------------
| Client knows every concrete class             | Client knows only the abstract Burger |
-----------------------------------------------------------------------------------------
| Client both creates and uses objects          | Factory creates, client uses (SRP)    |
-----------------------------------------------------------------------------------------
```

**Key idea:** **Separate "creating" an object from "using" it.** The client asks, and the factory builds.

### Examples

#### Example 1: BurgerFactory (from the lecture code)

##### ❌ Bad: client creates the burgers itself
```
                                                +---------------------+
                                                | <<abstract>> Burger |
                                                +---------------------+
                                                | + prepare() = 0     |
                                                +---------------------+
                                                           ^
                                                           | is-a
                                      +--------------------+--------------------+
                                      |                    |                    |
                              +---------------+  +------------------+  +-----------------+
                              |  BasicBurger  |  |  StandardBurger  |  |  PremiumBurger  |
                              +---------------+  +------------------+  +-----------------+
                              | + prepare()   |  | + prepare()      |  | + prepare()     |
                              +---------------+  +------------------+  +-----------------+
+------------------------------+      ^                    ^                    ^
|       main()  (Client)       |- - - +- - - - - - - - - - +- - - - - - - - - - +
+------------------------------+  creates (new) - knows all 3!
| if type == basic             |
|     -> new BasicBurger()     |
| if type == standard          |
|     -> new StandardBurger()  |
| if type == premium           |
|     -> new PremiumBurger()   |
| // copied in EVERY client    |
+------------------------------+
```

The client does `new BasicBurger()` / `new StandardBurger()` / `new PremiumBurger()` itself, inside its own if-else.
Adding a `VeggieBurger` means editing this if-else in **every** client.

##### ✅ Good: one BurgerFactory creates them
```
+----------------------------+  uses                +---------------------+
|      main()  (Client)      |- - - - - - - - - - ->| <<abstract>> Burger |
+----------------------------+                      +---------------------+
| - factory : BurgerFactory* |                      | + prepare() = 0     |
+----------------------------+                      +---------------------+
| burger = factory->         |                                 ^
|    createBurger(type)      |                                 | is-a
| burger->prepare()          |            +--------------------+--------------------+
+----------------------------+            |                    |                    |
               | has-a            +---------------+  +------------------+  +-----------------+
               |                  |  BasicBurger  |  |  StandardBurger  |  |  PremiumBurger  |
               |                  +---------------+  +------------------+  +-----------------+
               |                  | + prepare()   |  | + prepare()      |  | + prepare()     |
               v                  +---------------+  +------------------+  +-----------------+
  +-------------------------+             ^                    ^                    ^
  |      BurgerFactory      |- - - - - - -+- - - - - - - - - - +- - - - - - - - - - +
  +-------------------------+  creates (new)
  | + createBurger(type)    |
  |     : Burger*           |
  +-------------------------+
  | if-else lives HERE only |
  +-------------------------+
```

> Code: `SimpleFactory.cpp`: `Burger` + 3 burgers, `BurgerFactory::createBurger(type)` with the if-else, and `main()` asking the factory for a `"standard"` burger.
The client never writes `new StandardBurger()`. A new burger means editing **only** `BurgerFactory`.

#### Example 2: NotificationFactory (classic)
```
                                        +---------------------------+
                                        | <<abstract>> Notification |
                                        +---------------------------+
                                        | + send(msg) = 0           |
                                        +---------------------------+
                                                      ^
                                                      | is-a
                              +-----------------------+-----------------------+
                              |                       |                       |
                   +---------------------+  +-------------------+  +--------------------+
                   |  EmailNotification  |  |  SMSNotification  |  |  PushNotification  |
                   +---------------------+  +-------------------+  +--------------------+
                   | + send(msg)         |  | + send(msg)       |  | + send(msg)        |
                   +---------------------+  +-------------------+  +--------------------+
+----------------------+      ^                       ^                       ^
| NotificationFactory  |- - - +- - - - - - - - - - - -+- - - - - - - - - - - -+
+----------------------+  creates (new)
| + create(type)       |
|     : Notification*  |
+----------------------+
```

The client just calls `NotificationFactory::create("sms")` and then `send()`. It never names `SMSNotification`.

### Limitation (why we need the next pattern)
- The factory still has an **if-else**. A new burger type = **edit the factory** (not fully OCP).
- One factory = **one way** of making burgers. If a second shop makes **wheat** burgers, you'd need `if (brand == ...)` inside too, and the class grows forever.

### How to spot that you need it
- `new ConcreteClass()` + `if-else` on a type string appears in **many clients**.
- Clients `#include` / know about every concrete subclass.

### How to apply it
1. Make an **abstract product** (`Burger` with `prepare() = 0`).
2. Make concrete products inherit it (`BasicBurger`, ...).
3. Create a **factory class** with `Burger* createBurger(type)` containing the if-else.
4. Replace every `new ConcreteBurger()` in clients with `factory->createBurger(type)`.

### Where it is used (real world)
Wherever ONE place picks a class from an input (string, enum, config) and hides the `new`:

```
-----------------------------------------------------------------------------------------------
| Where                      | Input                    | Objects created                     |
-----------------------------------------------------------------------------------------------
| Notification service       | "email" / "sms" / "push" | EmailNotif, SMSNotif, PushNotif     |
-----------------------------------------------------------------------------------------------
| Logging setup from config  | "file" / "console"       | FileLogger, ConsoleLogger           |
-----------------------------------------------------------------------------------------------
| Database layer from config | "mysql" / "postgres"     | MySQLConnection, PostgresConnection |
-----------------------------------------------------------------------------------------------
| File viewer / parser       | file extension           | PdfParser, DocxParser, TxtParser    |
-----------------------------------------------------------------------------------------------
| Drawing apps (shape tool)  | selected tool            | Circle, Rectangle, Line             |
-----------------------------------------------------------------------------------------------
```

---

## 3. Factory Method

### Definition
> **"Define an interface for creating an object, but let SUBCLASSES decide which class to instantiate."** (GoF)

- The factory becomes **abstract**: `virtual Burger* createBurger(string& type) = 0;`
- Each **concrete factory** (`SinghBurger`, `KingBurger`) overrides it and creates **its own** products.
- The overridden `createBurger()` *is* the **"factory method"**.

Parts:
- **Product:** `Burger` (abstract).
- **Concrete products:** `BasicBurger`, ..., `BasicWheatBurger`, ...
- **Creator:** `BurgerFactory` (abstract, declares the factory method).
- **Concrete creators:** `SinghBurger`, `KingBurger` (implement the factory method).

### What problem it solves (why we study it)
In the lecture, there are now **two burger shops**: `SinghBurger` makes normal burgers and `KingBurger` makes **wheat** burgers. With one Simple Factory:
- The factory needs `if (brand == "singh") ... else if (brand == "king") ...` **inside** the type if-else.
- **A new shop = editing the factory** again (breaks OCP), and the class becomes huge (breaks SRP).
- Every shop's logic is mixed together, so a change for King can break Singh.

```
------------------------------------------------------------------------
| Problem with one Simple Factory   | Benefit with Factory Method      |
------------------------------------------------------------------------
| Nested if-else on brand AND type  | Each brand is its own class      |
------------------------------------------------------------------------
| New brand = edit the factory      | New brand = new subclass (OCP)   |
------------------------------------------------------------------------
| All brands mixed in one big class | One class per brand (SRP)        |
------------------------------------------------------------------------
| Client tied to one factory class  | Client uses BurgerFactory* (DIP) |
------------------------------------------------------------------------
```

**Key idea:** **Don't decide the brand with if-else. Let each subclass be one brand and create its own products.**

**Analogy 🏪:** a burger **franchise**. Head office defines *"every outlet must be able to make a burger"* (the abstract method). The Delhi outlet and the Mumbai outlet each **make it their own way**.

### Examples

#### Example 1: SinghBurger and KingBurger (from the lecture code)

##### ❌ Bad: one factory for all brands
```
+---------------------------------------------+
|  BurgerFactory  (ONE class for ALL brands)  |
+---------------------------------------------+
| + createBurger(brand, type)                 |
+---------------------------------------------+
| if brand == singh:                          |
|     basic    -> BasicBurger                 |
|     standard -> StandardBurger              |
|     premium  -> PremiumBurger               |
| else if brand == king:                      |
|     basic    -> BasicWheatBurger            |
|     standard -> StandardWheatBurger         |
|     premium  -> PremiumWheatBurger          |
| // new brand? EDIT this class (breaks OCP)  |
+---------------------------------------------+
```

##### ✅ Good: abstract factory method, one subclass per brand
```
+-----------------------------+  has-a   +----------------------------+
|       main()  (Client)      |--------->| <<abstract>> BurgerFactory |
+-----------------------------+          +----------------------------+
| - factory : BurgerFactory*  |          | + createBurger(type) = 0   |
+-----------------------------+          |     : Burger*              |
| factory = new SinghBurger() |          +----------------------------+
| factory->createBurger(type) |          | (creates nothing itself)   |
+-----------------------------+          +----------------------------+
                                                        ^
                                                        | is-a
                                           +------------+------------+
                                           |                         |
                               +----------------------+  +----------------------+
                               |     SinghBurger      |  |      KingBurger      |
                               +----------------------+  +----------------------+
                               | + createBurger(type) |  | + createBurger(type) |
                               +----------------------+  +----------------------+
```

Which concrete factory **creates** which burgers:
```
                                        +---------------------+
                                        | <<abstract>> Burger |
                                        +---------------------+
                                        | + prepare() = 0     |
                                        +---------------------+
                                                   ^
                                                   | is-a
                              +--------------------+--------------------+
                              |                    |                    |
                      +---------------+  +------------------+  +-----------------+
                      |  BasicBurger  |  |  StandardBurger  |  |  PremiumBurger  |
                      +---------------+  +------------------+  +-----------------+
                      | + prepare()   |  | + prepare()      |  | + prepare()     |
                      +---------------+  +------------------+  +-----------------+
+----------------------+      ^                    ^                    ^
|     SinghBurger      |- - - +- - - - - - - - - - +- - - - - - - - - - +
+----------------------+  creates (new)
| + createBurger(type) |
+----------------------+

                                            +---------------------+
                                            | <<abstract>> Burger |
                                            +---------------------+
                                            | + prepare() = 0     |
                                            +---------------------+
                                                       ^
                                                       | is-a
                              +------------------------+--------------------------+
                              |                        |                          |
                   +--------------------+  +-----------------------+  +----------------------+
                   |  BasicWheatBurger  |  |  StandardWheatBurger  |  |  PremiumWheatBurger  |
                   +--------------------+  +-----------------------+  +----------------------+
                   | + prepare()        |  | + prepare()           |  | + prepare()          |
                   +--------------------+  +-----------------------+  +----------------------+
+----------------------+      ^                        ^                          ^
|      KingBurger      |- - - +- - - - - - - - - - - - +- - - - - - - - - - - - - +
+----------------------+  creates (new)
| + createBurger(type) |
+----------------------+
```

> Code: `FactoryMethod.cpp`: abstract `BurgerFactory::createBurger(type) = 0`, `SinghBurger` (normal) and `KingBurger` (wheat) overriding it, and `main()` using `BurgerFactory* myFactory = new SinghBurger()`.
A 3rd shop? Add `class FarziBurger : public BurgerFactory`. **No existing class changes.**

> Note: the lecture's subclasses still have an if-else on `type`. That's fine (it's a *parameterized* factory method). The important part is that the **brand** choice moved from if-else into **subclasses**.

#### Example 2: Logistics (classic interview one)
```
         +--------------------------+                   +------------------------+
         |  <<abstract>> Logistics  |                   | <<abstract>> Transport |
         +--------------------------+                   +------------------------+
         | + createTransport() = 0  |                   | + deliver() = 0        |
         | + planDelivery()         |                   +------------------------+
         +--------------------------+                                ^
                       ^                                             | is-a
                       | is-a                                +-------+--------+
           +-----------+------------+                        |                |
           |                        |                 +-------------+  +-------------+
+---------------------+  +---------------------+      |     Ship    |  |    Truck    |
|    RoadLogistics    |  |     SeaLogistics    |      +-------------+  +-------------+
+---------------------+  +---------------------+      | + deliver() |  | + deliver() |
| + createTransport() |  | + createTransport() |      +-------------+  +-------------+
+---------------------+  +---------------------+             ^                ^
           |                        |                        |                |
           |                        +- - - -  creates  - - - +                |
           +- - - - - - - - - - - - - - - creates - - - - - - - - - - - - - - +
```

`planDelivery()` is written once in the parent; each subclass only decides **which transport to create**.

### How to spot that you need it
- A factory has an if-else on a **second dimension** (brand, platform, region...).
- You keep **editing the factory** when a new variant (shop, country, OS) appears.

### How to apply it
1. Make the factory **abstract** with `virtual Product* createX(...) = 0;`
2. Create **one concrete factory per variant** (`SinghBurger`, `KingBurger`).
3. Each one overrides the factory method and creates **its own** products.
4. The client holds `BurgerFactory*` and receives the concrete factory from outside (`main()`).

### Where it is used (real world)
Wherever a base class runs the common steps and each SUBCLASS decides which object to create:

```
-----------------------------------------------------------------------------------------------------------
| Where                           | Creator (subclasses)                      | Product each one creates  |
-----------------------------------------------------------------------------------------------------------
| Delivery / logistics apps       | RoadLogistics, SeaLogistics               | Truck, Ship               |
-----------------------------------------------------------------------------------------------------------
| Cross-platform UI dialogs       | WindowsDialog, MacDialog (createButton()) | WindowsButton, MacButton  |
-----------------------------------------------------------------------------------------------------------
| Java collections                | ArrayList, HashSet (iterator())           | Each one's own iterator   |
-----------------------------------------------------------------------------------------------------------
| Game levels                     | IceLevel, FireLevel (createEnemy())       | IceEnemy, FireEnemy       |
-----------------------------------------------------------------------------------------------------------
| Restaurant franchises (lecture) | SinghBurger, KingBurger                   | Their own burger variants |
-----------------------------------------------------------------------------------------------------------
```

---

## 4. Abstract Factory

### Definition
> **"Provide an interface for creating FAMILIES of related objects, without specifying their concrete classes."** (GoF)

- The factory has **several** creation methods, one per product (`createBurger()`, `createGarlicBread()`).
- Each **concrete factory = one family**: `SinghBurger` makes normal products, `KingBurger` makes **wheat** products.
- The client picks **one factory**, and every product it gets is guaranteed to **match**.

Parts:
- **Abstract factory:** `MealFactory` (`createBurger() = 0`, `createGarlicBread() = 0`).
- **Concrete factories:** `SinghBurger`, `KingBurger` (one per family).
- **Abstract products:** `Burger`, `GarlicBread`.
- **Concrete products:** `BasicBurger`, `CheeseGarlicBread`, `BasicWheatBurger`, `CheeseWheatGarlicBread`, ...

### What problem it solves (why we study it)
Now each shop sells a **meal: burger + garlic bread**, and they must belong to the **same family** (a wheat shop serves wheat burger *and* wheat garlic bread). With separate factories:
- The client picks the burger factory and the bread factory **separately**, so it can **mix families** (normal burger + wheat bread) by mistake. 💥
- The client has to manage **many factory objects**.
- Nothing in the code **guarantees** that the products go together.

```
------------------------------------------------------------------------------
| Problem with separate factories      | Benefit with Abstract Factory       |
------------------------------------------------------------------------------
| Can mix families by mistake          | ONE factory = ONE consistent family |
------------------------------------------------------------------------------
| Client manages many factories        | Client holds ONE MealFactory*       |
------------------------------------------------------------------------------
| Matching rules live in the client    | Matching is built into each factory |
------------------------------------------------------------------------------
| Switching family = change many lines | Switching family = change ONE line  |
------------------------------------------------------------------------------
```

**Key idea:** **One factory creates a whole matching set of products. Change the factory, and the whole family changes together.**

**Analogy 🍱:** a **combo meal counter**. You choose *"King combo"* once, and everything in the tray (burger, bread) comes from the wheat menu. You can't accidentally get half of another shop's combo.

### Examples

#### Example 1: MealFactory (from the lecture code)

##### ❌ Bad: separate factories, chosen separately
```
                             +-------------------------------------+
                             |           main()  (Client)          |
                             +-------------------------------------+
                             | burgerF = new SinghBurgerFactory()  |
                             | breadF  = new KingBreadFactory()    |
                             | // MIXED families! normal + wheat   |
                             +-------------------------------------+
                                                | has-a  (2 factories, chosen separately)
                       +------------------------+------------------------+
                       v                                                 v
        +----------------------------+                   +-------------------------------+
        | <<abstract>> BurgerFactory |                   |   <<abstract>> BreadFactory   |
        +----------------------------+                   +-------------------------------+
        | + createBurger(type) = 0   |                   | + createGarlicBread(type) = 0 |
        +----------------------------+                   +-------------------------------+
                       ^                                                 ^
                       | is-a                                            | is-a
           +-----------+-----------+                         +-----------+-----------+
           |                       |                         |                       |
+--------------------+  +--------------------+    +--------------------+  +--------------------+
| SinghBurgerFactory |  | KingBurgerFactory  |    | SinghBreadFactory  |  |  KingBreadFactory  |
+--------------------+  +--------------------+    +--------------------+  +--------------------+
```

The client picks `new SinghBurgerFactory()` for burgers and `new KingBreadFactory()` for bread, so it gets a normal burger with wheat bread 💥.
The code compiles, but the meal is **inconsistent**.

##### ✅ Good: one MealFactory per family
```
+---------------------------+  has-a         +--------------------------------+
|      main()  (Client)     |--------------->|    <<abstract>> MealFactory    |
+---------------------------+                +--------------------------------+
| - mealFactory             |                | + createBurger(type) = 0       |
|     : MealFactory*        |                | + createGarlicBread(type) = 0  |
+---------------------------+                +--------------------------------+
| mealFactory =             |                                 ^
|    new KingBurger()       |                                 | is-a
| ->createBurger(type)      |                 +---------------+----------------+
| ->createGarlicBread(type) |                 |                                |
+---------------------------+   +---------------------------+  +------------------------------+
                                |   SinghBurger  (NORMAL)   |  |     KingBurger  (WHEAT)      |
                                +---------------------------+  +------------------------------+
                                | + createBurger(type)      |  | + createBurger(type)         |
                                | + createGarlicBread(type) |  | + createGarlicBread(type)    |
                                +---------------------------+  +------------------------------+
                                | burger: Basic/Std/Premium |  | burger: Wheat Basic/Std/Prem |
                                | bread : Basic/Cheese      |  | bread : Wheat Basic/Cheese   |
                                +---------------------------+  +------------------------------+
```

The products:
```
     +---------------------+                    +--------------------------+
     | <<abstract>> Burger |                    | <<abstract>> GarlicBread |
     +---------------------+                    +--------------------------+
     | + prepare() = 0     |                    | + prepare() = 0          |
     +---------------------+                    +--------------------------+
                ^                                             ^
                | is-a                                        | is-a
       +--------+---------+                        +----------+-----------+
       |                  |                        |                      |
+-------------+  +----------------+      +------------------+  +---------------------+
| BasicBurger |  | ...WheatBurger |      | BasicGarlicBread |  | ...WheatGarlicBread |
+-------------+  +----------------+      +------------------+  +---------------------+
```

```
---------------------------------------------------------------------------------------------------
| Family (factory)     | Burger                                 | Garlic bread                    |
---------------------------------------------------------------------------------------------------
| SinghBurger (NORMAL) | Basic / Standard / Premium Burger      | Basic / Cheese GarlicBread      |
---------------------------------------------------------------------------------------------------
| KingBurger (WHEAT)   | Basic / Standard / Premium WheatBurger | Basic / Cheese WheatGarlicBread |
---------------------------------------------------------------------------------------------------
```

> Code: `AbstractFactory.cpp`: the `Burger` and `GarlicBread` products, `MealFactory` with `createBurger()` + `createGarlicBread()`, `SinghBurger` / `KingBurger`, and `main()` using `new KingBurger()`.
Change `new KingBurger()` to `new SinghBurger()`, and the **whole meal** switches to the normal family.

#### Example 2: Cross-platform UI (classic interview one)
```
+-------------------------+  has-a   +--------------------------+
|  Application  (Client)  |--------->| <<abstract>> GUIFactory  |
+-------------------------+          +--------------------------+
| - factory : GUIFactory* |          | + createButton() = 0     |
+-------------------------+          | + createCheckbox() = 0   |
| + renderUI()            |          +--------------------------+
+-------------------------+                        ^
                                                   | is-a
                                      +------------+------------+
                                      |                         |
                           +--------------------+    +--------------------+
                           |   WindowsFactory   |    |     MacFactory     |
                           +--------------------+    +--------------------+
                           | -> WindowsButton   |    | -> MacButton       |
                           | -> WindowsCheckbox |    | -> MacCheckbox     |
                           +--------------------+    +--------------------+
```

The products:
```
      +---------------------+                    +-----------------------+
      | <<abstract>> Button |                    | <<abstract>> Checkbox |
      +---------------------+                    +-----------------------+
      | + paint() = 0       |                    | + paint() = 0         |
      +---------------------+                    +-----------------------+
                 ^                                           ^
                 | is-a                                      | is-a
        +--------+---------+                       +---------+----------+
        |                  |                       |                    |
+---------------+  +---------------+      +-----------------+  +-----------------+
| WindowsButton |  |   MacButton   |      | WindowsCheckbox |  |   MacCheckbox   |
+---------------+  +---------------+      +-----------------+  +-----------------+
```

Pick `new MacFactory()` once (from the detected OS), and every button and checkbox it creates is a Mac one, never a Windows one.

### Trade-off
- ✅ **New family** (e.g. a `MultiGrainBurger` shop) = one new factory class. Easy.
- ❌ **New product type** (e.g. `Fries`) = add `createFries() = 0` to `MealFactory` and **edit every concrete factory**. Hard.

### How to spot that you need it
- You create **several related objects** that must **match** (same theme, OS, brand, DB vendor).
- You see if-elses on the same family flag (`isWheat`, `os == "mac"`) repeated for **each** product.

### How to apply it
1. List the **products** (`Burger`, `GarlicBread`) and make each an abstract class.
2. List the **families** (normal, wheat) and make concrete products for each family.
3. Make an **abstract factory** with one `create...() = 0` per product.
4. Make **one concrete factory per family** that creates only that family's products.
5. The client holds **one** `MealFactory*`, chosen once in `main()`.

### Where it is used (real world)
Wherever a whole FAMILY of related objects must match each other:

```
----------------------------------------------------------------------------------------------------------------------------
| Where                                       | Factories                           | Family of products                   |
----------------------------------------------------------------------------------------------------------------------------
| Cross-platform UI (Qt, Swing look-and-feel) | WindowsFactory, MacFactory          | Button + Checkbox + Menu             |
----------------------------------------------------------------------------------------------------------------------------
| App themes                                  | DarkThemeFactory, LightThemeFactory | Button + TextBox + ScrollBar colours |
----------------------------------------------------------------------------------------------------------------------------
| DB drivers (ADO.NET DbProviderFactory)      | One per DB vendor                   | Connection + Command + Reader        |
----------------------------------------------------------------------------------------------------------------------------
| Game worlds                                 | IceWorldFactory, FireWorldFactory   | Enemy + Obstacle + Background        |
----------------------------------------------------------------------------------------------------------------------------
| Restaurant meals (lecture)                  | SinghFactory, KingFactory           | Burger + GarlicBread                 |
----------------------------------------------------------------------------------------------------------------------------
```

---

## 5. Links to other principles
- **SRP:** creation logic moves out of the client into the factory; the client only *uses* objects.
- **OCP:** Factory Method / Abstract Factory add a new brand or family as a **new subclass**, without editing old code.
- **DIP:** the client depends on `Burger*` and `BurgerFactory*` / `MealFactory*` (abstractions), never on `BasicBurger` or `KingBurger`.
- **Strategy (Lecture 08):** Strategy chooses **how an object behaves**; Factory chooses **which object gets created**. They're often used together: a factory creates the right strategy.

## 6. Comparison / summary

```
-------------------------------------------------------------------------------------------------------------------------------------
|                  | Simple Factory             | Factory Method                           | Abstract Factory                       |
-------------------------------------------------------------------------------------------------------------------------------------
| What it is       | One class with an if-else  | Abstract method, subclasses create       | Abstract factory of a product FAMILY   |
-------------------------------------------------------------------------------------------------------------------------------------
| Creates          | ONE product type           | ONE product type                         | MANY related product types             |
-------------------------------------------------------------------------------------------------------------------------------------
| Factory classes  | 1 concrete class           | Abstract + 1 subclass per variant        | Abstract + 1 subclass per family       |
-------------------------------------------------------------------------------------------------------------------------------------
| Lecture code     | BurgerFactory              | BurgerFactory -> SinghBurger, KingBurger | MealFactory -> SinghBurger, KingBurger |
-------------------------------------------------------------------------------------------------------------------------------------
| New variant      | Edit the factory (not OCP) | New subclass (OCP)                       | New factory subclass (OCP)             |
-------------------------------------------------------------------------------------------------------------------------------------
| New product type | Edit the factory           | New factory hierarchy                    | Edit EVERY factory (hard)              |
-------------------------------------------------------------------------------------------------------------------------------------
| GoF pattern?     | No (idiom)                 | Yes                                      | Yes                                    |
-------------------------------------------------------------------------------------------------------------------------------------
```

---

## 7. Important interview questions

**Q1. What is the Factory pattern and why use it?**
It moves object creation (`new ConcreteClass()`) out of the client into a separate factory, so the client depends only on the abstract product. This removes duplicated if-elses and supports SRP, OCP and DIP.

**Q2. Difference between Simple Factory and Factory Method?**
Simple Factory is one concrete class with an if-else that creates objects. Factory Method makes the creation method abstract, and subclasses decide which class to create, so new variants are added without editing existing code.

**Q3. Difference between Factory Method and Abstract Factory?**
Factory Method creates **one** product through one overridable method. Abstract Factory groups **several** factory methods to create a **family** of related products that must be used together.

**Q4. Is Simple Factory a GoF design pattern?**
No. It's a common programming idiom. The GoF creational patterns are Factory Method, Abstract Factory, Builder, Prototype and Singleton.

**Q5. Which SOLID principles do factories support?**
SRP (creation separated from use), OCP (new variants = new subclasses in Factory Method / Abstract Factory) and DIP (the client depends on abstract products and factories).

**Q6. What's the downside of Abstract Factory?**
Adding a **new product type** (e.g. `Fries`) means changing the abstract factory and **every** concrete factory. Adding a new family is easy.

**Q7. Why does the factory return `Burger*` and not `BasicBurger*`?**
So the client only knows the abstraction. The concrete class can change without changing the client (DIP + LSP).

**Q8. Why does `Burger` have a virtual destructor?**
The client deletes products through a `Burger*`. Without a virtual destructor, `delete burger` would call only `~Burger()` and skip the derived destructor (undefined behaviour).

**Q9. Factory vs Strategy?**
Factory is **creational** and decides *which object is created*. Strategy is **behavioural** and decides *how an object does something*, swappable at runtime.

**Q10. Real-world examples?**
A notification service creating Email/SMS/Push senders, a logistics app creating Truck/Ship, a UI toolkit creating Windows/Mac widgets, and a DB layer creating MySQL/Postgres connections.

---

## 8. One-line revision
> **"Simple Factory: one class decides. Factory Method: subclasses decide. Abstract Factory: one factory builds a whole matching family."**

Related code in this folder: `SimpleFactory.cpp`, `FactoryMethod.cpp`, `AbstractFactory.cpp`.
Previous: **Strategy Design Pattern** (`../../Lecture 08/C++ Code/`). Next: **Singleton Pattern** (`../../Lecture 10/C++ Code/`).
