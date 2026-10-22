import random
from engine.spec import fn

EXAMPLE = [
    {"id": "p1", "emails": ["Ana@Mail.com"], "phones": []},
    {"id": "p2", "emails": [" ana@mail.com"], "phones": ["(415) 555-0101"]},
    {"id": "p3", "emails": ["not-an-email"], "phones": ["+1 415 555 0101"]},
    {"id": "p4", "emails": ["bo@x.io"], "phones": ["555-0101"]},
]


def P(i, emails=(), phones=()):
    return {"id": i, "emails": list(emails), "phones": list(phones)}


def messy_email(rng, person, domains):
    local = f"user{person}"
    dom = rng.choice(domains)
    r = rng.random()
    if r < 0.25:
        local = local[:2] + "." + local[2:]
    elif r < 0.45:
        local = local + "+" + rng.choice(["jobs", "mercor", "x"])
    elif r < 0.5:
        return rng.choice(["nobody", "a@@b.com", "@gmail.com", "+x@gmail.com", "x@"])
    if dom == "gmail.com" and rng.random() < 0.2:
        dom = "googlemail.com"
    s = local + "@" + dom
    if rng.random() < 0.3:
        s = s.upper()
    if rng.random() < 0.2:
        s = "  " + s + " "
    return s


def messy_phone(rng, person):
    d = f"{(person * 7919) % 10**10:010d}"
    r = rng.random()
    if r < 0.3:
        return f"({d[:3]}) {d[3:6]}-{d[6:]}"
    if r < 0.5:
        return f"+1 {d[:3]} {d[3:6]} {d[6:]}"
    if r < 0.6:
        return d[3:]                      # 7 digits: invalid
    if r < 0.65:
        return "2" + d                    # 11 digits not starting with 1: invalid
    return d


def random_profiles(rng, n, people, max_ids=3):
    domains = ["gmail.com", "mercor.com", "x.io"]
    out = []
    for i in range(n):
        person = rng.randrange(people)
        out.append(P(f"c{i:05d}",
                     [messy_email(rng, person if rng.random() < 0.8 else rng.randrange(people), domains) for _ in range(rng.randint(0, max_ids))],
                     [messy_phone(rng, person if rng.random() < 0.8 else rng.randrange(people)) for _ in range(rng.randint(0, max_ids - 1))]))
    rng.shuffle(out)
    return out


def tests():
    rng = random.Random(99)
    t = [
        fn("Example", "merge_profiles", EXAMPLE, False),
        fn("No profiles", "merge_profiles", [], False),
        fn("Profile with nothing", "merge_profiles", [P("z"), P("a")], False),
        fn("Transitive chain", "merge_profiles",
           [P("c", ["c@q.com"], ["4155550199"]), P("a", ["a@q.com"]), P("b", ["a@q.com", "c@q.com"]), P("d", [], ["415-555-0199"])], False),
        fn("Invalid ids don't glue people", "merge_profiles",
           [P("1", ["a@@b.com", "@x.com"], ["123"]), P("2", ["a@@b.com", "x@"], ["123"]), P("3", ["  "], ["+1"])], False),
        fn("Phone formats", "merge_profiles",
           [P("x", [], ["1-800-555-0000"]), P("y", [], ["8005550000"]), P("z", [], ["21800555000"]), P("w", [], ["+44 20 7946 0958"])], False),
        fn("Ids sort as strings", "merge_profiles", [P("10", ["s@s.s"]), P("9", ["S@S.S"]), P("100")], False),
        fn("Gmail aliases ignored in Part 1", "merge_profiles",
           [P("a", ["A.na+jobs@googlemail.com"]), P("b", ["ana@gmail.com"])], False),
        fn("Follow-up example", "merge_profiles",
           [P("a", ["A.na+jobs@googlemail.com"]), P("b", ["ana@gmail.com"])], True, tag="Follow-up"),
        fn("Follow-up: other domains untouched", "merge_profiles",
           [P("a", ["a.na+x@mercor.com"]), P("b", ["ana@mercor.com"]), P("c", ["an.a+1+2@gmail.com"]), P("d", ["ana@GMAIL.com"])],
           True, tag="Follow-up"),
        fn("Follow-up: empty local part is invalid", "merge_profiles",
           [P("a", ["+promo@gmail.com", "...@gmail.com"]), P("b", ["+other@gmail.com"]), P("c", [".+@googlemail.com"])],
           True, tag="Follow-up"),
    ]
    for s in range(3):
        t.append(fn(f"Random #{s + 1}", "merge_profiles", random_profiles(rng, 25, 12), False, hidden=True))
    for s in range(3):
        t.append(fn(f"Follow-up random #{s + 1}", "merge_profiles", random_profiles(rng, 25, 12), True, tag="Follow-up", hidden=True))
    t.append(fn("50k profiles", "merge_profiles", random_profiles(rng, 50000, 20000), False, hidden=True))
    t.append(fn("50k profiles, Gmail rules", "merge_profiles", random_profiles(rng, 50000, 20000), True, tag="Follow-up", hidden=True))
    return t


def scale(n):
    return fn(f"n={n}", "merge_profiles", random_profiles(random.Random(n), n, max(1, n // 3)), True)


SCALE = {"sizes": [1500, 3000, 6000, 12000, 24000, 48000], "label": "n = number of profiles"}
