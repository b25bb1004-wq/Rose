---
name: log-failure-as-skill
description: After a tool failure or a hard step that took 2+ attempts to solve, write the fix down as a short generalised skill so it is not rediscovered. Use at the end of any task where a workaround was needed.
quality: Archiving
---
# Turn failures into skills
**Trigger:** a command errored and a workaround was needed, a step took 2 or more attempts, or the user corrected your approach.
1. List `~/.claude/skills`. If a skill fits, update it instead of adding a duplicate.
2. If new, create `~/.claude/skills/<kebab-name>/SKILL.md` with frontmatter `name`, a `description` that says WHEN to use it, and `quality:` (Memory, Planning, Execution, Critique or Archiving).
3. Body, under 40 lines: the exact error text, what worked (a copy-pasteable command), what not to do, the date seen. Keep helper scripts in the same folder.
4. Generalise: name the class of problem ("no poppler installed"), not the one file or project.
5. Never write credentials or private notes into a skill.
6. Tell the user in one line which skill was added or updated.
Only write one when the problem will recur or cost over 10 minutes; a skill nobody needs is noise.
