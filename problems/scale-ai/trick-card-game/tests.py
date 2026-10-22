import random
from engine.spec import fn

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
FULL = [r + s for s in "CDHS" for r in RANKS]
EX = ["AS", "2C", "10H", "KD", "3S", "JC", "5H", "2D"]


def shuffled(rng, n=52):
    d = FULL[:]
    rng.shuffle(d)
    return d[:n]


def tests():
    rng = random.Random(2024)
    t = [
        fn("Example deal", "deal", EX),
        fn("Empty deck", "deal", []),
        fn("Sorted full deck", "deal", FULL),
        fn("Sort by suit then rank (10 after 9)", "deal", ["10C", "AH", "9D", "2S", "9C", "KH", "10D", "3S"]),
        fn("Example tricks", "play_tricks", EX, tag="Part 2"),
        fn("Must follow suit", "play_tricks", ["9H", "2H", "AC", "3D", "4C", "KH", "QC", "JD"], tag="Part 2"),
        fn("Leader rank tie -> clubs first", "play_tricks", ["AC", "2D", "3D", "4D", "AH", "5D", "6D", "7D"], tag="Part 2"),
        fn("Void player discards lowest", "play_tricks", ["KS", "3H", "5C", "2C", "QS", "2H", "9D", "JS"], tag="Part 2"),
        fn("Winner leads next trick", "play_tricks", shuffled(random.Random(1), 12), tag="Part 2"),
        fn("Example score", "score_game", EX, tag="Part 3"),
        fn("Nobody scores -> player 0 wins", "score_game", ["2C", "3C", "4C", "6C"], tag="Part 3"),
        fn("Tie -> lowest index", "score_game", ["KS", "2S", "3S", "4S", "2H", "3H", "KH", "4H"], tag="Part 3"),
        fn("Full game", "score_game", shuffled(random.Random(9)), tag="Part 3"),
    ]
    for s in range(4):
        t.append(fn(f"Random deal #{s + 1}", "deal", shuffled(rng, 4 * rng.randint(1, 13)), hidden=True))
    for s in range(6):
        t.append(fn(f"Random full game log #{s + 1}", "play_tricks", shuffled(rng), tag="Part 2", hidden=True))
    for s in range(6):
        t.append(fn(f"Random full game score #{s + 1}", "score_game", shuffled(rng), tag="Part 3", hidden=True))
    return t
