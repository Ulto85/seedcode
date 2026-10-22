import random
from engine.spec import fn

F, G = "crawl", "crawl_times"
EX = {
    "http://news.com/": ["http://news.com/a", "http://news.com/b#comments", "http://ads.com/x"],
    "http://news.com/a": ["http://news.com/", "http://NEWS.com:8080/c"],
    "http://news.com/b": ["http://news.com/a#top"],
}
U = lambda p: f"http://s.io/{p}"
SIM = {U(""): [U("a"), U("b"), U("c")], U("a"): [U("d")], U("b"): [], U("c"): [U("d"), U("e")]}
SIM_LAT = {U(""): 1, U("a"): 5, U("b"): 1, U("c"): 2, U("d"): 1, U("e"): 1}


def random_web(rng, n, deg=4, foreign=0.1):
    hosts = ["http://site.com", "https://site.com:443", "http://SITE.com"]
    urls = [f"{rng.choice(hosts)}/p{i}" for i in range(n)]
    pages = {}
    for i, u in enumerate(urls):
        if rng.random() < 0.1:
            continue                         # dead link: fetch returns []
        links = []
        for _ in range(rng.randint(0, deg * 2)):
            r = rng.random()
            if r < foreign:
                links.append(f"http://other{rng.randint(0, 3)}.com/p{rng.randint(0, n)}")
            elif r < foreign + 0.1:
                links.append(urls[rng.randrange(n)] + "#frag" + str(rng.randint(0, 3)))
            else:
                links.append(urls[rng.randrange(n)])
        pages[u] = links
    lat = {u: rng.randint(1, 20) for u in urls if rng.random() < 0.8}
    return urls[0], pages, lat


def tests():
    rng = random.Random(99)
    t = [
        fn("Example", F, "http://news.com/", EX, compare="unordered"),
        fn("Start URL not in pages", F, "http://x.com/start", {}, compare="unordered"),
        fn("Start URL has a fragment", F, "http://x.com/#intro", {"http://x.com/": ["http://x.com/#a", "http://x.com/b"]}, compare="unordered"),
        fn("Cycle + self-link", F, "http://c.org/1", {"http://c.org/1": ["http://c.org/1", "http://c.org/2"],
                                                      "http://c.org/2": ["http://c.org/3"], "http://c.org/3": ["http://c.org/1"]}, compare="unordered"),
        fn("Subdomain is another host", F, "http://a.com/", {"http://a.com/": ["http://www.a.com/", "http://blog.a.com/x", "https://a.com/secure"]}, compare="unordered"),
        fn("Query string and trailing slash matter", F, "http://q.com/", {"http://q.com/": ["http://q.com/s?x=1", "http://q.com/s?x=2", "http://q.com/s", "http://q.com/s/"]}, compare="unordered"),
        fn("Unreachable page isn't crawled", F, "http://u.com/", {"http://u.com/": ["http://u.com/a"], "http://u.com/island": ["http://u.com/"]}, compare="unordered"),
        fn("Example (2 workers)", G, U(""), SIM, SIM_LAT, 2, tag="Follow-up"),
        fn("One worker = sequential", G, U(""), SIM, SIM_LAT, 1, tag="Follow-up"),
        fn("Plenty of workers", G, U(""), SIM, SIM_LAT, 10, tag="Follow-up"),
        fn("Default latency + fragments", G, "http://news.com/", EX, {}, 2, tag="Follow-up"),
        fn("One worker follows the FIFO queue", G, U(""),
           {U(""): [U("slow"), U("fast")], U("slow"): [U("x")], U("fast"): [U("y")]},
           {U(""): 1, U("slow"): 3, U("fast"): 3, U("x"): 2, U("y"): 1}, 1, tag="Follow-up"),
        fn("Same finish time, 2 workers", G, U(""),
           {U(""): [U("p"), U("q")], U("p"): [U("x"), U("y")], U("q"): [U("y"), U("z")]},
           {U(""): 2, U("p"): 3, U("q"): 3, U("x"): 4, U("y"): 1, U("z"): 2}, 2, tag="Follow-up"),
    ]
    for s in range(3):
        start, pages, _ = random_web(rng, 40)
        t.append(fn(f"Random web #{s + 1}", F, start, pages, compare="unordered", hidden=True))
    for s in range(3):
        start, pages, lat = random_web(rng, 40)
        t.append(fn(f"Random concurrent #{s + 1}", G, start, pages, lat, rng.randint(1, 6), tag="Follow-up", hidden=True))
    start, pages, _ = random_web(rng, 60000)
    t.append(fn("60k pages", F, start, pages, compare="unordered", hidden=True))
    start, pages, lat = random_web(rng, 60000)
    t.append(fn("60k pages, 64 workers", G, start, pages, lat, 64, tag="Follow-up", hidden=True))
    return t


def scale(n):
    start, pages, _ = random_web(random.Random(n), n)
    return fn(f"n={n}", F, start, pages, compare="unordered")


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000], "label": "n = number of pages (~4 links each)"}
