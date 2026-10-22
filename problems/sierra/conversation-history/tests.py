import random
from engine.spec import cls


def C(name, limit, ops, **kw):
    return cls(name, "ConversationHistory", [limit], ops, **kw)


def add(i, role, tok): return ["add", [i, role, tok]]
CTX = ["context", []]
TOT = ["total_tokens", []]


def random_ops(rng, n, limit, roles, max_tok, ctx_rate=0.05):
    ops, k = [], 0
    weights = {"user": 4, "assistant": 4, "system": 1, "tool": 3}
    pool = [r for r in roles for _ in range(weights[r])]
    for _ in range(n):
        r = rng.random()
        if r < ctx_rate:
            ops.append(CTX)
        elif r < ctx_rate + 0.1:
            ops.append(TOT)
        else:
            role = rng.choice(pool)
            tok = rng.randint(1, max_tok // 4 if role == "system" else max_tok)
            ops.append(add(f"m{k}", role, tok))
            k += 1
    ops.append(CTX)
    ops.append(TOT)
    return ops


def tests():
    rng = random.Random(23)
    t = [
        C("Example", 10, [add("u1", "user", 4), add("a1", "assistant", 3), add("u2", "user", 5), CTX,
                          add("big", "user", 11), CTX, add("u3", "user", 10), CTX, TOT]),
        C("Empty history", 5, [CTX, TOT]),
        C("Exactly at the limit", 6, [add("a", "user", 3), add("b", "assistant", 3), CTX, TOT, add("c", "user", 1), CTX]),
        C("One message equal to the limit", 4, [add("a", "user", 1), add("b", "user", 4), CTX, add("c", "user", 5), CTX, TOT]),
        C("Drop several at once", 10, [add("a", "user", 2), add("b", "assistant", 2), add("c", "user", 2), add("d", "assistant", 3), add("e", "user", 8), CTX, TOT]),
        C("Rejected message changes nothing", 5, [add("a", "user", 3), add("x", "assistant", 6), CTX, TOT, add("b", "user", 2), CTX]),
        C("Part 2 example", 10, [add("s1", "system", 3), add("u1", "user", 4), add("a1", "assistant", 4), CTX,
                                 add("u2", "user", 8), add("s2", "system", 2), CTX, TOT], tag="Part 2"),
        C("System message drops others", 10, [add("u1", "user", 4), add("a1", "assistant", 4), add("s1", "system", 5), CTX, TOT], tag="Part 2"),
        C("System messages fill the limit", 6, [add("s1", "system", 4), add("s2", "system", 3), add("s3", "system", 2), add("u1", "user", 2), add("u2", "user", 3), CTX, TOT], tag="Part 2"),
        C("System stays in insertion order", 9, [add("u1", "user", 3), add("s1", "system", 1), add("u2", "user", 3), add("u3", "user", 3), CTX, add("u4", "user", 5), CTX], tag="Part 2"),
        C("Follow-up example", 12, [add("u1", "user", 2), add("a1", "assistant", 3), add("t1", "tool", 4), add("u2", "user", 4),
                                    add("a2", "assistant", 2), CTX, TOT], tag="Follow-up"),
        C("Tool with no unit starts its own", 5, [add("t0", "tool", 2), add("t1", "tool", 2), CTX, add("u1", "user", 3), CTX, TOT], tag="Follow-up"),
        C("Tool rejected when its unit would overflow", 10, [add("s", "system", 2), add("a1", "assistant", 4), add("t1", "tool", 4), add("t2", "tool", 1), CTX, TOT], tag="Follow-up"),
        C("Tool joins newest unit across a system message", 10, [add("a1", "assistant", 3), add("s1", "system", 2), add("t1", "tool", 2), add("u1", "user", 3), add("u2", "user", 2), CTX, TOT], tag="Follow-up"),
        C("Tool after its unit was dropped", 8, [add("a1", "assistant", 3), add("s1", "system", 6), add("t1", "tool", 2), CTX, add("u1", "user", 1), CTX], tag="Follow-up"),
    ]
    for s in range(2):
        t.append(C(f"Random user/assistant #{s + 1}", 30, random_ops(rng, 60, 30, ["user", "assistant"], 12, 0.15), hidden=True))
        t.append(C(f"Random with system #{s + 1}", 30, random_ops(rng, 60, 30, ["user", "assistant", "system"], 12, 0.15), tag="Part 2", hidden=True))
        t.append(C(f"Random with tools #{s + 1}", 30, random_ops(rng, 80, 30, ["user", "assistant", "system", "tool"], 10, 0.15), tag="Follow-up", hidden=True))
    t.append(C("200k messages, long history", 400_000, random_ops(rng, 200000, 0, ["user", "assistant"], 40, 0.00003), hidden=True))
    t.append(C("100k messages with tools", 200_000, random_ops(rng, 100000, 0, ["user", "assistant", "tool"], 40, 0.00003), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} adds", n * 5, random_ops(random.Random(n), n, 0, ["user", "assistant"], 40, 0.0))


SCALE = {"sizes": [6250, 12500, 25000, 50000, 100000, 200000], "label": "n = number of add calls"}
