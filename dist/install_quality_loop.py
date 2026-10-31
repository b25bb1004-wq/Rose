#!/usr/bin/env python3
"""quality-loop-kit installer (single file, standard library only, Python 3.9+).

  python3 install_quality_loop.py              install
  python3 install_quality_loop.py --dry-run    show what would change, write nothing
  python3 install_quality_loop.py --check      verify an installed copy
  python3 install_quality_loop.py --uninstall  remove it and restore settings.json and CLAUDE.md
  --force                                      replace a same-named skill you already have (a backup is kept)

It adds 4 skills, 1 agent, 2 hooks (UserPromptSubmit reminder, PreToolUse reminder) and a toolbelt, and edits
~/.claude/settings.json and ~/.claude/CLAUDE.md. Both edits are reversible: the originals are saved first.
"""
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zlib

PAYLOAD = "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"  # base64(zlib(json {relative path: text}))
HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, ".claude")
KIT = os.path.join(ROOT, "quality-loop")
MANIFEST = os.path.join(KIT, "manifest.json")
SETTINGS = os.path.join(ROOT, "settings.json")
CLAUDE_MD = os.path.join(ROOT, "CLAUDE.md")
BEGIN, END = "<!-- quality-loop-kit:begin -->", "<!-- quality-loop-kit:end -->"
HOOKS = [("UserPromptSubmit", None, "python3 -I ~/.claude/quality-loop/hooks/quality_prompt.py", 5),
         ("PreToolUse", "Agent|Bash", "python3 -I ~/.claude/quality-loop/hooks/quality_guard.py", 5)]


def files():
    return json.loads(zlib.decompress(base64.b64decode(PAYLOAD)).decode())


def dest(rel):
    if rel.startswith(("skills/", "agents/")):
        return os.path.join(ROOT, rel)
    return os.path.join(KIT, rel)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    try:
        with open(p, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None


def write(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp%d" % os.getpid()
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, p)


def load_manifest():
    try:
        return json.loads(read(MANIFEST) or b"")
    except ValueError:
        return None


def hook_entries(settings, add):
    """Add (or find) our hook commands. Returns the number of entries added."""
    hooks = settings.setdefault("hooks", {})
    n = 0
    for event, matcher, cmd, timeout in HOOKS:
        groups = hooks.setdefault(event, [])
        if any(h.get("command") == cmd for g in groups for h in g.get("hooks", [])):
            continue
        if add:
            g = {"hooks": [{"type": "command", "command": cmd, "timeout": timeout}]}
            if matcher:
                g["matcher"] = matcher
            groups.append(g)
        n += 1
    return n


def strip_hooks(settings):
    hooks = settings.get("hooks", {})
    for event in list(hooks):
        groups = []
        for g in hooks[event]:
            g["hooks"] = [h for h in g.get("hooks", []) if "quality-loop/hooks/" not in h.get("command", "")]
            if g["hooks"]:
                groups.append(g)
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]
    if not hooks:
        settings.pop("hooks", None)


