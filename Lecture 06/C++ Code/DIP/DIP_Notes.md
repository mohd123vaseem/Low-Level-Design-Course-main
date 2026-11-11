# Dependency Inversion Principle (DIP): Notes

## 1. Overview
This file covers two connected topics:
1. **Dependency Inversion Principle (DIP)**: the *rule* (depend on abstractions).
2. **Dependency Injection (DI)**: the *technique* used to follow that rule (pass the dependency in from outside).

---

## 2. Dependency Inversion Principle (DIP)

### Definition
> **"High-level modules should not depend on low-level modules. Both should depend on abstractions."**
> **"Abstractions should not depend on details. Details should depend on abstractions."** (Robert C. Martin, the D in SOLID)

Key words in plain language:
- **High-level module:** the class with the **business logic**, the "what" (`UserService`: *store a user*).
- **Low-level module:** the class with the **technical details**, the "how" (`MySQLDatabase`: *run an INSERT query*).
- **Abstraction:** an abstract class / interface in between (`Database` with `save() = 0`).
- **"Depends on":** uses it as a member, parameter or return type, or creates it with `new`.

**Why "inversion"?**
```
Normal (bad) flow:   UserService  ------------>  MySQLDatabase
                      (high)        depends on      (low)

Inverted (DIP):      UserService  ---->  Database  <----  MySQLDatabase
                      (high)      uses   (abstract)  is-a     (low)
```
The low-level class used to be the thing everyone pointed **to**. Now it points **up** to the abstraction. The dependency arrow is **inverted**.

### What problem it solves (why we study it)
Without DIP, the important business class is **glued to specific tools** (MySQL, Email, a particular payment gateway):
- **Switching tools means editing business logic.** Moving from MySQL to MongoDB forces changes inside `UserService`.
- **Every new tool adds new methods** (`storeUserToSQL`, `storeUserToMongo`...), which also breaks **OCP**.
- **Hard to unit test:** you can't test `UserService` without a real MySQL database, because you can't swap in a fake one.
- **Changes ripple upward:** a change in a low-level detail class breaks the high-level class that uses it.

```
-----------------------------------------------------------------------------------------------
| Problem without DIP                               | Benefit with DIP                        |
-----------------------------------------------------------------------------------------------
| Business class tied to one specific tool          | Business class works with ANY tool      |
-----------------------------------------------------------------------------------------------
| Switching DB / sender means editing business code | Switch by passing a different object    |
-----------------------------------------------------------------------------------------------
| New tool = new methods in the high-level class    | New tool = new subclass only (OCP)      |
-----------------------------------------------------------------------------------------------
| Can't test without the real DB / service          | Pass a fake/mock object in tests        |
-----------------------------------------------------------------------------------------------
| Low-level changes break high-level code           | Both sides only meet at the abstraction |
-----------------------------------------------------------------------------------------------
```

**Key idea:** The **business logic should not care HOW things are done**. It talks to an abstraction, and the details plug in from below.

**Analogy 🔌:** your phone doesn't depend on one specific charger. It depends on the **USB-C port standard** (the abstraction). Any charger that follows USB-C (the details) works. The phone maker and the charger maker both depend on the standard, not on each other.

### Examples

#### Example 1: UserService and Databases (from the lecture code)

##### ❌ Bad: high-level class depends on concrete databases
```
           +------------------------------+
           |  UserService  (HIGH-level)   |
           +------------------------------+
           | - sqlDb : MySQLDatabase      |
           | - mongoDb : MongoDBDatabase  |
           +------------------------------+
           | + storeUserToSQL(user)       |
           | + storeUserToMongo(user)     |
           +------------------------------+
                           | has-a (concrete classes!)
            +--------------+--------------+
            v                             v
+-----------------------+    +------------------------+
|  MySQLDatabase  (LOW) |    | MongoDBDatabase  (LOW) |
+-----------------------+    +------------------------+
| + saveToSQL(data)     |    | + saveToMongo(data)    |
+-----------------------+    +------------------------+
```

