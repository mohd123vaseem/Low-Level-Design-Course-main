# LLD Course: Study Notes Conventions

The user is studying this Low-Level Design course **in C++ only**. Ignore the `Java Code/` folders.

## Where notes go
- One notes file per topic folder, next to the lecture's `.cpp` files:
  `Lecture XX/C++ Code/<Topic>/<Topic>_Notes.md` (e.g. `SRP/SRP_Notes.md`, `PropertiesRules/PropertiesRules_Notes.md`).
- Always read the lecture's `.cpp` files first and base Example 1 on them (same class names, same scenario).

## Structure of every notes file
Crisp and to the point. Numbered `##` sections separated by `---`:
1. **What is X?**: one-line quoted definition, then 2-3 bullets. Add a summary table if the topic has several rules.
2. **Why do we need it?**: a "Problem without / Benefit with" table, or a short client-perspective explanation, plus a bold **Key idea:** line.
3. **How to spot a violation**: bullet list of smells.
4. **How to apply it**: numbered steps.
5. **Examples** (usually 2-3):
   - Example 1 from the lecture code, then 1-2 classic or interview examples (Payment, Shapes, Birds, Rectangle/Square...).
   - Each example has `### ❌ Bad` and `### ✅ Good` with an **ASCII class diagram**, then a C++ snippet, then 1-2 lines on why.
6. **Links to other principles** (e.g. SRP + OCP, LSP and OCP).
7. **Common interview questions**: `**Q1. ...?**` followed by a 1-2 line answer.
8. **One-line revision**: a bold quote.
9. Footer: the related `.cpp` files in the folder, plus Previous/Next topic.

When the user asks for an extra explanation to be added "briefly, as a concept": a short `###` subsection (bullets + small snippet/diagram) placed next to the related section, not as a Q&A.

## Formatting rules
- **Tables are closed boxes made only of `-` and `|` (never `+`)**, inside a plain ``` fence:
  ```
  ------------------------------------------
  | Rule               | Child may         |
  ------------------------------------------
  | 1. Class Invariant | Keep / strengthen |
  ------------------------------------------
  ```
  - One long, smooth `-` line above the header, below the header, and after every row.
  - No `**bold**` or backticks inside (they don't render in a code block); use CAPS for emphasis.
  - Workflow: write a normal Markdown table, then run `python tools/notes_tools.py "<path>_Notes.md"`.
    It converts every table to this style and counts emoji (✅ ❌) as 2 columns, so the borders line up.
- **Class diagrams are plain ASCII only** (`+ - | ^ v`), inside a plain ``` fence. No Unicode box characters.
  - UML-style boxes: title, then fields (`- private`, `# protected`), then methods (`+ public`), in separate sections.
  - Mark abstract classes `<<abstract>> Name` and pure virtuals `= 0`.
  - Parent above children; arrows labelled `is-a` (inheritance) or `has-a` (composition).
  - Generate diagrams with `box()`, `leaf()`, `tree()`, `beside()` from `tools/notes_tools.py` so every border lines up. Don't hand-draw them.
- C++ snippets: short, `using namespace std` style like the lecture code, `override` on overrides, `// ❌` / `// ✅` / `// 💥` comments on the key lines.

## Git
- Commit messages: short, one line (e.g. `Add SRP, OCP, LSP notes`).
- **No co-author / AI attribution lines** in commits.
- Commit only when the user asks. Remote: `origin` (GitHub, `main`).
