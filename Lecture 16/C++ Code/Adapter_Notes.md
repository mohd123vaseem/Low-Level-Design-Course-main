# Adapter Design Pattern: Notes

## 1. Adapter Design Pattern

### Definition
> **"Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces."** (GoF, a structural pattern)

- The client expects one interface (**Target**: `IReports`, gives JSON).
- An existing class does the job but with a **different interface** (**Adaptee**: `XmlDataProvider`, gives XML).
- The **Adapter** sits in between: it **is-a** Target (so the client can use it) and **has-a** Adaptee (to do the real work), and **converts** between them.

Analogy: an Indian charger doesn't fit a UK socket. You don't rewire the charger or the wall. You plug in a travel adapter that fits both.

### What problem it solves (why we study it)
The client works with JSON, but the data source (`XmlDataProvider`) only returns XML. It may be a third-party or old class that we **can't or shouldn't change**. Without an adapter:
- **The client does the conversion itself:** XML parsing ends up inside `Client` (mixed jobs, breaks SRP).
- **Duplicated code:** every client that needs JSON repeats the same parsing.
- **Tight coupling:** the client depends on the concrete `XmlDataProvider` class. A different data source means editing every client.
- **Editing the adaptee** to return JSON could break all its other users.

```
---------------------------------------------------------------------------------
| Problem without Adapter               | Benefit with Adapter                  |
---------------------------------------------------------------------------------
| Client parses XML itself              | Conversion lives in ONE adapter class |
---------------------------------------------------------------------------------
| Same parsing copied into every client | Written once, reused                  |
---------------------------------------------------------------------------------
| Client tied to XmlDataProvider        | Client only knows IReports            |
---------------------------------------------------------------------------------
| Must edit the old / third-party class | Adaptee stays untouched               |
---------------------------------------------------------------------------------
| New data source = edit clients        | New data source = new adapter (OCP)   |
---------------------------------------------------------------------------------
```

**Key idea:** **Don't change the client or the old class. Put a translator in between that speaks the client's interface and calls the old class inside.**

### Standard UML (from `Standard UML.jpeg`)
```
+--------------+  uses   +----------------------+
|    Client    | - - - ->| <<abstract>> ITarget |
+--------------+         +----------------------+
| knows ONLY   |         | + request() = 0      |
| ITarget      |         +----------------------+
+--------------+                     ^
                                     | is-a
                        +------------------------+  has-a   +---------------------+
                        |        Adapter         |--------->|       Adaptee       |
                        +------------------------+          +---------------------+
                        | - adaptee : Adaptee*   |          | + specificRequest() |
                        +------------------------+          +---------------------+
                        | + request()            |
                        |   -> adaptee->         |
                        |      specificRequest() |
                        +------------------------+
```

- **ITarget** (abstract): what the client expects (`request()`).
- **Client** works only with `ITarget`.
- **Adapter** is-a ITarget **and** has-a `Adaptee*`. Its `request()` calls `adaptee->specificRequest()` and converts the result.
- **Adaptee**: the existing class with the "wrong" interface (`specificRequest()`). It knows nothing about the adapter.

### Example: XML data to JSON report (lecture code)

Mapping to the UML (`Example UML.jpeg`):

```
--------------------------------------------------------------
| Standard UML      | Lecture code                           |
--------------------------------------------------------------
| Client            | Client (getReport(IReports*, rawData)) |
--------------------------------------------------------------
| ITarget           | IReports                               |
--------------------------------------------------------------
| request()         | getJsonData(data)                      |
--------------------------------------------------------------
| Adapter           | XmlDataProviderAdapter                 |
--------------------------------------------------------------
| Adaptee adaptee   | XmlDataProvider* xmlProvider           |
--------------------------------------------------------------
| Adaptee           | XmlDataProvider                        |
--------------------------------------------------------------
| specificRequest() | getXmlData(data)                       |
--------------------------------------------------------------
```

#### ❌ Bad: the client uses the XML class directly
```
+-------------------------------+  uses (directly)   +-----------------------+
|             Client            |- - - - - - - - - ->|    XmlDataProvider    |
+-------------------------------+                    +-----------------------+
| + getReport(XmlDataProvider*, |                    | + getXmlData(data)    |
|     rawData)                  |                    |   gives XML, not JSON |
|   calls getXmlData()          |                    +-----------------------+
|   parses XML -> JSON HERE     |
|   (in EVERY client)           |
+-------------------------------+
```