```cpp
class MySQLDatabase {                       // Low-level module
public:
    void saveToSQL(string data) {
        cout << "Executing SQL Query: INSERT INTO users VALUES('" << data << "');" << endl;
    }
};

class MongoDBDatabase {                     // Low-level module
public:
    void saveToMongo(string data) {
        cout << "Executing MongoDB Function: db.users.insert({name: '" << data << "'})" << endl;
    }
};

class UserService {                         // High-level module (tightly coupled) ❌
    MySQLDatabase sqlDb;                    // direct dependency on MySQL
    MongoDBDatabase mongoDb;                // direct dependency on MongoDB
public:
    void storeUserToSQL(string user)   { sqlDb.saveToSQL(user); }
    void storeUserToMongo(string user) { mongoDb.saveToMongo(user); }
    // PostgreSQL tomorrow? -> edit UserService again ❌
};
```
`UserService` knows every database **by name**. Each new database means changing the business class.

##### ✅ Good: both depend on the Database abstraction
```
            +----------------------------+
            | UserService  (HIGH-level)  |
            +----------------------------+
            | - db : Database*           |
            +----------------------------+
            | + UserService(Database*)   |
            | + storeUser(user)          |
            +----------------------------+
                           | has-a (abstraction only)
                           v
              +------------------------+
              | <<abstract>> Database  |
              +------------------------+
              | + save(data) = 0       |
              +------------------------+
                           ^
                           | is-a
            +--------------+--------------+
            |                             |
+-----------------------+    +------------------------+
|  MySQLDatabase  (LOW) |    | MongoDBDatabase  (LOW) |
+-----------------------+    +------------------------+
| + save(data)          |    | + save(data)           |
+-----------------------+    +------------------------+
```

```cpp
// Abstraction (Interface)
class Database {
public:
    virtual void save(string data) = 0;
};

// Low-level modules depend on the abstraction (is-a)
class MySQLDatabase : public Database {
public:
    void save(string data) override {
        cout << "Executing SQL Query: INSERT INTO users VALUES('" << data << "');" << endl;
    }
};

class MongoDBDatabase : public Database {
public:
    void save(string data) override {
        cout << "Executing MongoDB Function: db.users.insert({name: '" << data << "'})" << endl;
    }
};

// High-level module depends only on the abstraction (has-a) ✅
class UserService {
    Database* db;
public:
    UserService(Database* database) { db = database; }   // dependency injection
    void storeUser(string user) { db->save(user); }
};

int main() {
    MySQLDatabase mysql;
    MongoDBDatabase mongodb;

    UserService service1(&mysql);
    service1.storeUser("Aditya");

    UserService service2(&mongodb);       // same class, different DB ✅
    service2.storeUser("Rohit");
}
```
`UserService` never mentions MySQL or MongoDB. PostgreSQL tomorrow? Add `class PostgresDatabase : public Database`, and **`UserService` doesn't change**.

#### Example 2: Notification Service (classic interview one)

##### ❌ Bad
```
+-------------------------+
|   NotificationService   |
+-------------------------+
| - email : EmailSender   |
+-------------------------+
| + notify(msg)           |
+-------------------------+
             | has-a (concrete)
             v
  +--------------------+
  |    EmailSender     |
  +--------------------+
  | + sendEmail(msg)   |
  +--------------------+
```

```cpp
class EmailSender {
public:
    void sendEmail(string msg) { cout << "Email: " << msg << endl; }
};

class NotificationService {
    EmailSender email;                       // ❌ stuck with email forever
public:
    void notify(string msg) { email.sendEmail(msg); }
};
```

