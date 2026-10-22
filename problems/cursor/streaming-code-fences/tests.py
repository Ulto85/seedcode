import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "FenceParser", [], ops, **kw)


def feeds(chunks, finish=True):
    ops = [["feed", [c]] for c in chunks]
    return ops + ([["finish", []]] if finish else [])


def split_random(rng, text, max_len):
    out, i = [], 0
    while i < len(text):
        k = rng.randint(1, max_len)
        out.append(text[i:i + k])
        i += k
    return out


PROSE = ["Here's the fix:", "", "Run it with `python main.py`.", "  indented text", "Done!", "`` not a fence",
         "use ``` inline", "x = 1"]
CODE = ["def f(x):", "    return x + 1", "", "print(f(2))", "  ```", "```python", "``", "# comment", "~~~"]


def rand_doc(rng, blocks, tildes):
    lines = []
    for _ in range(blocks):
        lines += [rng.choice(PROSE) for _ in range(rng.randint(0, 3))]
        if tildes and rng.random() < 0.4:
            ch = "~"
        else:
            ch = "`"
        k = rng.choice([3, 3, 3, 4, 5])
        lang = rng.choice(["", "python", "ts", " js extra", "go "])
        lines.append(ch * k + lang)
        body = [l for l in CODE if tildes or not l.startswith("~")]
        lines += [rng.choice(body) for _ in range(rng.randint(0, 4))]
        if rng.random() < 0.85:
            lines.append(ch * rng.choice([k, k, k + 1]) + rng.choice(["", "", "  "]))
    if tildes:
        lines.append(rng.choice(["```js`", "~~~~ shell", "Done!"]))
    text = "\n".join(lines)
    return text + ("\n" if rng.random() < 0.7 else "")


EXAMPLE = ["Here is the fix:\n``", "`py", "thon\ndef add(a, b):\n    return a + b\n", "``", "`\nDone", "!"]


def tests():
    rng = random.Random(11)
    t = [
        C("Example", feeds(EXAMPLE)),
        C("Plain text only", feeds(["hello\nwor", "ld\n"])),
        C("Empty stream", feeds([])),
        C("Empty chunks", feeds(["", "a", "", "\n", ""])),
        C("Blank lines are text and code", feeds(["\n\n```\n\n```\n"])),
        C("Fence split one char at a time", feeds(list("```go\nx := 1\n```\n"))),
        C("Language is the first word of the info string", feeds(["```  rust  edition=2021 \nfn main() {}\n```\n"])),
        C("Indented or shorter backticks are not fences", feeds(["  ```\n``\n```\n  ```\n```python\n``\n```\n"])),
        C("Longer closing fence closes, closing fence can't have info", feeds(["````md\n```\n```js\n`````\nafter\n"])),
        C("Closing fence with trailing spaces", feeds(["```\ncode\n```   \ntext\n"])),
        C("Unterminated block closed by finish", feeds(["```sh\necho hi\nls"])),
        C("Last line without newline", feeds(["a\n```\nb\n```"])),
        C("Tilde fences", feeds(["~~~py\nx = 1\n~~~\nafter\n"]), tag="Follow-up"),
        C("Closing char must match", feeds(["~~~\n```\nstill code\n~~~~\n```\nin backticks\n~~~\n```\n"]), tag="Follow-up"),
        C("Backtick info string can't contain a backtick", feeds(["```js`\n~~~ a`b\nx\n~~~\n"]), tag="Follow-up"),
    ]
    for i in range(3):
        doc = rand_doc(rng, 4, False)
        t.append(C(f"Random chunking #{i + 1}", feeds(split_random(rng, doc, 7)), hidden=True))
    for i in range(3):
        doc = rand_doc(rng, 4, True)
        t.append(C(f"Random chunking with tildes #{i + 1}", feeds(split_random(rng, doc, 7)), tag="Follow-up", hidden=True))
    doc = rand_doc(random.Random(99), 3000, False)
    t.append(C("Long response in 30,000 tiny chunks", feeds(split_random(random.Random(5), doc, 7)[:30000]), hidden=True))
    long_line = "```\n" + "x" * 300000 + "\n```\n"
    t.append(C("300,000-char line streamed in 3-char chunks",
               feeds([long_line[i:i + 3] for i in range(0, len(long_line), 3)]), hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    doc = rand_doc(rng, n, True)
    return C(f"{n} blocks", feeds(split_random(rng, doc, 8)))


SCALE = {"sizes": [100, 200, 400, 800, 1600, 3200, 6400], "label": "n = code blocks in the stream"}
