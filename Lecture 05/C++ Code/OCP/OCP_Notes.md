# Open/Closed Principle (OCP): Notes

## 1. What is OCP?
> **"Software entities should be OPEN for extension, but CLOSED for modification."** (Bertrand Meyer, the O in SOLID)

- **Open for extension:** you can add new behaviour (a new DB, payment type, shape...).
- **Closed for modification:** you add it **without editing existing, tested code**.
- How: **abstraction (abstract class / interface) + inheritance + polymorphism**.

### What does "extendable behaviour" mean?
Your app already saves carts to SQL and MongoDB. A new requirement comes in: **also save to Redis.**

- **Without OCP:** you open `ShoppingCartStorage` and add `saveToRedis()`. You've edited working, tested code, so SQL and Mongo can break and the whole class needs retesting.
- **With OCP:** you **add one new class** and touch nothing else:

```cpp
class RedisPersistence : public Persistence {            // NEW class only
public:
    void save(ShoppingCart* cart) override { cout << "Saving to Redis...
"; }
};

void checkout(ShoppingCart* cart, Persistence* db) { db->save(cart); }   // unchanged
checkout(cart, new RedisPersistence());                                 // just works
```

```
         +----------------------------+
         |  <<abstract>> Persistence  |   <- CLOSED: never edited
         +----------------------------+
                        ^
                        | is-a
      +-----------------+-----------------+
      |                 |                 |
+-----------+     +-----------+     +-----------+
|    SQL    |     |   Mongo   |     |   Redis*  |   <- OPEN: Redis* is a new class, just plugged in
+-----------+     +-----------+     +-----------+
```

The system's **behaviour grows** (it can now save to Redis) while the **old code stays frozen**. That is extension.
Analogy: a **power strip**. You plug in a new device without rewiring the strip.

##One-liner

>Extendable = new feature means a new class plugged into an existing abstraction. Zero edits to old classes.

---

## 2. Why do we need OCP?

| Problem without OCP                         | Benefit with OCP                            |
|---------------------------------------------|---------------------------------------------|
| Every new feature edits old, tested code    | New feature = new class, old code untouched |
| Risk of breaking features that already work | Existing behaviour stays safe               |
| Need to retest the whole class every time   | Only test the new class                     |
| Long if-else / switch chains keep growing   | Polymorphism replaces if-else               |
| Tight coupling to concrete types            | Code depends on an abstraction              |

**Key idea:** Every edit to old code is a chance to break something that already works. With OCP, new features are **new classes**, not edits.

---

## 3. How do you spot an OCP violation?
- Long **if-else / switch on a "type"** (`if type == "UPI" ... else if "CARD"`).
- Methods like `saveToSQL()`, `saveToMongo()`, `saveToFile()`, so every new option adds a method.
- To add a feature, you must **open an existing class and edit it**.

## 4. How do you apply OCP?
1. Find the part that **varies** (DB type, payment type, shape...).
2. Put it behind an **abstract class** with a pure virtual function.
3. Write **one subclass per variant**.
4. The client code uses the **base pointer** (`Persistence*`), so it never changes.
5. New variant? **Add a new subclass.** No old code is touched.

---

## 5. Example 1: Cart Storage (from the lecture code)

### ❌ Violating OCP
```
+--------------------------+
|   ShoppingCartStorage    |
+--------------------------+
| - cart : ShoppingCart*   |
+--------------------------+
| + saveToSQLDatabase()    |
| + saveToMongoDatabase()  |
| + saveToFile()           |
| + saveToRedis() ???      |  <- every new DB = edit this class
+--------------------------+
```

```cpp
class ShoppingCartStorage {
    ShoppingCart* cart;
public:
    ShoppingCartStorage(ShoppingCart* cart) { this->cart = cart; }

    void saveToSQLDatabase()   { cout << "Saving to SQL DB...\n"; }
    void saveToMongoDatabase() { cout << "Saving to Mongo DB...\n"; }
    void saveToFile()          { cout << "Saving to File...\n"; }
    // Need Redis? -> open this class and edit it again
};
```
SRP is followed (the class only saves), but **OCP is broken**: every new storage type means modifying this class.

### ✅ Following OCP
```
                        +----------------------------+
                        |  <<abstract>> Persistence  |
                        +----------------------------+
                        | + save(ShoppingCart*) = 0  |
                        +----------------------------+
                                       ^
                                       | is-a (inherits)
            +--------------------------+--------------------------+
            |                          |                          |
+-----------------------+  +-----------------------+  +-----------------------+
|     SQLPersistence    |  |    MongoPersistence   |  |    FilePersistence    |
+-----------------------+  +-----------------------+  +-----------------------+
| + save(ShoppingCart*) |  | + save(ShoppingCart*) |  | + save(ShoppingCart*) |
+-----------------------+  +-----------------------+  +-----------------------+
```

```cpp
class Persistence {                              // abstraction
public:
    virtual void save(ShoppingCart* cart) = 0;   // pure virtual
};

class SQLPersistence : public Persistence {
public:
    void save(ShoppingCart* cart) override { cout << "Saving to SQL DB...\n"; }
};

class MongoPersistence : public Persistence {
public:
    void save(ShoppingCart* cart) override { cout << "Saving to MongoDB...\n"; }
};

class FilePersistence : public Persistence {
public:
    void save(ShoppingCart* cart) override { cout << "Saving to a file...\n"; }
};

int main() {
    ShoppingCart* cart = new ShoppingCart();
    cart->addProduct(new Product("Laptop", 50000));

    Persistence* db = new SQLPersistence();      // base pointer
    db->save(cart);                              // runtime polymorphism

    db = new MongoPersistence();
    db->save(cart);
}
```
Need Redis? Just **add** `class RedisPersistence : public Persistence`. **Zero changes** to existing classes.

