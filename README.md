# quality-loop-kit

A small kit for Claude Code that makes a coding agent plan before it acts, check its own work, and write down what it learned. It adds no service and no dependency: four skills, one agent, two hooks, one keyword lookup, and a single-file installer that you can undo.

Status: v0.1, built and tested on one machine. Not yet published.

## What you get

| Piece | What it does |
|---|---|
| `quality-loop` skill | Picks a lane (quick, standard, heavy) and runs Plan, Execute, Critique, Archive, Learn. A plan is an outcome, one check, boundaries and a stop condition. |
| `replan-on-failure` skill | Stop, probe once, rewrite only the remaining steps, at most 2 replans. |
| `score-against-plan` skill | Run the plan's own checks, score them, scan for known failure modes. |
| `selftest-mutation-check` skill | Prove a new test can fail before trusting it. |
| `planning-scout` agent | Cheap lookup-only helper that maps plan steps to installed skills. |
| `quality_prompt.py` hook (UserPromptSubmit) | One-line reminder when a prompt starts real work. Silent for questions, thanks, slash commands, and sessions that already have a task list. A different line for scheduled loop ticks. |
| `quality_guard.py` hook (PreToolUse) | One-line reminder before `git commit`/`push`, destructive commands (`rm -rf`, `git clean`, `reset --hard`) and subagent launches. It parses the shell, so `echo "git push"`, a grep pattern or a heredoc body does not fire it. |
| `toolbelt.py` | `python3 -I ~/.claude/quality-loop/toolbelt.py "<task>"` ranks your installed skills for a task (BM25 over names and descriptions). Free, offline. |

Hooks only remind. They never block a tool call, never raise, and exit 0 on any input.

## Install

```
python3 dist/install_quality_loop.py --dry-run   # see exactly what changes
python3 dist/install_quality_loop.py             # install, then start a new session
python3 dist/install_quality_loop.py --check
python3 dist/install_quality_loop.py --uninstall # restores settings.json and CLAUDE.md byte for byte
```

It writes skills to `~/.claude/skills/`, the agent to `~/.claude/agents/`, the hooks and toolbelt to `~/.claude/quality-loop/`, merges two hook entries into `~/.claude/settings.json`, and appends a marked block to `~/.claude/CLAUDE.md`. Originals are saved first. A skill of yours with the same name is never overwritten unless you pass `--force`. Invalid `settings.json` aborts with nothing changed.

Customise the guard in `~/.claude/quality-loop/config.json`: `{"messages": {"git": "..."}, "disable": ["destructive"]}`.

## Tests

`python3 tests/test_kit.py` rebuilds the installer and runs 9 tests in throwaway `HOME` directories, under the system Python 3.9 as well when present: install, check, uninstall leaves the tree identical; existing files restored byte for byte; idempotent second install; dry run writes nothing; invalid settings aborts; user edits survive uninstall; hook behaviour on 12 shell commands and 6 non-task prompts plus malformed input; a secret-pattern scan of the repo and of the embedded payload. Set `QL_DENYLIST=/path/to/file` (outside the repo) to also scan for personal strings.

## Evidence, and its limits

These numbers come from the author's own setup, which is larger than this kit. They show the approach is measurable, not that it will work for you.

- Without any hook, the agent used the quality-loop skill or a task list on 1 of 102 task prompts over 72 hours (0.98%). That is why the reminder hook exists. The rate after the hook has not been measured yet; do not assume it is high.
- The prompt classifier, checked against 1,474 historical prompts labelled by "the agent made 3 or more tool calls": it fired on 58% of those, and on about 46% of all prompts. It is a blunt reminder, not a router.
- Skill retrieval on 40 hand-written queries over about 750 skills: BM25 alone put the right skill in the top 3 for 65%; adding local embeddings reached 78%. **This kit ships BM25 only.** On a smaller skill set it should do better, but nobody has measured that.
- The guard was replayed over 7,780 real shell commands. The simple substring version it replaced fired on many false positives (grep patterns, `docker rm`, `2>/dev/null`); the parser removed them and caught commands like `git -c user.name=x commit` that the old one missed.

Known limits: the lane choice is still the model's judgement; reminders can be ignored; `quality:` tags are guessed from keywords for skills that have none; no Windows testing; hook commands call `python3`.

## Before publishing (checklist for the author)

- [ ] Choose licence (MIT file is a draft) and repository name.
- [ ] Run `QL_DENYLIST=... python3 tests/test_kit.py` with a denylist of your own names, paths and hosts.
- [ ] Read every file in `src/` once as a stranger would.
- [ ] Measure adherence after a week with the hooks on and replace the baseline above.
