---
name: plan-any-task
description: Plan any heavy task (research, build, study, writing, admin, files, career, a decision; not only code) the way a researcher handles a new job. Read it, look at what already exists, understand it, choose, write checked steps with their sources, ask the user in up to 3 rounds, freeze the plan, then have one agent ready the skills. Use at the start of a heavy task, or when the user asks for a proper plan.
quality: Planning
---
# Plan any task
Heavy lane only: more than one repo, spends money, publishes or pushes, feeds a deliverable, or the user asks for a proper plan. Quick and standard lanes skip this. The plan has no length limit; it is as long as the task needs. Tokens are saved by free lookups first, stored digests, one question round per phase, and one skills agent at the end.

## Phase 0. Choose the planning tools first
1. Read the task once. Write one line: what kind of job this is and what is unknown (already done or published? stale knowledge? who reads it? what is reversible? money, long jobs, outward actions? must it look right?).
2. Pick planning tools for the unknown, not for the label. Run `python3 -I ~/.claude/quality-loop/toolbelt.py "<job in words>"` and use this table for what Rose ships:
| Unknown | Tool |
|---|---|
| is it already done or published | `prior-art-audit` |
| what does the user really want | ask in round 1 below |
| will the idea survive | try to break it before executing (see `quality-loop`) |
| long, costly or parallel work | `bounded-delegation` |
| an outward action (mail, post, push) | `verify-before-commit-push` |
| files or notes that might be removed | `archive-before-delete` |
| a third-party skill or plugin | `vet-third-party-skill` |
| a score or metric to trust | `eval-harness-sanity-check`, `selftest-mutation-check` |
3. Write them at the top of the plan ("planned with: ..."). No tool, no reason, no entry.

## Phases 1 to 6. The plan (one note, template below)
1. **Read the job.** Goal, what done looks like, who it is for, constraints, what is irreversible. **Ask round 1** (purpose and success).
2. **Look at what exists**, cheapest first: your notes, your files and repos, then papers, the web, people or records as the task needs. "Existing work" means whatever the domain has: papers and repos for research, the codebase and its conventions for a build, notes and earlier versions for writing, an inventory for file cleanup, records and deadlines for admin, options and prices for a decision. Tag each source `[read]`, `[abstract]`, `[search]`, `[memory, unchecked]` or `[user said]`.
3. **Understand it.** One digest per source: what it did or says, what it assumed, what it does not show, what it means for this job. Keep digests in the plan so no source is read twice. Never trust a search snippet for a number.
4. **Choose.** Adopt, adapt, build or reject, each with a reason and a source. Two or three routes with cost in tokens, time and money, and a recommendation. **Ask round 2** (the real choices, the cost cap, approvals).
5. **Write the steps.** Numbered. Each has its sources, one check that can fail, what can go wrong, and what was ruled out. Add the stop condition and an Archive step. **Ask round 3** (the riskiest assumptions in the draft; "what would you regret?").
6. **Freeze.** Fold the answers in, mark the plan frozen with the date, create the steps in the task list.

## The questions (3 rounds is a maximum, not a quota)
1 to 4 questions per round, each with a recommended default first, each understandable on its own. Ask only what your notes, files and sources cannot answer. If the answers are already clear, skip the round and say so in one line. Rounds sit between phases (1, 4, 5) so each is informed. Never send, post, push or spend on a default; those need an explicit yes.

## Phase 7. Ready the skills, once, after the freeze
1. Free pass: run `toolbelt.py` on each step in plain words and read the finalists' SKILL.md. Judge fit yourself.
2. If every step has a fitting skill, put its name in the step and start.
3. If more than 3 steps have gaps or near-misses, launch ONE `skill-fitter` agent. State its cost first (a subagent carries a large baseline context; plan for roughly 100k tokens). Give it the frozen plan with its digests, not raw sources. It fixes near-fits, writes missing skills and returns a manifest. Keep polishing the plan while it runs.
4. Execution starts with the frozen plan and the manifest.

## Non-code tasks
Same skeleton. When no skill fits, say so: write a small checklist or skill, use a connector you have (mail drafts, calendar, documents), or mark the step "by hand". Never force a coding tool onto a non-code step.

## Plan template
```
# <job>        status: draft | frozen | done      date:
Planned with: <tools and why>
1 The job: goal, done looks like, for whom, constraints, irreversible parts, unknowns
2 What exists: <source> [tag]: digest
3 Choice: adopt / adapt / build / reject, routes with cost, recommendation
4 Steps: n. step | sources | check that can fail | can go wrong | ruled out | skill
  Stop condition. Archive step.
5 Questions log: rounds, answers, defaults accepted
6 Skills manifest: step, skill, fixed or new
7 Outcome: result, score against plan, lesson
```
Save finished plans by job type; the next job of that type starts as a diff from the last. End with `score-against-plan`.
