import random
from engine.spec import fn


def digits(rng, n, alphabet="0123456789"):
    return "".join(rng.choice(alphabet) for _ in range(n))


def tests():
    rng = random.Random(11)
    t = [
        fn("Example", "sort_digits", "3141592653"),
        fn("All the same", "sort_digits", "000"),
        fn("Empty", "sort_digits", ""),
        fn("Single digit", "sort_digits", "7"),
        fn("Already sorted", "sort_digits", "0123456789"),
        fn("Reverse sorted", "sort_digits", "9988776655443322110"),
        fn("Only two distinct digits", "sort_digits", "9090909"),
        fn("Follow-up example", "sorted_digit_at", ["3141", "", "5926"], [0, 2, 7, 8, -1, 3], tag="Follow-up"),
        fn("No chunks at all", "sorted_digit_at", [], [0, 1, -1], tag="Follow-up"),
        fn("Only empty chunks", "sorted_digit_at", ["", "", ""], [0], tag="Follow-up"),
        fn("Boundaries between digit runs", "sorted_digit_at", ["000", "22", "9"], [0, 2, 3, 4, 5, 6], tag="Follow-up"),
        fn("Repeated and unordered positions", "sorted_digit_at", ["5", "1", "5", "1"], [3, 0, 3, 0, 2, 1, 1000000000, -1000000000], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(fn(f"Random #{s + 1}", "sort_digits", digits(rng, rng.randint(20, 200)), hidden=True))
    t.append(fn("Skewed random", "sort_digits", digits(rng, 500, "1111111113"), hidden=True))
    for s in range(3):
        chunks = [digits(rng, rng.randint(0, 30)) for _ in range(rng.randint(1, 20))]
        total = sum(map(len, chunks))
        pos = [rng.randint(-3, total + 3) for _ in range(40)]
        t.append(fn(f"Random lookups #{s + 1}", "sorted_digit_at", chunks, pos, tag="Follow-up", hidden=True))
    t.append(fn("Two million digits", "sort_digits", digits(rng, 2_000_000), hidden=True))
    big_chunks = [digits(rng, rng.randint(0, 40)) for _ in range(20000)]
    total = sum(map(len, big_chunks))
    big_pos = [rng.randint(-10, total + 10) for _ in range(100000)]
    t.append(fn("400k digits, 100k lookups", "sorted_digit_at", big_chunks, big_pos, tag="Follow-up", hidden=True))
    return t


def scale(n):
    return fn(f"n={n}", "sort_digits", digits(random.Random(n), n))


SCALE = {"sizes": [50000, 100000, 200000, 400000, 800000, 1600000], "label": "n = len(digits)"}