`Client` now knows the XML class and does the XML -> JSON parsing itself. Every other client that wants JSON copies the same parsing, and switching to another data source means editing all of them.

#### ✅ Good: an adapter converts XML to JSON
```
+------------------------+  uses   +-------------------------+
|         Client         | - - - ->|  <<abstract>> IReports  |
+------------------------+         +-------------------------+
| + getReport(IReports*, |         | + getJsonData(data) = 0 |
|     rawData)           |         +-------------------------+
+------------------------+                      ^
                                                | is-a
                              +----------------------------------+  has-a   +---------------------+
                              |      XmlDataProviderAdapter      |--------->|   XmlDataProvider   |
                              +----------------------------------+          +---------------------+
                              | - xmlProvider : XmlDataProvider* |          | + getXmlData(data)  |
                              +----------------------------------+          |   "Alice:42" -> XML |
                              | + getJsonData(data)              |          +---------------------+
                              |   1. xmlProvider->getXmlData()   |
                              |   2. parse <name>, <id>          |
                              |   3. build JSON                  |
                              +----------------------------------+
```

> Code: `AdpaterPattern.cpp`: `IReports`, `XmlDataProvider::getXmlData()`, `XmlDataProviderAdapter::getJsonData()` (get XML, parse `<name>` and `<id>`, build JSON), `Client::getReport()` and `main()`.

- `Client` only knows **`IReports*`**. It never sees XML or `XmlDataProvider`.
- `XmlDataProvider` is **unchanged**: it still only knows how to make XML.
- All conversion lives in `XmlDataProviderAdapter::getJsonData()`.
- `Client` gets the report as a **parameter** in `getReport()` and keeps nothing, so its arrow is a dashed **uses**, not has-a.
- The parsing is deliberately simple (`find` + `substr`): fine for the demo format, not a real XML parser.

**What happens on `client->getReport(adapter, "Alice:42")`:**
```
client->getReport(adapter, "Alice:42")
   |
   +-- report->getJsonData("Alice:42")          (IReports* --> XmlDataProviderAdapter)
          |
          +-- xmlProvider->getXmlData("Alice:42")  --> "<user><name>Alice</name><id>42</id></user>"
          +-- cut out name = "Alice", id = "42"
          +-- return {"name":"Alice", "id":42}
   |
   +-- prints: Processed JSON: {"name":"Alice", "id":42}
```

**`main()` step by step:**

```
----------------------------------------------------------------------------
| Step in main()                      | What it does                       |
----------------------------------------------------------------------------
| new XmlDataProvider()               | create the adaptee (old XML class) |
----------------------------------------------------------------------------
| new XmlDataProviderAdapter(xmlProv) | wrap it; store it as IReports*     |
----------------------------------------------------------------------------
| rawData = "Alice:42"                | input in name:id format            |
----------------------------------------------------------------------------
| client->getReport(adapter, rawData) | prints the JSON                    |
----------------------------------------------------------------------------
| delete adapter, delete xmlProv      | main() owns both, so it frees both |
----------------------------------------------------------------------------
```

### Two kinds of Adapter: Object vs Class
**Object Adapter** (the lecture code): the adapter **has-a** adaptee (composition), as drawn above.

**Class Adapter** (from `class adapter.png`): the adapter **inherits from BOTH** the target and the adaptee (multiple inheritance, which C++ allows), and calls the adaptee's method on itself:
```
+-------------------------+    +---------------------+
|  <<abstract>> IReports  |    |   XmlDataProvider   |
+-------------------------+    +---------------------+
| + getJsonData(data) = 0 |    | + getXmlData(data)  |
+-------------------------+    +---------------------+
             ^                            ^
             |                            |
             +-------------+--------------+
                           | is-a BOTH (multiple inheritance)
              +-------------------------+
              |  XmlDataProviderAdapter |
              +-------------------------+
              | + getJsonData(data)     |
              |   -> this->getXmlData() |
              |      then convert       |
              +-------------------------+
```

```
---------------------------------------------------------------------------------------
| Point                           | Object Adapter (lecture) | Class Adapter          |
---------------------------------------------------------------------------------------
| Relation to adaptee             | has-a (pointer)          | is-a (inherits it)     |
---------------------------------------------------------------------------------------
| Works with adaptee's subclasses | YES, pass any object     | NO, fixed to one class |
---------------------------------------------------------------------------------------
| Can override adaptee's methods  | NO                       | YES                    |
---------------------------------------------------------------------------------------
| Needs multiple inheritance      | NO                       | YES (C++ ok, Java no)  |
---------------------------------------------------------------------------------------
| Usually preferred               | YES (composition)        | rarely                 |
---------------------------------------------------------------------------------------
```

