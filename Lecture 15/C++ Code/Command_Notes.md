# Command Design Pattern: Notes

## 1. Command Design Pattern

### Definition
> **"Encapsulate a REQUEST as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations."** (GoF, a behavioural pattern)

- Turn an **action** ("turn the light on") into an **object** (`LightCommand`) with `execute()` and `undo()`.
- The one who **asks** for the action (the remote) and the one who **does** it (the light) no longer know each other. The command object sits in between.
- Because the action is an object, it can be **stored** in a button, **swapped** at runtime, and **undone**.

Analogy: in a restaurant, the waiter (invoker) doesn't cook. They write your order on a slip (command) and hand it to the kitchen, where the chef (receiver) cooks it. The waiter works the same way for every dish.

### The 4 roles
```
-----------------------------------------------------------------------------------------
| Role            | Job                                      | Lecture code             |
-----------------------------------------------------------------------------------------
| Command         | Interface: execute() and undo()          | Command                  |
-----------------------------------------------------------------------------------------
| ConcreteCommand | Holds a receiver, calls its methods      | LightCommand, FanCommand |
-----------------------------------------------------------------------------------------
| Receiver        | Does the real work                       | Light, Fan               |
-----------------------------------------------------------------------------------------
| Invoker         | Holds commands, calls execute() / undo() | RemoteController         |
-----------------------------------------------------------------------------------------
```

`main()` plays the **client**: it creates the receivers and the commands and puts the commands into the remote's buttons.

### What problem it solves (why we study it)
Without Command, the remote has to know every device and call it directly:
- **Tight coupling:** `RemoteController` has a `Light*`, a `Fan*`, ... and calls `light->on()` itself.
- **if-else chain:** `pressButton()` grows a new branch for every device (breaks OCP).
- **Buttons are fixed:** button 0 is always the light; you can't re-assign it at runtime.
- **No common undo:** each device turns off in its own way, so a generic "undo" is impossible.

```
-----------------------------------------------------------------------------------
| Problem without Command           | Benefit with Command                        |
-----------------------------------------------------------------------------------
| Remote knows every device class   | Remote only knows Command                   |
-----------------------------------------------------------------------------------
| New device = edit pressButton()   | New device = new command class (OCP)        |
-----------------------------------------------------------------------------------
| Button meaning fixed in code      | setCommand() re-assigns a button at runtime |
-----------------------------------------------------------------------------------
| No common way to undo             | Every command has undo()                    |
-----------------------------------------------------------------------------------
| Can't store / queue / log actions | Actions are objects: store, queue, log them |
-----------------------------------------------------------------------------------
```

**Key idea:** **Wrap each request in an object with `execute()` / `undo()`. The invoker just presses "execute" and never knows what really happens.**

### Standard UML (from `Standard UML.jpg`)
```
+-------------------------+  has-a   +-----------------------+
|         Invoker         |--------->| <<abstract>> ICommand |
+-------------------------+          +-----------------------+
| - c : ICommand*         |          | + execute() = 0       |
+-------------------------+          | + undo() = 0          |
| + setCommand(ICommand*) |          +-----------------------+
+-------------------------+                      ^
                                                 | is-a
                                       +-------------------+  has-a   +------------+
                                       |  ConcreteCommand  |--------->|  Receiver  |
                                       +-------------------+          +------------+
                                       | - r : Receiver*   |          | + action() |
                                       +-------------------+          +------------+
                                       | + execute()       |
                                       | + undo()          |
                                       +-------------------+
```

- **ICommand** (abstract): `execute()` and `undo()`.
- **Invoker** has-a `ICommand*` and only calls `execute()` / `undo()` on it.
- **ConcreteCommand** is-a ICommand and **has-a Receiver**. `execute()` calls the receiver's `action()`.
- **Receiver**: the class that really does the work. It knows nothing about commands.

### Example: Smart home remote (lecture code)

Mapping to the UML (`Example UML.jpg`):

```
------------------------------------------------------------------
| Standard UML    | Lecture code                                 |
------------------------------------------------------------------
| Invoker         | RemoteController                             |
------------------------------------------------------------------
| ICommand c      | Command* buttons[4] (one command per button) |
------------------------------------------------------------------
| setCommand(c)   | setCommand(idx, Command*)                    |
------------------------------------------------------------------
| ICommand        | Command (execute() = 0, undo() = 0)          |
------------------------------------------------------------------
| ConcreteCommand | LightCommand, FanCommand                     |
------------------------------------------------------------------
| Receiver        | Light, Fan                                   |
------------------------------------------------------------------
| action()        | on() / off()                                 |
------------------------------------------------------------------
```

