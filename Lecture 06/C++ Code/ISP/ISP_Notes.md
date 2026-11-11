# Interface Segregation Principle (ISP): Notes

## 1. Definition
> **"Clients should not be forced to depend on methods they do not use."** (Robert C. Martin, the I in SOLID)

- Prefer **many small, focused interfaces** over **one big "fat" interface**.
- A class should implement **only the methods that make sense for it**.
- In C++ an "interface" is an **abstract class with only pure virtual functions** (`= 0`). A class can implement several of them using **multiple inheritance**.

---

## 2. What problem it solves (why we study it)
When an interface is too big, every class that implements it must write **every** method, even the ones that don't apply to it. It ends up with:
- **Dummy methods** that do nothing, or that `throw "not supported"`.
- **Crashes** when a client calls one of those methods through the base pointer, which is also an **LSP violation**.
- **Needless recompiles and changes**: adding a method to the fat interface forces **every** class to change, even classes that don't care about it.

```
-------------------------------------------------------------------------------------------------------------
| Problem without ISP                             | Benefit with ISP                                        |
-------------------------------------------------------------------------------------------------------------
| Classes forced to write methods they don't need | Classes implement only what they use                    |
-------------------------------------------------------------------------------------------------------------
| Dummy / throwing methods (breaks LSP)           | No fake methods, safe substitution                      |
-------------------------------------------------------------------------------------------------------------
| One change to the interface touches every class | Changes stay inside the small interface that needs them |
-------------------------------------------------------------------------------------------------------------
| Hard to read: what can this class REALLY do?    | Interface names show exact capabilities                 |
-------------------------------------------------------------------------------------------------------------
| Tight coupling to things a client never uses    | Clients depend only on what they call                   |
-------------------------------------------------------------------------------------------------------------
```

**Key idea:** An interface should describe **one capability**. If some implementers have to say "not supported", the interface is too fat. **Split it.**

**Restaurant analogy 🍽️:** a vegetarian customer shouldn't be handed a menu where they must order a chicken dish with every meal. Give a **veg menu** and a **non-veg menu**; each customer picks the one that fits.

---

## 3. Examples

### Example 1: 2D and 3D Shapes (from the lecture code)

#### ❌ Bad: one fat Shape interface
```
                        +----------------------+
                        |  <<abstract>> Shape  |
                        +----------------------+
                        | + area() = 0         |
                        | + volume() = 0       |
                        +----------------------+
                                    ^
                                    | is-a
           +------------------------+------------------------+
           |                        |                        |
+---------------------+  +---------------------+  +---------------------+
|        Square       |  |      Rectangle      |  |         Cube        |
+---------------------+  +---------------------+  +---------------------+
| + area()            |  | + area()            |  | + area()            |
| + volume()  THROWS  |  | + volume()  THROWS  |  | + volume()          |
+---------------------+  +---------------------+  +---------------------+
```

```cpp
// Single interface for all shapes (Violates ISP)
class Shape {
public:
    virtual double area() = 0;
    virtual double volume() = 0;      // 2D shapes don't have volume!
};

class Square : public Shape {
    double side;
public:
    Square(double s) : side(s) {}
    double area() override { return side * side; }
    double volume() override {
        throw logic_error("Volume not applicable for Square");   // ❌ forced, useless method
    }
};

class Cube : public Shape {
    double side;
public:
    Cube(double s) : side(s) {}
    double area() override { return 6 * side * side; }
    double volume() override { return side * side * side; }
};

int main() {
    Shape* square = new Square(5);
    cout << square->volume();         // 💥 throws at runtime
}
```
`Square` and `Rectangle` are **forced** to write `volume()` just because `Cube` needs it.

#### ✅ Good: split into 2D and 3D interfaces
```
+-----------------------------------+    +-------------------------------------+
|  <<abstract>> TwoDimensionalShape |    |  <<abstract>> ThreeDimensionalShape |
+-----------------------------------+    +-------------------------------------+
| + area() = 0                      |    | + area() = 0                        |
+-----------------------------------+    | + volume() = 0                      |
                  ^                      +-------------------------------------+
                  | is-a                                    ^
         +--------+--------+                                | is-a
         |                 |                        +--------------+
 +--------------+  +--------------+                 |     Cube     |
 |    Square    |  |  Rectangle   |                 +--------------+
 +--------------+  +--------------+                 | + area()     |
 | + area()     |  | + area()     |                 | + volume()   |
 +--------------+  +--------------+                 +--------------+
```

```cpp
// Separate interface for 2D shapes
class TwoDimensionalShape {
public:
    virtual double area() = 0;
};

// Separate interface for 3D shapes
class ThreeDimensionalShape {
public:
    virtual double area() = 0;
    virtual double volume() = 0;
};

class Square : public TwoDimensionalShape {        // only 2D methods ✅
    double side;
public:
    Square(double s) : side(s) {}
    double area() override { return side * side; }
};

class Cube : public ThreeDimensionalShape {        // 3D methods ✅
    double side;
public:
    Cube(double s) : side(s) {}
    double area() override { return 6 * side * side; }
    double volume() override { return side * side * side; }
};

int main() {
    TwoDimensionalShape* square = new Square(5);
    ThreeDimensionalShape* cube = new Cube(3);
    cout << square->area() << " " << cube->volume();
    // square->volume();   // doesn't even compile -> the mistake is caught early ✅
}
```
Now `square->volume()` is a **compile error** instead of a **runtime crash**.

---

### Example 2: Printer / Scanner / Fax (classic interview one)

