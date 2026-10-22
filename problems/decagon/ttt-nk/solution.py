def count_games_nk(n: int, k: int) -> int:
    lines = []
    for r in range(n):
        for c in range(n):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = [(r + i * dr, c + i * dc) for i in range(k)]
                if all(0 <= a < n and 0 <= b < n for a, b in cells):
                    lines.append([a * n + b for a, b in cells])
    by_cell = [[] for _ in range(n * n)]
    for line in lines:
        for x in line:
            by_cell[x].append(line)

    memo = {}
    board = ["."] * (n * n)

    def go(player, filled):
        key = "".join(board)
        if key in memo:
            return memo[key]
        total = 0
        for i in range(n * n):
            if board[i] == ".":
                board[i] = player
                if filled + 1 == n * n or any(all(board[j] == player for j in l) for l in by_cell[i]):
                    total += 1
                else:
                    total += go("O" if player == "X" else "X", filled + 1)
                board[i] = "."
        memo[key] = total
        return total

    return go("X", 0)
