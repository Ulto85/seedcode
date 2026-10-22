from engine.spec import fn


def tests():
    return [
        fn("1x1, k=1", "count_games_nk", 1, 1),
        fn("2x2, k=2", "count_games_nk", 2, 2),
        fn("3x3, k=3 (classic)", "count_games_nk", 3, 3),
        fn("3x3, k=2", "count_games_nk", 3, 2),
        fn("3x3, k=1", "count_games_nk", 3, 1, hidden=True),
        fn("2x2, k=1", "count_games_nk", 2, 1, hidden=True),
        # precomputed: the reference takes ~40s and ~80s on these
        fn("4x4, k=3 (memoization)", "count_games_nk", 4, 3, tag="Stretch", expected=1281016086768),
        fn("4x4, k=4 (memoization)", "count_games_nk", 4, 4, tag="Stretch", expected=15038733958272),
    ]
