---
title: Flaky Catalog Product Resolver
difficulty: Medium
source: In the style of Sierra's reported technical screen. PracHub's Sierra guide (2026) mentions resolving product IDs through fallback endpoints "with retries, ordering and caching" and a flaky mock API, and an Exponent APX report describes adding exponential retries and traversing related catalog items. The exact rules here are ours, not a reported question.
order: 4
minutes: 45
tags: retries, exponential backoff, caching, memoization, cycle detection
---
A retail customer's support agent needs to tell shoppers which product they can actually buy. Customers ask about
old product IDs, and the catalog marks discontinued products with a **replacement** (which may itself be
discontinued). The catalog service is flaky. Resolve every requested ID to the product a shopper can buy today.

The `CatalogAPI` class in the starter wraps the test data (don't edit it):
```
api = CatalogAPI(catalog, flaky)
api.get(product_id) -> dict | None     # may raise TransientError
api.sleep(ms)                          # "wait" before a retry (just records the time)

resolve_products(requests, catalog, flaky, max_retries, base_ms, use_cache=False)
    -> {"results": [...], "calls": api.calls, "wait_ms": api.waited_ms}
```
- `catalog[id] = {"status": "active" | "discontinued", "replacement": id | None}`. `get` returns `None` for an id
  that isn't in the catalog.
- `flaky[id] = k` means the first `k` calls to `get(id)` raise `TransientError` (counted over the whole run).

### Part 1
Resolve each request in order; `results[i]` is the answer for `requests[i]`.

**Fetching one id (retries with exponential backoff).** Call `get(id)`. If it raises, retry: before retry number
`r` (1, 2, ..., `max_retries`), call `api.sleep(base_ms * 2**(r-1))`. If all `1 + max_retries` attempts fail,
the fetch has failed (no sleep after the last attempt).

**Following replacements.** Starting at the requested id:
1. If this id was already visited **during this request**, the answer is `"CYCLE"` (don't fetch it again).
2. Fetch it. Failed fetch: the answer is `"FAILED"`. `None`: the answer is `"NOT_FOUND"`.
3. `"active"`: the answer is this id. `"discontinued"` with no replacement: `"UNAVAILABLE"`. Otherwise move to the
   replacement and repeat.

Without a cache, every request fetches every id on its path again.

### Follow-up: cache
With `use_cache=True`, never ask the service for something you already know:
- A **successful** `get` response (a product or `None`) is remembered for the rest of the run, so that id is
  never fetched again. A failed fetch is not remembered: a later request tries again (and the flaky counter has
  moved on, so it may now succeed).
- Requests can repeat and chains can be long and shared (thousands of old ids replaced by the same chain), so
  don't re-walk a chain you've already resolved. A `"FAILED"` answer must never be reused.

### Example
```
catalog = {"p1": active,        "p2": discontinued -> p3,  "p3": discontinued -> p1,
           "p4": discontinued -> None,  "p5": discontinued -> p6,  "p6": discontinued -> p5,
           "p7": discontinued -> p9}                                  # p9 doesn't exist
flaky = {"p3": 2};  requests = ["p2", "p4", "p5", "p7", "p2"];  max_retries = 3, base_ms = 100

no cache:  p2: get p2, get p3 fails, sleep 100, fails, sleep 200, ok, get p1   -> "p1"   (5 calls)
           p4 -> "UNAVAILABLE" (1)    p5: p5, p6, then p5 again -> "CYCLE" (2)
           p7: p7, p9 -> "NOT_FOUND" (2)    p2: p2, p3, p1 -> "p1" (3)
  -> {"results": ["p1", "UNAVAILABLE", "CYCLE", "NOT_FOUND", "p1"], "calls": 13, "wait_ms": 300}
use_cache: the second "p2" makes no calls -> same results, "calls": 10, "wait_ms": 300

max_retries = 1, requests = ["p2", "p2"], no cache:
  first:  p2, p3 fails, sleep 100, p3 fails  -> "FAILED"
  second: p2, p3 (third call: ok now), p1    -> "p1"
  -> {"results": ["FAILED", "p1"], "calls": 6, "wait_ms": 100}
```
(In the test data, an entry written `p2: discontinued -> p3` is `{"status": "discontinued", "replacement": "p3"}`.)

### Constraints
- Up to `5 * 10^4` requests and catalog entries; `0 <= max_retries <= 5`; `1 <= base_ms <= 1000`.

### What the interviewer cares about
- Retry logic that's easy to read and gives up cleanly; exact backoff bookkeeping
- Cycle detection that doesn't loop forever on bad data
- Knowing what's safe to cache (successful responses, definitive answers) and what isn't (failures)
- Preserving request order in the output
