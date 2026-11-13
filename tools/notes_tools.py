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


def tree(top, children, label, gap="  ", down=False, dash=False):
    """Parent box centered above its children, joined by a '^ | label' arrow.
    children = list of leaf(box) or another tree() result (for multi-level hierarchies).
    down=True points the arrows from the top box DOWN to the children (use for has-a / uses).
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
    if not down:
        out.append(_at(total, [mid], ["^"]))
    out.append(_at(total, [mid], ["| " + label]))
    if len(children) > 1:
        line = [" "]*total
        _bus(line, sorted(set(centers + [mid])), dash)
        out.append("".join(line).rstrip())
        out.append(_at(total, centers, ["v" if down else "|"]*len(centers)))
    elif down:
        out.append(_at(total, [mid], ["v"]))
    return out + kids, mid


def above(top, below, col, label):
    """Put `top` centered on column `col` above an existing diagram, with a down arrow (has-a / uses)."""
    off = col - len(top[0]) // 2
    shift = max(0, -off)
    out = [" " * (off + shift) + l for l in top]
    out.append(_at(col + shift + 80, [col + shift], ["| " + label]))
    out.append(_at(col + shift + 80, [col + shift], ["v"]))
    return out + [" " * shift + l if l else l for l in below]


def _line(n, dash):
    """n chars of arrow shaft: solid '-----' (has-a / is-a) or dashed '- - -' (creates / uses = dependency)."""
    return "".join("-" if not dash or (n - 1 - k) % 2 == 0 else " " for k in range(n))


def _bus(row, joints, dash):
    """Draw a horizontal bus on `row` (a char list): '+' at each joint (except the first, which is the
    box edge when it is a '|'), and solid or dashed '- - -' between joints, each gap starting with '-'."""
    for a, b in zip(joints, joints[1:]):
        for k in range(a + 1, b):
            row[k] = "-" if not dash or (k - a - 1) % 2 == 0 else " "
    for j in joints:
        if row[j] != "|":
            row[j] = "+"


def side(a, b, label, ra=1, rb=1, minlen=6, dash=False):
    """Put diagram b to the RIGHT of diagram a, joined by a horizontal '----->' arrow (label above it)
    from the box edge on a's row `ra` to the box on b's row `rb` (row 1 = a box's title row).
    Prefer this over above() so diagrams grow sideways instead of downwards."""
    sa, sb = max(rb - ra, 0), max(ra - rb, 0)
    A, B = [""] * sa + list(a), [""] * sb + list(b)
    r = ra + sa
    lead = len(B[r]) - len(B[r].lstrip())
    start = len(A[r].rstrip())
    X = start + max(minlen, len(label) + 4) + 1 - lead                # column where b begins
    for i in range(min(len(A), len(B))):                              # no row may collide (2-space gap)
        if A[i].strip() and B[i].strip():
            X = max(X, len(A[i].rstrip()) + 3 - (len(B[i]) - len(B[i].lstrip())))
    X = max(X, 0)
    h = max(len(A), len(B))
    out = []
    for i in range(h):
        a_, b_ = (A[i] if i < len(A) else "").rstrip(), (B[i] if i < len(B) else "")
        lb = len(b_) - len(b_.lstrip())
        out.append((a_.ljust(X + lb) + b_.lstrip()).rstrip() if b_.strip() else a_)
    out[r] = A[r].rstrip() + _line(X + lead - 1 - start, dash) + ">" + B[r].lstrip()
    lab = list(out[r - 1].ljust(X + lead))
    assert all(c == " " for c in lab[start + 1:start + 2 + len(label)]), "no room for label"
    lab[start + 2:start + 2 + len(label)] = label
    out[r - 1] = "".join(lab).rstrip()
    return out


def fan(left, children, label, r=1, gap="  ", pad=4, dash=False):
    """Box on the LEFT; from its row r a bus line runs right and drops 'v' into each child
    (children = leaf()/tree() results). A sideways version of tree(down=True) for has-a."""
    ws = [max(len(l) for l in c[0]) for c in children]
    h = max(len(c[0]) for c in children)
    kids = [gap.join((c[0][i] if i < len(c[0]) else "").ljust(w) for c, w in zip(children, ws)).rstrip()
            for i in range(h)]
    centers, x = [], 0
    for (lines, c), w in zip(children, ws):
        centers.append(x + c)
        x += w + len(gap)
    wl = max(len(l) for l in left)
    S = wl + max(pad, len(label) + 4 - centers[0])        # column where the children begin
    rows = max(len(left), r + 2 + len(kids))
    out = []
    for i in range(rows):
        lp = left[i] if i < len(left) else ""
        k = i - (r + 2)
        kp = kids[k] if 0 <= k < len(kids) else ""
        out.append((lp.ljust(S) + kp).rstrip())
    start = len(left[r].rstrip())
    bus = list(left[r].ljust(S + centers[-1] + 1))
    _bus(bus, [start - 1] + [S + c for c in centers], dash)
    out[r] = "".join(bus)
    out[r + 1] = _at(S + x + 10, [S + c for c in centers], ["v"] * len(centers)) if r + 1 >= len(left) else \
        left[r + 1].ljust(S) + _at(x + 10, centers, ["v"] * len(centers))
    lab = list(out[r - 1].ljust(start + 3 + len(label)))
    lab[start + 2:start + 2 + len(label)] = label
    out[r - 1] = "".join(lab).rstrip()
    return out


def box_centers(line):
    """Centers of the boxes on a border line like '+----+  +------+' (same center rule as leaf())."""
    out, i = [], 0
    while i < len(line):
        if line[i] == "+" and i + 1 < len(line) and line[i + 1] == "-":
            j = line.index("+", i + 1)
            out.append(i + (j - i + 1) // 2)
            i = j + 1
        else:
            i += 1
    return out


def feed(left, diag, label, dash=True, r=1, pick=None, pad=6, gap=3):
    """Box (or side() diagram) on the LEFT, under `diag`; from its row r a bus runs right UNDER the
    bottom row of boxes of `diag` and points '^' up into them (all, or only indexes in `pick`).
    Use it for 'creates': Factory - - -> concrete products, while diag keeps the
    <<abstract>> parent above the products (tree())."""
    cols = box_centers(diag[-1])
    if pick is not None:
        cols = [cols[k] for k in pick]
    wl = max(len(l) for l in left)
    B = len(diag) + 1                                   # bus row
    top = B - r                                         # first row of the left box
    X = max(0, wl + pad - cols[0])
    for i in range(max(top, 0), len(diag)):             # rows where diag and left overlap
        li = i - top
        if 0 <= li < len(left) and diag[i].strip():
            X = max(X, len(left[li].rstrip()) + gap - (len(diag[i]) - len(diag[i].lstrip())))
    rows = max(len(diag) + 2, top + len(left))
    out = []
    for i in range(rows):
        li = i - top
        lp = (left[li] if 0 <= li < len(left) else "").rstrip()
        dp = diag[i] if i < len(diag) else ""
        if i == B - 1:
            dp = _at(cols[-1] + 2, cols, ["^"] * len(cols))
        if dp.strip():
            lead = len(dp) - len(dp.lstrip())
            lp = lp.ljust(X + lead) + dp.lstrip()
        out.append(lp.rstrip())
    start = len(left[r].rstrip())
    bus = list(out[B].ljust(X + cols[-1] + 1))
    _bus(bus, [start - 1] + [X + c for c in cols], dash)
    out[B] = "".join(bus)
    lab = list(out[B + 1].ljust(start + 3 + len(label))) if B + 1 < len(out) else list(" " * (start + 3 + len(label)))
    lab[start + 2:start + 2 + len(label)] = label
    if B + 1 < len(out):
        out[B + 1] = "".join(lab).rstrip()
    else:
        out.append("".join(lab).rstrip())
    return out


def connect_below(diag, links, dash=True):
    """Route arrows UNDER a diagram: links = [(src_col, dst_col, label)]. Each goes down from the box
    above src_col, along its own bus row, and up '^' into the box above dst_col (label sits on the bus).
    Inner (shorter) links get the higher rows, so nested pairs never cross.
    e.g. beside(Logistics tree, Transport tree) + RoadLogistics - - creates - -> Truck."""
    W = max(len(l) for l in diag) + 2
    g = [list(l.ljust(W)) for l in diag]
    H = len(g)
    links = sorted(links, key=lambda t: abs(t[1] - t[0]))
    g += [[" "] * W for _ in range(len(links) + 1)]
    bottom = lambda c: max(i for i in range(H) if g[i][c] != " ")
    for k, (s, d, label) in enumerate(links):
        R = H + 1 + k
        for c, head in ((s, False), (d, True)):
            b = bottom(c)
            for i in range(b + 1, R):
                g[i][c] = "|"
            if head:
                g[b + 1][c] = "^"
        lo, hi = min(s, d), max(s, d)
        _bus(g[R], [lo, hi], dash)
        g[R][lo] = g[R][hi] = "+"
        t = " " + label + " "
        m = (lo + hi - len(t)) // 2 + 1
        g[R][m:m + len(t)] = t
    return ["".join(r).rstrip() for r in g]


def factory_view(client, factory, diag, has="has-a", creates="creates (new)", uses="uses"):
    """Full creational picture, using the space well:
         Client - - uses - -> <<abstract>> Product        (client calls methods on Product*)
           | has-a                 ^ is-a
           v                 ConcreteA  ConcreteB ...
         Factory - - - creates - - -^ - - - - -^          (factory news the CONCRETE classes)
    `diag` is the product tree(); `client` may be None."""
    if client is None:
        return feed(factory, diag, creates)
    cc = len(client[0]) // 2
    off = cc - len(factory[0]) // 2
    sc, sf = max(0, -off), max(0, off)
    k = len(diag) - len(client)                    # rows of the has-a arrow, so Factory's title = bus row
    assert k >= 2, "client box too tall for this product tree"
    L = [" " * sc + l for l in client]
    L += [_at(cc + sc + 10, [cc + sc], ["| " + has])] + [_at(cc + sc + 2, [cc + sc], ["|"])] * (k - 2) +          [_at(cc + sc + 2, [cc + sc], ["v"])]
    L += [" " * sf + l for l in factory]
    out = feed(L, diag, creates, r=len(client) + k + 1, gap=len(uses) + 8)
    # the 'uses' arrow: client title row (1) -> product parent box (row 1 of diag)
    row = out[1]
    a = len(L[1].rstrip())
    b = row.index("|", a)
    out[1] = row[:a] + _line(b - 1 - a, True) + ">" + row[b:]
    lab = list(out[0].ljust(a + 3 + len(uses)))
    lab[a + 2:a + 2 + len(uses)] = uses
    out[0] = "".join(lab).rstrip()
    return out


def beside(a, b, gap="        "):
    """Place two diagrams side by side."""
    wa = max(len(l) for l in a)
    h = max(len(a), len(b))
    return [((a[i] if i < len(a) else "").ljust(wa) + gap + (b[i] if i < len(b) else "")).rstrip()
            for i in range(h)]


def multi(parents, child, label, gap="    "):
    """Multiple inheritance: several parent boxes side by side, one child box below pointing up to all of them."""
    ws = [len(p[0]) for p in parents]
    centers, x = [], 0
    for w in ws:
        centers.append(x + w // 2)
        x += w + len(gap)
    h = max(len(p) for p in parents)
    out = [gap.join((p[i] if i < len(p) else "").ljust(w) for p, w in zip(parents, ws)).rstrip() for i in range(h)]
    total = x + 200
    mid = (centers[0] + centers[-1]) // 2
    out.append(_at(total, centers, ["^"] * len(centers)))
    out.append(_at(total, centers, ["|"] * len(centers)))
    line = [" "] * total
    for c in range(centers[0], centers[-1] + 1):
        line[c] = "-"
    for c in centers + [mid]:
        line[c] = "+"
    out.append("".join(line).rstrip())
    out.append(_at(total, [mid], ["| " + label]))
    off = mid - len(child[0]) // 2
    return out + [" " * off + l for l in child]


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
