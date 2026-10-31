---
name: replan-on-failure
description: When a step's check fails, a tool errors, or an assumption turns out false mid-task. Use to stop, diagnose by one measurement, and rewrite only the remaining steps, with a cap on replans.
quality: Execution
---
# Replan on failure
1. **Stop.** Do not retry the same action. Record in the task list: step, what failed, the evidence (exact error or number).
2. **Classify** in one word: wrong assumption, environment problem, bad plan, or external limit.
3. **Probe once:** the cheapest measurement that separates the causes (run a command, read a log line). No new theory without it.
4. **Rewrite only the remaining steps.** Keep finished steps and their results; give each new step a check.
5. **Cap:** 2 replans per task. A third failure: stop, report the evidence and the options, ask the user.
6. If the lesson is reusable, write it down in the Archive step.

Never turn a failing check green by weakening the check (deleting assertions, loosening a bound, skipping a test). Fix the cause, or report the check as failed.
