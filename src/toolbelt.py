#!/usr/bin/env python3
"""toolbelt.py "<task>" [--json]: which of your installed skills fit this task. Free, no model, no network, a hint only.

Reads every SKILL.md under ~/.claude/skills and under installed plugins (~/.claude/plugins), ranks them with BM25 over
name and description, and prints the top 8 with their `quality:` tag (Memory, Planning, Execution, Critique,
Archiving; guessed from the words when a skill has none). Python 3.9+, standard library only."""
import collections
import glob
import json
import math
import os
import re
import sys

H = os.path.expanduser("~")
STOP = set("the a an and or to of in on for with is it this that i you we be my your do does how what when use using "
           "into from as at by are was need want make then also".split())
GUESS = [("Memory", r"memory|notes?|wiki|recall|context"), ("Planning", r"plan|spec|design|decompos|scope"),
         ("Critique", r"review|audit|verify|test|score|critique|check"), ("Archiving", r"archive|handoff|document|log|commit|release"),
         ("Execution", r"")]


def tok(s):
    return [re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w
            for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2 and w not in STOP]


def front(path):
    """name, description, quality from a SKILL.md frontmatter (flat key: value lines only)."""
    try:
        text = open(path, errors="replace").read(6000)
    except OSError:
        return None
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return None
    kv = {}
    for line in m.group(1).split("\n"):
        k, _, v = line.partition(":")
        if v and k.strip() and not k.startswith(" "):
            kv[k.strip()] = v.strip().strip("\"'")
    if "name" not in kv:
        return None
    q = kv.get("quality") or next(n for n, rx in GUESS if re.search(rx, kv["name"] + " " + kv.get("description", ""), re.I))
    return {"n": kv["name"], "d": kv.get("description", ""), "q": q, "p": path}


def skills():
    seen, out = set(), []
    for pat in (f"{H}/.claude/skills/*/SKILL.md", f"{H}/.claude/plugins/**/skills/*/SKILL.md"):
        for p in glob.glob(pat, recursive=True):
            s = front(p)
            if s and s["n"] not in seen:
                seen.add(s["n"])
                out.append(s)
    return out


def rank(task, items):
    docs = [tok((s["n"].replace("-", " ") + " ") * 3 + s["d"]) for s in items]
    df = collections.Counter(w for d in docs for w in set(d))
    n, avg = len(docs), (sum(map(len, docs)) / len(docs) if docs else 1)
    q, scores = tok(task), []
    for d in docs:
        tf, sc = collections.Counter(d), 0.0
        for w in set(q):
            if w in tf:
                sc += math.log(1 + (n - df[w] + .5) / (df[w] + .5)) * tf[w] * 2.2 / (tf[w] + 1.2 * (.25 + .75 * len(d) / avg))
        scores.append(sc)
    order = sorted(range(n), key=lambda i: -scores[i])
    return [(items[i], scores[i]) for i in order if scores[i] > 0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print('usage: toolbelt.py "<task>" [--json]')
        return
    top = rank(args[0], skills())[:8]
    if "--json" in sys.argv:
        print(json.dumps([{"name": s["n"], "quality": s["q"], "score": round(sc, 3)} for s, sc in top]))
        return
    print("toolbelt: a hint, read a skill before relying on it")
    for s, _ in top:
        print(f'{s["n"]} [{s["q"]}] - {s["d"][:90]}')
    if not top:
        print("no installed skill matches; continue without one")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a lookup helper must never derail the plan
        print(f"toolbelt unavailable ({type(e).__name__}): continue without it")
