---
title: Article Vote Tracker
difficulty: Easy
source: Rippling SWE coding screen, "article voting tracker" (reported Dec 2025 and May 2026; follow-up reconstructed)
order: 4
minutes: 40
timeout: 20
tags: design, hash map, deque, heap
---
Build the vote tracker behind an internal knowledge base. Users upvote or downvote articles, and the product wants
each user's recent voting activity, plus (in the follow-up) live article scores.

### Part 1
```
VoteTracker()
vote(user_id: str, article_id: str, vote: str) -> str      # vote is "UP" or "DOWN"
get_last_votes(user_id: str) -> list                        # list of [article_id, vote, event_number]
```
Only a **change** counts. Each `(user, article)` pair remembers the user's latest vote on that article:
- First vote by this user on this article → counted, return `"NEW"`.
- Different from their latest vote on it → counted, return `"FLIP"`. (`UP → DOWN → UP` is three counted votes.)
- Same as their latest vote on it → ignored, return `"DUPLICATE"`.

Every counted vote gets an **event number** from a single counter shared by all users: `1, 2, 3, …`. Ignored votes
don't consume a number.

`get_last_votes(user_id)` returns that user's **3 most recent counted votes, newest first**, each as
`[article_id, vote, event_number]`. Fewer than 3 → return what there is; unknown user or no counted votes → `[]`.

### Follow-up: scores
```
score(article_id: str) -> int
top_article() -> str | None
```
- An article's **score** is (number of users whose latest vote on it is `UP`) − (number whose latest vote is
  `DOWN`). A flip from `UP` to `DOWN` therefore moves the score by `-2`. Unknown article → `0`.
- `top_article()` returns the article with the highest score among articles that have **ever received a counted
  vote** (even if their score is now `0` or negative). Ties → the lexicographically smallest `article_id`. No counted
  votes yet → `None`.

### Example
```
t = VoteTracker()
t.vote("ann", "a1", "UP")      -> "NEW"         # event 1
t.vote("ann", "a1", "UP")      -> "DUPLICATE"
t.vote("bob", "a2", "DOWN")    -> "NEW"         # event 2
t.vote("ann", "a1", "DOWN")    -> "FLIP"        # event 3
t.vote("ann", "a3", "UP")      -> "NEW"         # event 4
t.vote("ann", "a2", "UP")      -> "NEW"         # event 5
t.get_last_votes("ann")        -> [["a2", "UP", 5], ["a3", "UP", 4], ["a1", "DOWN", 3]]
t.get_last_votes("zed")        -> []
t.score("a1")                  -> -1
t.score("a2")                  -> 0             # bob DOWN, ann UP
t.top_article()                -> "a3"          # a3: 1, a2: 0, a1: -1
```

### Constraints
- Up to 2 × 10⁵ operations, up to 5 × 10⁴ distinct articles and users.
- Every operation should be `O(1)` or `O(log n)` (amortized). Scanning the whole history for `get_last_votes`, or
  every article for `top_article`, is too slow for the hidden tests.

### What the interviewer cares about
- Picking the right state: latest vote per `(user, article)`, a bounded recent-history per user (a `deque(maxlen=3)`).
- The "only count changes" rule and the global counter not advancing on duplicates.
- For the follow-up, keeping the max under updates: scores change one at a time, so a heap with **lazy deletion**
  (push the new `(-score, article)`, skip stale entries when reading the top) works well.
