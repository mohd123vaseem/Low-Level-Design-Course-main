# LSP Property Rules: Notes

## 1. What are Property Rules?
Signature rules check a method's **shape** (args, return, exceptions).
**Property rules** check the object's **state (data) and how it may change**.

## 1.1 Concept Explanation.
- **Class Invariant:** puts rules on the object's **state/data**. *"Balance must never be negative."*
- **History Constraint:** puts rules on the object's **behaviour/abilities that change its state**. *"It must still be able to withdraw and deposit."*

History isn't about *every* behaviour (like `printBalance()`). It covers only the abilities that **modify the data**, meaning *how the state is allowed to evolve*. That's why both are **Property** Rules: both are about the object's data. One covers what the data can be; the other covers how the data can change.

> **Invariant puts rules on the object's STATE (what its data can be).
> History puts rules on the object's ABILITIES to change that state (how its data can change).
> A child must keep both.**

**Cricket analogy 🏏**
- **Invariant:** *"A team always has 11 players on the field."* That's a rule about the state at **any moment**.
- **History:** *"A batsman is allowed to run between the wickets."* That's a rule about **which actions are allowed**.
- A team fielding 12 players breaks the **invariant** (bad state).
- A team that says "our batsmen won't run, only boundaries" breaks the **history** (an allowed move was taken away).

**Memory trick:**
- **Invariant** is about **what the state can be** (e.g. `balance >= 0`).
- **History** is about **how the state can change** (e.g. "withdraw is allowed").

---

## 2. Why do we need them?
The client trusts the **parent's guarantees**:
- *"Balance is never negative"*, so the client never checks for negative balance.
- *"I can withdraw from any BankAccount"*, so the client calls `withdraw()` freely.

If a child silently breaks a guarantee, the client gets **wrong data or a crash**, even though the code compiles fine. The compiler **cannot** check these rules; they are **your design responsibility**.

---

## 3. Rule 1: Class Invariant Definition.
> **The invariant of the parent must stay true in the child. The child can maintain or strengthen it, never weaken it.**

**Invariant:** a rule about the object's data that must hold **before and after every public method call**.
Example: `BankAccount`'s invariant is **balance can never be negative**.

```
              +--------------------------+
              |       BankAccount        |
              +--------------------------+
              | # balance                |
              +--------------------------+
              | + withdraw(amt)          |
              +--------------------------+
              | INVARIANT: balance >= 0  |
              +--------------------------+
                            ^
                            | is-a
             +--------------+--------------+
             |                             |
+------------------------+    +------------------------+
| CheatAccount  (WRONG)  |    | MinBalanceAccount (OK) |
+------------------------+    +------------------------+
| + withdraw(amt)        |    | + withdraw(amt)        |
+------------------------+    +------------------------+
| balance can go < 0     |    | balance >= 1000        |
| invariant BROKEN       |    | invariant STRENGTHENED |
+------------------------+    +------------------------+
```

### ❌ Breaking the invariant
```cpp
// Invariant : Balance cannot be negative
class BankAccount {
protected:
    double balance;
public:
    BankAccount(double b) {
        if (b < 0) throw invalid_argument("Balance can't be negative");
        balance = b;
    }
    virtual void withdraw(double amount) {
        if (balance - amount < 0) throw runtime_error("Insufficient funds");
        balance -= amount;
        cout << "Amount withdrawn. Remaining balance is " << balance << endl;
    }
};

class CheatAccount : public BankAccount {
public:
    CheatAccount(double b) : BankAccount(b) {}

    void withdraw(double amount) override {
        balance -= amount;            // ❌ no check -> balance can go negative
        cout << "Amount withdrawn. Remaining balance is " << balance << endl;
    }
};

int main() {
    BankAccount* acc = new CheatAccount(100);
    acc->withdraw(500);               // balance = -400 💥 parent's promise broken
}
```

### ✅ Keeping or strengthening the invariant
```cpp
class MinBalanceAccount : public BankAccount {
public:
    MinBalanceAccount(double b) : BankAccount(b) {}

    void withdraw(double amount) override {
        if (balance - amount < 1000)                    // stricter rule: >= 1000
            throw runtime_error("Must keep minimum balance of 1000");
        balance -= amount;
    }
};
```
`balance >= 1000` **also guarantees** `balance >= 0`, so the parent's promise still holds ✅.

**Tip:** to protect an invariant, keep the data `private` and let children change it only through a checked parent method. A child can't break what it can't touch directly.

---

## 4. Rule 2: History Constraint
> **A child must not restrict state changes the parent allows (or allow changes the parent forbids).**

The parent's methods define the object's **allowed history**: *"balance can go down via withdraw()"*. A child must not take that ability away.

### ❌ Breaking the history constraint
```
+--------------------------+
|       BankAccount        |
+--------------------------+
| # balance                |
+--------------------------+
| + deposit(amt)           |
| + withdraw(amt)  allowed |
+--------------------------+
              ^
              | is-a
+--------------------------+
|   FixedDepositAccount    |
+--------------------------+
| + withdraw(amt)  THROWS  |
+--------------------------+
```

