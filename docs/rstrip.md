# Python notes for Java / C / JavaScript developers

Running notes explaining Python constructs used in
`exercises/transform_file/loan_prices_US_MDLOAN00002.py` for a developer coming from Java, C
and JavaScript.

---

## Q1 &mdash; `lines = [ln.rstrip("\r\n") for ln in fh if ln.strip()]`

### Context

```python
with fichero_in.open("r", encoding="utf-8", errors="replace") as fh:
    lines = [ln.rstrip("\r\n") for ln in fh if ln.strip()]
```

`fh` is a file handle. The whole right-hand side is a single Python
expression called a **list comprehension** that reads the file line by
line, filters out blanks, strips line endings, and stores the result in
a list.

### Anatomy

The general shape of a list comprehension is:

```
[ <expression>  for <element> in <iterable>  if <condition> ]
```

Mapping it to our line:

| Piece               | Role                                             | Value here              |
| ------------------- | ------------------------------------------------ | ----------------------- |
| `ln.rstrip("\r\n")` | Expression evaluated for every kept element      | Strip trailing CR/LF    |
| `for ln in fh`      | Loop binding `ln` to each iterated value         | One file line at a time |
| `if ln.strip()`     | Filter: keep element only if condition is truthy | Discard blank lines     |

The `if` clause is optional. If you omit it, every iterated element is
kept.

### Java / C / JS equivalents

**Java (verbose, pre-streams):**

```java
List<String> lines = new ArrayList<>();
try (BufferedReader fh = Files.newBufferedReader(path)) {
    String ln;
    while ((ln = fh.readLine()) != null) {
        if (!ln.trim().isEmpty()) {
            lines.add(ln.replaceAll("[\\r\\n]+$", ""));
        }
    }
}
```

**Java 8+ streams:**

```java
List<String> lines;
try (Stream<String> s = Files.lines(path)) {
    lines = s
        .filter(ln -> !ln.trim().isEmpty())   // if ln.strip()
        .map(ln -> ln.replaceAll("[\\r\\n]+$", ""))  // ln.rstrip("\r\n")
        .collect(Collectors.toList());
}
```

**JavaScript:**

```javascript
const lines = fs
  .readFileSync(path, 'utf8')
  .split('\n')
  .filter((ln) => ln.trim() !== '')
  .map((ln) => ln.replace(/[\r\n]+$/, ''));
```

**C (closest mental model):**

```c
char buf[BUFSIZ];
while (fgets(buf, sizeof buf, fh)) {
    if (is_blank(buf)) continue;        // if ln.strip()
    rstrip_crlf(buf);                   // ln.rstrip("\r\n")
    push_back(lines, buf);
}
```

In Python the **whole loop + filter + transform + collect** is one
expression. There is no explicit `add()` / `push_back()`; the brackets
`[ ... ]` say "collect everything into a list".

### Why this works at all &mdash; iteration over a file

In Java you usually call `readLine()` in a loop. In Python a file object
is **already an iterator over its own lines**. Each `for ln in fh` step
calls `fh.__next__()` under the hood, which reads up to and including
the next `\n`. So:

- `ln` is a `str` that **still contains** the trailing newline (and
  possibly a carriage return on Windows files): `"LX238555;...\n"`.
- You do not have to call any "readLine" method explicitly.
- Memory usage stays low &mdash; the file is read lazily, one line at a
  time, even though the comprehension produces a list at the end.

This is the same idea as `Files.lines(path)` in Java 8+ or
`readline()`-based generators in Node.

### Why `if ln.strip()`?

`str.strip()` returns a copy of the string with **leading and trailing
whitespace removed** (spaces, tabs, `\r`, `\n`, etc.). It returns the
empty string `""` if the original was only whitespace.

Now here is the **Pythonic truthiness rule**:

| Value                                   | Boolean context |
| --------------------------------------- | --------------- |
| `""` (empty string)                     | `False`         |
| `"anything"` (non-empty)                | `True`          |
| `0`, `0.0`, `None`, `[]`, `{}`, `set()` | `False`         |
| Everything else                         | `True`          |

So `if ln.strip()` is **idiomatic Python for "if the line has any
non-whitespace content"**. It is the equivalent of Java's
`!ln.trim().isEmpty()` or JS's `ln.trim() !== ""`.