def install(dry, force):
    payload, man = files(), load_manifest() or {"files": {}}
    plan, skipped = [], []
    for rel, text in sorted(payload.items()):
        p, data = dest(rel), text.encode()
        cur = read(p)
        if cur == data:
            continue
        if cur is not None and man["files"].get(rel) != sha(cur) and not force:
            skipped.append(rel)  # a file of yours with the same name: never overwrite silently
            continue
        plan.append((rel, p, data, cur))
    raw = read(SETTINGS)
    try:
        settings = json.loads(raw.decode()) if raw and raw.strip() else {}
    except ValueError:
        sys.exit("settings.json is not valid JSON; fix it first. Nothing was changed.")
    added = hook_entries(settings, add=True)
    md = read(CLAUDE_MD)
    need_md = md is None or BEGIN.encode() not in md
    print(("DRY RUN, nothing written\n" if dry else "") + f"files to write: {len(plan)}; kept (yours): {skipped or 'none'}; "
          f"hooks to add: {added}; CLAUDE.md block: {'add' if need_md else 'present'}")
    for rel, p, _, cur in plan:
        print(("  replace " if cur is not None else "  add     ") + p.replace(HOME, "~"))
    if dry:
        return
    os.makedirs(os.path.join(KIT, "backup"), exist_ok=True)
    first = not os.path.exists(MANIFEST)
    if first:  # keep the originals once, so uninstall can restore them exactly
        for name, p in (("settings.json", SETTINGS), ("CLAUDE.md", CLAUDE_MD)):
            orig = read(p)
            write(os.path.join(KIT, "backup", name + (".orig" if orig is not None else ".absent")), orig or b"")
    for rel, p, data, cur in plan:
        if cur is not None:
            write(os.path.join(KIT, "backup", rel.replace("/", "__") + ".bak"), cur)
        write(p, data)
        if p.endswith(".py"):
            os.chmod(p, 0o755)
    if added:
        write(SETTINGS, (json.dumps(settings, indent=2, ensure_ascii=False) + "\n").encode())
    if need_md:
        block = (BEGIN + "\n" + payload["claude_md_block.md"].rstrip("\n") + "\n" + END + "\n").encode()
        sep = b"" if md is None or md.endswith(b"\n\n") or not md else (b"\n" if md.endswith(b"\n") else b"\n\n")
        write(CLAUDE_MD, (md or b"") + sep + block)
    man["files"] = {rel: sha(read(dest(rel)) or b"") for rel in payload if read(dest(rel)) == payload[rel].encode()}
    man["settings_sha"], man["claude_md_sha"] = sha(read(SETTINGS) or b""), sha(read(CLAUDE_MD) or b"")
    write(MANIFEST, json.dumps(man, indent=2).encode())
    print("installed. Start a new Claude Code session so the hooks load. Undo with --uninstall.")


def uninstall():
    man = load_manifest()
    if man is None:
        sys.exit("not installed (no manifest)")
    for rel, h in man["files"].items():
        p = dest(rel)
        cur = read(p)
        if cur is None:
            continue
        if sha(cur) != h:
            print("  kept (you edited it): " + p.replace(HOME, "~"))
            continue
        os.remove(p)
        d = os.path.dirname(p)
        if d != ROOT and not os.listdir(d) and d.startswith(ROOT):
            os.rmdir(d)
    for name, p, key in (("settings.json", SETTINGS, "settings_sha"), ("CLAUDE.md", CLAUDE_MD, "claude_md_sha")):
        cur, bdir = read(p), os.path.join(KIT, "backup")
        untouched = cur is not None and sha(cur) == man.get(key)
        if untouched:  # nothing changed it since we did: restore the original bytes
            orig = read(os.path.join(bdir, name + ".orig"))
            if orig is not None:
                write(p, orig)
            elif os.path.exists(os.path.join(bdir, name + ".absent")):
                os.remove(p)
        elif cur is not None and name == "settings.json":
            s = json.loads(cur.decode())
            strip_hooks(s)
            write(p, (json.dumps(s, indent=2, ensure_ascii=False) + "\n").encode())
        elif cur is not None:
            text = cur.decode()
            a, b = text.find(BEGIN), text.find(END)
            if a >= 0 and b > a:
                write(p, (text[:a].rstrip("\n") + "\n" + text[b + len(END):].lstrip("\n")).encode() if text[:a].strip() else text[b + len(END):].lstrip("\n").encode())
    shutil.rmtree(KIT, ignore_errors=True)
    print("uninstalled; settings.json and CLAUDE.md restored.")


def check():
    man = load_manifest()
    if man is None:
        sys.exit("not installed")
    bad = [rel for rel, h in man["files"].items() if sha(read(dest(rel)) or b"") != h]
    s = json.loads((read(SETTINGS) or b"{}").decode())
    cmds = [h.get("command") for g in sum(s.get("hooks", {}).values(), []) for h in g.get("hooks", [])]
    missing = [c for _, _, c, _ in HOOKS if c not in cmds]
    r = subprocess.run([sys.executable, "-I", os.path.join(KIT, "toolbelt.py"), "plan a release"], capture_output=True, text=True)
    print(f"files changed or missing: {bad or 'none'}; hooks missing: {missing or 'none'}; toolbelt exit {r.returncode}")
    sys.exit(1 if bad or missing or r.returncode else 0)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--uninstall" in a:
        uninstall()
    elif "--check" in a:
        check()
    else:
        install("--dry-run" in a, "--force" in a)
