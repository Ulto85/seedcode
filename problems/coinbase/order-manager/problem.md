---
title: Crypto Order Manager
difficulty: Easy
source: Coinbase SWE coding round, "crypto order management system" / "stateful trading order manager" (reported 2026)
order: 1
minutes: 40
tags: design, hash map, state machine
---
You're building the in-memory order manager behind a crypto trading screen. Orders don't match against
each other here. You only track each order's **lifecycle**.

Each order has an `order_id` (string), a `symbol` such as `"BTC-USD"`, a `side` (`"buy"` or `"sell"`), a
`quantity` (positive integer) and a **state**:

```
            pause            
   LIVE  ─────────▶  PAUSED
     ▲  ◀─────────     │
     │     resume      │
     └──── cancel ─────┴──▶  CANCELLED   (final)
```

### Part 1
```
OrderManager()
create(order_id, symbol, side, quantity) -> bool   # new order starts LIVE
pause(order_id)  -> bool                           # LIVE   -> PAUSED
resume(order_id) -> bool                           # PAUSED -> LIVE
cancel(order_id) -> bool                           # LIVE or PAUSED -> CANCELLED
get(order_id)    -> str | None                     # "LIVE" | "PAUSED" | "CANCELLED", None if unknown
count(state)     -> int                            # number of orders currently in that state
```

Rules:
- `create` returns `False` (and changes nothing) if `order_id` was **ever** used before (even if that
  order is cancelled), if `side` isn't exactly `"buy"` or `"sell"`, or if `quantity` isn't a positive integer.
- `pause` / `resume` / `cancel` return `False` (no change) for an unknown id or a transition the diagram
  doesn't allow: pausing a PAUSED order, resuming a LIVE one, anything on a CANCELLED order.
- `count` of any string that isn't one of the three states returns `0`.

### Follow-up: bulk cancel and live view
```
cancel_all(symbol)  -> int         # cancel every LIVE or PAUSED order for symbol; return how many changed
live_orders(symbol) -> list[str]   # ids of LIVE orders for symbol, in the order they were created
```
An unknown symbol gives `0` / `[]`. Paused orders are **not** live, but once resumed they reappear at their
original creation position, not at the end.

### Example
```
create("o1", "BTC-USD", "buy", 2)   -> True
create("o2", "BTC-USD", "sell", 1)  -> True
create("o1", "ETH-USD", "buy", 5)   -> False   # id already used
pause("o1")                         -> True
resume("o2")                        -> False   # o2 is LIVE, not PAUSED
count("LIVE")                       -> 1
live_orders("BTC-USD")              -> ["o2"]
resume("o1")                        -> True
live_orders("BTC-USD")              -> ["o1", "o2"]
cancel_all("BTC-USD")               -> 2
get("o1")                           -> "CANCELLED"
```

### Constraints
- Up to 2·10⁵ operations. `get`, `count`, and each transition should be **O(1)**: don't scan all orders.
- `cancel_all` / `live_orders` should only touch that symbol's orders.

*Reconstructed from candidate reports. The exact command format (the original reads commands from stdin
and prints `ERROR`) has been turned into method calls with boolean results.*
