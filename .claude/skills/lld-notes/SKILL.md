---
name: lld-notes
description: Write or edit the C++ study notes (<Topic>_Notes.md) for this Low-Level Design course, and explain any LLD concept, principle or rule to the user. Use whenever the user asks for notes on a lecture folder, asks to add/explain a concept, or asks "explain X".
---

# Writing LLD notes and explaining concepts

The user studies this course **in C++ only**. Ignore the `Java Code/` folders.
Always read the lecture's `.cpp` files first and base the first example of each topic on them (same class names, same scenario).

## Core rule: finish one topic completely, then move on
Explain each topic/concept/rule **fully in one place** before starting the next one. Never scatter a topic's definition, reasons and examples across separate sections.

For **every topic** (a principle, or each rule inside a principle) write, in this order:
1. **Definition**: a clear, one-line quoted definition, then 1-3 bullets in plain words.
2. **What problem it solves / why we study it**: the pain without it, and what goes wrong for the client code. For a principle, add a boxed "Problem without X / Benefit with X" table. End with a bold **Key idea:** line.
3. **Examples** (if any):
   - **Only examples from the lecture's own code** (same classes, same scenario), plus the lecture's UML image if there is one. No extra classic/interview examples unless the user asks. The ❌ Bad version uses the same lecture classes.
   - Useful extras built from the lecture code: a UML -> lecture-class mapping table, a call-flow sketch, a `main()` step-by-step table.
   - Each example: `### ❌ Bad` and `### ✅ Good`, each with an ASCII class diagram, then 1-2 lines on why. **No code blocks** (see Formatting).
   - A simple real-life analogy if it makes the idea clearer (cricket, shop, car...).
4. **How to spot a violation** (for principles/rules): a bullet list of smells.
5. **How to apply it** (for principles/rules): numbered steps.
5b. **Where it is used (real world)** (for every DESIGN PATTERN, as the last subsection of that pattern):
   one intro line, then a boxed table of 5-6 well-known real uses (apps, libraries, STL, frameworks) whose columns
   name the pattern's roles (e.g. Where | Subject | Observers). This table is the one allowed exception to
   "lecture-only examples". Keep it within about 120 columns.
6. Only then start the **next topic**, with the same steps.

After all topics:
7. **Links to other principles** (e.g. SRP + OCP, LSP and OCP), when relevant.
8. **Comparison / summary** (only when there are several related topics): one boxed table.
9. **Important interview questions**: at the very END only, `**Q1. ...?**` followed by a 1-2 line answer.
10. **One-line revision**: a bold quote.
11. Footer: the related `.cpp` files in the folder, plus Previous/Next topic.

### Skeleton
```
# <Topic> : Notes

## 1. Overview            <- 2-3 lines: what this file covers (skip if only one topic)

## 2. <Topic/Rule 1>
### Definition
### What problem it solves (why we study it)
### Examples
#### ❌ Bad   (diagram + code + why)
#### ✅ Good  (diagram + code + why)
### How to spot a violation
### How to apply it

---

## 3. <Topic/Rule 2>
### Definition
### What problem it solves (why we study it)
### Examples
...

---

## N-1. Links to other principles (if relevant)
## N. Comparison / summary      (if several topics)
## N+1. Important interview questions
## N+2. One-line revision
```

The same order applies when explaining in chat: definition, then problem/why, then examples, one topic at a time, with interview questions last.

## Style
- Crisp and to the point; simple words. The user prefers very simple explanations with analogies when a concept is confusing.
- Use `---` between topics.
- When the user asks to add something "briefly, as a concept", write a short `###` subsection (bullets plus a small diagram) inside the related topic, not as a Q&A.

## Formatting
- **Tables are closed boxes made only of `-` and `|` (never `+`)**, inside a plain ``` fence:
  ```
  ------------------------------------------
  | Rule               | Child may         |
  ------------------------------------------
  | 1. Class Invariant | Keep / strengthen |
  ------------------------------------------
  ```
  - Don't use `**bold**` or backticks inside, because they don't render in a code block. Use CAPS for emphasis.
  - Workflow: write a normal Markdown table, then run `python tools/notes_tools.py "<path>_Notes.md"`.
    It converts every table to this style and counts emoji (✅ ❌) as 2 columns.
- **Class diagrams are plain ASCII only** (`+ - | ^ v`), inside a plain ``` fence. No Unicode box characters.
  - UML-style boxes: title, then fields (`- private`, `# protected`), then methods (`+ public`), in separate sections.
  - Mark abstract classes `<<abstract>> Name` and pure virtuals `= 0`.
  - Put the parent above its children. Label arrows `is-a` (inheritance) or `has-a` (composition).
  - Generate diagrams with `box()`, `leaf()`, `tree()`, `beside()` from `tools/notes_tools.py`. Don't hand-draw them.
  - **Grow diagrams sideways, not downwards.** `is-a` trees stay top-down (parent above children), but
    `has-a` / `creates` / `uses` links go LEFT -> RIGHT: `side(client, tree, "has-a")` puts the box to the left
    with a `----->` arrow; `fan(box, [trees], "has-a")` fans one box out to several children.
    Don't stack Client above Factory above Product with `above()`.
  - **Show every relation.** If a class holds, creates or uses another, draw that arrow. No floating boxes.
    - `has-a`: SOLID `----->`. Only when the class keeps the other as a MEMBER (pointer/object field).
    - `creates` / `uses`: DASHED `- - ->` (`dash=True` in `side()`, `fan()`, `tree()`). A dependency: makes or uses it and keeps nothing.
    - Draw creation from the CONCRETE creator to the CONCRETE product (`SinghBurger - - -> BasicBurger`),
      never from an abstract factory to an abstract product. The abstract class creates nothing.
    - **Always draw the `<<abstract>>` parent** of products above them (`tree()`); never shortcut with "is-a X" text in a box.
    - Creational diagrams: `factory_view(client, factory, product_tree)` gives Client -uses-> <<abstract>> Product,
      Client -has-a-> Factory, Factory - -creates- -> each concrete product. `feed(creator, product_tree)` without a client.
      Several creator/product pairs (RoadLogistics->Truck, SeaLogistics->Ship): `connect_below(beside(t1, t2), links)`.
  - Keep a diagram within about 120 columns.
- **No C++ code blocks in notes.** The code already lives in the lecture's `.cpp` files.
  - For a lecture example, add one pointer line after the diagram, like: > Code: `File.cpp`: <what to look at>.
  - Short inline `code` names are fine (`notifySubscribers()`).

## Where notes go
`Lecture XX/C++ Code/<Topic>/<Topic>_Notes.md`, next to the lecture's `.cpp` files.