#### ❌ Bad: one fat Machine interface
```
            +----------------------+
            | <<abstract>> Machine |
            +----------------------+
            | + print() = 0        |
            | + scan() = 0         |
            | + fax() = 0          |
            +----------------------+
                        ^
                        | is-a
           +------------+------------+
           |                         |
+--------------------+    +--------------------+
|   SimplePrinter    |    |  AllInOnePrinter   |
+--------------------+    +--------------------+
| + print()          |    | + print()          |
| + scan()  THROWS   |    | + scan()           |
| + fax()   THROWS   |    | + fax()            |
+--------------------+    +--------------------+
```

```cpp
class Machine {
public:
    virtual void print() = 0;
    virtual void scan()  = 0;
    virtual void fax()   = 0;
};

class SimplePrinter : public Machine {
public:
    void print() override { cout << "Printing\n"; }
    void scan()  override { throw logic_error("Can't scan"); }   // ❌
    void fax()   override { throw logic_error("Can't fax"); }    // ❌
};
```

#### ✅ Good: one small interface per capability
```
+----------------------+    +----------------------+    +----------------------+
| <<abstract>> Printer |    | <<abstract>> Scanner |    |   <<abstract>> Fax   |
+----------------------+    +----------------------+    +----------------------+
| + print() = 0        |    | + scan() = 0         |    | + fax() = 0          |
+----------------------+    +----------------------+    +----------------------+
            ^                           ^                           ^
            |                           |                           |
            +---------------------------+---------------------------+
                                        | is-a (implements all 3)
                             +--------------------+
                             |  AllInOnePrinter   |
                             +--------------------+
                             | + print()          |
                             | + scan()           |
                             | + fax()            |
                             +--------------------+
```

```
+----------------------+
| <<abstract>> Printer |
+----------------------+
| + print() = 0        |
+----------------------+
            ^
            | is-a (only what it needs)
 +--------------------+
 |   SimplePrinter    |
 +--------------------+
 | + print()          |
 +--------------------+
```

```cpp
class Printer { public: virtual void print() = 0; virtual ~Printer() {} };
class Scanner { public: virtual void scan()  = 0; virtual ~Scanner() {} };
class Fax     { public: virtual void fax()   = 0; virtual ~Fax()     {} };

class SimplePrinter : public Printer {                            // only what it can do ✅
public:
    void print() override { cout << "Printing\n"; }
};

class AllInOnePrinter : public Printer, public Scanner, public Fax {   // multiple inheritance ✅
public:
    void print() override { cout << "Printing\n"; }
    void scan()  override { cout << "Scanning\n"; }
    void fax()   override { cout << "Faxing\n"; }
};

void printReport(Printer* p) { p->print(); }   // client depends ONLY on print()
```
`printReport()` works with **both** printers and doesn't care about scan or fax.

---

## 4. How to spot a violation
- A class implements a method by **throwing** `"not supported"` / `"not applicable"`.
- **Empty method bodies** `{ }` that exist only to satisfy the interface.
- The interface has methods for **different kinds of users** (print + scan + fax, area + volume).
- Adding one method to an interface forces you to **edit many unrelated classes**.
- Interface names like `Machine`, `Manager`, `IEverything` that describe *a thing*, not *a capability*.

## 5. How to apply it
1. List the methods of the fat interface.
2. **Group them by capability / by which clients use them** (2D: `area`; 3D: `area + volume`).
3. Make **one small abstract class per group**.
4. Each class **inherits only the interfaces it can fully support** (use multiple inheritance to combine them).
5. Clients take a pointer to the **smallest interface they need** (`Printer*`, not `Machine*`).

---

## 6. Links to other principles
- **SRP for interfaces:** SRP says one reason to change *per class*; ISP says one capability *per interface*.
- **LSP:** a fat interface forces classes to `throw` for methods they can't support, which is exactly an LSP violation. Lecture 05's `DepositOnlyAccount` / `WithdrawableAccount` split was **ISP in action**.
- **OCP:** small interfaces are easy to extend. Add a new capability as a new interface, without touching existing ones.

```
----------------------------------------------------------------------------------------------------
|         | LSP                                    | ISP                                           |
----------------------------------------------------------------------------------------------------
| Focus   | Child must BEHAVE like the parent      | Interface must not be TOO BIG                 |
----------------------------------------------------------------------------------------------------
| Symptom | Child throws / changes meaning         | Class forced to write methods it doesn't need |
----------------------------------------------------------------------------------------------------
| Fix     | Correct hierarchy, split by capability | Split fat interface into small ones           |
----------------------------------------------------------------------------------------------------
```

---

## 7. Important interview questions

**Q1. What is ISP?**
Clients shouldn't be forced to depend on methods they don't use. Use many small interfaces instead of one fat one.

**Q2. What is a "fat" interface?**
An interface with methods for several different capabilities, so most implementers only need part of it.

**Q3. How do you implement ISP in C++ when there is no `interface` keyword?**
Use abstract classes with only pure virtual functions, and let a class inherit several of them (multiple inheritance).

**Q4. How are ISP and LSP related?**
Fat interfaces force classes to throw or fake methods, which breaks LSP. Splitting the interface (ISP) usually fixes the LSP violation.

**Q5. ISP vs SRP?**
SRP is about a class having one reason to change. ISP is about an interface exposing one focused capability to its clients.

**Q6. Can ISP be overdone?**
Yes. One method per interface for everything leads to too many tiny interfaces. Split by **real client needs**, not blindly.

**Q7. Real-world example?**
A printer, scanner and fax: a basic printer implements only `Printer`, an all-in-one implements `Printer`, `Scanner` and `Fax`.

---

## 8. One-line revision
> **"Many small, focused interfaces are better than one fat interface. Never force a class to implement what it can't do."**

Related code in this folder: `ISP_violated.cpp`, `ISP_followed.cpp`.
Previous: **LSP Rules** (`../LSP-Rules/`). Next: **DIP** (`../DIP/`).
