# LSP Signature Rules: Notes

## 1. What are Signature Rules?
LSP says a child must be usable wherever the parent is used. **Signature rules** are the checks on a method's **"shape"** that make this possible:

```
-------------------------------------------------------------------------------------------
| Rule                    | What the child may do                        | Fancy name     |
-------------------------------------------------------------------------------------------
| 1. Method Argument Rule | Accept the same or wider argument types      | Contravariance |
-------------------------------------------------------------------------------------------
| 2. Return Type Rule     | Return the same or narrower type             | Covariance     |
-------------------------------------------------------------------------------------------
| 3. Exception Rule       | Throw the same, fewer or narrower exceptions | n/a            |
-------------------------------------------------------------------------------------------
```

**Memory trick:** the child must **accept at least as much** and **give back nothing surprising**.
- **Input** (args): can only get **wider** (more accepting).
- **Output** (return, exceptions): can only get **narrower** (more specific).

---

## 2. Why do we need them?
The **client only knows the parent** (`Parent* p`). It was written against the parent's signature:
- It **passes** what the parent accepts, so the child must accept that too.
- It **expects back** what the parent returns, so the child can't return something else.
- It **catches** what the parent throws, so the child can't throw something the client won't catch.

Break any one of these and swapping `Parent` for `Child` breaks the client, which is an LSP violation.

---

## 3. Rule 1: Method Argument Rule
> **Child method arguments must be identical to, or wider than, the parent's.**

```
+----------------------+
|        Parent        |
+----------------------+
| + print(string msg)  |
+----------------------+
            ^
            | is-a  (same signature)
+----------------------+
|        Child         |
+----------------------+
| + print(string msg)  |
+----------------------+
```

```cpp
class Parent {
public:
    virtual void print(string msg) { cout << "Parent: " << msg << endl; }
};

class Child : public Parent {
public:
    void print(string msg) override { cout << "Child: " << msg << endl; }   // same args ✅
};

class Client {
    Parent* p;
public:
    Client(Parent* p) { this->p = p; }
    void printMsg() { p->print("Hello"); }      // client passes a string
};

int main() {
    Client* client = new Client(new Child());    // swap Parent -> Child: still works ✅
    client->printMsg();
}
```

**Why "wider" is OK but "narrower" is not:**
- The client passes a `string`. If the child only accepted something narrower (say, only short messages), some client calls would fail.
- If the child accepted something wider, every client call would still work.

**How C++ handles it:** C++ **enforces identical parameters** for overriding. If the child changes the parameter type, it is **not an override**. It becomes a *new* function that **hides** the parent's one. With the `override` keyword, the compiler catches this:
```cpp
class Child : public Parent {
public:
    void print(const char* msg) override { }   // ❌ compile error: doesn't override anything
};
```
So in C++ this rule is **automatically safe**: just keep the signature the same and always write `override`.

---

## 4. Rule 2: Return Type Rule (Covariance)
> **Child's overridden method must return the same type, or a narrower one (a subtype).**

```
+-------------------------+        +------------+
|          Parent         |        |   Animal   |
+-------------------------+        +------------+
| + getAnimal() : Animal* |               ^
+-------------------------+               | is-a
             ^                     +------------+
             | is-a                |    Dog     |
+-------------------------+        +------------+
|          Child          |
+-------------------------+
| + getAnimal() : Dog*    |
+-------------------------+
```

```cpp
class Animal { /* common animal stuff */ };
class Dog : public Animal { /* dog-specific stuff */ };

class Parent {
public:
    virtual Animal* getAnimal() {
        cout << "Parent : Returning Animal instance" << endl;
        return new Animal();
    }
};

class Child : public Parent {
public:
    Dog* getAnimal() override {        // narrower return type (Dog* is-a Animal*) ✅
        cout << "Child : Returning Dog instance" << endl;
        return new Dog();
    }
};

class Client {
    Parent* p;
public:
    Client(Parent* p) { this->p = p; }
    void takeAnimal() { Animal* a = p->getAnimal(); }   // client expects an Animal*
};
```

**Why it works:** the client expects an `Animal*`. A `Dog*` **is-a** `Animal*`, so the client is happy.
**Why wider fails:** if the child returned something *more general* than `Animal` (e.g. `void*` / `Object*`), the client could receive something that is **not** an Animal.

**How C++ handles it:** C++ **enforces** this through **covariant return types**:
- ✅ Allowed: `Animal*` → `Dog*` and `Animal&` → `Dog&` (pointers/references to a derived class)
- ❌ Compile error: returning an unrelated type, or changing `int` to `double`
- Covariance only works with **pointers or references**, not with objects by value.

