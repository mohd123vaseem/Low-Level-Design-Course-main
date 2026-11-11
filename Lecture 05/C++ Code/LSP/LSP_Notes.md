# Liskov Substitution Principle (LSP): Notes

## 1. What is LSP?
> **"Objects of a subclass should be replaceable for objects of the parent class without breaking the program."** (Barbara Liskov, the L in SOLID)

- If `B` is-a `A`, then **anywhere you use `A*`, you can pass a `B*`** and everything still works.
- A child must **keep the promises** of its parent. It can do *more*, never *less*.
- Test: "Is-a" is not enough. Ask **"Does the child BEHAVE like the parent?"**

---

## 2. Why do we need LSP?

```
----------------------------------------------------------------------------------------
| Problem without LSP                        | Benefit with LSP                        |
----------------------------------------------------------------------------------------
| Child crashes / throws where parent worked | Any child can replace the parent safely |
----------------------------------------------------------------------------------------
| Client needs typeid / dynamic_cast checks  | Client code stays simple and generic    |
----------------------------------------------------------------------------------------
| Adding a new child breaks old client code  | New children plug in (helps OCP)        |
----------------------------------------------------------------------------------------
| Surprising behaviour, hidden bugs          | Predictable, trustworthy hierarchy      |
----------------------------------------------------------------------------------------
```

**Key idea:** Polymorphism only works if every child is a **true** substitute. One "bad child" forces `if (type == ...)` checks everywhere, which also breaks OCP.

---

