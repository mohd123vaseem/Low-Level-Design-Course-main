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
   - Example 1 from the lecture code, then 1-2 classic/interview examples if they help (Payment, Shapes, Birds, Rectangle/Square...).
   - Each example: `### ❌ Bad` and `### ✅ Good`, each with an ASCII class diagram, then a short C++ snippet, then 1-2 lines on why.
   - A simple real-life analogy if it makes the idea clearer (cricket, shop, car...).
4. **How to spot a violation** (for principles/rules): a bullet list of smells.
5. **How to apply it** (for principles/rules): numbered steps.
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
- When the user asks to add something "briefly, as a concept", write a short `###` subsection (bullets plus a small snippet or diagram) inside the related topic, not as a Q&A.

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
- C++ snippets: short, `using namespace std` style like the lecture code, `override` on overrides, `// ❌` / `// ✅` / `// 💥` on key lines.

## Where notes go
`Lecture XX/C++ Code/<Topic>/<Topic>_Notes.md`, next to the lecture's `.cpp` files.
