# Observer Design Pattern: Notes

## 1. Observer Design Pattern

### Definition
> **"Define a ONE-TO-MANY dependency between objects, so that when one object changes state, all its dependents are notified and updated automatically."** (GoF, a behavioural pattern)

- **Observable / Subject:** the object being watched. It keeps a **list of observers** and tells them when something changes (`Channel`).
- **Observer:** an object that wants to know about the change. It only needs an `update()` method (`Subscriber`).
- Observers can **subscribe** (join the list) and **unsubscribe** (leave it) at any time, at runtime.
- Also called **Publish-Subscribe**: the channel *publishes*, the subscribers *subscribe*.

### What problem it solves (why we study it)
When many objects care about **one object's changes** (a new video), they need to find out somehow. Without the pattern:
- **Polling:** every subscriber keeps asking the channel *"anything new?"*. Most checks are wasted, and a new video is noticed **late**.
- **Hard-coding:** the channel would have to know every subscriber's **concrete class** and call it directly. A new kind of subscriber means **editing `Channel`** (breaks OCP and DIP).
- **No runtime control:** you can't easily add or remove listeners while the program runs.

```
-----------------------------------------------------------------------------------------------------
| Problem without Observer                       | Benefit with Observer                            |
-----------------------------------------------------------------------------------------------------
| Subscribers poll again and again (wasted work) | Channel tells them ONCE, exactly when it changes |
-----------------------------------------------------------------------------------------------------
| Updates are noticed late                       | Updates are instant                              |
-----------------------------------------------------------------------------------------------------
| Channel knows concrete subscriber classes      | Channel only knows ISubscriber (loose coupling)  |
-----------------------------------------------------------------------------------------------------
| New subscriber type = edit Channel             | New subscriber type = new class (OCP)            |
-----------------------------------------------------------------------------------------------------
| Fixed listeners                                | subscribe() / unsubscribe() at runtime           |
-----------------------------------------------------------------------------------------------------
```

**Key idea:** **Don't keep asking. Subscribe once, and the subject calls YOU when something changes.** ("Don't call us, we'll call you.")

### Standard UML (from `Standard UML.jpg`)
```
    +---------------------------+
    | <<interface>> IObservable |
    +---------------------------+
    | + add(IObserver*) = 0     |
    | + remove(IObserver*) = 0  |
    | + notify() = 0            |
    +---------------------------+
                  ^                                    +-------------------------+
                  | is-a                               | <<interface>> IObserver |
+----------------------------------+  has-a (1..*)     +-------------------------+
|        ConcreteObservable        |------------------>| + update() = 0          |
+----------------------------------+                   +-------------------------+
| - observers : vector<IObserver*> |                                ^
+----------------------------------+                                | is-a
| + add(IObserver*)                |  has-a      +------------------------------------+
| + remove(IObserver*)             |<------------|          ConcreteObserver          |
| + notify()                       |             +------------------------------------+
+----------------------------------+             | - observable : ConcreteObservable* |
                                                 +------------------------------------+
                                                 | + update()                         |
                                                 +------------------------------------+
```

- **IObservable** (interface): `add()`, `remove()`, `notify()`.
- **ConcreteObservable** is-a IObservable. It **has-a list (1..\*) of `IObserver*`**, and `notify()` loops over it calling `update()`.
- **IObserver** (interface): just `update()`.
- **ConcreteObserver** is-a IObserver. It **has-a** pointer back to the ConcreteObservable, so inside `update()` it can read the new data.
- The lecture's drawing puts the 1..\* has-a arrow between the two interfaces. In the code, the `vector` lives in the **concrete** class, so it's drawn from there.

### Example: YouTube Channel (lecture code)

Mapping to the UML:

```
-----------------------------------------------------------------------------------
| Standard UML                | Lecture code                                      |
-----------------------------------------------------------------------------------
| IObservable                 | IChannel                                          |
-----------------------------------------------------------------------------------
| add() / remove() / notify() | subscribe() / unsubscribe() / notifySubscribers() |
-----------------------------------------------------------------------------------
| ConcreteObservable          | Channel ("CoderArmy")                             |
-----------------------------------------------------------------------------------
| vector of IObserver*        | vector of ISubscriber* subscribers                |
-----------------------------------------------------------------------------------
| IObserver                   | ISubscriber                                       |
-----------------------------------------------------------------------------------
| ConcreteObserver            | Subscriber ("Varun", "Tarun")                     |
-----------------------------------------------------------------------------------
```

