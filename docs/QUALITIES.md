# The five qualities and the skills for each

Rose organises work into five qualities. Every task touches them in this order, and repeats: **Memory** (a service every step calls), **Planning**, **Execution**, **Critique**, **Archiving**. Tag your own skills with `quality: <name>` in the frontmatter and `toolbelt.py` will file them here; skills without the tag are guessed from their words.

Rose ships thirteen skills and three agents. The rest of this page points at public plugins that add more. Nothing from those plugins is copied into this repo: install them from their own repositories.

| Quality | Ships with Rose | Good public skills for it (plugin:skill) |
|---|---|---|
| **Memory**: recall what matters, keep context lean | `handoff-before-clear` | `ecc:unified-memory`, `ecc:context-budget`, `ecc:strategic-compact`, `ecc:save-session`, `token-optimizer:resume-checkpoint` |
| **Planning**: outcome, one check, boundaries, stop condition | `quality-loop`, `bounded-delegation`, `prior-art-audit`, agent `planning-scout` | `ecc:plan`, `ecc:prp-plan`, `agent-skills:spec`, `agent-skills:planning-and-task-breakdown`, `agent-skills:idea-refine` |
| **Execution**: follow the plan, stay observable, replan when it breaks | `replan-on-failure` | `agent-skills:incremental-implementation`, `agent-skills:debugging-and-error-recovery`, `vercel:*` for Vercel work |
| **Critique**: run the plan's own checks, never grade alone | `score-against-plan`, `selftest-mutation-check`, `verify-before-commit-push`, `eval-harness-sanity-check`, `vet-third-party-skill` | `ecc:code-review`, `ecc:verification-loop`, `ecc:security-review`, `ecc:tdd-workflow`, `agent-skills:code-review-and-quality`, `ponytail:ponytail-review`, `andrej-karpathy-skills:karpathy-guidelines` |
| **Archiving**: notes, docs, lessons, handoff | `log-failure-as-skill`, `archive-before-delete` | `ecc:update-docs`, `agent-skills:documentation-and-adrs`, `ecc:architecture-decision-records` |

Memory is the thinnest slot: `handoff-before-clear` writes a handoff note, and what you remember beyond that depends on where you keep notes.

## Where the plugins come from

Add a marketplace once, then install: `/plugin marketplace add <repo>` and `/plugin install <plugin>@<marketplace>`. Check `/plugin` for what you already have.

| Plugin | Marketplace repo |
|---|---|
| `ecc` | `affaan-m/ECC` |
| `agent-skills` | `addyosmani/agent-skills` |
| `token-optimizer` | `alexgreensh/token-optimizer` |
| `ponytail` | `DietrichGebert/ponytail` |
| `andrej-karpathy-skills` | `multica-ai/andrej-karpathy-skills` |
| `superpowers` | `obra/superpowers-marketplace` |
| `vercel` | `anthropics/claude-plugins-official` |

The picks above were taken from one working install and their quality tags come from the toolbelt's own classification of them, not from a benchmark. Read a skill before relying on it, and read a third-party skill before you install it: skills run with your agent's permissions.

## Finding the right one for a task

`python3 -I ~/.claude/quality-loop/toolbelt.py "<task>"` ranks every skill you have installed, plugin skills included, and prints the top 8 with their quality tag. It is keyword search over names and descriptions, so it is a hint, not an answer.
