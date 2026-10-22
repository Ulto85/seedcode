# SeedCode 🌱

*LeetCode is for FAANG. SeedCode is for the startups.*

LeetCode-style practice for the coding interviews top startups **actually** ask, rebuilt from public interview reports,
with real test suites and an AI interviewer you can probe for hints.

- **Reported questions, by company.** Versioned carts, CIDR firewalls, order books, currency graphs, and
  other practical multi-part problems, not textbook puzzles.
- **Real test suites.** Visible examples, hidden edge cases, and large hidden tests that catch slow solutions. Expected
  outputs are generated from reference solutions, so they're always consistent.
- **📈 Complexity profiler.** Runs your code on growing inputs, fits the curve, and charts your time and memory against
  the reference: "yours O(n²) vs reference O(n)".
- **⏱ Interview timer.** A per-problem countdown (or stopwatch) you can pause, resume, reset and resize. It goes red
  when you're over time.
- **🎲 Interview mode.** Picks a random unsolved problem from a company with a fresh editor and a running clock.
- **Probe the interviewer.** Ask Claude for a nudge, a hint, debugging, a complexity explanation, an interviewer-style
  review, the approach or the full solution. Claude Code reads your code and test results and answers in your terminal.
  The prompt is also copied to your clipboard for any other AI chat.
- **Zero dependencies.** Python 3.9+ standard library. No build step.

## Quick start
```bash
git clone <this repo> && cd seedcode
python3 server.py
# open http://localhost:8765
```

### With Claude Code (recommended)
```bash
claude            # in the repo root
> let's practice
```
Claude starts the server and watches the **Probe** button. When you click it, Claude answers in the terminal at the
level you chose. See [CLAUDE.md](CLAUDE.md) for the protocol. Without Claude Code, Probe still copies a ready-made prompt
to your clipboard.

## Keyboard
| | |
|---|---|
| Cmd/Ctrl + Enter | Run visible tests |
| Cmd/Ctrl + Shift + Enter | Submit (hidden + stretch tests) |
| Cmd/Ctrl + I | Probe |
| Alt + P | Pause / resume timer |
| Esc | Close dialogs |

## Companies
66 problems across 16 companies. 57 are based on questions candidates reported; the 9 marked * are practice problems written in a company's reported style, for companies with little public data (labeled "Practice · in their style" in the app).

Want another company? In Claude Code, just say **"add <company>"** (see [SEARCH.md](SEARCH.md)).

| Company | Problems |
|---|---|
| **Anthropic** | Stack Samples to Trace Events, In-Memory Banking System (4 Levels), Same-Host Web Crawler, Greedy Longest-Match Tokenizer |
| **Cognition** | Agent File Editor Tool *, Apply a Model-Generated Patch *, Code Search Index *, Directory Sync Plan * |
| **Coinbase** | Range & Interleaving Iterators, Crypto Order Manager, Limit Order Book, In-Memory Banking System |
| **Cursor (Anysphere)** | Merkle Tree Repo Diff, Streaming Code Fence Parser, Hierarchical Notification Rate Limiter, Transactional Key-Value Store |
| **Databricks** | KV Store Load Monitor, CIDR Firewall, Snapshot Set Iterator, Fastest Commute Mode |
| **Decagon** | Versioned Recipe Cart, Count Legal Tic-Tac-Toe Games, Count Game Completions From a Board, N×N, K-in-a-Row Game Count, CSAT Sliding Window Tracker, Exclusive CPU Time From Nested Logs |
| **Glean** | Parallel Document Indexers, Department-Scoped Typeahead, BPE Tokenizer, Synonyms From Shared Context |
| **Harvey** | Source Highlighting with Citations, Document Vault with Duplicate Names, Eager Spreadsheet, Cosine Retrieval and Recall@k |
| **Mercor** | One-Way Street Parking, Referral Network, Merge Duplicate Candidate Profiles *, Contractor Payouts with Referral Bonuses * |
| **Modal** | Sort a Hundred Million Digits, Replayable Shuffle, Image Chunk Cache with Pinning *, GPU Task Placement * |
| **OpenAI** | cd With Symbolic Links, GPU Credit Ledger, Spreadsheet With Formulas, Leftmost-Fit Memory Allocator |
| **Perplexity** | Task Dependencies and Failure, Time-Versioned KV Store with Restore, In-Memory File System, Credit Tracker with Expirations |
| **Ramp** | Flight Tracker, URL Maze, Recurring Transactions, Concatenation Spreadsheet |
| **Rippling** | Delivery Cost Tracker, Expense Rules Engine, Flatten the Org Chart, Article Vote Tracker |
| **Scale AI** | Dependency-Aware Task Scheduler, Party Hours by Town, Update a Neuron Grid, Four-Player Trick-Taking Game |
| **Sierra** | Fetch All Pages, Then Compact to a Token Budget, Conversation History Compaction, Header-Aware Markdown Chunker, Flaky Catalog Product Resolver * |

## How it works
```
app/index.html     single-page UI (CodeMirror editor, Markdown problems)
server.py          tiny HTTP API
engine/harness.py  runs your code in an isolated subprocess (tests / record / benchmark modes)
engine/core.py     discovers problems, generates + caches expected outputs, fits complexity curves
problems/          one folder per company, one folder per problem
```
Your code is saved in the browser and to `work/` on every run. Solved problems are marked in the sidebar.

## Contributing
Easiest way: open Claude Code in the repo and say **"add <company>"**. It follows [SEARCH.md](SEARCH.md) to research
reported questions, write problems with test suites, and validate them.

By hand: New companies and problems are just folders. See [CONTRIBUTING.md](CONTRIBUTING.md), then run
`python3 tools/validate.py <company>`. Questions are written in our own words from public reports. Please don't paste
paywalled content.

## Disclaimer
Not affiliated with any company listed. Problems are reconstructions of publicly reported interview questions and may
differ from what you'll see. Use them for practice, not as leaks.

## License
MIT