##### ✅ Good
```
             +---------------------------+
             |    NotificationService    |
             +---------------------------+
             | - sender : MessageSender* |
             +---------------------------+
             | + notify(msg)             |
             +---------------------------+
                           | has-a
                           v
            +----------------------------+
            | <<abstract>> MessageSender |
            +----------------------------+
            | + send(msg) = 0            |
            +----------------------------+
                           ^
                           | is-a
        +------------------+-------------------+
        |                  |                   |
+---------------+  +---------------+  +----------------+
|  EmailSender  |  |   SMSSender   |  | WhatsAppSender |
+---------------+  +---------------+  +----------------+
| + send(msg)   |  | + send(msg)   |  | + send(msg)    |
+---------------+  +---------------+  +----------------+
```

```cpp
class MessageSender {
public:
    virtual void send(string msg) = 0;
    virtual ~MessageSender() {}
};

class EmailSender : public MessageSender {
public:
    void send(string msg) override { cout << "Email: " << msg << endl; }
};

class SMSSender : public MessageSender {
public:
    void send(string msg) override { cout << "SMS: " << msg << endl; }
};

class NotificationService {
    MessageSender* sender;                   // ✅ any sender
public:
    NotificationService(MessageSender* s) : sender(s) {}
    void notify(string msg) { sender->send(msg); }
};

int main() {
    NotificationService byEmail(new EmailSender());
    NotificationService bySMS(new SMSSender());
    byEmail.notify("Order placed");
    bySMS.notify("OTP: 4821");
}
```

### How to spot a violation
- A high-level class has **members of concrete low-level types** (`MySQLDatabase sqlDb;`).
- It **creates its own dependencies** with `new ConcreteClass()` inside.
- Method names contain the **technology** (`storeUserToSQL`, `sendViaEmail`).
- Swapping a tool, or testing with a fake, means **editing the business class**.

### How to apply it
1. Identify the **high-level** class (business logic) and the **low-level** classes (DB, email, file, API...).
2. Create an **abstraction** describing *what* the high-level class needs (`Database::save()`).
3. Make every low-level class **inherit** that abstraction.
4. In the high-level class, keep only a **pointer/reference to the abstraction** (`Database* db`).
5. **Pass the concrete object in from outside** (Dependency Injection, next topic).

---

## 3. Dependency Injection (DI)

### Definition
> **"Give a class its dependencies from OUTSIDE, instead of letting it create them inside."**

- A **dependency** is an object a class needs to do its job (`UserService` needs a `Database`).
- **Injection** means someone else (usually `main()` or a factory) **creates it and passes it in**.
- DIP is the **principle** (depend on abstractions); DI is the **technique** that makes it possible.

### What problem it solves (why we study it)
Even with a `Database` abstraction, DIP is still broken if the class does this:
```cpp
class UserService {
    Database* db;
public:
    UserService() { db = new MySQLDatabase(); }   // ❌ still hard-wired to MySQL
};
```
The member's type is abstract, but the class **still chooses the concrete class itself**. Switching or testing still means editing `UserService`. DI moves that choice **outside** the class.

**Key idea:** A class should **use** its tools, not **build** them.

**Analogy 🍳:** a chef doesn't grow the vegetables. The restaurant **supplies (injects)** them. Change the supplier, and the chef cooks the same way.

### Examples

#### ❌ Bad: creating the dependency inside
```cpp
class UserService {
    Database* db = new MySQLDatabase();       // ❌ decided inside
public:
    void storeUser(string user) { db->save(user); }
};
```

#### ✅ Good 1: Constructor injection (used in the lecture code, the most common)
```cpp
class UserService {
    Database* db;
public:
    UserService(Database* database) { db = database; }   // ✅ passed in
    void storeUser(string user) { db->save(user); }
};

MySQLDatabase mysql;
UserService service(&mysql);                 // main() decides which DB
```

#### ✅ Good 2: Setter injection (change the dependency later)
```cpp
class UserService {
    Database* db = nullptr;
public:
    void setDatabase(Database* database) { db = database; }   // ✅ swap anytime
    void storeUser(string user) { db->save(user); }
};

UserService service;
service.setDatabase(new MongoDBDatabase());
```

