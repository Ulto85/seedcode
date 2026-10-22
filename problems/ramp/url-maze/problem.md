---
title: URL Maze
difficulty: Medium
source: Ramp SWE phone screen, "HTTP maze / find the exit URL" (reported 2025-2026)
order: 2
minutes: 45
tags: graph, bfs, state search
---
In the real interview you're given a URL and an HTTP API: each `GET` returns a page that links to other URLs, and some
pages are exits. Here the maze is handed to you up front, so you can focus on the search itself.

```
edges: list[list[str]]     # [from_url, to_url], a directed link
```
A room's links are the edges leaving it, **in the order they appear in `edges`**.

### Part 1
```
find_exit(start: str, exits: list[str], edges: list[list[str]]) -> str | None
```
Run a **breadth-first search** from `start`. Visit each room at most once, and explore a room's links in edge order.
Return the first exit room the BFS visits (`start` itself counts, if it's an exit), or `None` if no exit is reachable.

### Follow-up: locked rooms and flaky servers
```
find_exit_with_keys(start, exits, edges, required_keys: dict[str, str], keys_found: dict[str, str],
                    failures: dict[str, int], max_retries: int) -> str | None
```
- `failures[url]` = how many times `url` answers `503` before it works. If that is **greater than `max_retries`**, the room
  can never be entered. (Missing → 0.)
- `required_keys[url]` = the key you must be holding to enter `url` (`401` otherwise). Rooms not listed need no key.
- `keys_found[url]` = the key you pick up when you enter `url`. You hold **at most one key**: picking one up replaces
  the one you had. You start with no key.
- The same rules apply to `start`: if it can't be entered, return `None`.

Because what you can enter depends on your key, a search state is **(room, key held after entering it)**. The same room
may be visited again holding a different key, but never twice with the same key. BFS over these states: pop a state,
return its room if it's an exit; otherwise, for each link in edge order, if the target can be entered with your current
key, it becomes the state (target, `keys_found.get(target, current key)`), enqueued if new.

### Example
```
edges = [["/", "/a"], ["/", "/b"], ["/a", "/vault"], ["/b", "/key"], ["/key", "/a"]]
exits = ["/vault"]

find_exit("/", exits, edges)  -> "/vault"         # / -> /a -> /vault

required_keys = {"/vault": "red"},  keys_found = {"/key": "red"}
find_exit_with_keys("/", exits, edges, required_keys, keys_found, {}, 0)
  -> "/vault"   # (/,-) (/a,-) (/b,-) ... /vault locked from (/a,-); (/key,red) -> (/a,red) -> (/vault,red)
```

### What the interviewer cares about
- The maze has **cycles**: track visited states or you loop forever.
- Distinguishing permanent failures (401 without the key, retries exhausted) from retryable ones, and bounding retries.
- For the follow-up: realizing that "visited" must include the key.

### Constraints
- Up to 2·10⁵ edges and 10⁵ exits; URLs are case-sensitive strings. Edges may repeat or be self-loops.
- `0 ≤ max_retries ≤ 10`, at most 10 distinct keys.

*The real follow-up is an HTTP client (503 → retry, 401 → send the key as a Bearer token). This offline version with
explicit failure counts is a fully specified reconstruction of it.*
