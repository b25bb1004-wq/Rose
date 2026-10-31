---
name: score-against-plan
description: Critique a finished task by running the plan's own checks and giving a score. Use at the end of any standard or heavy task, before archiving.
quality: Critique
---
# Score against the plan
1. List the checks written in the plan. Run each one (command, test, count). Record pass, fail or **unverified** with the evidence. Never mark pass without running it.
2. **Score** = passed / total. Unverified counts as not passed.
3. Heavy tasks only: add four 0 to 5 marks: correctness, cleanliness (no leftovers, no stray files), cost (against the estimate), completeness.
4. **Award:** Good = all checks passed and cleanliness at least 4; Fair = at most one failure; Needs work otherwise. Say why in one line.
5. **Failure-mode scan:** check the list in `quality-loop`. Any hit caps the award at Fair and is named in the output.
6. Heavy: ask a judge that is not the author (another model, or the user) with the plan and the evidence; it must quote the text it objects to. Do not grade alone.
7. Output 6 lines: checks run, score, award, what broke, what to improve, where it was archived. Pass the verdict to the Archive step.
