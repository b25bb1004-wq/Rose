---
name: archive-before-delete
description: Cleaning folders, notes or repos when the user says "clear", "gone", "garbage" or "get rid of". Use before any delete or move of the user's files.
quality: Archiving
---
# Archive before delete
1. **Wording like "gone", "clear the clutter", "hide it" usually means archive, not delete.** If unsure, ask one question with options (junk only / archive / delete) before touching anything.
2. **Delete only provable junk:** `.DS_Store`, empty directories, zero-byte stubs, scratch dirs. Check each with `ls` or `cat` first.
3. **Untracked and gitignored files are not in git, so deleting them is unrecoverable.** List `.gitignore` entries and `git status --ignored` before any removal. Move such files to an archive folder; never `rm` them. Do not run `git clean -fd` without reading its `-n` output first.
4. **Order for git moves:** `git mv` first, delete junk after. If tracked files are deleted first, `git mv` of the parent folder fails with "bad source"; fix with `git rm -r --cached <junk>` and retry.
5. **To hide without deleting:** move to an `Archive/` folder and drop it from any index or ignore list your tools read. Links by name still resolve.
6. **After the cleanup,** run `git status` and `ls` and tell the user exactly what was and was not touched.