```cpp
class BankAccount {
protected:
    double balance;
public:
    BankAccount(double b) {
        if (b < 0) throw invalid_argument("Balance can't be negative");
        balance = b;
    }
    // History Constraint : withdraw should be allowed
    virtual void withdraw(double amount) {
        if (balance - amount < 0) throw runtime_error("Insufficient funds");
        balance -= amount;
        cout << "Amount withdrawn. Remaining balance is " << balance << endl;
    }
};

class FixedDepositAccount : public BankAccount {
public:
    FixedDepositAccount(double b) : BankAccount(b) {}

    void withdraw(double amount) override {
        throw runtime_error("Withdraw not allowed in Fixed Deposit");   // ❌ parent allowed it
    }
};
```
Client code that does `acc->withdraw(...)` on any `BankAccount*` **breaks** when given a `FixedDepositAccount`.

### ✅ Fix: don't inherit an ability you can't honour
Same fix as Lecture 05's LSP example: **split by capability**.

```
                 +-----------------------------------+
                 |  <<abstract>> DepositOnlyAccount  |
                 +-----------------------------------+
                 | + deposit(amt) = 0                |
                 +-----------------------------------+
                                   ^
                                   | is-a
                  +----------------+-----------------+
                  |                                  |
+-----------------------------------+     +---------------------+
|  <<abstract>> WithdrawableAccount |     | FixedDepositAccount |
+-----------------------------------+     +---------------------+
| + withdraw(amt) = 0               |     | + deposit(amt)      |
+-----------------------------------+     +---------------------+
                  ^
                  | is-a
        +------------------+
        |  SavingsAccount  |
        +------------------+
        | + deposit(amt)   |
        | + withdraw(amt)  |
        +------------------+
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

class FixedDepositAccount : public DepositOnlyAccount {     // never promised withdraw ✅
    double balance = 0;
public:
    void deposit(double amount) override { balance += amount; }
};
```
Now nobody can even call `withdraw()` on a fixed deposit, so there is no broken promise.

**The other direction is also a violation:** if the parent is **immutable** (e.g. `ImmutablePoint` with no setters), a child that adds `setX()` allows a state change the parent's clients never expect.

---

## 5. Invariant vs History: quick comparison

### Simplified: Photo vs Video
- **Invariant = PHOTO 📷.** Freeze the object at any moment and check: is the STATE valid? (`balance >= 0`)
- **History = VIDEO 🎥.** Watch it over time and check: can it still make every MOVE the parent allowed? (deposit, withdraw)

Each lecture example breaks only one of them:
- `CheatAccount`: withdraw still works ✅ (history OK), but balance becomes -400 ❌ (invariant broken).
- `FixedDepositAccount`: balance is never negative ✅ (invariant OK), but withdraw is gone ❌ (history broken).

> **Invariant asks "Is the STATE valid?" History asks "Are all the MOVES still allowed?"**

```
------------------------------------------------------------------------------------------------------
|                      | Class Invariant                       | History Constraint                  |
------------------------------------------------------------------------------------------------------
| Talks about          | What state is valid                   | How state may change over time      |
------------------------------------------------------------------------------------------------------
| Example              | balance >= 0 always                   | withdraw() is allowed               |
------------------------------------------------------------------------------------------------------
| Violation            | CheatAccount lets balance go negative | FixedDepositAccount blocks withdraw |
------------------------------------------------------------------------------------------------------
| Child may            | Keep or strengthen                    | Keep the same allowed changes       |
------------------------------------------------------------------------------------------------------
| Checked by compiler? | ❌ No                                 | ❌ No                               |
------------------------------------------------------------------------------------------------------
```

---

## 6. Common interview questions

**Q1. What is a class invariant?**
A condition about an object's state that is always true before and after any public method call, e.g. `balance >= 0`.

**Q2. Can a child class change the parent's invariant?**
It can **strengthen** it (`balance >= 1000`), never **weaken** it (allowing negative balance).

**Q3. What is the history constraint?**
A child must not restrict state changes the parent allows (or add changes the parent forbids). The object must evolve the way parent clients expect.

**Q4. Example of a history constraint violation?**
`FixedDepositAccount` overriding `withdraw()` to throw, or a mutable child of an immutable parent.

**Q5. How do you protect invariants in C++?**
Keep data `private`, validate in constructors and setters, and let children change state only through parent methods that check the rules.

**Q6. How do you fix a history violation?**
Don't inherit a capability you can't support. Split the base class (`DepositOnlyAccount` / `WithdrawableAccount`) or use composition.

---

## 7. One-line revision
> **"A child must keep the parent's promises about its data: what the state can be (invariant) and how it can change (history)."**

Related code in this folder: `ClassInvariants.cpp`, `HistoryConstraint.cpp`.
Previous: **Signature Rules** (`../SingatureRules/`). Next: **Method Rules** (`../MethodRules/`).
