LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
BY_CELL = [[l for l in LINES if c in l] for c in range(9)]


def game_outcomes() -> dict:
    res = {"X": 0, "O": 0, "draw": 0}
    board = ["."] * 9

    def dfs(player, filled):
        for i in range(9):
            if board[i] != ".":
                continue
            board[i] = player
            if any(all(board[j] == player for j in line) for line in BY_CELL[i]):
                res[player] += 1
            elif filled + 1 == 9:
                res["draw"] += 1
            else:
                dfs("O" if player == "X" else "X", filled + 1)
            board[i] = "."

    dfs("X", 0)
    return res


def count_games() -> int:
    return sum(game_outcomes().values())
