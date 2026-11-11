"""Helpers for writing the *_Notes.md files: aligned ASCII class diagrams and aligned Markdown tables.

Diagrams:
    from notes_tools import box, leaf, tree, beside, D
    parent = box("<<abstract>> Shape", [["+ area() = 0"]], 22)
    lines, _ = tree(parent, [leaf(box("Circle", [["+ area()"]], 14)),
                             leaf(box("Square", [["+ area()"]], 14))], "is-a")
    print(D(lines))          # fenced ``` block ready to paste into the .md

Tables (write normal Markdown tables, then run this to box them):
    python tools/notes_tools.py "Lecture 06/C++ Code/LSP-Rules/PropertiesRules/PropertiesRules_Notes.md"
"""
import sys
import unicodedata


# ---------- diagrams ----------

def box(title, sections, inner):
    """UML-style box. sections = list of line lists (fields, methods, notes); inner = width inside the borders."""
    bar = "+" + "-"*inner + "+"
    out = [bar, "|" + title.center(inner) + "|", bar]
    for sec in sections:
        for line in sec:
            out.append("| " + line.ljust(inner-1) + "|")
        out.append(bar)
    return out


def leaf(b):
    """Wrap a single box so it can be passed as a child of tree()."""
    return (b, len(b[0]) // 2)


def _at(total, cols, chars):
    row = [" "]*total
    for c, ch in zip(cols, chars):
        for k, cc in enumerate(ch):
            row[c+k] = cc
    return "".join(row).rstrip()


def tree(top, children, label, gap="  "):
    """Parent box centered above its children, joined by a '^ | label' arrow.
    children = list of leaf(box) or another tree() result (for multi-level hierarchies).
    Returns (lines, center_column)."""
    ws = [max(len(l) for l in c[0]) for c in children]
    h = max(len(c[0]) for c in children)
    kids = [gap.join((c[0][i] if i < len(c[0]) else "").ljust(w) for c, w in zip(children, ws)).rstrip()
            for i in range(h)]
    centers, x = [], 0
    for (lines, c), w in zip(children, ws):
        centers.append(x + c)
        x += w + len(gap)
    mid = centers[len(centers)//2] if len(centers) % 2 else (centers[0] + centers[-1]) // 2
    off = mid - len(top[0])//2
    if off < 0:
        shift = -off
        kids = [" "*shift + k if k else k for k in kids]
        centers = [c + shift for c in centers]
        mid += shift
        off = 0
    total = x + 200
    out = [" "*off + l for l in top]
    out.append(_at(total, [mid], ["^"]))
    out.append(_at(total, [mid], ["| " + label]))
    if len(children) > 1:
        line = [" "]*total
        for c in range(centers[0], centers[-1]+1):
            line[c] = "-"
        for c in centers + [mid]:
            line[c] = "+"
        out.append("".join(line).rstrip())
        out.append(_at(total, centers, ["|"]*len(centers)))
    return out + kids, mid


def beside(a, b, gap="        "):
    """Place two diagrams side by side."""
    wa = max(len(l) for l in a)
    h = max(len(a), len(b))
    return [((a[i] if i < len(a) else "").ljust(wa) + gap + (b[i] if i < len(b) else "")).rstrip()
            for i in range(h)]


def D(lines):
    """Wrap diagram lines in a plain ``` fence."""
    return "```\n" + "\n".join(l.rstrip() for l in lines) + "\n```"


# ---------- tables ----------

def width(s):
    """Display width in a monospace font (emoji like ✅ ❌ take 2 columns)."""
    w = 0
    for ch in s:
        if unicodedata.combining(ch) or ch == "️":
            continue
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def _pad(s, w):
    return s + " " * (w - width(s))


def _split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _plain(cell):
    """Inside a code fence Markdown doesn't render, so drop ** and ` markers."""
    return cell.replace("**", "").replace("`", "")


def grid(rows):
    """Closed boxy table: '-' rules above, below and between rows, '|' columns, no '+'. rows[0] is the header."""
    ws = [max(width(r[k]) for r in rows) for k in range(len(rows[0]))]
    line = lambda r: "| " + " | ".join(_pad(c, w) for c, w in zip(r, ws)) + " |"
    rule = "-" * width(line(rows[0]))
    return [rule] + [l for r in rows for l in (line(r), rule)]


def boxify_tables(text):
    """Turn every Markdown table outside code fences into a fenced grid() table."""
    lines = text.split("\n")
    out, i, in_code = [], 0, False
    while i < len(lines):
        if lines[i].startswith("```"):
            in_code = not in_code
        if in_code or not lines[i].startswith("|"):
            out.append(lines[i])
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].startswith("|"):
            j += 1
        rows = [[_plain(c) for c in _split_row(l)] for l in lines[i:j]]
        rows = [r for r in rows if not all(c and set(c) <= set("-:") for c in r)]
        n = max(len(r) for r in rows)
        rows = [r + [""] * (n - len(r)) for r in rows]
        out += ["```"] + grid(rows) + ["```"]
        i = j
    return "\n".join(out)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        new = boxify_tables(text)
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print("boxed:", path)
