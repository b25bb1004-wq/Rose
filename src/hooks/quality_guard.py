#!/usr/bin/env python3
"""PreToolUse hook: remind before a risky tool call. Reminder only: it never blocks and never raises.

Shell commands are parsed (heredoc bodies dropped, quoted text ignored, split into simple commands, ssh and
`sh -c` strings followed two levels deep) so a rule fires only when the program really starts a command, not when
its name sits inside a commit message, an echo or a grep pattern. Python 3.9+, standard library only.
Override messages or switch rules off in ~/.claude/quality-loop/config.json:
  {"messages": {"git": "my text"}, "disable": ["destructive"]}
"""
import json
import os
import re
import sys

WRAP = {"sudo", "doas", "time", "nohup", "exec", "command", "builtin", "env", "nice", "caffeinate", "xargs",
        "stdbuf", "timeout"}
RESERVED = {"do", "then", "else", "elif", "if", "while", "until", "!"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
SSH_VAL = {"-o", "-i", "-p", "-l", "-F", "-J", "-L", "-R", "-D", "-b", "-c", "-e", "-m", "-O", "-S", "-W", "-w", "-E",
           "-B", "-I", "-Q"}
HEREDOC = re.compile(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")
MSG = {
    "agent": "Before launching a subagent: state the item count and expected cost in one line. One subagent at a time.",
    "git": "Before committing or pushing: check the author, the staged files, and that nothing secret is staged.",
    "destructive": "Destructive command: list the target first, check it is not untracked work, prefer trash or an archive.",
}
CONFIG = os.path.expanduser("~/.claude/quality-loop/config.json")


def drop_heredocs(text):
    """Remove heredoc bodies; keep the line that opens them (it may carry a pipe to a real command)."""
    out, pending = [], []
    for line in text.split("\n"):
        if pending:
            if line.strip() == pending[0]:
                pending.pop(0)
            continue
        out.append(line)
        pending = [m.group(2) for m in HEREDOC.finditer(line)]
    return "\n".join(out)


def commands(text):
    """Split a shell string into simple commands, each a list of tokens. Quote-aware; no expansion."""
    text = drop_heredocs(text.replace("\\\n", " "))
    cmds, toks, cur, i, n = [], [], [], 0, len(text)

    def end_tok():
        if cur:
            toks.append("".join(cur))
            del cur[:]

    def end_cmd():
        nonlocal toks
        end_tok()
        if toks:
            cmds.append(toks)
        toks = []

    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            cur.append(text[i + 1])
            i += 2
        elif c == "'":
            j = text.find("'", i + 1)
            j = n if j < 0 else j
            cur.append(text[i + 1:j])
            i = j + 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            cur.append(text[i + 1:j])
            i = j + 1
        elif c == "#" and not cur:
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif c in ";&|\n()`{}":
            end_cmd()
            i += 1
        elif c in " \t":
            end_tok()
            i += 1
        else:
            cur.append(c)
            i += 1
    end_cmd()
    return cmds


def lead(toks):
    """Drop env assignments and wrapper programs from the front of a command."""
    t = list(toks)
    while t:
        if re.match(r"^[A-Za-z_]\w*=", t[0]) or t[0] in RESERVED:
            t.pop(0)
        elif os.path.basename(t[0]) in WRAP:
            w = os.path.basename(t.pop(0))
            while t and t[0].startswith("-"):
                t.pop(0)
            if w == "timeout" and t:
                t.pop(0)
        else:
            break
    return t


def git_sub(args):
    """Return (subcommand, rest) skipping git's global options."""
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
            i += 2
        elif a.startswith("-"):
            i += 1
        else:
            return a, args[i + 1:]
    return "", []


def inner(toks):
    """Command lines that run somewhere else: ssh remote commands and shell -c strings."""
    t = lead(toks)
    if not t:
        return []
    prog, args = os.path.basename(t[0]), t[1:]
    if prog == "ssh":
        i, host = 0, None
        while i < len(args):
            if args[i] in SSH_VAL:
                i += 2
            elif args[i].startswith("-"):
                i += 1
            elif host is None:
                host, i = args[i], i + 1
            else:
                break
        rest = " ".join(args[i:]) if host else ""
        return [rest] if rest else []
    if prog in SHELLS:
        for k, a in enumerate(args[:-1]):
            if re.match(r"^-[a-z]*c$", a):
                return [args[k + 1]]
    return []


def rule_for(toks):
    t = lead(toks)
    if not t:
        return None
    prog, args = os.path.basename(t[0]), t[1:]
    if prog == "git":
        sub, rest = git_sub(args)
        if sub in ("commit", "push"):
            return "git"
        if sub in ("clean", "restore") or (sub == "reset" and "--hard" in rest) or (sub == "checkout" and "--" in rest):
            return "destructive"
    if prog == "rm" and any(a in ("--recursive", "--force") or (re.match(r"^-[A-Za-z]+$", a) and re.search(r"[rRf]", a))
                            for a in args):
        return "destructive"
    if prog == "mv" and "/dev/null" in args:
        return "destructive"
    return None


def rules(text, depth=0):
    """Every rule that fires for a command line, following ssh and shell -c strings two levels deep."""
    found = []
    for toks in commands(text):
        r = rule_for(toks)
        if r:
            found.append(r)
        if depth < 2:
            for sub in inner(toks):
                found += rules(sub, depth + 1)
    return found


ORDER = ("agent", "git", "destructive")


def picks(tool, inp):
    """Rules that apply to this tool call, in a fixed order."""
    if tool == "Agent":
        return ["agent"]
    if tool == "Bash":
        hit = set(rules(inp.get("command", "") or ""))
        return [r for r in ORDER if r in hit]
    return []


def main():
    d = json.load(sys.stdin)
    try:
        cfg = json.load(open(CONFIG))
    except Exception:
        cfg = {}
    msgs = [cfg.get("messages", {}).get(r, MSG[r]) for r in picks(d.get("tool_name", ""), d.get("tool_input") or {})
            if r not in cfg.get("disable", [])]
    if msgs:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": " ".join(msgs)}}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:  # a reminder must never break a tool call
        pass
    sys.exit(0)