Important: `ln.strip()` here is only used as a **boolean check**. We do
not assign its result to anything. The variable `ln` is still the
original raw line with its `\n` intact. That is why the next step uses
`rstrip` on `ln`, not on the stripped value.

### Why `rstrip("\r\n")` and not `strip()` or `rstrip()`?

Three different "strip" methods:

| Method        | What it removes                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------- |
| `s.strip()`   | Whitespace at **both** ends (default).                                                                   |
| `s.rstrip()`  | Whitespace at **right** end only.                                                                        |
| `s.rstrip(X)` | Any character **listed in `X`** at the right end. Not a regex, not a suffix &mdash; a **character set**. |

`ln.rstrip("\r\n")` removes any combination of `\r` and `\n` characters
from the right end. So:

- `"abc\r\n"` &rarr; `"abc"`
- `"abc\n"` &rarr; `"abc"`
- `"abc"` &rarr; `"abc"` (no change)
- `"abc\n\n"` &rarr; `"abc"` (all trailing newlines removed)
- `"a\nb\n"` &rarr; `"a\nb"` (only the trailing one; the embedded `\n` survives)

We do NOT use `.strip()` because that would also remove leading spaces,
and we want to preserve column values exactly &mdash; the CSV may use
spaces meaningfully.

We do NOT use `.rstrip()` without arguments because that would strip
**all whitespace** at the right (including spaces and tabs), which
again could damage the last column value (e.g. a trailing space inside
a quoted field).

By passing `"\r\n"` we guarantee that only the line terminator is
removed, nothing else.

### Equivalent expanded loop

The list comprehension is purely syntactic sugar. The verbose Python
form is:

```python
lines = []
for ln in fh:
    if ln.strip():               # filter
        lines.append(ln.rstrip("\r\n"))   # transform + collect
```

Both produce the **same list**. The comprehension form is preferred in
Python because:

1. It is shorter.
2. It signals intent ("I am building a list by mapping/filtering").
3. The interpreter can run it slightly faster &mdash; the `LIST_APPEND`
   bytecode is more efficient than a manual `list.append()` call.

### Common variants you will see

```python
# Map only (no filter)
[ x * 2 for x in nums ]

# Filter only (identity transform)
[ x for x in nums if x > 0 ]

# Multiple for/if clauses
[ (i, j) for i in range(3) for j in range(3) if i != j ]

# Generator expression (lazy, no list built):
sum(x * x for x in nums)

# Set comprehension
{ x.lower() for x in names }

# Dict comprehension
{ k: v for k, v in pairs if v is not None }
```

### Pitfalls to remember as a Java / C / JS dev

1. **No need for `readLine`** &mdash; iterating a file gives you lines.
   You can also do `fh.readlines()` to read everything at once, but
   that loads the full file into memory; the comprehension form above
   is incremental.
2. **`ln` still has the `\n`** when you iterate a file in Python.
   Always `rstrip` if you care about the value as data.
3. **`strip(chars)` is a character set**, not a substring. So
   `"abXX".rstrip("X")` &rarr; `"ab"`, but
   `"abXX".rstrip("XX")` &rarr; `"ab"` too (same as above, because `XX`
   is just the set `{X}`). To remove a literal suffix, use
   `removesuffix("XX")` (Python 3.9+) or slicing.
4. **The `if` clause is filtering, not assignment** &mdash; Python
   list comprehensions do not have a way to bind a new name inside
   them without the walrus operator `:=` (3.8+). For complex logic,
   fall back to a normal `for` loop.
5. **List comprehensions allocate a list eagerly.** For large files
   prefer a generator expression `(...)` or process the file
   line-by-line in a normal loop &mdash; otherwise memory use scales
   with the file size.

### One-line takeaway

> "For every line in the file, keep it only if it is not blank, strip
> off any trailing CR/LF, and collect all the survivors into a list."

---

## Q2 &mdash; `return [header.index(name) for name in wanted]`

### Context

```python
def resolve_indexes(header: Sequence[str], wanted: Sequence[str]) -> List[int]:
    """Devuelve los indices (0-based) de cada columna pedida en la cabecera."""
    return [header.index(name) for name in wanted]
```

`header` is the list of column names read from the CSV header line
(e.g. `["LX", "FCN", "OAS", "Bid", "Offer"]`). `wanted` is the list of
column names the caller asked for (e.g. `["LX", "OAS"]`). The function
returns a list of **positions** of those wanted columns inside the
header, in the same order. For the example above it returns `[0, 2]`.