## 3. How do you spot an LSP violation?
- A child method **throws** `"not supported"` / `"not allowed"` for something the parent offers.
- A child overrides a method with an **empty body** or does nothing.
- The client checks the type: `typeid(*acc) == typeid(X)` or `dynamic_cast`.
- A child **changes the meaning** of a method (Square's `setWidth` also changes height).

## 4. How do you apply LSP?
1. Ask: can **every** child honour **every** method of the parent?
2. If not, the parent is **too big**. Split it into smaller abstractions by capability (`DepositOnlyAccount`, `WithdrawableAccount`).
3. Let each child inherit **only the capabilities it really has**.
4. Let the client depend on the **exact abstraction it needs**.

---

## 5. Example 1: Bank Accounts (from the lecture code)

### ❌ Violating LSP
```
                 +------------------------+
                 |  <<abstract>> Account  |
                 +------------------------+
                 | + deposit(amt) = 0     |
                 | + withdraw(amt) = 0    |
                 +------------------------+
                              ^
                              | is-a
         +--------------------+----------------------+
         |                    |                      |
+-----------------+  +-----------------+  +---------------------+
|  SavingAccount  |  |  CurrentAccount |  |   FixedTermAccount  |
+-----------------+  +-----------------+  +---------------------+
| + deposit()     |  | + deposit()     |  | + deposit()         |
| + withdraw()    |  | + withdraw()    |  | + withdraw() THROWS |
+-----------------+  +-----------------+  +---------------------+
```

```cpp
class Account {
public:
    virtual void deposit(double amount) = 0;
    virtual void withdraw(double amount) = 0;
};

class FixedTermAccount : public Account {
    double balance = 0;
public:
    void deposit(double amount) { balance += amount; }
    void withdraw(double amount) {
        throw logic_error("Withdrawal not allowed in Fixed Term Account!");   // ❌
    }
};

class BankClient {
    vector<Account*> accounts;
public:
    BankClient(vector<Account*> accounts) { this->accounts = accounts; }
    void processTransactions() {
        for (Account* acc : accounts) {
            acc->deposit(1000);
            acc->withdraw(500);     // 💥 crashes for FixedTermAccount
        }
    }
};
```
`FixedTermAccount` **is-a** `Account` on paper, but it **cannot be substituted** for it.

### ⚠️ "Followed wrongly" (the quick hack)
```cpp
for (Account* acc : accounts) {
    acc->deposit(1000);
    if (typeid(*acc) == typeid(FixedTermAccount))     // type check ❌
        cout << "Skipping withdrawal for Fixed Term Account.\n";
    else
        acc->withdraw(500);
}
```
It no longer crashes, but:
- The client must **know about concrete child classes**.
- Each new "special" account means **editing the client**, which **breaks OCP**.
- The bad hierarchy is still there. We only **hid** the problem.

### ✅ Following LSP: split the abstraction
```
                  +-----------------------------------+
                  |  <<abstract>> DepositOnlyAccount  |
                  +-----------------------------------+
                  | + deposit(amt) = 0                |
                  +-----------------------------------+
                                    ^
                                    | is-a
                   +----------------+----------------+
                   |                                 |
 +-----------------------------------+     +------------------+
 |  <<abstract>> WithdrawableAccount |     | FixedTermAccount |
 +-----------------------------------+     +------------------+
 | + withdraw(amt) = 0               |     | + deposit()      |
 +-----------------------------------+     +------------------+
                   ^
                   | is-a
         +---------+---------+
         |                   |
+----------------+  +----------------+
| SavingAccount  |  | CurrentAccount |
+----------------+  +----------------+
| + deposit()    |  | + deposit()    |
| + withdraw()   |  | + withdraw()   |
+----------------+  +----------------+
```

```cpp
class DepositOnlyAccount {
public:
    virtual void deposit(double amount) = 0;
};

class WithdrawableAccount : public DepositOnlyAccount {
public:
    virtual void withdraw(double amount) = 0;
};

class SavingAccount : public WithdrawableAccount {
    double balance = 0;
public:
    void deposit(double amount) { balance += amount; }
    void withdraw(double amount) {
        if (balance >= amount) balance -= amount;
        else cout << "Insufficient funds!\n";
    }
};

class FixedTermAccount : public DepositOnlyAccount {    // only what it can do
    double balance = 0;
public:
    void deposit(double amount) { balance += amount; }
};

class BankClient {
    vector<WithdrawableAccount*> withdrawableAccounts;
    vector<DepositOnlyAccount*>  depositOnlyAccounts;
public:
    BankClient(vector<WithdrawableAccount*> w, vector<DepositOnlyAccount*> d)
        : withdrawableAccounts(w), depositOnlyAccounts(d) {}

    void processTransactions() {
        for (WithdrawableAccount* acc : withdrawableAccounts) {
            acc->deposit(1000);
            acc->withdraw(500);       // safe for EVERY item ✅
        }
        for (DepositOnlyAccount* acc : depositOnlyAccounts)
            acc->deposit(5000);       // safe for EVERY item ✅
    }
};
```
Now **every** object in each list fully supports what is called on it. No throws, no type checks.

---

## 6. Example 2: Rectangle and Square (classic interview one)

### ❌ Bad
```
  +----------------------+
  |      Rectangle       |
  +----------------------+
  | # width, height      |
  +----------------------+
  | + setWidth(w)        |
  | + setHeight(h)       |
  | + area()             |
  +----------------------+
              ^
              | is-a
+--------------------------+
|          Square          |
+--------------------------+
| + setWidth(w)  -> w=h=w  |
| + setHeight(h) -> w=h=h  |
+--------------------------+
```

```cpp
class Rectangle {
protected:
    int width, height;
public:
    virtual void setWidth(int w)  { width = w; }
    virtual void setHeight(int h) { height = h; }
    int area() { return width * height; }
};

class Square : public Rectangle {
public:
    void setWidth(int w)  override { width = height = w; }   // changes meaning ❌
    void setHeight(int h) override { width = height = h; }
};

void test(Rectangle* r) {
    r->setWidth(5);
    r->setHeight(4);
    cout << r->area();   // expect 20 -> Square gives 16 💥
}
```
Mathematically "a square is a rectangle", but **behaviourally** it is not. It breaks the parent's promise that "width and height are independent".

### ✅ Good
```
          +----------------------+
          |  <<abstract>> Shape  |
          +----------------------+
          | + area() = 0         |
          +----------------------+
                      ^
                      | is-a
          +-----------+-----------+
          |                       |
+------------------+    +------------------+
|    Rectangle     |    |      Square      |
+------------------+    +------------------+
| - width, height  |    | - side           |
| + area()         |    | + area()         |
+------------------+    +------------------+
```

```cpp
class Shape {
public:
    virtual int area() = 0;
    virtual ~Shape() {}
};

class Rectangle : public Shape {
    int width, height;
public:
    Rectangle(int w, int h) : width(w), height(h) {}
    int area() override { return width * height; }
};

class Square : public Shape {
    int side;
public:
    Square(int s) : side(s) {}
    int area() override { return side * side; }
};
```

---

## 7. Example 3: Birds (quick one)

### ❌ Bad
```
           +--------------+
           |     Bird     |
           +--------------+
           | + eat()      |
           | + fly()      |
           +--------------+
                   ^
                   | is-a
        +----------+----------+
        |                     |
+--------------+    +-------------------+
|   Sparrow    |    |      Penguin      |
+--------------+    +-------------------+
| + fly()      |    | + fly()  THROWS   |
+--------------+    +-------------------+
```

```cpp
class Bird    { public: virtual void fly() { cout << "Flying\n"; } };
class Penguin : public Bird {
public:
    void fly() override { throw logic_error("Penguins can't fly!"); }   // ❌
};
```

### ✅ Good
```
                     +--------------+
                     |     Bird     |
                     +--------------+
                     | + eat()      |
                     +--------------+
                             ^
                             | is-a
               +-------------+--------------+
               |                            |
       +--------------+              +-------------+
       |  FlyingBird  |              |   Penguin   |
       +--------------+              +-------------+
       | + fly()      |              | + swim()    |
       +--------------+              +-------------+
               ^
               | is-a
       +-------+--------+
       |                |
+-------------+  +-------------+
|   Sparrow   |  |    Eagle    |
+-------------+  +-------------+
| + fly()     |  | + fly()     |
+-------------+  +-------------+
```

```cpp
class Bird       { public: virtual void eat() { cout << "Eating\n"; } };
class FlyingBird : public Bird { public: virtual void fly() = 0; };

class Sparrow : public FlyingBird { public: void fly() override { cout << "Sparrow flies\n"; } };
class Penguin : public Bird       { public: void swim() { cout << "Penguin swims\n"; } };

// void makeItFly(FlyingBird* b) { b->fly(); }   // Penguin can't even be passed here ✅
```
Same fix as the bank example: **split by capability**.

---

## 8. LSP with SRP and OCP
- **SRP:** one class, one job.
- **OCP:** extend by adding subclasses.
- **LSP:** makes sure those subclasses are **safe to plug in**. Without LSP, OCP fails, because the client starts adding `if (type == ...)` again.
- Bad LSP usually means the **parent interface is too fat**. Splitting it leads straight into **ISP** (Interface Segregation), which is next.

## 9. LSP rules (short preview; detailed in Lecture 06 `LSP-Rules`)
A child must:
- **Not throw new exceptions** that the parent doesn't throw.
- **Not strengthen preconditions:** accept at least what the parent accepts.
- **Not weaken postconditions:** give at least what the parent promises.
- **Keep the invariants:** for example, balance never goes negative, if the parent guarantees that.

---

## 10. Common interview questions

**Q1. What is LSP?**
A subclass object must be usable wherever a parent object is expected, without breaking correctness.

**Q2. Is "is-a" enough for inheritance?**
No. It must be **behaviourally** is-a. Square is-a Rectangle in maths, but not in code.

**Q3. Common signs of an LSP violation?**
A child throws "not supported", has an empty override, or the client uses `typeid` / `dynamic_cast` checks.

**Q4. Why is the `typeid` fix wrong?**
It hides the bad hierarchy, couples the client to concrete classes and breaks OCP.

**Q5. How do you fix an LSP violation?**
Split the base class into smaller capability-based abstractions, or use composition instead of inheritance.

**Q6. How are LSP and OCP related?**
OCP depends on adding subclasses. LSP guarantees those subclasses work without changing client code.

**Q7. Real-world analogy?**
A substitute teacher must actually be able to teach the class. If they can only take attendance, they are not a real substitute.

---

## 11. One-line revision
> **"A child must be usable everywhere its parent is used, with no surprises."**

Related code in this folder: `LSP_Violated.cpp`, `LSP_followed_wrongly.cpp`, `LSP_followed.cpp`.
Next: **Lecture 06**, covering LSP rules, ISP and DIP.