#### ❌ Bad: the remote talks to every device directly
```
+-------------------------------+  has-a (every device)
|        RemoteController       |------------------------+--------------+----------------+
+-------------------------------+                        v              v                v
| - light : Light*              |                   +---------+    +---------+    +------------+
| - fan : Fan*                  |                   |  Light  |    |   Fan   |    | ... AC, TV |
+-------------------------------+                   +---------+    +---------+    +------------+
| + pressButton(idx)            |                   | + on()  |    | + on()  |
|   if idx == 0: light->on()    |                   | + off() |    | + off() |
|   else if idx == 1: fan->on() |                   +---------+    +---------+
|   else if ... (grows forever) |
+-------------------------------+
```

The remote holds every device and decides in `pressButton()` what to call. Adding an AC means editing `RemoteController` again, and the buttons can't be re-assigned.

#### ✅ Good: buttons hold commands
```
+-----------------------------+  has-a (0..4)   +----------------------+
|       RemoteController      |---------------->| <<abstract>> Command |
+-----------------------------+                 +----------------------+
| - buttons[4] : Command*     |                 | + execute() = 0      |
| - buttonPressed[4] : bool   |                 | + undo() = 0         |
+-----------------------------+                 +----------------------+
| + setCommand(idx, Command*) |                             ^
| + pressButton(idx)          |                             | is-a
| + ~RemoteController()       |       +---------------------+----------------------+
+-----------------------------+       |                                            |
                            +------------------+  has-a   +---------+    +------------------+  has-a   +---------+
                            |   LightCommand   |--------->|  Light  |    |    FanCommand    |--------->|   Fan   |
                            +------------------+          +---------+    +------------------+          +---------+
                            | - light : Light* |          | + on()  |    | - fan : Fan*     |          | + on()  |
                            +------------------+          | + off() |    +------------------+          | + off() |
                            | + execute()      |          +---------+    | + execute()      |          +---------+
                            | + undo()         |                         | + undo()         |
                            +------------------+                         +------------------+
```

> Code: `CommandPattern.cpp`: `Command`, `Light`, `Fan`, `LightCommand`, `FanCommand`, `RemoteController` (`setCommand()`, `pressButton()` toggle, destructor) and `main()`.

- `RemoteController` stores only **`Command*`**. It doesn't know `Light` or `Fan` exist.
- `LightCommand` **has-a `Light*`**: `execute()` = `light->on()`, `undo()` = `light->off()`. Same for `FanCommand` with `Fan`.
- **Toggle:** `buttonPressed[i]` remembers each button's state. Pressing once runs `execute()`, pressing again runs `undo()`.
- **Memory:** the remote **owns the commands**: `setCommand()` deletes the old command on that button, and `~RemoteController()` deletes all of them. The receivers (`Light`, `Fan`) are **not** owned by the commands, so `main()` deletes them.
- The class comment says "6 buttons (3 rows, 2 cols)", but the code has **4 buttons** (`numButtons = 4`) in a plain array.

**What happens on `pressButton(0)`:**
```
remote->pressButton(0)
   |
   +-- buttons[0] != nullptr ?            (else: "No command assigned at button 0")
   +-- buttonPressed[0] == false ?
   |      yes --> buttons[0]->execute()   --> LightCommand::execute() --> light->on()  --> "Light is ON"
   |      no  --> buttons[0]->undo()      --> LightCommand::undo()    --> light->off() --> "Light is OFF"
   +-- buttonPressed[0] = !buttonPressed[0]
```

**`main()` step by step:**

```
----------------------------------------------------------------------------------------------
| Step in main()                         | Button state    | Output                          |
----------------------------------------------------------------------------------------------
| setCommand(0, new LightCommand(light)) | 0 = Light (off) | -                               |
----------------------------------------------------------------------------------------------
| setCommand(1, new FanCommand(fan))     | 1 = Fan (off)   | -                               |
----------------------------------------------------------------------------------------------
| pressButton(0)                         | 0 = on          | Light is ON                     |
----------------------------------------------------------------------------------------------
| pressButton(0)                         | 0 = off         | Light is OFF                    |
----------------------------------------------------------------------------------------------
| pressButton(1)                         | 1 = on          | Fan is ON                       |
----------------------------------------------------------------------------------------------
| pressButton(1)                         | 1 = off         | Fan is OFF                      |
----------------------------------------------------------------------------------------------
| pressButton(2)                         | 2 = empty       | No command assigned at button 2 |
----------------------------------------------------------------------------------------------
| delete remote                          | -               | deletes both commands           |
----------------------------------------------------------------------------------------------
| delete light, delete fan               | -               | receivers freed by main()       |
----------------------------------------------------------------------------------------------
```