#### ✅ Bonus: Easy unit testing
```cpp
class FakeDatabase : public Database {
public:
    void save(string data) override { cout << "[TEST] pretend-saved " << data << endl; }
};

UserService service(new FakeDatabase());     // test without a real DB ✅
```

### How to spot a violation
- `new ConcreteClass()` **inside** a high-level class's constructor or methods.
- You can't test the class without a **real** database / network / file.

### How to apply it
1. Remove `new Concrete...()` from inside the class.
2. Add a **constructor parameter** (or setter) of the **abstract type**.
3. Create the concrete object in **`main()`** (or a factory) and pass it in.

---

## 4. Links to other principles
- **OCP:** DIP makes the high-level class *closed for modification*. New databases are new subclasses (extension).
- **LSP:** any `Database` subclass must work correctly wherever `Database*` is used, or the injected object breaks the service.
- **ISP:** keep the abstraction small (`save()` only), so low-level classes don't implement things the high-level class never calls.
- **SRP:** `UserService` handles user logic, and each database class handles storage.

## 5. Comparison / summary

```
-------------------------------------------------------------------------------------------------------------
|              | Dependency Inversion (DIP)                   | Dependency Injection (DI)                   |
-------------------------------------------------------------------------------------------------------------
| What it is   | A design PRINCIPLE                           | A coding TECHNIQUE                          |
-------------------------------------------------------------------------------------------------------------
| Says         | Depend on abstractions, not concrete classes | Pass dependencies in from outside           |
-------------------------------------------------------------------------------------------------------------
| Answers      | WHAT should my class depend on?              | HOW does my class get that dependency?      |
-------------------------------------------------------------------------------------------------------------
| Lecture code | UserService uses Database*                   | UserService(Database* database) constructor |
-------------------------------------------------------------------------------------------------------------
```

**All of SOLID in one line each:**

```
-------------------------------------------------------------
| Principle | One line                                      |
-------------------------------------------------------------
| S - SRP   | One class, one reason to change               |
-------------------------------------------------------------
| O - OCP   | Add new classes instead of editing old ones   |
-------------------------------------------------------------
| L - LSP   | A child must work everywhere its parent works |
-------------------------------------------------------------
| I - ISP   | Many small interfaces, not one fat one        |
-------------------------------------------------------------
| D - DIP   | Depend on abstractions, inject the details    |
-------------------------------------------------------------
```

---

## 6. Important interview questions

**Q1. What is DIP?**
High-level modules should not depend on low-level modules; both should depend on abstractions. Abstractions should not depend on details.

**Q2. What are high-level and low-level modules?**
High-level modules hold the business logic (`UserService`). Low-level modules handle technical details (`MySQLDatabase`, `EmailSender`).

**Q3. What is "inverted" in Dependency Inversion?**
The direction of the dependency arrow. Instead of high-level → low-level, the low-level class now depends upward on an abstraction that the high-level class owns.

**Q4. Difference between Dependency Inversion and Dependency Injection?**
DIP is the principle (depend on abstractions). DI is the technique (pass the dependency in from outside, e.g. via the constructor) that helps achieve it.

**Q5. Types of dependency injection?**
Constructor injection (most common, the object is ready from the start), setter injection (can change later), and interface/method injection (passed as a method parameter).

**Q6. Is `Database* db = new MySQLDatabase();` inside the class DIP-compliant?**
No. The pointer type is abstract, but the class still chooses the concrete class itself. The concrete object should be injected from outside.

**Q7. How does DIP help testing?**
You can inject a fake/mock implementation of the abstraction, so the class is tested without a real database or network.

**Q8. Real-world analogy?**
A phone depends on the USB-C standard, not on a specific charger; any charger that follows the standard works.

---

## 7. One-line revision
> **"Business logic talks to an abstraction; the details plug in from outside."**

Related code in this folder: `DIP_violated.cpp`, `DIP_followed.cpp`.
Previous: **ISP** (`../ISP/`). That completes **SOLID**.
