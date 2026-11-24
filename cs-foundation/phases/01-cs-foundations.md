# Phase 1 — Computer science foundations

**Dates:** 2026-12-21 → 2027-03-14 (W4–W15) · **Buffer:** W16, 2027-03-15 → 2027-03-21
**Prerequisites:** Phase 0 · [← Phase 0](00-setup.md) · [Learning path](../learning-path.md) · [Next: Phase 2 →](02-databases.md)

## Goal

Learn what is happening *under* my Python code: how memory works, why some algorithms are fast and others slow, what the OS does with processes and threads, and how a request travels across a network. Every later phase depends on this. Indexes are trees and hash maps, Docker is OS isolation, APIs are HTTP over TCP, Spark is distributed algorithms.

The project track turns my loose question-bank scripts into a real, tested Python package with a search engine I write myself.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | How computers represent data; C basics; compiling | [CS50x](https://cs50.harvard.edu/x/) Weeks 1–2 (lecture + 1 problem set) | Notes: bits, bytes, ASCII/Unicode, why Python ints are objects |
| 2 | Memory: stack, heap, pointers, `malloc`/`free` | CS50x Week 4 (Memory) | Diagram of stack vs heap for a small program |
| 3 | Big-O; binary search; sorting | CS50x Week 3 + *Grokking Algorithms* ch. 1–4 | Big-O table for common Python operations (list, dict, set) |
| 4 | Arrays, linked lists, hash tables, stacks, queues | CS50x Week 5 + *Grokking* ch. 5 | Explain why `dict` lookup is O(1) on average |
| 5 | Trees, BSTs, tries, heaps | [NeetCode roadmap](https://neetcode.io/roadmap): Trees, Tries, Heap sections (videos) | Hand-draw insert/delete for BST and heap |
| 6 | Graphs: BFS, DFS, topological sort, Dijkstra | *Grokking* ch. 6–9 | Notes: where DAGs appear later (Airflow, dbt!) |
| 7 | Greedy, dynamic programming | *Grokking* ch. 10–11 + NeetCode 1-D DP videos | Solve 1 DP problem 3 ways: brute → memo → table |
| 8 | OS: processes, scheduling, system calls | [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/) ch. 2, 4–7 | Explain fork/exec and what `ps` shows |
| 9 | OS: virtual memory, files, I/O | OSTEP ch. 13–15, 39–40 | Why reading a file in chunks saves memory |
| 10 | Concurrency: threads, locks, race conditions; Python GIL, asyncio | OSTEP ch. 26–28 + [Python asyncio docs](https://docs.python.org/3/library/asyncio.html) | Table: threads vs processes vs asyncio, when to use each |
| 11 | Networking: IP, TCP vs UDP, ports, DNS | [High Performance Browser Networking](https://hpbn.co/) ch. 1–3 + Julia Evans' [DNS explainer](https://wizardzines.com/comics/) | Trace `dig` and `curl -v` output line by line |
| 12 | HTTP/1.1 vs 2, TLS, how the web works end-to-end | HPBN ch. 4, 9–12 + [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview) | Write "what happens when I type a URL" in ≤ 1 page |

## Project track (in `quizlab`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | Domain models with `dataclasses` (`Subject`, `Question`); load `questions.csv`; type hints + `mypy` | `src/quizlab/domain.py` | Typing, OOP |
| 2 | CLI with [Typer](https://typer.tiangolo.com/): `quizlab list`, `quizlab add`, `quizlab show <id>` | Working CLI | Packaging, entry points |
| 3 | Repository pattern: one interface, two implementations (CSV, Postgres via psycopg, reusing [database/](../../database/) code) | `src/quizlab/storage/` | Abstraction, dependency injection |
| 4 | Test suite: fixtures, parametrize, temp Postgres via compose; coverage ≥ 80% | `tests/` + coverage report | Testing |
| 5 | **Inverted index from scratch:** tokenize, map token → set of question ids, AND/OR queries | `quizlab search "unit force"` | Hash maps, sets |
| 6 | TF-IDF ranking for search results; **trie** autocomplete for topic names | Ranked search + autocomplete | Tries, scoring |
| 7 | Benchmark linear scan vs index on 100k generated questions; plot time vs N | `docs/search-benchmark.md` with chart | Big-O in practice, viz |
| 8 | Quiz mode: Fisher-Yates shuffle; spaced repetition queue using `heapq` (next-due question) | `quizlab quiz` | Heaps, randomness |
| 9 | Streaming CSV import with generators + Postgres `COPY` in chunks; measure memory with `tracemalloc` | Import 1M rows using < 100 MB | Files, I/O, memory |
| 10 | Parallel import: threads vs processes vs async psycopg; measure and explain results | `docs/concurrency-benchmark.md` | Concurrency, GIL |
| 11 | Tiny HTTP server with raw `socket` (no framework) that serves a question as JSON | `scripts/raw_http_server.py`; tested with `curl -v` | TCP, HTTP by hand |
| 12 | Polish: README usage section, ADR 0002 (package structure), tag `v0.1.0` | GitHub release | Writing, Git |

## Done when

- [ ] I can explain the Big-O of list/dict/set operations and why without notes.
- [ ] I can draw stack vs heap memory, and explain process vs thread.
- [ ] I can explain "what happens when I type a URL" end-to-end.
- [ ] `quizlab` v0.1.0: CLI with search + quiz, ≥ 80% test coverage, mypy clean.
- [ ] Two benchmark reports (search, concurrency) with charts and conclusions.

## Threads this phase

- **DSA:** 2 [NeetCode 150](https://neetcode.io/practice) problems/week on that week's topic, saved in [python/](../../python/). Use my [practice loop](../../docs/how-to-practice-coding.md). After this phase, drop to 1/week.
- **Testing:** every module gets tests before it is merged.
- **Writing:** ADR 0002.

## Stretch goals

- CS50x Week 6–7 problem sets (Python, SQL) for extra practice.
- Implement a hash map with open addressing from scratch and compare with `dict`.
- Read *Computer Systems: A Programmer's Perspective* ch. 1 (big picture).

## Resources

- [Teach Yourself CS](https://teachyourselfcs.com/): reference map if I want to go deeper later
- *Grokking Algorithms* (2nd ed.), Aditya Bhargava
- [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/) (free)
- [High Performance Browser Networking](https://hpbn.co/) (free)
