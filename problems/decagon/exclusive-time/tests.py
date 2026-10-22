import random
from engine.spec import fn


def random_logs(rng, n, steps):
    logs, stack, t = [], [], 0
    for _ in range(steps):
        if stack and rng.random() < 0.5:
            logs.append(f"{stack.pop()}:end:{t}")
            t += 1
        else:
            f = rng.randrange(n)
            stack.append(f)
            logs.append(f"{f}:start:{t}")
        t += rng.randint(0, 2)
    while stack:
        logs.append(f"{stack.pop()}:end:{t}")
        t += rng.randint(1, 2)
    return logs


def tests():
    rng = random.Random(3)
    t = [
        fn("Example", "exclusive_time", 2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]),
        fn("Recursive call, called twice", "exclusive_time", 1, ["0:start:0", "0:start:2", "0:end:5", "0:start:6", "0:end:6", "0:end:7"]),
        fn("Back to back", "exclusive_time", 2, ["0:start:0", "0:end:0", "1:start:1", "1:end:1"]),
        fn("Single", "exclusive_time", 1, ["0:start:0", "0:end:0"]),
        fn("Deep nesting", "exclusive_time", 3, ["0:start:0", "1:start:1", "2:start:2", "2:end:3", "1:end:4", "0:end:10"]),
        fn("Parent with two children", "exclusive_time", 3, ["0:start:0", "1:start:2", "1:end:3", "2:start:5", "2:end:5", "0:end:9"]),
    ]
    for s in range(2):
        n = rng.randint(1, 6)
        t.append(fn(f"Random logs #{s + 1}", "exclusive_time", n, random_logs(rng, n, 40), hidden=True))
    t.append(fn("Random logs (20k)", "exclusive_time", 4, random_logs(rng, 4, 20000), hidden=True))
    return t


def scale(n):
    return fn(f"{n} logs", "exclusive_time", 8, random_logs(random.Random(n), 8, n))


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of log lines"}
