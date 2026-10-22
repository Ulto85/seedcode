import random
from engine.spec import fn

F = "evaluate_rules"

VENDORS = {
    "meals": [("restaurant", "Nopa"), ("restaurant", "Zuni"), ("cafe", "Blue Bottle"), ("bar", "Trick Dog")],
    "travel": [("airline", "United"), ("airline", "Delta"), ("rideshare", "Uber"), ("rail", "Amtrak")],
    "lodging": [("hotel", "Hilton"), ("hotel", "Marriott"), ("rental", "Airbnb")],
    "software": [("saas", "Figma"), ("saas", "GitHub")],
}


def E(i, trip, amount, etype, vtype, vname):
    return {"id": i, "trip_id": trip, "amount": amount, "expense_type": etype, "vendor_type": vtype, "vendor_name": vname}


EXAMPLE_EXPENSES = [
    E("e1", "t1", 8000, "meals", "restaurant", "Nopa"),
    E("e2", "t1", 30000, "travel", "airline", "United"),
    E("e3", "t2", 7000, "meals", "restaurant", "Zuni"),
]
EXAMPLE_RULES = [
    {"id": "no_big_dinners", "scope": "EXPENSE", "conditions": [["vendor_type", "EQ", "restaurant"], ["amount", "GT", 7500]]},
    {"id": "trip_cap", "scope": "TRIP", "threshold": 35000, "conditions": []},
    {"id": "meal_cap", "scope": "TRIP", "threshold": 10000, "conditions": [["expense_type", "EQ", "meals"]]},
]


def rand_expenses(rng, n, trips):
    out = []
    for i in range(n):
        et = rng.choice(list(VENDORS))
        vt, vn = rng.choice(VENDORS[et])
        out.append(E(f"e{i}", f"t{rng.randint(1, trips)}", rng.choice([0, rng.randint(1, 5000), rng.randint(1, 60000)]),
                     et, vt, vn))
    return out


def rand_condition(rng):
    r = rng.random()
    if r < 0.4:
        return ["amount", rng.choice(["EQ", "NE", "GT", "GE", "LT", "LE"]), rng.choice([0, 2500, 5000, 7500, 20000])]
    field = rng.choice(["expense_type", "vendor_type", "vendor_name"])
    pool = {"expense_type": list(VENDORS),
            "vendor_type": sorted({v for vs in VENDORS.values() for v, _ in vs}),
            "vendor_name": sorted({n for vs in VENDORS.values() for _, n in vs})}[field]
    op = rng.choice(["EQ", "NE", "IN"])
    value = rng.sample(pool, rng.randint(1, 3)) if op == "IN" else rng.choice(pool)
    return [field, op, value]


def rand_rules(rng, n, trip=True):
    rules = []
    for i in range(n):
        conds = [rand_condition(rng) for _ in range(rng.randint(0, 3))]
        if trip and rng.random() < 0.5:
            rules.append({"id": f"r{i}", "scope": "TRIP", "threshold": rng.choice([0, 10000, 50000, 150000]),
                          "conditions": conds})
        else:
            rules.append({"id": f"r{i}", "scope": "EXPENSE", "conditions": conds})
    return rules


def tests():
    rng = random.Random(2026)
    ex = EXAMPLE_EXPENSES
    t = [
        fn("Example (expense rule only)", F, ex, EXAMPLE_RULES[:1]),
        fn("No rules", F, ex, []),
        fn("No expenses", F, [], EXAMPLE_RULES),
        fn("Empty conditions match everything", F, ex, [{"id": "all", "scope": "EXPENSE", "conditions": []}]),
        fn("Boundary: GT vs GE", F, ex, [
            {"id": "gt", "scope": "EXPENSE", "conditions": [["amount", "GT", 8000]]},
            {"id": "ge", "scope": "EXPENSE", "conditions": [["amount", "GE", 8000]]}]),
        fn("Case-sensitive strings, NE and IN", F, ex, [
            {"id": "lower", "scope": "EXPENSE", "conditions": [["vendor_name", "EQ", "nopa"]]},
            {"id": "not_meals", "scope": "EXPENSE", "conditions": [["expense_type", "NE", "meals"]]},
            {"id": "in", "scope": "EXPENSE", "conditions": [["vendor_name", "IN", ["Zuni", "United"]]]}]),
        fn("One expense, several rules (rule order kept)", F, ex, [
            {"id": "z_big", "scope": "EXPENSE", "conditions": [["amount", "GE", 7000]]},
            {"id": "a_meal", "scope": "EXPENSE", "conditions": [["expense_type", "EQ", "meals"]]}]),
        fn("Conditions on id / trip_id", F, ex, [
            {"id": "t1_only", "scope": "EXPENSE", "conditions": [["trip_id", "EQ", "t1"], ["id", "NE", "e2"]]}]),
        fn("Example (full)", F, ex, EXAMPLE_RULES, tag="Follow-up"),
        fn("Trip sum strictly greater than threshold", F, ex, [
            {"id": "eq", "scope": "TRIP", "threshold": 38000, "conditions": []},
            {"id": "just_under", "scope": "TRIP", "threshold": 37999, "conditions": []}], tag="Follow-up"),
        fn("Trips sorted as strings (t10 < t9)", F, [
            E("a", "t9", 500, "meals", "cafe", "Blue Bottle"), E("b", "t10", 700, "meals", "cafe", "Blue Bottle"),
            E("c", "t2", 900, "meals", "cafe", "Blue Bottle"), E("d", "t10", 100, "travel", "rideshare", "Uber")],
           [{"id": "any", "scope": "TRIP", "threshold": 0, "conditions": [["expense_type", "EQ", "meals"]]}], tag="Follow-up"),
        fn("Zero-amount matches don't exceed threshold 0", F, [
            E("a", "t1", 0, "meals", "cafe", "Blue Bottle"), E("b", "t2", 1, "meals", "cafe", "Blue Bottle")],
           [{"id": "r", "scope": "TRIP", "threshold": 0, "conditions": []}], tag="Follow-up"),
        fn("Mixed scopes interleaved", F, ex, [
            {"id": "trip_any", "scope": "TRIP", "threshold": 5000, "conditions": [["vendor_type", "IN", ["restaurant"]]]},
            {"id": "air", "scope": "EXPENSE", "conditions": [["vendor_type", "EQ", "airline"]]},
            {"id": "trip_air", "scope": "TRIP", "threshold": 1000, "conditions": [["vendor_type", "EQ", "airline"]]}],
           tag="Follow-up"),
    ]
    for s in range(3):
        t.append(fn(f"Random expense rules #{s + 1}", F, rand_expenses(rng, 25, 4), rand_rules(rng, 6, trip=False),
                    hidden=True))
    for s in range(3):
        t.append(fn(f"Random mixed rules #{s + 1}", F, rand_expenses(rng, 40, 6), rand_rules(rng, 8),
                    tag="Follow-up", hidden=True))
    t.append(fn("10k expenses, 3k trips, 30 rules", F, rand_expenses(rng, 10000, 3000), rand_rules(rng, 30),
                tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return fn(f"n={n}", F, rand_expenses(rng, n, max(1, n // 5)), rand_rules(rng, 10))


SCALE = {"sizes": [500, 1000, 2000, 4000, 8000, 16000, 32000], "label": "n = number of expenses (10 rules)"}