#### ❌ Bad: no Observer, subscribers keep checking (polling)
```
+---------------------------+  has-a, asks AGAIN and AGAIN   +---------------------------+
|    Subscriber  (Varun)    |------------------------------->|    Channel  (CoderArmy)   |
+---------------------------+                                +---------------------------+
| - channel : Channel*      |                                | - latestVideo : string    |
+---------------------------+                                +---------------------------+
| + checkForNewVideo()      |                                | + uploadVideo(title)      |
|   every few minutes:      |                                | + getVideoData() : string |
|   channel->getVideoData() |                                |   (tells NO ONE)          |
|   same as last time?      |                                +---------------------------+
+---------------------------+
```

The channel tells no one. Varun has to keep calling `getVideoData()` and compare it with the last result. Most calls find nothing new, and with 1 million subscribers that's 1 million wasted checks every few minutes.

#### ✅ Good: the Channel notifies its subscribers
```
   +---------------------------------+
   |      <<interface>> IChannel     |
   +---------------------------------+
   | + subscribe(ISubscriber*) = 0   |
   | + unsubscribe(ISubscriber*) = 0 |
   | + notifySubscribers() = 0       |
   +---------------------------------+
                    ^
                    | is-a
+--------------------------------------+  has-a (1..*)     +---------------------------+
|               Channel                |------------------>| <<interface>> ISubscriber |
+--------------------------------------+                   +---------------------------+
| - subscribers : vector<ISubscriber*> |                   | + update() = 0            |
| - name : string                      |                   +---------------------------+
| - latestVideo : string               |                                 ^
+--------------------------------------+                                 | is-a
| + subscribe(ISubscriber*)            |  has-a              +----------------------+
| + unsubscribe(ISubscriber*)          |<--------------------|      Subscriber      |
| + notifySubscribers()                |                     +----------------------+
| + uploadVideo(title)                 |                     | - name : string      |
| + getVideoData() : string            |                     | - channel : Channel* |
+--------------------------------------+                     +----------------------+
                                                             | + update()           |
                                                             +----------------------+
```

> Code: `ObserverDesignPattern.cpp`: `ISubscriber`, `IChannel`, `Channel` (subscribe without duplicates, unsubscribe, notify, `uploadVideo()`, `getVideoData()`), `Subscriber::update()`, and `main()`.

- `Channel` only knows **`ISubscriber*`**, never the `Subscriber` class, so it works with any kind of subscriber.
- `subscribe()` skips **duplicates** (it uses `find` before `push_back`). `unsubscribe()` removes the subscriber only if present.
- `Subscriber` keeps a **`Channel*`**, so in `update()` it can call `channel->getVideoData()` to read the latest video.

**What happens when a video is uploaded:**
```
channel->uploadVideo("Observer Pattern Tutorial")
   |
   +-- latestVideo = title
   +-- notifySubscribers()
          |
          +-- Varun->update() --> channel->getVideoData() --> "Hey Varun, Checkout our new Video : ..."
          +-- Tarun->update() --> channel->getVideoData() --> "Hey Tarun, Checkout our new Video : ..."
```

**`main()` step by step:**

```
-----------------------------------------------------------------------------------
| Step in main()                            | Subscriber list | Who gets notified |
-----------------------------------------------------------------------------------
| new Channel("CoderArmy")                  | empty           | -                 |
-----------------------------------------------------------------------------------
| subscribe(Varun), subscribe(Tarun)        | Varun, Tarun    | -                 |
-----------------------------------------------------------------------------------
| uploadVideo("Observer Pattern Tutorial")  | Varun, Tarun    | Varun AND Tarun   |
-----------------------------------------------------------------------------------
| unsubscribe(Varun)                        | Tarun           | -                 |
-----------------------------------------------------------------------------------
| uploadVideo("Decorator Pattern Tutorial") | Tarun           | ONLY Tarun        |
-----------------------------------------------------------------------------------
```

### Push vs Pull (the lecture uses PULL)
- **Push model:** the subject sends the data inside the call, e.g. `update(videoTitle)`. Observers get it directly, but every observer receives the same data whether it needs it or not.
- **Pull model:** the subject only says *"something changed"* with `update()` (no arguments). The observer then **pulls** what it needs (`channel->getVideoData()`).
- The lecture code is **pull**: `update()` has no parameters, which is why `Subscriber` must keep a `Channel*`.

