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