### How to spot that you need it
- An object (button, menu item, scheduler) must **trigger actions without knowing who does them**.
- You see `if (button == 0) light->on(); else if (button == 1) fan->on(); ...`.
- You need **undo/redo**, or to **queue, log or schedule** actions.
- Actions must be **re-assigned at runtime** (re-mapping a button).

### How to apply it
1. Create the **command interface** with `execute()` and `undo()` (`Command`), plus a virtual destructor.
2. Keep the **receivers** as normal classes that do the work (`Light`, `Fan`).
3. Create one **concrete command per action**: it has-a receiver pointer and calls it in `execute()` / `undo()` (`LightCommand`, `FanCommand`).
4. Make the **invoker** hold `Command*` slots and only call `execute()` / `undo()` (`RemoteController`).
5. In the **client** (`main()`), create receivers and commands, and plug the commands into the invoker with `setCommand()`.

### Where it is used (real world)
Wherever an action must be stored, re-assigned, queued, logged or undone:

```
-----------------------------------------------------------------------------------------------------------
| Where                               | Invoker                | Commands                                 |
-----------------------------------------------------------------------------------------------------------
| Text editors (VS Code, Word)        | Editor + history stack | Type, delete, paste (undo / redo)        |
-----------------------------------------------------------------------------------------------------------
| Menus, toolbars, shortcuts          | Menu item, Ctrl+S      | SaveCommand (one command, many triggers) |
-----------------------------------------------------------------------------------------------------------
| Smart home apps / remotes (lecture) | Remote, app button     | LightCommand, FanCommand                 |
-----------------------------------------------------------------------------------------------------------
| Job queues / thread pools           | Worker threads         | Tasks queued and run later               |
-----------------------------------------------------------------------------------------------------------
| Database migrations                 | Migration runner       | Migrations: up = execute, down = undo    |
-----------------------------------------------------------------------------------------------------------
| Games                               | Input handler          | Jump, shoot (re-mappable keys, replays)  |
-----------------------------------------------------------------------------------------------------------
```

---

## 2. Links to other principles
- **SRP:** the remote only manages buttons, each command only maps one action, each receiver only does its own work.
- **OCP:** a new device = a new receiver + a new command class. `RemoteController` never changes.
- **DIP:** the remote depends on the `Command` abstraction, not on `Light` or `Fan`.
- **Strategy (Lecture 08):** both hold an interface pointer and call it. Strategy swaps **how** one job is done; Command wraps **what** request to run (and can undo it).

---

## 3. Important interview questions

**Q1. What is the Command pattern?**
A behavioural pattern that wraps a request in an object with `execute()` (and often `undo()`), so the invoker can trigger it without knowing the receiver.

**Q2. Name the 4 roles in the lecture code.**
Command (interface), LightCommand / FanCommand (concrete commands), Light / Fan (receivers), RemoteController (invoker). `main()` is the client that wires them.

**Q3. Why doesn't `RemoteController` know about `Light`?**
It only stores `Command*`. The command holds the `Light*`, so new devices need no change in the remote (loose coupling, OCP).

**Q4. How does undo work in the lecture?**
Each command has `undo()` doing the opposite action (`light->off()`). The remote keeps `buttonPressed[i]` and calls `execute()` or `undo()` alternately (toggle).

**Q5. How would you support multi-level undo (undo the last N actions)?**
Push every executed command onto a history stack; "undo" pops the top command and calls its `undo()`.

**Q6. Who deletes what in the lecture code?**
The remote owns the commands (deleted in `setCommand()` on replace and in `~RemoteController()`). The receivers are deleted by `main()`, because several commands could share one receiver.

**Q7. Command vs Strategy?**
Strategy picks one of many ways to do the SAME job. Command turns a REQUEST into an object to store, queue, log or undo.

**Q8. Real-world uses?**
Remote controls and UI buttons/menus, undo/redo in editors, task queues and job schedulers, and transaction logs.

---

## 4. One-line revision
> **"Wrap each request in an object with execute() / undo(); the invoker holds commands, each command holds its receiver, and nobody else needs to know who does the work."**

Related code in this folder: `CommandPattern.cpp` (and `../Standard UML.jpg`, `../Example UML.jpg`).
Previous: **Lecture 14: Notification System** (`../../Lecture 14/C++ Code/`). Next: **Adapter Pattern** (`../../Lecture 16/C++ Code/`).
