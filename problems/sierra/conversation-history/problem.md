---
title: Conversation History Compaction
difficulty: Medium
source: Sierra SWE technical screen, "Conversation agent history: paginated fetching, then token-limit compaction" (reported on PracHub, 2026). This is the compaction part; pinned-system and tool-group rules are reconstructed from the reported follow-up topics.
order: 2
minutes: 50
tags: design, deque, running total, LLM context
---
You're building the message-history layer of a conversation agent: the component that stores a conversation's
messages and hands them to the language model. The model has a **token limit**, so after every new message the
history must be compacted by dropping the **oldest** messages until it fits. Token counts are given; you never
tokenize text.

```
ConversationHistory(limit)
add(msg_id, role, tokens) -> int     # number of messages dropped by this add, or -1 if rejected
context() -> list[str]               # ids currently in the history, oldest first (insertion order)
total_tokens() -> int                # sum of tokens currently in the history
```

`role` is one of `"user"`, `"assistant"`, `"system"`, `"tool"`. Ids are unique, `1 <= tokens`, `1 <= limit`.

### Part 1
Only `"user"` and `"assistant"` messages.
- After adding a message, while the total is **greater than** `limit`, drop the oldest message. A total exactly
  equal to `limit` is fine.
- The newest message is never silently dropped: if a message on its own is bigger than `limit`, `add` **rejects**
  it, returns `-1` and changes nothing.
- `add` will be called after every message of a long conversation, so it must be cheap: no re-summing the history
  and no shifting a whole list to drop from the front.

```
h = ConversationHistory(10)
h.add("u1", "user", 4)       -> 0       # [u1]          total 4
h.add("a1", "assistant", 3)  -> 0       # [u1, a1]      total 7
h.add("u2", "user", 5)       -> 1       # 12 > 10, drop u1 -> [a1, u2] total 8
h.add("big", "user", 11)     -> -1      # can never fit: rejected, nothing changes
h.add("u3", "user", 10)      -> 2       # drop a1, u2 -> [u3] total 10
h.total_tokens()             -> 10
```

### Part 2: pinned system messages
`"system"` messages (instructions, policies) are **pinned**: they count toward the total but are never dropped.
Compaction drops the oldest **non-system** messages. `context()` still lists every message in insertion order,
system messages included.
- Any message (system or not) is rejected with `-1` if `pinned_tokens + its tokens > limit`, where
  `pinned_tokens` is the sum of system messages already in the history. Otherwise it's added, and older non-system
  messages are dropped as needed (adding a system message can drop non-system ones).
```
h = ConversationHistory(10)
h.add("s1", "system", 3)     -> 0       # pinned 3
h.add("u1", "user", 4)       -> 0       # total 7
h.add("a1", "assistant", 4)  -> 1       # 11 > 10, drop u1 -> [s1, a1]
h.add("u2", "user", 8)       -> -1      # 3 + 8 > 10
h.add("s2", "system", 2)     -> 0       # [s1, a1, s2] total 9
```

### Follow-up: tool results stay with their call
A `"tool"` message is the result of a tool call, and the model breaks if it sees a result without the call that
produced it. So messages are dropped in **units**:
- Every `"user"` or `"assistant"` message starts a new unit.
- A `"tool"` message joins the **newest unit currently in the history**. If there is no unit (none added yet, or
  all dropped), it starts its own unit.
- Compaction drops whole units, oldest first. System messages are not part of any unit.
- Rejection: a tool message that joins a unit is rejected (`-1`, no change) if `pinned_tokens + unit_tokens +
  its tokens > limit`. Otherwise the unit it's in (the newest) is never dropped by that add.
```
h = ConversationHistory(12)
h.add("u1", "user", 2)       -> 0       # units: [u1]
h.add("a1", "assistant", 3)  -> 0       # units: [u1] [a1]
h.add("t1", "tool", 4)       -> 0       # units: [u1] [a1 t1]      total 9
h.add("u2", "user", 4)       -> 1       # 13 > 12, drop [u1]        total 11
h.add("a2", "assistant", 2)  -> 2       # 13 > 12, drop [a1 t1]     total 6
h.context()                  -> ["u2", "a2"]
```
`add` returns the number of **messages** dropped (a unit of 3 messages counts 3).

### What the interviewer cares about
- A running total and O(1) removal from the front (a deque), so compaction is cheap after every message
- Spelling out the edge cases before coding: exactly at the limit, an oversized message, empty history
- Extending cleanly when the rules change: pinned messages, grouped messages