---

## 5. Rule 3: Exception Rule
> **A child should throw the same, fewer or narrower exceptions than the parent. Never additional or broader ones.**

**C++ exception hierarchy (the part you need):**
```
                                   +------------------+
                                   |  std::exception  |
                                   +------------------+
                                             ^
                                             | is-a
                     +-----------------------+-----------------------+
                     |                                               |
            +-----------------+                             +-----------------+
            |   logic_error   |                             |  runtime_error  |
            +-----------------+                             +-----------------+
                     ^                                               ^
                     | is-a                                          | is-a
          +----------+----------+                         +----------+----------+
          |                     |                         |                     |
+------------------+  +------------------+      +------------------+  +------------------+
| invalid_argument |  |   out_of_range   |      |  overflow_error  |  |   range_error    |
+------------------+  +------------------+      +------------------+  +------------------+
```
"Narrower" means **lower in this tree** (a child class of the parent's exception).

```
                +--------------------------+
                |          Parent          |
                +--------------------------+
                | + getValue()             |
                |   throws logic_error     |
                +--------------------------+
                              ^
                              | is-a
              +---------------+---------------+
              |                               |
+--------------------------+    +--------------------------+
|       Child  (OK)        |    |      Child  (WRONG)      |
+--------------------------+    +--------------------------+
| + getValue()             |    | + getValue()             |
|   throws out_of_range    |    |   throws runtime_error   |
+--------------------------+    +--------------------------+
```

```cpp
class Parent {
public:
    virtual void getValue() noexcept(false) {
        throw logic_error("Parent error");
    }
};

class Child : public Parent {
public:
    void getValue() noexcept(false) override {
        throw out_of_range("Child error");        // ✅ out_of_range is-a logic_error
        // throw runtime_error("Child Error");    // ❌ different branch, client won't catch it
    }
};

class Client {
    Parent* p;
public:
    Client(Parent* p) { this->p = p; }
    void takeValue() {
        try {
            p->getValue();
        }
        catch (const logic_error& e) {             // client only prepared for logic_error
            cout << "Logic error exception occured : " << e.what() << endl;
        }
    }
};
```

**Why:**
- The client catches `logic_error`. `out_of_range` is a `logic_error`, so it gets **caught** ✅.
- `runtime_error` is **not** a `logic_error`, so it **escapes** the catch block and the program **crashes** 💥.

**How C++ handles it:** C++ does **NOT** enforce this. There is **no compile error**; it fails only at **runtime**. Following it is **your responsibility**.
(`noexcept` is the one exception: if the parent is `noexcept`, the child must be `noexcept` too, or the compiler errors.)

---

## 6. Summary: who enforces what in C++?

```
---------------------------------------------------------------------------------------------------------------
| Rule            | Child may                    | C++ compiler enforces?                                     |
---------------------------------------------------------------------------------------------------------------
| Method Argument | same (or wider) params       | ✅ Yes. A different param means no override (use override) |
---------------------------------------------------------------------------------------------------------------
| Return Type     | same or narrower (covariant) | ✅ Yes, for pointers/references                            |
---------------------------------------------------------------------------------------------------------------
| Exception       | same / fewer / narrower      | ❌ No. Your job                                            |
---------------------------------------------------------------------------------------------------------------
```

---

## 7. Common interview questions

**Q1. What are LSP signature rules?**
Rules on arguments, return types and exceptions of overridden methods, so a child can safely replace its parent.

**Q2. What is return type covariance?**
An overriding method can return a **more derived** type than the parent (`Animal*` → `Dog*`).

**Q3. What is argument contravariance? Does C++ support it?**
The child accepts a **more general** argument type. C++ does **not** support it for overriding: parameters must be identical, otherwise the method **hides** the parent's instead of overriding it.

**Q4. Can a child throw a new exception type?**
Only if it's a **subclass** of what the parent throws. A broader or unrelated exception breaks clients that only catch the parent's exception.

**Q5. Does C++ check the exception rule?**
No. It is checked only at runtime (the program crashes). Only `noexcept` mismatches are caught at compile time.

**Q6. Why always write `override`?**
It makes the compiler verify you're really overriding. Without it, a signature mistake silently creates a new hiding function.

---

## 8. One-line revision
> **"Inputs can get wider, outputs can only get narrower."** Accept everything the parent accepts; return and throw nothing the client isn't ready for.

Related code in this folder: `MethodArgumentRule.cpp`, `ReturnTypeRule.cpp`, `ExceptionRule.cpp`.
Next: **Property Rules** (`../PropertiesRules/`) and **Method Rules** (`../MethodRules/`).
