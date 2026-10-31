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

PAYLOAD = "__PAYLOAD__"  # base64(zlib(json {relative path: text}))
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
