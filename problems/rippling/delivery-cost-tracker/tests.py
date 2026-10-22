import random
from engine.spec import cls

K = "DeliveryTracker"


def C(name, ops, **kw):
    return cls(name, K, [], ops, **kw)


def random_ops(rng, n, drivers=8, horizon=200000, follow=False, max_len=7200):
    ops = [["add_driver", [d, rng.randint(1, 5000)]] for d in range(1, drivers + 1)]
    clock = 0
    for _ in range(n):
        r = rng.random()
        clock += rng.randint(0, 40)
        if r < 0.45:
            s = rng.randint(0, horizon)
            e = s + rng.randint(-50, max_len)
            ops.append(["record_delivery", [rng.randint(0, drivers + 1), s, e]])
        elif r < 0.6:
            ops.append(["get_total_cost", []])
        elif r < 0.75:
            ops.append(["pay_up_to", [rng.randint(0, horizon + max_len)]])
        elif r < 0.9:
            ops.append(["get_unpaid_cost", []])
        elif r < 0.95:
            ops.append(["add_driver", [rng.randint(1, drivers + 3), rng.randint(1, 5000)]])
        elif follow:
            ops.append(["max_active_drivers", [rng.randint(0, horizon + 86400)]])
        else:
            ops.append(["get_total_cost", []])
    return ops


EXAMPLE = [
    ["add_driver", [1, 2000]], ["add_driver", [2, 1500]], ["add_driver", [1, 9999]],
    ["record_delivery", [1, 0, 5400]], ["record_delivery", [2, 3600, 4500]], ["record_delivery", [3, 0, 10]],
    ["get_total_cost", []], ["record_delivery", [2, 0, 100]], ["get_total_cost", []],
    ["pay_up_to", [5000]], ["get_unpaid_cost", []], ["pay_up_to", [5000]], ["max_active_drivers", [5000]],
]


def tests():
    rng = random.Random(7)
    t = [
        C("Example (Part 1 calls)", EXAMPLE[:9]),
        C("Empty tracker", [["get_total_cost", []], ["add_driver", [5, 100]], ["get_total_cost", []]]),
        C("Unknown driver / end before start", [["add_driver", [1, 3600]], ["record_delivery", [2, 0, 100]],
                                                ["record_delivery", [1, 100, 50]], ["get_total_cost", []]]),
        C("Zero-length delivery is valid and free", [["add_driver", [1, 3600]], ["record_delivery", [1, 70, 70]],
                                                     ["get_total_cost", []]]),
        C("Duplicate add keeps the original rate", [["add_driver", [1, 1000]], ["add_driver", [1, 99999]],
                                                    ["record_delivery", [1, 0, 3600]], ["get_total_cost", []]]),
        C("Round only once (3 x 1/3 cent)", [["add_driver", [1, 1]], ["record_delivery", [1, 0, 1200]],
                                             ["get_total_cost", []], ["record_delivery", [1, 5000, 6200]],
                                             ["get_total_cost", []], ["record_delivery", [1, 9000, 10200]],
                                             ["get_total_cost", []]]),
        C("Exact half cent rounds up", [["add_driver", [7, 1]], ["record_delivery", [7, 0, 1800]], ["get_total_cost", []],
                                        ["record_delivery", [7, 0, 3600]], ["get_total_cost", []]]),
        C("Overlapping deliveries both charged", [["add_driver", [1, 6000]], ["record_delivery", [1, 0, 3600]],
                                                  ["record_delivery", [1, 1800, 5400]], ["get_total_cost", []]]),
        C("Example (with payments + follow-up)", EXAMPLE, tag="Follow-up"),
        C("Pay boundary: end == time is paid", [["add_driver", [1, 3600]], ["record_delivery", [1, 0, 100]],
                                                ["record_delivery", [1, 50, 101]], ["pay_up_to", [100]],
                                                ["get_unpaid_cost", []], ["get_total_cost", []]], tag="Part 2"),
        C("Paying twice / earlier time", [["add_driver", [1, 3600]], ["record_delivery", [1, 0, 100]],
                                          ["pay_up_to", [500]], ["pay_up_to", [500]], ["pay_up_to", [10]],
                                          ["get_unpaid_cost", []]], tag="Part 2"),
        C("Late-recorded delivery settled by a later pay", [["add_driver", [1, 3600]], ["pay_up_to", [1000]],
                                                            ["record_delivery", [1, 0, 200]], ["get_unpaid_cost", []],
                                                            ["pay_up_to", [1000]], ["get_unpaid_cost", []]], tag="Part 2"),
        C("Unpaid cost rounds on the remaining exact sum", [["add_driver", [1, 1]], ["record_delivery", [1, 0, 1200]],
                                                            ["record_delivery", [1, 0, 1201]], ["record_delivery", [1, 0, 3000]],
                                                            ["pay_up_to", [1200]], ["get_unpaid_cost", []]], tag="Part 2"),
        C("Same driver overlapping counts once", [["add_driver", [1, 100]], ["add_driver", [2, 100]],
                                                  ["record_delivery", [1, 0, 1000]], ["record_delivery", [1, 500, 1500]],
                                                  ["record_delivery", [2, 1400, 2000]], ["max_active_drivers", [3000]]],
          tag="Follow-up"),
        C("Back-to-back deliveries don't overlap", [["add_driver", [1, 100]], ["add_driver", [2, 100]],
                                                    ["record_delivery", [1, 0, 100]], ["record_delivery", [2, 100, 200]],
                                                    ["max_active_drivers", [1000]]], tag="Follow-up"),
        C("24h window edges", [["add_driver", [1, 100]], ["add_driver", [2, 100]], ["add_driver", [3, 100]],
                               ["record_delivery", [1, 0, 1000]], ["record_delivery", [2, 900, 1100]],
                               ["record_delivery", [3, 86400, 90000]],
                               ["max_active_drivers", [87000]], ["max_active_drivers", [87500]],
                               ["max_active_drivers", [86400]], ["max_active_drivers", [200000]]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random #{s + 1}", random_ops(rng, 60), tag="Part 2", hidden=True))
    for s in range(2):
        t.append(C(f"Random with window queries #{s + 1}", random_ops(rng, 80, drivers=5, follow=True),
                   tag="Follow-up", hidden=True))
    t.append(C("60k ops (no rescanning on every query)", random_ops(rng, 60000, drivers=200, horizon=10**8),
               tag="Part 2", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", random_ops(random.Random(n), n, drivers=50, horizon=10**8))


SCALE = {"sizes": [4000, 8000, 16000, 32000, 64000, 128000, 256000], "label": "n = number of operations"}
