import random
from engine.spec import cls

RECIPES = {
    "pasta":  {"tomato": 3, "garlic": 2, "basil": 1, "pasta": 1},
    "salad":  {"tomato": 2, "lettuce": 1, "cucumber": 1},
    "pizza":  {"tomato": 2, "cheese": 2, "basil": 2, "dough": 1},
    "soup":   {"tomato": 4, "garlic": 1, "onion": 2},
    "omelet": {"egg": 3, "cheese": 1, "onion": 1},
}
DEALS = {"tomato": [5, 2], "garlic": [3, 1], "basil": [2, 1], "cheese": [3, 4], "onion": [2, 1], "egg": [6, 3]}
INIT = [RECIPES, DEALS]


def C(name, ops, **kw):
    return cls(name, "RecipeCart", INIT, ops, **kw)


def random_ops(rng, n, max_v):
    names = list(RECIPES) + ["ghost"]
    ops = []
    for _ in range(n):
        r = rng.random()
        if r < 0.45: ops.append(["add_recipe", [rng.choice(names)]])
        elif r < 0.7: ops.append(["remove_recipe", [rng.choice(names)]])
        elif r < 0.85: ops.append(["get_total_discounts", []])
        elif r < 0.93: ops.append(["checkout", [rng.randint(-1, max_v)]])
        else: ops.append(["get_version", []])
    return ops


def tests():
    rng = random.Random(42)
    t = [
        C("Basic add + discount", [["add_recipe", ["pasta"]], ["get_total_discounts", []], ["add_recipe", ["salad"]], ["get_total_discounts", []]]),
        C("Same recipe twice", [["add_recipe", ["pizza"]], ["add_recipe", ["pizza"]], ["get_total_discounts", []]]),
        C("Remove recipe", [["add_recipe", ["soup"]], ["add_recipe", ["pasta"]], ["get_total_discounts", []], ["remove_recipe", ["soup"]], ["get_total_discounts", []]]),
        C("Remove missing / unknown recipe", [["remove_recipe", ["pasta"]], ["add_recipe", ["unicorn"]], ["add_recipe", ["salad"]], ["remove_recipe", ["pasta"]], ["get_total_discounts", []]]),
        C("Remove twice after one add", [["add_recipe", ["pasta"]], ["remove_recipe", ["pasta"]], ["remove_recipe", ["pasta"]], ["get_total_discounts", []]]),
        C("Empty cart", [["get_total_discounts", []]]),
        C("Versions increment", [["get_version", []], ["add_recipe", ["pasta"]], ["get_version", []], ["add_recipe", ["salad"]], ["get_version", []], ["remove_recipe", ["omelet"]], ["get_version", []]], tag="Follow-up"),
        C("Checkout older version", [["add_recipe", ["pasta"]], ["add_recipe", ["soup"]], ["add_recipe", ["pizza"]], ["get_total_discounts", []], ["checkout", [1]], ["get_version", []], ["get_total_discounts", []]], tag="Follow-up"),
        C("Checkout discards future", [["add_recipe", ["pasta"]], ["add_recipe", ["soup"]], ["checkout", [1]], ["checkout", [2]], ["add_recipe", ["omelet"]], ["get_version", []], ["get_total_discounts", []]], tag="Follow-up"),
        C("Checkout 0 and invalid", [["add_recipe", ["pizza"]], ["checkout", [5]], ["checkout", [-1]], ["checkout", [0]], ["get_total_discounts", []], ["get_version", []]], tag="Follow-up"),
        C("Checkout current version is a no-op", [["add_recipe", ["pizza"]], ["add_recipe", ["pizza"]], ["checkout", [2]], ["get_version", []], ["get_total_discounts", []]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random ops #{s + 1}", random_ops(rng, 60, 40), tag="Follow-up", hidden=True))
    t.append(C("Random ops (3000 ops)", random_ops(rng, 3000, 800), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", random_ops(random.Random(n), n, n // 4))


SCALE = {"sizes": [250, 500, 1000, 2000, 4000, 8000, 16000], "label": "n = number of operations"}
