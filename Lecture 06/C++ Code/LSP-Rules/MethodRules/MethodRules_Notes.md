# LSP Method Rules: Notes

## 1. What are Method Rules?
Signature rules check a method's **shape**. Property rules check the object's **data**.
**Method rules** check a method's **contract**: what it **needs before** it runs and what it **promises after** it runs.

## 1.1 Clear Definitions

**Precondition**
> A condition that **must be true BEFORE** a method is called. It is the **caller's duty** to satisfy it.
> Example: `setPassword()` needs *password length >= 8*.
> **A child can WEAKEN a precondition (demand less), but can never STRENGTHEN it (demand more).**

**Postcondition**
> A condition that the method **guarantees will be true AFTER** it finishes. It is the **method's promise** to the caller.
> Example: after `brake()`, *speed has decreased*.
> **A child can STRENGTHEN a postcondition (promise more), but can never WEAKEN it (promise less).**


```
------------------------------------------------------------------------------------------------------------------------
| Rule                              | Child may                     | Child must NOT                                   |
------------------------------------------------------------------------------------------------------------------------
| 1. Precondition (BEFORE the call) | Weaken it: accept MORE inputs | Strengthen it: reject inputs the parent accepted |
------------------------------------------------------------------------------------------------------------------------
| 2. Postcondition (AFTER the call) | Strengthen it: guarantee MORE | Weaken it: skip something the parent guaranteed  |
------------------------------------------------------------------------------------------------------------------------
```

**Memory trick:** **"Demand LESS, promise MORE."**

**Shop analogy 🛒**
- **Precondition:** the shop says *"Pay at least Rs 100 to order."* A branch that says *"Pay at least Rs 50"* is fine (demands less). A branch that says *"Pay at least Rs 500"* turns away customers who were promised service ❌.
- **Postcondition:** the shop promises *"Delivery within 30 minutes."* A branch that delivers in 20 minutes is fine (promises more). A branch that takes 2 hours breaks the promise ❌.

---

## 2. Why do we need them?
The client is written against the **parent's contract**:
- It prepares inputs that satisfy the **parent's precondition** (e.g. an 8-character password). If the child demands more (10 characters), those valid calls suddenly **fail**.
- It relies on the **parent's postcondition** (e.g. the car slows down after `brake()`). If the child delivers less, the client's logic **silently breaks**.

Like property rules, the **compiler cannot check these**; they are your design responsibility.

---

## 3. Rule 1: Precondition Rule
> **Preconditions can be weakened in the child, never strengthened.**

```
                  +----------------------+
                  |         User         |
                  +----------------------+
                  | + setPassword(pw)    |
                  +----------------------+
                  | PRE: length >= 8     |
                  +----------------------+
                              ^
                              | is-a
              +---------------+----------------+
              |                                |
+---------------------------+    +---------------------------+
|      AdminUser  (OK)      |    |    StrictUser  (WRONG)    |
+---------------------------+    +---------------------------+
| + setPassword(pw)         |    | + setPassword(pw)         |
+---------------------------+    +---------------------------+
| PRE: length >= 6          |    | PRE: length >= 10         |
| WEAKER -> accepts more    |    | STRONGER -> rejects more  |
+---------------------------+    +---------------------------+
```

### ✅ Weakening the precondition (from the lecture code)
```cpp
class User {
public:
    // Precondition: Password must be at least 8 characters long
    virtual void setPassword(string password) {
        if (password.length() < 8)
            throw invalid_argument("Password must be at least 8 characters long!");
        cout << "Password set successfully" << endl;
    }
};

class AdminUser : public User {
public:
    // Precondition: Password must be at least 6 characters (WEAKER) ✅
    void setPassword(string password) override {
        if (password.length() < 6)
            throw invalid_argument("Password must be at least 6 characters long!");
        cout << "Password set successfully" << endl;
    }
};

int main() {
    User* user = new AdminUser();
    user->setPassword("Admin1");     // works: AdminUser allows shorter passwords
}
```
Every password valid for `User` (>= 8) is **also** valid for `AdminUser` (>= 6), so the client never breaks ✅.

### ❌ Strengthening the precondition
```cpp
class StrictUser : public User {
public:
    // Precondition: at least 10 characters (STRONGER) ❌
    void setPassword(string password) override {
        if (password.length() < 10)
            throw invalid_argument("Password must be at least 10 characters long!");
        cout << "Password set successfully" << endl;
    }
};

User* user = new StrictUser();
user->setPassword("Secret12");   // 8 chars: valid for User, but THROWS here 💥
```
The client followed the parent's rule (8 chars) and still crashed.

---

## 4. Rule 2: Postcondition Rule
> **Postconditions can be strengthened in the child, never weakened.**