### How to spot that you need it
- An existing class **does the job, but its method names / data format don't match** what your code expects.
- The class is **third-party, legacy, or shared**, so you can't change it.
- You see **conversion code (XML -> JSON, units, formats) inside client classes**.

### How to apply it
1. Define the **target interface** the client wants (`IReports` with `getJsonData()`).
2. Keep the **adaptee** as it is (`XmlDataProvider`).
3. Create the **adapter**: is-a target, has-a `Adaptee*` set in its constructor (`XmlDataProviderAdapter`).
4. In the target method, **call the adaptee and convert** the result (`getXmlData()` -> parse -> JSON).
5. Make the **client depend only on the target** (`getReport(IReports*, ...)`) and pass it the adapter.

### Where it is used (real world)
Wherever an existing class does the job but its interface doesn't fit:

```
----------------------------------------------------------------------------------------------------------------
| Where                               | Client expects (target)      | Adaptee (existing interface)            |
----------------------------------------------------------------------------------------------------------------
| Payment gateways                    | One IPayment interface       | Razorpay, Stripe, PayPal SDKs           |
----------------------------------------------------------------------------------------------------------------
| Legacy / third-party APIs (lecture) | JSON report                  | Old XML data provider                   |
----------------------------------------------------------------------------------------------------------------
| C++ STL container adapters          | stack, queue, priority_queue | deque / vector underneath               |
----------------------------------------------------------------------------------------------------------------
| Logging facades (SLF4J)             | One logger interface         | Log4j, Logback                          |
----------------------------------------------------------------------------------------------------------------
| Java InputStreamReader              | Character stream (Reader)    | Byte stream (InputStream)               |
----------------------------------------------------------------------------------------------------------------
| Real life                           | Your socket / laptop         | Travel plug adapter, memory card reader |
----------------------------------------------------------------------------------------------------------------
```

---

## 2. Links to other principles
- **SRP:** the conversion has its own class; the client only prints, the adaptee only makes XML.
- **OCP:** a new data source (say CSV) = a new `CsvAdapter`. `Client` and `XmlDataProvider` don't change.
- **DIP:** `Client` depends on the `IReports` abstraction, not on a concrete provider.
- **Composition over inheritance:** the lecture's object adapter wraps the adaptee (has-a) instead of inheriting it.
- **Decorator (Lecture 13):** both wrap an object. Decorator keeps the **same** interface and adds behaviour; Adapter **changes** the interface.

---

## 3. Important interview questions

**Q1. What is the Adapter pattern?**
A structural pattern that converts one class's interface into another interface the client expects, so incompatible classes can work together.

**Q2. Name the roles in the lecture code.**
Target = `IReports`, Adaptee = `XmlDataProvider`, Adapter = `XmlDataProviderAdapter`, Client = `Client`.

**Q3. Why not just change `XmlDataProvider` to return JSON?**
It may be third-party or legacy code, and other code may depend on its XML output. The adapter adds JSON without touching it (OCP).

**Q4. Object adapter vs class adapter?**
An object adapter has-a adaptee (composition, works with any adaptee subclass). A class adapter inherits both target and adaptee (multiple inheritance, fixed to one class). The lecture uses an object adapter.

**Q5. Adapter vs Decorator?**
Both wrap an object. A decorator keeps the same interface and adds behaviour; an adapter changes the interface so it fits.

**Q6. Why is `Client`'s arrow "uses" and not "has-a"?**
`getReport()` receives `IReports*` as a parameter and stores nothing, so it's a dependency, not a member.

**Q7. Who deletes what in the lecture code?**
`main()` created both the adapter and the provider, so it deletes both. The adapter doesn't delete `xmlProvider` because it didn't create it.

**Q8. Real-world uses?**
Wrapping third-party or legacy APIs, payment gateway wrappers (one `IPayment` over Razorpay / Stripe / PayPal), data-format converters (XML/CSV -> JSON), and phone chargers / card readers in real life.

---

## 4. One-line revision
> **"An adapter is-a Target and has-a Adaptee: the client calls the interface it knows, the adapter calls the old class and converts the result."**

Related code in this folder: `AdpaterPattern.cpp` (and `../Standard UML.jpeg`, `../Example UML.jpeg`, `../class adapter.png`).
Previous: **Command Pattern** (`../../Lecture 15/C++ Code/`). Next: **Lecture 17** (`../../Lecture 17/C++ Code/`).
