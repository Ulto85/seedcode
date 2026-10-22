---
title: CIDR Firewall
difficulty: Medium
source: Databricks SWE technical phone screen, "IpFirewall" / CIDR rule matching (widely reported 2025–2026)
order: 1
minutes: 60
tags: bit manipulation, trie, design
---
You're writing the rule engine for a network firewall. It's configured with an **ordered** list of rules; each rule
pairs an action with an IPv4 pattern.

```
rules: list[list[str]]     # [[action, pattern], ...]   action is "ALLOW" or "DENY"
```

A pattern is either a single address like `"10.0.0.7"` (same as `/32`) or a CIDR block like `"10.0.0.0/8"`.
A CIDR `a.b.c.d/p` covers every address whose first `p` bits equal the first `p` bits of `a.b.c.d`
(`0 ≤ p ≤ 32`; `/0` covers everything). If the host bits of the pattern aren't zero, ignore them
(`"10.1.2.3/8"` means `"10.0.0.0/8"`).

**First match wins:** an address gets the action of the *earliest* rule in the list that covers it.
If no rule covers it, the answer is `"DENY"` (default deny).

### Part 1
```
Firewall(rules)
check(ip: str) -> str          # "ALLOW" or "DENY"
```

### Follow-up: whole blocks
```
check_block(cidr: str) -> str  # "ALLOW" | "DENY" | "MIXED"
```
Return `"ALLOW"` if **every** address in the block would be allowed by `check`, `"DENY"` if every address would be
denied, and `"MIXED"` otherwise. `cidr` uses the same pattern format (a bare address is a `/32` block).

### Example
```
rules = [["DENY",  "10.0.0.7"],
         ["ALLOW", "10.0.0.0/24"],
         ["DENY",  "10.0.0.0/8"],
         ["ALLOW", "0.0.0.0/0"]]

check("10.0.0.7")     -> "DENY"    # rule 0 matches first
check("10.0.0.8")     -> "ALLOW"   # rule 1
check("10.9.9.9")     -> "DENY"    # rule 2
check("8.8.8.8")      -> "ALLOW"   # rule 3
check_block("10.0.0.0/24")  -> "MIXED"   # .7 is denied, the rest allowed
check_block("10.0.0.8/29")  -> "ALLOW"   # 10.0.0.8 – 10.0.0.15
check_block("10.1.0.0/16")  -> "DENY"
check_block("0.0.0.0/0")    -> "MIXED"
```

### Constraints
- Up to 10⁴ rules and 10⁵ calls; all inputs are well-formed.
- Scanning every rule on every call is O(R) per query; it is accepted for a first pass, but the large hidden tests
  expect something faster. Think about what structure gives you "all rules that are prefixes of this address".
- Exact rule input format and the `MIXED` follow-up are reconstructed from candidate reports (the original wording is
  not public). Some interviewers phrase the follow-up as "is this block fully allowed / fully cancelled?"
