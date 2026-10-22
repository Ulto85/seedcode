import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "TaskManager", [], ops, **kw)


def add(t): return ["add_task", [t]]
def dep(t, d): return ["add_dependency", [t, d]]
def fail(t): return ["fail_task", [t]]
def st(t): return ["get_status", [t]]
def done(t): return ["complete_task", [t]]
def ready(): return ["get_ready", []]


def random_ops(rng, n, k, follow_up):
    names = [f"t{i}" for i in range(k)]
    ops = []
    for _ in range(n):
        r = rng.random()
        if r < 0.15:
            ops.append(add(rng.choice(names)))
        elif r < 0.5:
            a, b = rng.choice(names), rng.choice(names)
            ops.append(dep(a, b))
        elif r < 0.58:
            ops.append(fail(rng.choice(names)))
        elif follow_up and r < 0.75:
            ops.append(done(rng.choice(names)))
        elif follow_up and r < 0.8:
            ops.append(ready())
        else:
            ops.append(st(rng.choice(names + ["ghost"])))
    return ops


def long_chain(n):
    """c1 depends on c0, c2 on c1, ... then fail from the far end backwards (naive re-walks are O(n^2))."""
    ops = [dep(f"c{i}", f"c{i - 1}") for i in range(1, n)]
    step = max(1, n // 2000)
    for i in range(n - 1, -1, -step):
        ops.append(fail(f"c{i}"))
    ops.append(fail("c0"))
    ops += [st(f"c{i}") for i in range(0, n, max(1, n // 50))]
    return ops


def layered_dag(layers, width):
    """Every node depends on every node in the previous layer: exponentially many paths."""
    ops = []
    for L in range(1, layers):
        for a in range(width):
            for b in range(width):
                ops.append(dep(f"L{L}_{a}", f"L{L - 1}_{b}"))
    ops.append(fail("L0_0"))
    ops += [st(f"L{layers - 1}_{a}") for a in range(width)]
    return ops


def tests():
    rng = random.Random(2025)
    t = [
        C("Example", [dep("B", "A"), dep("C", "B"), dep("D", "B"), dep("D", "C"), add("E"), fail("A"),
                      st("A"), st("B"), st("C"), st("D"), st("E"), dep("F", "C"), st("F"), st("Z")]),
        C("Unknown and new tasks", [st("x"), add("x"), st("x"), add("x"), st("x")]),
        C("Fail creates the task", [fail("solo"), st("solo"), dep("kid", "solo"), st("kid")]),
        C("Duplicate edges and repeat fails", [dep("B", "A"), dep("B", "A"), fail("A"), fail("A"), fail("B"), st("A"), st("B")]),
        C("Failure only flows to dependents", [dep("B", "A"), dep("C", "B"), fail("B"), st("A"), st("B"), st("C")]),
        C("Cycle", [dep("A", "B"), dep("B", "C"), dep("C", "A"), dep("D", "C"), add("E"), fail("B"),
                    st("A"), st("B"), st("C"), st("D"), st("E")]),
        C("Self-dependency", [dep("A", "A"), st("A"), fail("A"), st("A")]),
        C("Dependency added after failure", [fail("X"), add("Y"), dep("Z", "Y"), dep("Y", "X"), st("Y"), st("Z")]),
        C("Follow-up example", [dep("B", "A"), ready(), done("B"), done("A"), ready(), fail("A"), st("A"), st("B")], tag="Follow-up"),
        C("Complete unknown / failed / twice", [done("ghost"), fail("F"), done("F"), add("G"), done("G"), done("G"), st("G"), st("ghost")], tag="Follow-up"),
        C("Ready list is sorted, cycles never ready", [add("m"), add("b"), dep("z", "a"), dep("c1", "c2"), dep("c2", "c1"),
                                                       ready(), done("a"), ready(), done("c1"), ready()], tag="Follow-up"),
        C("Cascade stops at done tasks", [dep("B", "A"), dep("C", "B"), done("A"), done("B"), dep("B", "X"), dep("C2", "B"),
                                          fail("X"), st("B"), st("C"), st("C2"), fail("A"), st("A"), ready()], tag="Follow-up"),
        C("Failed tasks leave the ready list", [add("p"), add("q"), dep("r", "p"), ready(), fail("p"), ready(), st("r"), done("q"), ready()], tag="Follow-up"),
        C("Diamond completes in order", [dep("B", "A"), dep("C", "A"), dep("D", "B"), dep("D", "C"), done("A"), ready(),
                                          done("B"), ready(), done("D"), done("C"), ready(), done("D"), ready()], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random ops #{s + 1}", random_ops(rng, 80, 12, False), hidden=True))
    for s in range(3):
        t.append(C(f"Random follow-up ops #{s + 1}", random_ops(rng, 120, 15, True), tag="Follow-up", hidden=True))
    t.append(C("Chain of 60k tasks, failed from the end", long_chain(60000), hidden=True))
    t.append(C("Layered DAG with exponentially many paths", layered_dag(40, 12), hidden=True))
    t.append(C("Random follow-up ops (30k)", random_ops(rng, 30000, 3000, True), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"chain of {n}", long_chain(n))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = length of the dependency chain"}
