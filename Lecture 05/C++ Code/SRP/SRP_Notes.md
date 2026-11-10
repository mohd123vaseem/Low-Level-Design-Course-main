# Single Responsibility Principle (SRP): Notes

## 1. What is SRP?
> **"A class should have only ONE reason to change."** (Robert C. Martin, the S in SOLID)

- One class does **one job** and has **one responsibility**.
- A "reason to change" is a **stakeholder or concern**. For example, the billing team, the DB team or the UI team.
- SRP does **not** mean "one method per class". It means one **cohesive purpose**.

---

## 2. Why do we need SRP?

| Problem without SRP | Benefit with SRP |
|---|---|
| A change in one feature breaks another | Changes stay isolated |
| Huge "God classes" that are hard to read | Small, readable classes |
| Hard to unit test because everything is coupled | Each class is easy to test alone |
| Merge conflicts when many devs edit the same file | Teams work on separate classes |
| Poor reuse | Pieces can be reused, e.g. `Printer` for any invoice |

**Key idea:** If a class has many responsibilities, a change made for one of them can break the others.

---

## 3. How do you spot an SRP violation?
- The class name has **"And" / "Manager" / "Util"** in it, e.g. `UserAndEmailManager`.
- Describing the class needs the word **"and"**: "It calculates price **and** saves to DB **and** prints."
- **Unrelated imports** sit in one class: DB headers, file I/O, email and math together.
- Many **different people or teams** would ask you to change this one class.

## 4. How do you apply SRP?
1. List everything the class does.
2. Group the work by **reason to change**.
3. Move each group into its **own class**.
4. Use **composition** so a higher-level class uses these small classes.

---

## 5. Example 1: Shopping Cart (the classic one)

### ❌ Violating SRP

```
+--------------------------------+
|          ShoppingCart          |
+--------------------------------+
| - products : vector<Product*>  |
+--------------------------------+
| + addProduct(Product*)         |
| + calculateTotal() : double    |  <- business logic
| + printInvoice()               |  <- presentation
| + saveToDB()                   |  <- persistence
+--------------------------------+
```

```cpp
class Product {
public:
    string name;
    double price;
    Product(string n, double p) : name(n), price(p) {}
};

class ShoppingCart {
    vector<Product*> products;
public:
    void addProduct(Product* p) { products.push_back(p); }

    double calculateTotal() {
        double total = 0;
        for (auto p : products) total += p->price;
        return total;
    }

    void printInvoice() {                 // reason to change #2
        cout << "Invoice:\n";
        for (auto p : products) cout << p->name << " - " << p->price << "\n";
        cout << "Total: " << calculateTotal() << "\n";
    }

    void saveToDB() {                     // reason to change #3
        cout << "Saving cart to DB...\n";
    }
};
```
**This class has 3 reasons to change:** the pricing logic, the invoice format and the DB technology.

### ✅ Following SRP

```
+---------------------------+
|       ShoppingCart        |   (only manages items + total)
+---------------------------+
| - products: vector<Product*>
| + addProduct()            |
| + getProducts()           |
| + calculateTotal()        |
+---------------------------+
        ^              ^
        | has-a        | has-a
+-------------------+  +-------------------+
| CartInvoicePrinter|  |  CartDBStorage    |
+-------------------+  +-------------------+
| - cart: ShoppingCart*| - cart: ShoppingCart*
| + printInvoice()  |  | + saveToDB()      |
+-------------------+  +-------------------+
```

```cpp
class ShoppingCart {
    vector<Product*> products;
public:
    void addProduct(Product* p) { products.push_back(p); }
    const vector<Product*>& getProducts() { return products; }

    double calculateTotal() {
        double total = 0;
        for (auto p : products) total += p->price;
        return total;
    }
};

class CartInvoicePrinter {
    ShoppingCart* cart;
public:
    CartInvoicePrinter(ShoppingCart* c) : cart(c) {}
    void printInvoice() {
        cout << "Invoice:\n";
        for (auto p : cart->getProducts())
            cout << p->name << " - " << p->price << "\n";
        cout << "Total: " << cart->calculateTotal() << "\n";
    }
};

class CartDBStorage {
    ShoppingCart* cart;
public:
    CartDBStorage(ShoppingCart* c) : cart(c) {}
    void saveToDB() { cout << "Saving cart to DB...\n"; }
};

int main() {
    ShoppingCart* cart = new ShoppingCart();
    cart->addProduct(new Product("Laptop", 50000));
    cart->addProduct(new Product("Mouse", 500));

    CartInvoicePrinter printer(cart);
    printer.printInvoice();

    CartDBStorage db(cart);
    db.saveToDB();
}
```
Now if the DB changes from MySQL to MongoDB, you **only touch `CartDBStorage`**.

---

## 6. Example 2: Employee

### ❌ Bad
```
+-----------------------+
|       Employee        |
+-----------------------+
| + calculatePay()      |  -> Accounts team
| + generateReport()    |  -> HR team
| + saveEmployee()      |  -> DBA / Tech team
+-----------------------+
```

### ✅ Good
```
+--------------+     +-----------------+
|   Employee   |<----| PayCalculator   |  + calculatePay(Employee&)
|  (data only) |     +-----------------+
| - id, name,  |<----| ReportGenerator |  + generate(Employee&)
|   salary     |     +-----------------+
+--------------+<----| EmployeeRepo    |  + save(Employee&)
                     +-----------------+
```

```cpp
class Employee {
public:
    int id; string name; double salary;
};

class PayCalculator {
public:
    double calculatePay(Employee& e) { return e.salary * 0.9; }
};

class ReportGenerator {
public:
    void generate(Employee& e) { cout << "Report: " << e.name << "\n"; }
};

class EmployeeRepo {
public:
    void save(Employee& e) { cout << "Saved " << e.name << "\n"; }
};
```

---

## 7. Example 3: User Registration (quick one)

```
❌ UserService: register() + validateEmail() + sendWelcomeEmail() + logToFile()

✅ UserService ──uses──> EmailValidator   (validate)
               ──uses──> EmailSender      (send mail)
               ──uses──> Logger           (log)
```

---

## 8. Common interview questions

**Q1. What is SRP?**
A class should have only one reason to change, meaning one responsibility.

**Q2. Does SRP mean one method per class?**
No. A class can have many methods as long as they all serve **one purpose**.

**Q3. What is a "reason to change"?**
An actor or concern that may need the class modified, such as the UI, the DB or business rules.

**Q4. Downside of SRP?**
Overdoing it creates **too many tiny classes**, which is class explosion. Use judgment and split by real concerns.

**Q5. How is SRP related to cohesion and coupling?**
SRP gives **high cohesion**, because related things stay together. It also gives **low coupling**, because unrelated things are kept apart.

**Q6. What is a real-world analogy?**
In a restaurant, the **chef** cooks, the **waiter** serves and the **cashier** bills. If the chef did all three, a billing change would disturb cooking.

---

## 9. One-line revision
> **"Gather together things that change for the same reason; separate things that change for different reasons."**

Related code in this folder: `SRP_violated.cpp`, `SRP_followed.cpp`.
Next in this lecture: **OCP** (Open/Closed Principle) in `../OCP/`. It builds on SRP: once classes are split, you extend them instead of modifying them.
