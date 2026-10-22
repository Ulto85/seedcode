import random
from engine.spec import cls

C = "TaskManager"


def T(name, ops, **kw):
    return cls(name, C, [], ops, **kw)


def add(*tasks):
    return ["add_tasks", [[list(t) for t in tasks]]]


POP = ["consume_task", []]


def random_ops(rng, n_tasks, deps=True, batch=8, max_prereqs=3, ddl=50):
    """Tasks get ids 0..n-1 in a shuffled order; prereqs point at random other ids
    (sometimes ones added later) but always at a lower id, so the graph is acyclic."""
    ids = list(range(n_tasks))
    rng.shuffle(ids)
    ops, i = [], 0
    while i < len(ids):
        k = rng.randint(1, batch)
        chunk = []
        for tid in ids[i:i + k]:
            pre = []
            if deps and tid > 0:
                for _ in range(rng.randint(0, max_prereqs)):
                    pre.append(rng.randint(max(0, tid - 40), tid - 1))
            chunk.append([tid, rng.randint(-ddl, ddl), pre])
        ops.append(["add_tasks", [chunk]])
        i += k
        for _ in range(rng.randint(0, k + 1)):
            ops.append(POP)
    for _ in range(n_tasks // 4 + 2):
        ops.append(POP)
    return ops


def tests():
    rng = random.Random(7)
    t = [
        T("Example (Part 1)", [add((101, 5, []), (102, 2, []), (103, 8, [])), POP,
                               add((104, 2, []), (99, 5, [])), POP, POP, POP, POP, POP]),
        T("Empty manager", [POP, POP]),
        T("Tie on deadline -> smaller id", [add((7, 3, []), (2, 3, []), (5, 3, [])), POP, POP, POP]),
        T("Negative deadlines", [add((1, 0, []), (2, -5, []), (3, -1000000000, [])), POP, POP, POP]),
        T("Add after running dry", [add((1, 1, [])), POP, POP, add((2, 4, []), (3, 4, [])), POP, POP, POP]),
        T("Single add_tasks call, many tasks", [add(*[(i, (i * 7) % 5, []) for i in range(10)])] + [POP] * 11),
        T("Example (Follow-up)", [add((1, 9, []), (2, 1, [1]), (3, 4, [])), POP, POP, POP,
                                  add((5, 0, [4])), POP, add((4, 7, [1])), POP, POP], tag="Follow-up"),
        T("Blocked tasks only -> None", [add((2, 1, [1])), POP, add((1, 5, [])), POP, POP, POP], tag="Follow-up"),
        T("Diamond dependencies", [add((1, 10, []), (2, 3, [1]), (3, 1, [1]), (4, 0, [2, 3])), POP, POP, POP, POP, POP],
          tag="Follow-up"),
        T("Duplicate prereq ids count once", [add((1, 5, []), (2, 0, [1, 1, 1])), POP, POP, POP], tag="Follow-up"),
        T("Prereq already consumed", [add((1, 5, [])), POP, add((2, 0, [1]), (3, 1, [])), POP, POP], tag="Follow-up"),
        T("Unlocked task competes by deadline", [add((1, 0, []), (2, 9, []), (3, 5, [1]), (4, 6, [])), POP, POP, POP, POP],
          tag="Follow-up"),
    ]
    for s in range(3):
        t.append(T(f"Random no deps #{s + 1}", random_ops(rng, 30, deps=False), hidden=True))
    for s in range(3):
        t.append(T(f"Random with deps #{s + 1}", random_ops(rng, 30), tag="Follow-up", hidden=True))
    t.append(T("100k tasks, no deps", random_ops(rng, 100000, deps=False, batch=50, ddl=10**9), hidden=True))
    t.append(T("60k tasks with deps", random_ops(rng, 60000, batch=50, ddl=10**6), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return T(f"{n} tasks", random_ops(random.Random(n), n, batch=20, ddl=10**6), tag="Follow-up")


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of tasks"}