That list of positions is later used to extract the right cells from
every data row.

### Anatomy

Same list-comprehension shape as Q1, but **without filter** (no `if`
clause):

```
[ <expression>  for <element> in <iterable> ]
```

| Piece                | Role                            | Value here                                 |
| -------------------- | ------------------------------- | ------------------------------------------ |
| `header.index(name)` | Expression run for each element | Look up the position of `name` in `header` |
| `for name in wanted` | Loop binding                    | One wanted column name at a time           |

### What `list.index(value)` does

`list.index(x)` is a **built-in method on any Python list** (and more
generally any `Sequence`). It returns the **0-based position of the
first occurrence** of `x` in the list. If `x` is not present it raises
`ValueError`.

Java / C / JS equivalents:

| Language   | Equivalent                                                          |
| ---------- | ------------------------------------------------------------------- |
| Java       | `list.indexOf(x)` (but returns `-1` if missing, does **not** throw) |
| JavaScript | `arr.indexOf(x)` (also `-1` if missing)                             |
| C          | manual `for` loop with `strcmp`                                     |

The behavioural difference matters: Python **throws** when the column
is missing. That throw is caught one level up:

```python
try:
    indexes = resolve_indexes(header, campos)
except ValueError as exc:
    raise ValueError(f"columna no encontrada en la cabecera: {exc}") from exc
```

So if you ask for `"OAS"` and the header only has `"LX"` and `"FCN"`,
the script aborts loudly instead of silently producing `-1` like in
Java. That is intentional &mdash; better than writing a corrupted
output file.

### Java equivalent (one-to-one)

```java
List<Integer> indexes = new ArrayList<>();
for (String name : wanted) {
    int idx = header.indexOf(name);
    if (idx < 0) throw new IllegalArgumentException("column not found: " + name);
    indexes.add(idx);
}
return indexes;
```

…or with streams:

```java
return wanted.stream()
    .map(name -> {
        int idx = header.indexOf(name);
        if (idx < 0) throw new IllegalArgumentException("column not found: " + name);
        return idx;
    })
    .collect(Collectors.toList());
```

The Python version is one line because (a) the comprehension replaces
the loop + collector, and (b) `index()` already throws on miss.

### Why a list of indexes instead of a dictionary?

Could just as well be a dict `{name: pos}`. But downstream we need to
preserve the **order** in which the user asked for columns, because
the output line concatenates values in that same order. A list keeps
order trivially; with a dict we would have to iterate it carefully.
This is why the comprehension produces `List[int]` and not
`Dict[str, int]`.

### Complexity note

`list.index(x)` is **O(n)** &mdash; it scans the list linearly. So the
comprehension is O(len(wanted) \* len(header)). For our headers
(~20 columns) and `wanted` lists (~5) that is negligible. If the
header had thousands of columns and `wanted` was huge, you would build
an index map first:

```python
pos = {name: i for i, name in enumerate(header)}
return [pos[name] for name in wanted]   # each lookup is O(1)
```

But for this script the simple version is clearer and fast enough.

### One-line takeaway

> "For every column name the caller wants, find its position in the
> header, and return all positions in a list (raising if any name is
> missing)."

---

## Q3 &mdash; The `str.join()` method

### Context

```python
cabecera_out = SEP_COL_OUT.join(campos) + SEP_COL_OUT
...
rows.append(SEP_COL_OUT.join(quoted) + SEP_COL_OUT)
```

Where `SEP_COL_OUT = "#"`. So `SEP_COL_OUT.join(campos)` is really
just `"#".join(campos)`. The thing we want to understand is the
**`.join()` call itself**.

### Yes, it is a method

`.join()` is a **method defined on the built-in `str` class**. Every
string object in Python has it &mdash; the `str` class is roughly
Java's `String` class, and `join` is one of its instance methods. Its
full qualified name is `str.join`.

Signature (from the docs):

```python
str.join(iterable)  ->  str
```

- **Receiver** (the `self` / `this` in OO terms): the string used as
  the separator.
- **Argument**: any iterable that yields strings (`list`, `tuple`,
  generator, set, etc.).
- **Return value**: a brand new string with all the items concatenated,
  separated by the receiver.

So the call:

