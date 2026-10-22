from collections import defaultdict, deque

DEFAULT_LIMITS = {"user": [3, 600], "team": [10, 600], "company": [20, 600]}


def _simulate(user_to_team, team_to_company, attempts, limits):
    """One deque of accepted timestamps per (level, id). Timestamps never decrease, so expired
    entries are popped from the front: amortized O(1) per attempt, O(n) total.
    Space: O(accepted notifications still inside their window)."""
    levels = [(lvl, limits[lvl][0], limits[lvl][1]) for lvl in ("user", "team", "company") if lvl in limits]
    windows = defaultdict(deque)
    out = []
    for user, ts in attempts:
        team = user_to_team[user]
        ids = {"user": user, "team": team, "company": team_to_company[team]}
        queues = []
        ok = True
        for lvl, cap, window in levels:
            q = windows[(lvl, ids[lvl])]
            while q and ts - q[0] >= window:
                q.popleft()
            queues.append(q)
            if len(q) >= cap:
                ok = False
        if ok:
            for q in queues:
                q.append(ts)
        out.append(ok)
    return out


def should_send_notifications(user_to_team: dict, team_to_company: dict, attempts: list) -> list:
    return _simulate(user_to_team, team_to_company, attempts, DEFAULT_LIMITS)


def should_send_with_limits(user_to_team: dict, team_to_company: dict, attempts: list, limits: dict) -> list:
    return _simulate(user_to_team, team_to_company, attempts, limits)
