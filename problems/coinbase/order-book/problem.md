---
title: Limit Order Book
difficulty: Hard
source: Coinbase SWE coding round / take-home, "build an order book" (reported 2024-2026)
order: 2
minutes: 60
tags: design, sorted container, heap, simulation
---
Build the matching engine for a single trading pair (say BTC-USD). Traders send **limit orders**; the engine
matches them against resting orders using **price-time priority** (the rule Coinbase Exchange uses) and keeps
whatever is left on the book.

### Part 1
```
OrderBook()
place(order_id: str, side: str, price: int, qty: int) -> list[list] | None
cancel(order_id: str) -> bool
best_bid() -> list[int] | None    # [price, total resting qty at that price]
best_ask() -> list[int] | None
```

**Matching.** An incoming **buy** at price `P` trades against resting **sells** with price ≤ `P`, cheapest
first. An incoming **sell** at price `P` trades against resting **buys** with price ≥ `P`, highest first.
- Within one price level, the order that arrived **earliest** fills first.
- Each trade happens at the **resting** order's price, for `min(incoming remaining, resting remaining)`.
- Matching stops when the incoming order is fully filled or nothing on the other side crosses its price. Any
  remainder **rests** on the book at price `P` (behind earlier orders at that price).

`place` returns the list of fills **in execution order**, each as `[resting_order_id, price, qty]`
(`[]` if nothing traded). It returns `None` and changes nothing if `side` isn't `"buy"`/`"sell"`, `price` or
`qty` isn't positive, or `order_id` was **ever used before** (ids are never reused, even after a fill or cancel).

`cancel` removes a **resting** order (or what's left of it) and returns `True`. Unknown ids, fully filled orders
and already-cancelled orders return `False`.

`best_bid` / `best_ask` return the best price on that side with the **summed remaining qty** of all resting
orders at that price, or `None` if that side is empty.

### Follow-up: market orders and depth
```
place_market(order_id: str, side: str, qty: int) -> list[list] | None
depth(side: str, levels: int) -> list[list[int]]
```
- A market order matches like a limit order with **no price limit**, then any unfilled remainder is **discarded**
  (it never rests). Same fills format and same validation (`None` for bad side, non-positive qty, used id).
  A market order's id counts as used.
- `depth(side, levels)` returns up to `levels` price levels of resting orders on that side (`"buy"` = bids,
  `"sell"` = asks), best first, as `[price, total_qty]`. `[]` if `levels ≤ 0`, the side is empty or `side` is invalid.

### Example
```
place("s1", "sell", 101, 5) -> []
place("s2", "sell", 100, 2) -> []
place("s3", "sell", 101, 3) -> []
best_ask()                  -> [100, 2]
place("b1", "buy", 101, 6)  -> [["s2", 100, 2], ["s1", 101, 4]]   # best price first, then time
best_ask()                  -> [101, 4]                           # s1 has 1 left, s3 has 3
place("b2", "buy", 99, 4)   -> []                                 # doesn't cross, rests
cancel("s1")                -> True
depth("sell", 5)            -> [[101, 3]]
place_market("m1", "sell", 10) -> [["b2", 99, 4]]                 # other 6 discarded
best_bid()                  -> None
```

### Constraints
- Up to 10⁵ operations; prices 1 ≤ p ≤ 10⁶. Aim for O(log L) per price-level change (L = number of levels),
  O(1) per individual fill, and O(1) `cancel`. Don't scan every resting order per call.

*Rules were reconstructed from several candidate reports ("build out an order book", "order book
reconstruction") plus Coinbase Exchange's public matching-engine docs. Details like the fill format are our own.*
