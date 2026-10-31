## Quality loop
Every task runs Plan, Execute, Critique, Archive, Learn. Invoke the `quality-loop` skill at the start of any task bigger than a one-line answer; it sets the lane (quick, standard, heavy) and names the skill for each step.
- Before any subagent or batch job: state the item count and expected cost in one line.
- At plan time run `python3 -I ~/.claude/quality-loop/toolbelt.py "<task>"` for the skills to use, and create the Archive step in the task list so it cannot be forgotten.
- A hook (`quality_prompt.py`) adds a one-line reminder on task prompts; follow it. In a scheduled loop tick the queue is the plan: do the item, then the Archive step.
- A new skill carries `quality: Memory|Planning|Execution|Critique|Archiving` in its frontmatter.
