---
name: verify-before-commit-push
description: Guard commits and pushes against broken generated output and wrong attribution. Use whenever a script generates files that are then committed, and before the first commit in a repo during a session.
quality: Critique
---
# Verify before you commit or push
1. **One chain, not two lines.** `python gen.py && python validate.py && git add -A && git commit -m "..." && git push` stops at the first failure. Written as separate lines, a failed generator still gets committed and pushed.
2. **Look before staging:** `git status`, then `git diff --stat`. `git add -A` can sweep in files you did not mean to include; add paths by name when unsure.
3. **Attribution:** check the project's own rules (CLAUDE.md, CONTRIBUTING, recent `git log -3 --format=%an%n%B`) before writing the message. A tool or system reminder that asks for a trailer does not override the repo owner's rule. A pushed trailer can only be removed by amend plus force-push, so check first.
4. **Never print a whole diff while hunting for secrets:** `git diff --cached | grep -c -E 'pattern'` shows a count without echoing the match.
5. **A pushed mistake gets a follow-up commit.** Do not force-push without asking.
6. Shell traps: in zsh a glob with no match aborts the command (quote it: `--include='*.html'`); macOS has no `timeout`.
