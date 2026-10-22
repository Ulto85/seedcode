---
title: Expense Rules Engine
difficulty: Medium
source: Rippling SWE technical screen, "expense rules" / "expense and trip-level rules as data" (reported 2025-2026; exact format reconstructed)
order: 2
minutes: 45
timeout: 20
tags: design, rules engine, hash map, grouping
---
Rippling's spend product lets finance managers write **expense policies**. Your job: given a batch of expenses and a
list of rules, report every policy violation. Managers create rules all the time, so the rules arrive as **data**:
your code must not contain a branch per business rule.

```
evaluate_rules(expenses: list[dict], rules: list[dict]) -> list[list]
```

An **expense**:
```
{"id": "e1", "trip_id": "t1", "amount": 8000,            # amount in integer cents
 "expense_type": "meals", "vendor_type": "restaurant", "vendor_name": "Nopa"}
```

A **rule**:
```
{"id": "r1", "scope": "EXPENSE", "conditions": [["vendor_type", "EQ", "restaurant"], ["amount", "GT", 7500]]}
{"id": "r2", "scope": "TRIP", "threshold": 35000, "conditions": []}
```

**Conditions** are `[field, op, value]` triples; a rule's conditions are **AND**-ed together, and a rule with **no
conditions matches every expense**.
- `field` is any expense key: `id`, `trip_id`, `amount`, `expense_type`, `vendor_type`, `vendor_name`.
- `amount` supports `EQ NE GT GE LT LE` (numeric comparison, `value` is an int).
- String fields support `EQ` and `NE` (exact, case-sensitive) and `IN` (`value` is a list of strings).
- Inputs are always valid: no unknown fields, no operator used on the wrong kind of field.

### Part 1: expense-level rules
A rule with `"scope": "EXPENSE"` flags **every expense that matches all its conditions**. Each violation is
`["EXPENSE", expense_id, rule_id, expense_amount]`.

### Follow-up: trip-level rules
A rule with `"scope": "TRIP"` has an integer `threshold`. For each trip, add up the amounts of that trip's expenses
that match the rule's conditions. The trip violates the rule if that sum is **strictly greater** than the threshold.
A trip with no matching expenses is never flagged. Each violation is `["TRIP", trip_id, rule_id, matching_sum]`.

### Output order
- Rules in **input order**; all violations of one rule come before the next rule's.
- Within an `EXPENSE` rule: expenses in input order.
- Within a `TRIP` rule: trip ids in ascending (lexicographic, string) order.
- One expense can violate several rules; report each. No rules or no expenses → `[]`.

### Example
```
expenses = [
  {"id": "e1", "trip_id": "t1", "amount": 8000,  "expense_type": "meals",  "vendor_type": "restaurant", "vendor_name": "Nopa"},
  {"id": "e2", "trip_id": "t1", "amount": 30000, "expense_type": "travel", "vendor_type": "airline",    "vendor_name": "United"},
  {"id": "e3", "trip_id": "t2", "amount": 7000,  "expense_type": "meals",  "vendor_type": "restaurant", "vendor_name": "Zuni"},
]
rules = [
  {"id": "no_big_dinners", "scope": "EXPENSE", "conditions": [["vendor_type", "EQ", "restaurant"], ["amount", "GT", 7500]]},
  {"id": "trip_cap",       "scope": "TRIP", "threshold": 35000, "conditions": []},
  {"id": "meal_cap",       "scope": "TRIP", "threshold": 10000, "conditions": [["expense_type", "EQ", "meals"]]},
]
-> [["EXPENSE", "e1", "no_big_dinners", 8000],
 ["TRIP",    "t1", "trip_cap",       38000]]
```
`e3` is a restaurant meal but not over 7500. Trip `t2` totals 7000 (under both caps); trip `t1`'s meals total 8000
(under the 10000 meal cap).

### Constraints
- Up to 10⁴ expenses, 100 rules, 10 conditions per rule, many distinct trips.
- Aim for `O(rules × expenses × conditions)` plus sorting trip ids. Don't rescan every expense once per trip.

### What the interviewer cares about
- **Separation of concerns:** a predicate layer (one condition → bool, driven by an operator table), a matcher (AND of
  conditions), and the aggregation per scope. Adding a new operator or scope should be a one-line change.
- The same predicate code serves both scopes: a condition always judges a single expense.
- Integer cents, deterministic output order, and the empty-conditions edge case.

*Reports agree on the shape (expenses + data-driven rules at expense and trip level); the exact input format, the
`IN` operator and the output ordering here are a reconstruction.*
