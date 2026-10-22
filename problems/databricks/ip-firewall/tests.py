import random
from engine.spec import cls

EXAMPLE = [["DENY", "10.0.0.7"], ["ALLOW", "10.0.0.0/24"], ["DENY", "10.0.0.0/8"], ["ALLOW", "0.0.0.0/0"]]


def C(name, rules, ops, **kw):
    return cls(name, "Firewall", [rules], ops, **kw)


def chk(*ips):
    return [["check", [ip]] for ip in ips]


def blk(*cidrs):
    return [["check_block", [c]] for c in cidrs]


def ip_str(v):
    return ".".join(str((v >> s) & 255) for s in (24, 16, 8, 0))


def rand_rules(rng, n, base=10 << 24, spread=16):
    """Rules clustered under one /8 so they overlap a lot."""
    rules = []
    for _ in range(n):
        p = rng.choice([8, 12, 16, 20, 24, 26, 28, 30, 31, 32, 32])
        v = base | rng.getrandbits(32 - 8) if p > 8 else base
        v &= ~((1 << (32 - p)) - 1) & 0xFFFFFFFF
        if rng.random() < 0.5:   # sometimes leave junk host bits in
            v |= rng.getrandbits(32 - p) if p < 32 else 0
        pat = ip_str(v) if p == 32 and rng.random() < 0.5 else f"{ip_str(v)}/{p}"
        rules.append([rng.choice(["ALLOW", "DENY"]), pat])
    if rng.random() < 0.5:
        rules.append(["ALLOW", "0.0.0.0/0"])
    return rules


def rand_ops(rng, rules, n, blocks=True):
    pool = []
    for _, pat in rules:
        a = pat.split("/")[0]
        pool.append(a)
    ops = []
    for _ in range(n):
        r = rng.random()
        if blocks and r < 0.3:
            p = rng.choice([8, 16, 20, 24, 28, 30, 31, 32])
            base = rng.choice(pool) if pool else "10.0.0.0"
            ops.append(["check_block", [f"{base}/{p}"]])
        elif r < 0.75 and pool:
            v = int.from_bytes(bytes(int(x) for x in rng.choice(pool).split(".")), "big")
            v ^= rng.getrandbits(rng.choice([0, 2, 4, 8]))
            ops.append(["check", [ip_str(v)]])
        else:
            ops.append(["check", [ip_str((10 << 24) | rng.getrandbits(24) if rng.random() < .8 else rng.getrandbits(32))]])
    return ops


def tests():
    rng = random.Random(7)
    t = [
        C("Example: check", EXAMPLE, chk("10.0.0.7", "10.0.0.8", "10.9.9.9", "8.8.8.8")),
        C("No rules -> default deny", [], chk("1.2.3.4", "0.0.0.0", "255.255.255.255")),
        C("First match wins, not most specific", [["ALLOW", "192.168.0.0/16"], ["DENY", "192.168.1.1"]],
          chk("192.168.1.1", "192.168.200.3", "192.169.0.0")),
        C("Bare address equals /32", [["ALLOW", "1.2.3.4"], ["ALLOW", "5.6.7.8/32"]], chk("1.2.3.4", "1.2.3.5", "5.6.7.8")),
        C("/0 matches everything", [["DENY", "9.9.9.9"], ["ALLOW", "0.0.0.0/0"]], chk("9.9.9.9", "0.0.0.0", "255.255.255.255")),
        C("Host bits ignored", [["ALLOW", "10.1.2.3/8"], ["ALLOW", "172.16.5.77/12"]],
          chk("10.200.0.1", "11.0.0.0", "172.31.255.255", "172.32.0.0")),
        C("Odd prefix lengths", [["DENY", "128.0.0.0/1"], ["ALLOW", "64.0.0.0/3"], ["ALLOW", "100.64.0.0/10"]],
          chk("128.0.0.1", "127.255.255.255", "64.0.0.0", "95.255.255.255", "96.0.0.0", "100.127.255.255", "100.128.0.0")),
        C("Duplicate patterns: earlier wins", [["DENY", "10.0.0.0/8"], ["ALLOW", "10.0.0.0/8"]], chk("10.1.1.1")),
        C("Example: check_block", EXAMPLE, blk("10.0.0.0/24", "10.0.0.8/29", "10.1.0.0/16", "0.0.0.0/0", "10.0.0.7"), tag="Follow-up"),
        C("Block with no rules", [], blk("0.0.0.0/0", "1.2.3.0/24"), tag="Follow-up"),
        C("Block fully covered by small rules", [["ALLOW", "10.0.0.0/25"], ["ALLOW", "10.0.0.128/25"]],
          blk("10.0.0.0/24", "10.0.0.0/23", "10.0.0.64/26"), tag="Follow-up"),
        C("Earlier inner rule with the same action", [["ALLOW", "10.0.0.5"], ["ALLOW", "10.0.0.0/24"]],
          blk("10.0.0.0/24", "10.0.0.0/16"), tag="Follow-up"),
        C("Later inner rule is shadowed", [["DENY", "10.0.0.0/8"], ["ALLOW", "10.1.0.0/16"], ["ALLOW", "0.0.0.0/0"]],
          blk("10.0.0.0/8", "10.1.0.0/16", "8.0.0.0/5", "0.0.0.0/0"), tag="Follow-up"),
        C("Block given with host bits", EXAMPLE, blk("10.0.0.200/24", "10.0.0.9/29"), tag="Follow-up"),
    ]
    for s in range(3):
        rules = rand_rules(rng, rng.randint(3, 15))
        t.append(C(f"Random small #{s + 1}", rules, rand_ops(rng, rules, 40, blocks=False), hidden=True))
    for s in range(3):
        rules = rand_rules(rng, rng.randint(3, 15))
        t.append(C(f"Random blocks #{s + 1}", rules, rand_ops(rng, rules, 40), hidden=True, tag="Follow-up"))
    rules = rand_rules(rng, 5000)
    t.append(C("5k rules, 20k checks", rules, rand_ops(rng, rules, 20000, blocks=False), hidden=True))
    rules = rand_rules(rng, 5000)
    t.append(C("5k rules, 10k mixed calls", rules, rand_ops(rng, rules, 10000), hidden=True, tag="Follow-up"))
    return t


def scale(n):
    rng = random.Random(n)
    rules = rand_rules(rng, n)
    return C(f"n={n}", rules, rand_ops(rng, rules, n, blocks=False))


SCALE = {"sizes": [500, 1000, 2000, 4000, 8000, 16000], "label": "n = rules = check calls"}