```
               +------------------------+
               |          Car           |
               +------------------------+
               | # speed                |
               +------------------------+
               | + brake()              |
               +------------------------+
               | POST: speed decreases  |
               +------------------------+
                            ^
                            | is-a
             +--------------+---------------+
             |                              |
+-------------------------+    +-------------------------+
|     HybridCar  (OK)     |    |    BrokenCar  (WRONG)   |
+-------------------------+    +-------------------------+
| # charge                |    | + brake()               |
+-------------------------+    +-------------------------+
| + brake()               |    | POST: speed unchanged   |
+-------------------------+    | WEAKER -> gives less    |
| POST: speed decreases   |    +-------------------------+
|   AND charge increases  |
| STRONGER -> gives more  |
+-------------------------+
```

### ✅ Strengthening the postcondition (from the lecture code)
```cpp
class Car {
protected:
    int speed;
public:
    Car() { speed = 0; }

    void accelerate() {
        cout << "Accelerating" << endl;
        speed += 20;
    }

    // PostCondition : Speed must reduce after brake
    virtual void brake() {
        cout << "Applying brakes" << endl;
        speed -= 20;
    }
};

class HybridCar : public Car {
    int charge;
public:
    HybridCar() : Car() { charge = 0; }

    // PostCondition : Speed must reduce after brake
    // PostCondition : Charge must increase  (EXTRA promise) ✅
    void brake() override {
        cout << "Applying brakes" << endl;
        speed -= 20;
        charge += 10;
    }
};

int main() {
    Car* hybridCar = new HybridCar();
    hybridCar->brake();     // speed reduces AND charge increases
}
```
The client still gets what `Car` promised (speed goes down), **plus** a bonus. It feels no difference ✅.

### ❌ Weakening the postcondition
```cpp
class BrokenCar : public Car {
public:
    void brake() override {
        cout << "Applying brakes" << endl;
        // speed not reduced ❌ parent's promise skipped
    }
};

Car* car = new BrokenCar();
car->accelerate();
car->brake();        // client expects the car to slow down; it doesn't 💥
```

---

## 5. Pre vs Post: quick comparison

```
-----------------------------------------------------------------------------------------
|                      | Precondition                   | Postcondition                 |
-----------------------------------------------------------------------------------------
| When                 | BEFORE the method runs         | AFTER the method runs         |
-----------------------------------------------------------------------------------------
| Whose duty           | Caller's (provide valid input) | Method's (deliver the result) |
-----------------------------------------------------------------------------------------
| Lecture example      | password length >= 8           | speed decreases after brake() |
-----------------------------------------------------------------------------------------
| Child may            | Weaken (accept more)           | Strengthen (guarantee more)   |
-----------------------------------------------------------------------------------------
| Violation            | StrictUser demands 10 chars    | BrokenCar doesn't slow down   |
-----------------------------------------------------------------------------------------
| Checked by compiler? | ❌ No                          | ❌ No                         |
-----------------------------------------------------------------------------------------
```

---

## 6. All LSP rules at a glance (Signature + Property + Method)

```
--------------------------------------------------------------------
| Group     | Rule               | Child may                       |
--------------------------------------------------------------------
| Signature | Method arguments   | Same (or wider) params          |
--------------------------------------------------------------------
| Signature | Return type        | Same or narrower (covariant)    |
--------------------------------------------------------------------
| Signature | Exceptions         | Same, fewer or narrower         |
--------------------------------------------------------------------
| Property  | Class invariant    | Keep or strengthen              |
--------------------------------------------------------------------
| Property  | History constraint | Keep every allowed state change |
--------------------------------------------------------------------
| Method    | Precondition       | Keep or weaken                  |
--------------------------------------------------------------------
| Method    | Postcondition      | Keep or strengthen              |
--------------------------------------------------------------------
```

**Pattern:** the child must **accept at least as much** (args, preconditions) and **deliver at least as much** (return, postconditions, invariants, history). Then the client can never tell the difference.

---

## 7. Common interview questions

**Q1. What is a precondition?**
A condition that must be true before a method is called, for example a valid input range. Satisfying it is the caller's job.

**Q2. What is a postcondition?**
A condition the method guarantees after it finishes, for example "speed decreased". Delivering it is the method's job.

**Q3. Why can't a child strengthen a precondition?**
Clients written for the parent pass inputs the parent accepts. If the child rejects some of them, valid calls fail.

**Q4. Why can't a child weaken a postcondition?**
Clients rely on the parent's guarantee. If the child delivers less, client logic built on that guarantee breaks.

**Q5. Give an LSP-safe example of each.**
Precondition weakened: `AdminUser` accepts 6-char passwords where `User` needs 8. Postcondition strengthened: `HybridCar::brake()` slows down **and** charges the battery.

**Q6. What is "Design by Contract"?**
The idea (Bertrand Meyer) that every method has preconditions, postconditions and invariants. The LSP method rules are those contract rules applied to inheritance.

---

## 8. One-line revision
> **"Demand LESS before, promise MORE after."** A child may relax what it needs and add to what it gives, never the reverse.

Related code in this folder: `PreConditions.cpp`, `PostConditions.cpp`.
Previous: **Property Rules** (`../PropertiesRules/`). Next in Lecture 06: **ISP** (`../../ISP/`) and **DIP** (`../../DIP/`).
