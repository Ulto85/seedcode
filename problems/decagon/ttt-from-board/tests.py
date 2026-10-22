from engine.spec import fn

CASES = [
    (["...", "...", "..."], "X", "Empty board"),
    (["XOX", "OXX", "O.."], "O", "Two cells left, O to move"),
    (["XXX", "OO.", "..."], "O", "Already won by X (terminal)"),
    (["XOX", "XOO", "OXX"], "X", "Full board draw (terminal)"),
    (["X..", "...", "..."], "O", "X took a corner"),
    ([".X.", "...", "..."], "O", "X took an edge"),
    (["...", ".X.", "..."], "O", "X took the center"),
    (["XO.", "...", "..."], "X", "Two moves in"),
    (["XO.", ".X.", "..O"], "X", "Mid-game, X to move"),
    (["XX.", "OO.", "..."], "X", "X has an immediate win available"),
    (["OX.", "XO.", "X.."], "O", "O can win on the diagonal"),
    (["XOX", "...", "OXO"], "X", "Middle row open"),
]


def tests():
    return [fn(name, "count_sequences", b, p, hidden=i >= 8) for i, (b, p, name) in enumerate(CASES)]
