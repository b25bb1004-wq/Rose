#!/usr/bin/env python3
"""UserPromptSubmit hook: one short quality-loop reminder when a prompt starts real work.

Reminder only. It never blocks, never raises, and stays silent for factory prompts, slash commands,
system notices, short chatter and plain questions. On a task prompt it also runs the kit's toolbelt (BM25, local) and
injects the top installed skills, so the plan never depends on remembering to look; a session that already holds a
task-list ledger gets the shortlist without the reminder line.
Loop ticks (cron or /loop prompts) get a different line: the queue is the plan, only Archive is owed.
Python 3.9 compatible, standard library only, no network, no state, nothing logged.
"""
import json
import os
import re
import subprocess
import sys

TICK = re.compile(r"\bloop tick\b|<<autonomous-loop|\bscheduled (?:task|run|trigger)\b", re.I)
# Plain questions and acknowledgements stay silent; anything else that reads like an instruction fires.
QUESTION = re.compile(r"^\W*(?:what|why|how|which|who|when|where|is|are|was|were|does|do|did|explain|tell me|any|"
                      r"u see|you see|so what|hello|hi|hey|can|could|cant|can't|should|would|will|shall|wait|if|but)\b", re.I)
ACK = re.compile(r"^\W*(?:yes|yeah|yep|no|nope|nah|ok|okay|thanks|thank you|cool|nice|great|good|sure|hmm|alright|lol)\b", re.I)
WORK = re.compile(r"\b(?:build|make|create|write|implement|fix|add|apply|install|download|set ?up|run|deploy|push|"
                  r"commit|refactor|migrate|train|benchmark|publish|send|delete|remove|rename|update|change|edit|"
                  r"generate|design|plan|continue|finish|begin|start|integrate|load|move|convert|port|scan|test|"
                  r"verify|refine|improve|upgrade|clean|proceed|solve|keep (?:going|working)|resume|reopen|open|"
                  r"complete|restart|access|check|use|put|watch|read|look|find|search|get|pull|fetch|pick|show|"
                  r"analy[sz]e|explore|review|compare|summari[sz]e|prepare|configure|connect|copy|upload|enable|"
                  r"disable|kill|rerun|retry|try|reset|take care|handle|sort|organi[sz]e|ship|finali[sz]e|wrap|"
                  r"document|archive|back ?up|sync|merge|debug|investigate|figure|shut|close|stop|save|turn|"
                  r"go ahead|do it)\b", re.I)
GO = re.compile(r"\b(?:begin|apply|go ahead|do it|proceed|ship it|keep going|keep working)\b", re.I)
SKIP_START = ("# Your instructions", "/", "<", "This session is being continued", "Below is a conversation",
              "[Request interrupted", "Caveat:")

MSG_TASK = ("quality-loop: quick (an answer or a one-step edit) means just do it, say nothing. Standard or heavy: state "
            "the lane in one line, TaskCreate the steps plus an Archive step, name a tool from the shortlist on each step, and end with score-against-plan.")
MSG_TICK = ("quality-loop, loop tick: the queue is the plan, skip the toolbelt. Do the item, then the Archive step "
            "(a line in your notes, a lesson if any). Blocked: write one line and stop.")


def classify(prompt):
    """Return 'tick', 'task' or None."""
    p = (prompt or "").strip()
    if len(p) < 12 or p.startswith(SKIP_START):
        return None
    if TICK.search(p[:800]):
        return "tick"
    go, work = GO.search(p), WORK.search(p)
    if ACK.match(p) and len(p) < 40 and not go:
        return None
    if QUESTION.match(p) and len(p) < 300 and not go:
        return None
    if work or go:
        return "task"
    return "task" if len(p) >= 120 else None


def ledger_exists(transcript_path):
    """True when a TaskCreate call sits in the last 300 KB of this session's transcript."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 300_000))
            return re.search(rb'"name"\s*:\s*"TaskCreate"', f.read()) is not None
    except Exception:
        return False


def shortlist(prompt):
    """Top installed skills for this prompt from the kit's toolbelt (BM25, local, about 0.05 s); '' on any failure."""
    try:
        tb = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "toolbelt.py")
        out = subprocess.run([sys.executable, "-I", tb, prompt.strip()[:600]], capture_output=True, text=True, timeout=3).stdout.splitlines()
        rows = [l[:150] for l in out if re.match(r"^\S+ \[\w+\] - ", l)][:4]
        return "toolbelt shortlist (a hint from keywords, check that the skill fits):\n" + "\n".join(rows) if rows else ""
    except Exception:
        return ""


def main():
    data = json.load(sys.stdin)
    prompt = data.get("prompt", "")
    kind = classify(prompt)
    if kind is None:
        return
    if kind == "tick":
        msg = MSG_TICK
    else:
        msg = shortlist(prompt)
        if not ledger_exists(data.get("transcript_path", "")):
            msg = MSG_TASK + ("\n" + msg if msg else "")
        if not msg:
            return
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:  # a reminder must never break a prompt
        pass
    sys.exit(0)
