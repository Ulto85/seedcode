import operator
from collections import defaultdict

# One table drives every condition: adding an operator is one line, no per-rule branches.
OPS = {
    "EQ": operator.eq, "NE": operator.ne,
    "GT": operator.gt, "GE": operator.ge, "LT": operator.lt, "LE": operator.le,
    "IN": lambda a, b: a in b,
}


def matches(expense, conditions):
    return all(OPS[op](expense[field], value) for field, op, value in conditions)


def _expense_scope(rule, expenses):
    return [["EXPENSE", e["id"], rule["id"], e["amount"]]
            for e in expenses if matches(e, rule["conditions"])]


def _trip_scope(rule, expenses):
    sums = defaultdict(int)
    for e in expenses:
        if matches(e, rule["conditions"]):
            sums[e["trip_id"]] += e["amount"]
    return [["TRIP", trip, rule["id"], total]
            for trip, total in sorted(sums.items()) if total > rule["threshold"]]


SCOPES = {"EXPENSE": _expense_scope, "TRIP": _trip_scope}


def evaluate_rules(expenses, rules):
    """Each rule makes one pass over the expenses; TRIP rules aggregate into a dict keyed by trip.
    Time O(R * E * C + R * T log T), space O(T)."""
    out = []
    for rule in rules:
        out += SCOPES[rule["scope"]](rule, expenses)
    return out
