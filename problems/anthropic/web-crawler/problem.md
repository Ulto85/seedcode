---
title: Same-Host Web Crawler
difficulty: Medium
source: Anthropic SWE phone screen / onsite, "web crawler" (reported 2024-2026)
order: 3
minutes: 45
tags: BFS, graph, simulation, concurrency
---
Write a crawler that starts at one URL and finds every page reachable from it **on the same host**.

In the interview you get an `html_parser.get_urls(url)` that does a slow, blocking HTTP fetch, and the follow-up is
to make the crawl concurrent. Tests here run single-threaded, so the web is given as a dict and the follow-up is a
**deterministic simulation** of a crawl with a pool of workers.

```
pages: dict[str, list[str]]     # url -> the links on that page (absolute URLs, in page order)
```
Fetching a URL that isn't a key of `pages` succeeds but returns no links (it's still a crawled page).

### Rules (both parts)
- **Fragments:** a URL's identity is the URL with everything from the first `#` removed: `http://a.com/x#top` and
  `http://a.com/x` are the same page. Look up, store and return fragment-stripped URLs. Nothing else is normalized
  (`/x` and `/x/` are different pages; query strings are part of the identity).
- **Same host:** only follow links whose **hostname** equals the start URL's hostname, ignoring case. Scheme, port,
  path and query don't matter for this check (use `urllib.parse.urlparse(url).hostname`). `www.a.com` and `a.com` are
  different hosts.
- Each page is fetched **at most once**, even with cycles and self-links. The start URL is always crawled.

### Part 1
```
crawl(start_url: str, pages: dict) -> list[str]
```
Return every crawled URL (fragment-stripped), in **any order**.

```
pages = {
  "http://news.com/":       ["http://news.com/a", "http://news.com/b#comments", "http://ads.com/x"],
  "http://news.com/a":      ["http://news.com/", "http://NEWS.com:8080/c"],
  "http://news.com/b":      ["http://news.com/a#top"],
}
crawl("http://news.com/", pages)
-> ["http://news.com/", "http://news.com/a", "http://news.com/b", "http://NEWS.com:8080/c"]   (any order)
```
`ads.com` is another host, so it's never fetched or returned. `NEWS.com:8080` is the same hostname.

### Follow-up: concurrent crawl (simulated)
Now `get_urls` is slow and you run `workers` fetches in parallel. Simulate it:
```
crawl_times(start_url: str, pages: dict, latency: dict, workers: int) -> dict[str, int]
```
- Fetching `url` takes `latency.get(url, 1)` ms (look up by the fragment-stripped URL).
- A URL is **discovered** when a fetch that links to it finishes. New same-host URLs go to the back of a FIFO queue,
  in link order. A URL already discovered is never queued again.
- At time `0` the start URL is queued. Whenever a worker is free and the queue is non-empty, the worker starts the
  URL at the front of the queue.
- If several fetches finish at the same time `t`, process their links in the order those fetches **started**; then
  idle workers pick up work at time `t`.
- The crawl ends when the queue is empty **and** no fetch is in flight (an empty queue alone doesn't mean done).

Return `{url: time its fetch finished}` for every crawled URL.

```
pages = {"s": ...}   # with URLs written short for readability:
s -> [a, b, c],  a -> [d],  b -> [],  c -> [d, e]
latency: s=1, a=5, b=1, c=2, d=1, e=1;  workers = 2
t=0 start s          t=1 s done: queue a, b, c; start a (ends 6), b (ends 2)
t=2 b done; start c (ends 4)         t=4 c done: d is new, e is new; start d (ends 5)
t=5 d done; start e (ends 6)         t=6 a and e done
-> {s: 1, a: 6, b: 2, c: 4, d: 5, e: 6}
```

### Constraints
- Up to 10⁵ pages and 5·10⁵ links. `1 <= workers <= 1000`, latencies are ints `>= 1`.

*Reconstructed: reports agree on the same-host rule, fragment stripping, fetch-once and the concurrent follow-up; the
dict-based web and the worker simulation are this site's deterministic adaptation of the threaded version.*
