---
name: bounded-delegation
description: Plan subagent or batch fan-out so it cannot drain your usage limits. Use before spawning any subagent, background worker or batch job, and when a request names many parallel research tasks.
quality: Planning
---
# Bounded delegation
**Failure this prevents:** several unbounded research subagents launched for one request hit the daily and weekly usage limits, and some outputs were lost.
1. **Say it first, in one line:** item count and expected cost. If you cannot estimate the cost, run one item and measure.
2. **No parallel fan-out by default.** One worker at a time; do the thinking and judging inline.
3. **Every job gets a brief:** a deliverable path, a size cap (report in at most 10 lines), and a self-test. Workers write results to disk as they finish, so hitting a limit loses nothing.
4. **Check size before reading:** `wc -c` the output, then `head` or `grep` it. A 45 KB note read whole once cost about 9% of a limit.
5. **Re-run only the lost items,** inline, not the whole set.
6. **Waiting:** use a bounded loop (`for i in $(seq 1 60)`), never an open-ended one. `pgrep -f "worker"` inside a wait loop matches the loop's own shell and never ends; use the bracket trick `pgrep -f "[w]orker"` or test for the output file. macOS has no `timeout` command.