```python
"#".join(["LX", "FCN", "OAS"])
```

reads as: "take the string `#`, and use it to glue together the items
`LX`, `FCN`, `OAS`". Result: `"LX#FCN#OAS"`.

### Why the receiver is the separator (and not the list)

This is the part that feels backwards to Java / JS developers:

| Language   | Idiom                     | Receiver      |
| ---------- | ------------------------- | ------------- |
| Python     | `"#".join(items)`         | the separator |
| Java       | `String.join("#", items)` | static method |
| JavaScript | `items.join("#")`         | the array     |

The reason is design symmetry. In Python, **the separator decides how
to glue**, and the items only need to be _iterable_ and _string-like_.
Any iterable can be passed in &mdash; lists, tuples, generators, sets,
even file objects &mdash; without `join` needing to know about each
container type. If `join` were a method on `list`, every other
iterable type would need its own copy of it. Putting it on `str`
keeps the language smaller.

### Step by step: how it works under the hood

Conceptually, `"#".join(["LX", "FCN", "OAS"])` is equivalent to:

```python
def join(sep, items):
    items = list(items)            # consume the iterable
    if not items:
        return ""
    out = items[0]
    for x in items[1:]:
        out = out + sep + x
    return out
```

So for `["LX", "FCN", "OAS"]` and separator `"#"` you get
`"LX" + "#" + "FCN" + "#" + "OAS"` = `"LX#FCN#OAS"`. CPython actually
does it much more efficiently than that &mdash; in **one C-level pass**
that pre-computes the final length and allocates the output string
once, instead of repeatedly concatenating (which would be O(n^2)).
That is why `str.join` is the recommended way to build big strings in
Python rather than `+=` in a loop.

### What it accepts as input

The argument must be an **iterable of strings**. Lists are the
common case but anything that iterates works:

```python
",".join(["a", "b", "c"])              # list   -> "a,b,c"
",".join(("a", "b", "c"))              # tuple  -> "a,b,c"
",".join({"a", "b", "c"})              # set    -> "a,b,c" (order not guaranteed)
",".join(x.upper() for x in names)     # generator
",".join(open("file.txt"))             # file -> each line is an item
```

### What it does NOT do: auto-stringify

`str.join` requires every item to be **already** a string. It does
not call `str()` on them implicitly:

```python
",".join([1, 2, 3])
# TypeError: sequence item 0: expected str instance, int found
```

Workarounds:

```python
",".join(str(x) for x in [1, 2, 3])    # "1,2,3"
",".join(map(str, [1, 2, 3]))          # "1,2,3"
```

This is intentional &mdash; Python tries to avoid silent type
coercions. Java's `String.join` does the same: it expects
`CharSequence` items.

### Edge cases worth knowing

```python
",".join([])           # -> ""           empty iterable -> empty string
",".join(["only"])     # -> "only"       one item -> no separator added
",".join(["a", ""])    # -> "a,"         empty strings count as items
"".join(["a", "b"])    # -> "ab"         empty separator -> plain concat
```

Last one is a common idiom for **flattening a list of strings without
any separator**.

### Why `.join()` and not the `+` operator?

Both produce the same string, but performance and clarity differ.

```python
# Bad: O(n^2), every += allocates a new string
out = ""
for x in items:
    out += sep + x

# Good: O(n), one allocation in C
out = sep.join(items)
```

For 3 items it does not matter. For 10 000 items the `+=` version is
hundreds of times slower because strings in Python are **immutable**
&mdash; every concatenation produces a new object. `join` knows the
final length up front and reserves the buffer once.

This is the Python equivalent of using `StringBuilder` in Java instead
of `+=` on `String`.

### Mapping back to the script

```python
cabecera_out = SEP_COL_OUT.join(campos) + SEP_COL_OUT
#              "#".join(["LX", "FCN", "OAS"])  + "#"
#              "LX#FCN#OAS"                    + "#"
#              "LX#FCN#OAS#"
```

`join` only places the separator **between** items. The format needs
a trailing `#` after the last column too, so we append `+ SEP_COL_OUT`
explicitly. Same pattern with `SEP_REG_OUT` for records.

### One-line takeaway

> "`str.join(iterable)` is an instance method on every Python string:
> the string itself is the separator, the argument is any iterable of
> strings, and it returns a single new string with all the items glued
> together in one efficient C-level pass."