---

## 6. Example 2: Payment Processor

### ❌ Bad
```
+----------------------------+
|      PaymentProcessor      |
+----------------------------+
| + pay(type, amount)        |
+----------------------------+
| if type == "UPI"   ...     |
| else if "CARD"     ...     |
| else if "NETBANK"  ...     |
| else if ???  <- edit again |
+----------------------------+
```

```cpp
class PaymentProcessor {
public:
    void pay(string type, double amount) {
        if (type == "UPI")          cout << "Paid " << amount << " via UPI\n";
        else if (type == "CARD")    cout << "Paid " << amount << " via Card\n";
        else if (type == "NETBANK") cout << "Paid " << amount << " via NetBanking\n";
        // new method = edit this if-else
    }
};
```

### ✅ Good
```
                +---------------------------+
                |      PaymentProcessor     |
                +---------------------------+
                | - method : PaymentMethod* |
                +---------------------------+
                | + checkout(amount)        |
                +---------------------------+
                              | has-a
                              v
               +----------------------------+
               | <<abstract>> PaymentMethod |
               +----------------------------+
               | + pay(amount) = 0          |
               +----------------------------+
                              ^
                              | is-a
         +--------------------+--------------------+
         |                    |                    |
+-----------------+  +-----------------+  +-----------------+
|    UPIPayment   |  |   CardPayment   |  |    NetBanking   |
+-----------------+  +-----------------+  +-----------------+
| + pay(amount)   |  | + pay(amount)   |  | + pay(amount)   |
+-----------------+  +-----------------+  +-----------------+
```

```cpp
class PaymentMethod {
public:
    virtual void pay(double amount) = 0;
    virtual ~PaymentMethod() {}
};

class UPIPayment : public PaymentMethod {
public:
    void pay(double amount) override { cout << "Paid " << amount << " via UPI\n"; }
};

class CardPayment : public PaymentMethod {
public:
    void pay(double amount) override { cout << "Paid " << amount << " via Card\n"; }
};

class PaymentProcessor {
    PaymentMethod* method;                       // has-a
public:
    PaymentProcessor(PaymentMethod* m) : method(m) {}
    void checkout(double amount) { method->pay(amount); }
};

int main() {
    PaymentProcessor p(new UPIPayment());
    p.checkout(500);
}
```
`PaymentProcessor` is **closed**: it never changes. The system is **open**: add `WalletPayment` anytime.

---

## 7. Example 3: Area Calculator (quick one)

### ❌ Bad
```cpp
double area(Shape s) {
    if (s.type == "circle")    return 3.14 * s.r * s.r;
    else if (s.type == "rect") return s.w * s.h;
    // new shape = edit here
}
```

### ✅ Good
```
              +----------------------+
              |  <<abstract>> Shape  |
              +----------------------+
              | + area() = 0         |
              +----------------------+
                          ^
                          | is-a
        +-----------------+-----------------+
        |                 |                 |
+--------------+  +--------------+  +--------------+
|    Circle    |  |  Rectangle   |  |   Triangle   |
+--------------+  +--------------+  +--------------+
| - r          |  | - w, h       |  | - b, h       |
| + area()     |  | + area()     |  | + area()     |
+--------------+  +--------------+  +--------------+
```

```cpp
class Shape {
public:
    virtual double area() = 0;
    virtual ~Shape() {}
};

class Circle : public Shape {
    double r;
public:
    Circle(double r) : r(r) {}
    double area() override { return 3.14 * r * r; }
};

// total area -> this loop never changes, whatever shapes you add
// for (Shape* s : shapes) total += s->area();
```

---

## 8. OCP and SRP together
- **SRP** first splits the class: `ShoppingCartStorage` only saves.
- **OCP** then makes that piece extendable: `Persistence` + subclasses.
- In OCP you see **both** relationships:
  - **is-a** (inheritance): `SQLPersistence` is-a `Persistence`. This is how you extend.
  - **has-a** (composition): `PaymentProcessor` has-a `PaymentMethod*`. This is how the client stays unchanged.

---

## 9. Common interview questions

**Q1. What is OCP?**
Classes should be open for extension but closed for modification: add new behaviour by adding code, not by changing existing code.

**Q2. How do you achieve OCP in C++?**
An abstract class with **pure virtual functions**, plus subclasses, plus **runtime polymorphism** through a base class pointer.

**Q3. Biggest sign of an OCP violation?**
An if-else / switch on a type that grows every time a new type is added.

**Q4. Does OCP mean you can never modify code?**
No. Bug fixes and requirement changes still modify code. OCP is about **adding new variants** without touching what already works.

**Q5. Downside of OCP?**
Over-abstraction: creating interfaces "just in case" adds complexity. Apply it where change is **likely**.

**Q6. Why add a virtual destructor in the base class?**
So `delete basePtr;` also runs the derived class destructor. Without it, you get undefined behaviour and leaks.

**Q7. Real-world analogy?**
A phone charger port: new devices just plug in. You don't rebuild the wall socket for every new phone.

---

## 10. One-line revision
> **"Add new features by adding new classes, not by editing old ones."**

Related code in this folder: `OCP_violated.cpp`, `OCP_followed.cpp`.
Next in this lecture: **LSP** (Liskov Substitution Principle) in `../LSP/`.
