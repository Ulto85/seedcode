import random
from engine.spec import fn

EDGES = [["/", "/a"], ["/", "/b"], ["/a", "/vault"], ["/b", "/key"], ["/key", "/a"]]
F, G = "find_exit", "find_exit_with_keys"


def rand_maze(rng, n, m, n_exits):
    rooms = [f"/r{i}" for i in range(n)]
    edges = [[rng.choice(rooms), rng.choice(rooms)] for _ in range(m)]
    exits = rng.sample(rooms[1:], min(n_exits, n - 1)) if n > 1 else []
    return rooms, edges, exits


def rand_locks(rng, rooms, n_keys, p_lock, p_key, p_fail):
    keys = [f"k{i}" for i in range(n_keys)]
    req = {r: rng.choice(keys) for r in rooms[1:] if rng.random() < p_lock}
    found = {r: rng.choice(keys) for r in rooms if rng.random() < p_key}
    fails = {r: rng.randint(1, 5) for r in rooms if rng.random() < p_fail}
    return req, found, fails


def chain_maze(n, rng):
    """Long path /r0 -> ... -> /r{n-1} (the only exit), plus back-edges making many cycles."""
    rooms = [f"/r{i}" for i in range(n)]
    edges = [[rooms[i], rooms[i + 1]] for i in range(n - 1)]
    edges += [[rooms[rng.randrange(n)], rooms[rng.randrange(n)]] for _ in range(n)]
    rng.shuffle(edges)
    return rooms, edges, [rooms[-1]]


def gauntlet(segments, rng):
    """Hubs in a row. Each hub links to two key rooms (red / blue) that link back to the hub, and to a door that
    needs one of the keys. You must come back to each hub holding a different key, so visited must include the key."""
    edges, req, found = [], {}, {}
    for i in range(segments):
        h, ka, kb, d, nxt = f"/h{i}", f"/h{i}/red", f"/h{i}/blue", f"/h{i}/door", f"/h{i + 1}"
        edges += [[h, ka], [h, kb], [ka, h], [kb, h], [h, d], [d, nxt]]
        found[ka], found[kb] = "red", "blue"
        req[d] = rng.choice(["red", "blue"])
    edges += [[f"/h{rng.randrange(segments)}", f"/h{rng.randrange(segments)}"] for _ in range(segments)]
    fails = {f"/h{i}/door": rng.randint(0, 2) for i in range(segments)}
    return edges, [f"/h{segments}"], req, found, fails


def tests():
    rng = random.Random(5)
    t = [
        fn("Example", F, "/", ["/vault"], EDGES),
        fn("Start is an exit", F, "/", ["/", "/a"], EDGES),
        fn("No exit reachable", F, "/", ["/island"], EDGES),
        fn("No edges, no exits", F, "/", [], []),
        fn("Cycle must terminate", F, "/a", ["/z"], [["/a", "/b"], ["/b", "/c"], ["/c", "/a"], ["/a", "/a"]]),
        fn("BFS returns the closer exit", F, "/", ["/far", "/near"], [["/", "/x"], ["/x", "/far"], ["/", "/near"]]),
        fn("Same depth -> edge order decides", F, "/", ["/p", "/q"], [["/", "/q"], ["/", "/p"]]),
        fn("Directed edges", F, "/", ["/up"], [["/up", "/"]]),
        fn("Case-sensitive URLs", F, "/", ["/Exit"], [["/", "/exit"]]),
        fn("Example with key", G, "/", ["/vault"], EDGES, {"/vault": "red"}, {"/key": "red"}, {}, 0, tag="Follow-up"),
        fn("Wrong key held", G, "/", ["/vault"], EDGES, {"/vault": "red"}, {"/key": "blue"}, {}, 0, tag="Follow-up"),
        fn("Retries: within budget vs exhausted", G, "/", ["/x", "/y"], [["/", "/x"], ["/", "/y"]], {}, {}, {"/x": 3, "/y": 2}, 2, tag="Follow-up"),
        fn("max_retries = 0 blocks any flaky room", G, "/", ["/x"], [["/", "/x"]], {}, {}, {"/x": 1}, 0, tag="Follow-up"),
        fn("Start locked", G, "/", ["/"], [], {"/": "k"}, {}, {}, 0, tag="Follow-up"),
        fn("Revisit start holding a different key", G, "/", ["/end"],
           [["/", "/gateB"], ["/", "/getA"], ["/getA", "/A"], ["/A", "/getB"], ["/getB", "/"], ["/gateB", "/end"]],
           {"/A": "a", "/gateB": "b"}, {"/getA": "a", "/getB": "b"}, {}, 0, tag="Follow-up"),
        fn("Picking up a new key locks you out", G, "/", ["/end"],
           [["/", "/swap"], ["/swap", "/door"], ["/door", "/end"]],
           {"/door": "gold"}, {"/": "gold", "/swap": "tin"}, {}, 0, tag="Follow-up"),
    ]
    for s in range(3):
        rooms, edges, exits = rand_maze(rng, 30, 60, 3)
        t.append(fn(f"Random maze #{s + 1}", F, "/r0", exits, edges, hidden=True))
    for s in range(4):
        rooms, edges, exits = rand_maze(rng, 40, 120, 3)
        req, found, fails = rand_locks(rng, rooms, 3, 0.4, 0.4, 0.1)
        t.append(fn(f"Random locked maze #{s + 1}", G, "/r0", exits, edges, req, found, fails, rng.randint(0, 3), tag="Follow-up", hidden=True))
    rooms, edges, exits = chain_maze(100000, rng)
    t.append(fn("100k rooms, long path, many cycles", F, "/r0", exits, edges, hidden=True))
    edges, exits, req, found, fails = gauntlet(6, rng)
    t.append(fn("Small gauntlet: revisit hubs with another key", G, "/h0", exits, edges, req, found, fails, 2, tag="Follow-up", hidden=True))
    edges, exits, req, found, fails = gauntlet(20000, rng)
    t.append(fn("20k-hub gauntlet", G, "/h0", exits, edges, req, found, fails, 2, tag="Follow-up", hidden=True))
    edges, exits, req, found, fails = gauntlet(200, rng)
    t.append(fn("Gauntlet with flaky doors (retries 1)", G, "/h0", exits, edges, req, found, fails, 1, tag="Follow-up", hidden=True))
    return t


def scale(n):
    edges, exits, req, found, fails = gauntlet(n, random.Random(n))
    return fn(f"n={n}", G, "/h0", exits, edges, req, found, fails, 2)


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000], "label": "n = hubs (4n rooms, 7n edges)"}
