LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def _won(b):
    return any(b[a] != "." and b[a] == b[c] == b[d] for a, c, d in LINES)


def count_sequences(board: list[str], player: str) -> int:
    b = list("".join(board))
    if _won(b) or "." not in b:
        return 1

    def dfs(turn):
        total = 0
        for i in range(9):
            if b[i] == ".":
                b[i] = turn
                if _won(b) or "." not in b:
                    total += 1
                else:
                    total += dfs("O" if turn == "X" else "X")
                b[i] = "."
        return total

    return dfs(player)
