import random
from engine.spec import fn

F = "cd"

EX_LINKS = {"/home/me": "/data/users/me", "/data/users/me/tmp": "/tmp", "/loop1": "/loop2", "/loop2": "/loop1"}


def rand_world(rng, n_links, alpha):
    """Links at depth 1 or 2 over names a0..a{alpha-1}. Depth-1 links point into /tK/...;
    depth-2 links point to /tK/... or to a depth-1 path (which may itself be a link). No cycles."""
    names = [f"a{i}" for i in range(alpha)]
    links = {}
    while len(links) < n_links:
        if rng.random() < 0.3:
            key = "/" + rng.choice(names)
            target = f"/t{rng.randrange(alpha)}/" + rng.choice(names)
        else:
            key = "/" + rng.choice(names) + "/" + rng.choice(names)
            target = "/" + rng.choice(names) if rng.random() < 0.5 else f"/t{rng.randrange(alpha)}"
        links[key] = target
    return names, links


def rand_path(rng, n, names, max_depth=30):
    comps, d = [], 0
    for _ in range(n):
        r = rng.random()
        if d >= max_depth or r < 0.42:
            comps.append(".."); d = max(0, d - 1)
        elif r < 0.47:
            comps.append(".")
        elif r < 0.5:
            comps.append("")
        else:
            comps.append(rng.choice(names)); d += 1
    return ("/" if rng.random() < 0.5 else "") + "/".join(comps)


def tests():
    rng = random.Random(23)
    t = [
        fn("Example: relative child", F, "/foo/bar", "baz", {}),
        fn("Example: dots", F, "/foo/bar", "../baz/./qux", {}),
        fn("Example: absolute with extra slashes", F, "/foo/bar", "/x//y/", {}),
        fn("Example: above root", F, "/", "../../a", {}),
        fn("Empty path stays put", F, "/foo/bar", "", {}),
        fn("Only dots", F, "/foo/bar", "./././", {}),
        fn("Back to root", F, "/foo/bar", "../..", {}),
        fn("Just a slash", F, "/foo/bar", "/", {}),
        fn("Dots inside names are names", F, "/x", "...//.hidden/a.b", {}),
        fn("Follow-up: into a link", F, "/", "home/me/docs", EX_LINKS, tag="Follow-up"),
        fn("Follow-up: .. after a redirect", F, "/home", "me/..", EX_LINKS, tag="Follow-up"),
        fn("Follow-up: link found after a redirect", F, "/", "home/me/tmp/x", EX_LINKS, tag="Follow-up"),
        fn("Follow-up: two-link cycle", F, "/", "loop1", EX_LINKS, tag="Follow-up"),
        fn("Follow-up: whole components only", F, "/", "home/meh", EX_LINKS, tag="Follow-up"),
        fn("Follow-up: a cycle you never enter is harmless", F, "/", "x/../y", EX_LINKS, tag="Follow-up"),
        fn("Follow-up: link to its own subdirectory", F, "/", "/a", {"/a": "/a/x"}, tag="Follow-up"),
        fn("Follow-up: same link reused in sequence", F, "/", "a/up/up", {"/a/up": "/a"}, tag="Follow-up"),
        fn("Follow-up: chain of links", F, "/", "p/z", {"/p": "/q", "/q": "/r/s", "/r": "/m"}, tag="Follow-up"),
        fn("Follow-up: link to root", F, "/w", "r/etc", {"/w/r": "/"}, tag="Follow-up"),
        fn("Follow-up: three-link cycle through a target's middle", F, "/", "x/y", {"/x": "/y/k", "/y": "/z", "/z/k": "/x"}, tag="Follow-up"),
    ]
    for i in range(3):
        cwd = "/" + "/".join(rng.choice(["a", "b", "c"]) for _ in range(rng.randint(0, 3)))
        t.append(fn(f"Random no links #{i + 1}", F, cwd, rand_path(rng, 25, ["a", "b", "c"]), {}, hidden=True))
    for i in range(4):
        names, links = rand_world(rng, 12, 5)
        t.append(fn(f"Random with links #{i + 1}", F, "/", rand_path(rng, 30, names, 6), links, tag="Follow-up", hidden=True))
    names, _ = rand_world(rng, 1, 50)
    t.append(fn("100k components, no links", F, "/start", rand_path(rng, 100000, names), {}, hidden=True))
    names, links = rand_world(rng, 50000, 400)
    t.append(fn("100k components, 50k links", F, "/", rand_path(rng, 100000, names), links, tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    names, links = rand_world(rng, n // 2, 300)
    return fn(f"n={n}", F, "/", rand_path(rng, n, names), links)


SCALE = {"sizes": [4000, 8000, 16000, 32000, 64000, 128000], "label": "n = path components (links = n / 2)"}
