from engine.spec import fn


def tests():
    return [
        fn("Total legal games", "count_games"),
        fn("Outcome breakdown", "game_outcomes", tag="Follow-up"),
    ]
