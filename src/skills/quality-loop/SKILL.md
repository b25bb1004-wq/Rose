---
name: quality-loop
description: Start-of-task structure. Use at the start of any task bigger than a one-line answer, to pick a lane (quick, standard, heavy) and run Plan, Execute, Critique, Archive, Learn with the right skill at each step.
quality: Planning
---
# Quality loop
**Lane (decide first, one line):** quick = an answer or a small edit; standard = 3 to 5 steps; heavy = ambiguous, costly, risky or multi-session.

| Step | Quick | Standard | Heavy |
|---|---|---|---|
| Memory (service) | read your notes only if a project is named | same, plus grep past lessons | same, plus re-check any fact that may be stale |
| Plan | none | steps in the task list, each with a check, plus a toolbelt line per step | `python3 -I ~/.claude/quality-loop/toolbelt.py "<task>"`, then write the plan, then try to break it before executing. For a heavy task use `plan-any-task` (any task type, not only code): read the job, look at what exists, understand it, choose, write checked steps with sources, ask the user in up to 3 rounds, freeze, then ready the skills (one `skill-fitter` agent only if there are gaps; state its cost first). `planning-scout` stays as an optional lookup helper |
| Execute | do it | follow the steps; mark each done only after its check | same; a failed check: `replan-on-failure` |
| Critique | one check | `score-against-plan` | `score-against-plan` plus a judge that is not the author |
| Archive | none | one line in your notes | note, lessons, handoff |
| Learn | none | none | name one improvement; if reusable, write a skill with `quality:` in its frontmatter |

**Plan = outcome + one check + boundaries (what you are not doing) + stop condition.** Four lines, written before executing.
**Ledger = the task list.** Create the Archive step at plan time so it cannot be forgotten.
**Loop tick** (a scheduled prompt that says to run the next queue item): the queue is the plan. Skip the lane choice and the toolbelt, do the item, then the Archive step. Blocked: one line and stop.
**Cost rule:** state the item count and expected cost before any subagent or batch job; one subagent at a time.

## Rules
- Quick lane asks three questions only: is it irreversible, does it spend or send, may my knowledge be stale. Unsure: standard. A surprise at the first check upgrades the lane.
- Same check fails twice: replan (max 2), then stop and report.
- What already fires on its own (hooks, auto-loaded skills) is listed by your agent's settings; do not invoke it again.

## Failure modes to scan at Plan and at Critique
1 building before the user said go; 2 subagent fan-out; 3 forgetting the Archive step; 4 destructive cleanup without looking at the target first; 5 stating live facts from memory; 6 shipping UI or artifacts unchecked; 7 trusting an eval without a 10-item sanity check; 8 scope creep. Keep your own list here as you learn it.