### How to spot that you need it
- Several objects need to **react when one object changes** (new video, price change, order status).
- You see **polling loops** asking *"changed yet?"*.
- A class calls **many unrelated classes directly** after a change, and keeps growing as new ones are added.

### How to apply it
1. Create the **observer interface** with `update()` (`ISubscriber`).
2. Create the **subject interface** with `subscribe()`, `unsubscribe()`, `notifySubscribers()` (`IChannel`).
3. In the **concrete subject**, keep a `vector<ISubscriber*>`, and in `notifySubscribers()` call `update()` on each.
4. Call `notifySubscribers()` whenever the state changes (inside `uploadVideo()`).
5. In each **concrete observer**, implement `update()`. For the pull model, keep a pointer to the subject to read the new data.

### Where it is used (real world)
Wherever many objects must react when ONE object changes:

```
------------------------------------------------------------------------------------------------------
| Where                          | Subject (observable) | Observers                                  |
------------------------------------------------------------------------------------------------------
| YouTube / newsletters          | Channel, newsletter  | Subscribers                                |
------------------------------------------------------------------------------------------------------
| UI events (button click)       | Button               | onClick listeners (JS addEventListener)    |
------------------------------------------------------------------------------------------------------
| Stock / crypto apps            | Price ticker         | Watchlist, price alerts, charts            |
------------------------------------------------------------------------------------------------------
| Food delivery (Swiggy, Zomato) | Order status         | Customer app, restaurant, delivery partner |
------------------------------------------------------------------------------------------------------
| MVC / React state              | Model / state        | Views that re-render                       |
------------------------------------------------------------------------------------------------------
| Kafka, RabbitMQ (pub-sub)      | Topic                | Consumer services                          |
------------------------------------------------------------------------------------------------------
```

---

## 2. Links to other principles
- **OCP:** new kinds of subscribers are new `ISubscriber` classes, and `Channel` never changes.
- **DIP:** `Channel` depends on the `ISubscriber` abstraction, not on the concrete `Subscriber`.
- **SRP:** `Channel` manages videos and the subscriber list; each `Subscriber` decides what to do with a notification.
- **Composition (has-a):** the subject *has-a* list of observers, the same "hold objects, don't inherit behaviour" idea as **Strategy** (Lecture 08).

---

## 3. Important interview questions

**Q1. What is the Observer pattern?**
A behavioural pattern that defines a one-to-many dependency: when the subject changes, all its registered observers are notified automatically through `update()`.

**Q2. What are the main parts?**
The subject interface (`IChannel`: subscribe, unsubscribe, notify), the concrete subject (`Channel`, holds the observer list), the observer interface (`ISubscriber`: update) and the concrete observers (`Subscriber`).

**Q3. Why does the subject store `ISubscriber*` and not `Subscriber*`?**
For loose coupling (DIP). The channel can notify any kind of subscriber without knowing its class, and new kinds are added without editing `Channel` (OCP).

**Q4. Push vs pull model?**
Push sends the data in `update(data)`. Pull just calls `update()`, and the observer fetches what it needs from the subject. The lecture uses pull, which is why `Subscriber` keeps a `Channel*`.

**Q5. Why does the lecture's `subscribe()` check for duplicates?**
Without it, the same subscriber could be added twice and would get every notification twice.

**Q6. What's the advantage over polling?**
Observers are told exactly when something changes, so there are no wasted "anything new?" checks and no delay.

**Q7. Any downsides?**
Observers are notified in list order, with no priority. Many observers can make `notify` slow. And if an observer is deleted without unsubscribing, the subject holds a **dangling pointer** (crash on the next notify).

**Q8. Real-world uses?**
YouTube or newsletter subscriptions, button click listeners in UIs, stock price alerts, and event systems / message queues (pub-sub).

---

## 4. One-line revision
> **"One subject keeps a list of observers; when it changes, it calls update() on each one. Subscribe once, never poll."**

Related code in this folder: `ObserverDesignPattern.cpp` (and `../Standard UML.jpg`).
Previous: **Lecture 11** (`../../Lecture 11/`). Next: **Decorator Pattern** (`../../Lecture 13/C++ Code/`).
