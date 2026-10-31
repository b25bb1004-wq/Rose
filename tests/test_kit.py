"""End-to-end tests for the kit, run in throwaway HOME directories. Usage: python3 tests/test_kit.py"""
import hashlib
import warnings

warnings.simplefilter("ignore", ResourceWarning)
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(ROOT, "dist", "install_quality_loop.py")
PYS = [sys.executable] + (["/usr/bin/python3"] if os.path.exists("/usr/bin/python3") and sys.executable != "/usr/bin/python3" else [])


def run(home, *args, py=None, stdin=None):
    env = dict(os.environ, HOME=home)
    return subprocess.run([py or sys.executable, "-I", *args], capture_output=True, text=True, env=env, input=stdin, timeout=60)


def tree(home):
    out = {}
    for base, _, names in os.walk(home):
        for n in names:
            p = os.path.join(base, n)
            out[os.path.relpath(p, home)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


class Kit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name
        os.makedirs(os.path.join(self.home, ".claude"))

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, data):
        p = os.path.join(self.home, ".claude", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)

    def test_fresh_install_check_uninstall_leaves_nothing(self):
        for py in PYS:
            before = tree(self.home)
            self.assertEqual(run(self.home, INSTALLER, py=py).returncode, 0)
            self.assertEqual(run(self.home, INSTALLER, "--check", py=py).returncode, 0)
            self.assertEqual(run(self.home, INSTALLER, "--uninstall", py=py).returncode, 0)
            self.assertEqual(tree(self.home), before, "uninstall must leave the tree exactly as it was")

    def test_existing_files_restored_byte_for_byte(self):
        settings = b'{\n\t"model":"x",   "hooks":{"Stop":[{"hooks":[{"type":"command","command":"echo hi"}]}]}\n}'  # odd format, no newline
        md = b"# mine\nno trailing newline"
        self.put("settings.json", settings)
        self.put("CLAUDE.md", md)
        self.put("skills/score-against-plan/SKILL.md", b"---\nname: score-against-plan\ndescription: mine\n---\nmy own\n")
        before = tree(self.home)
        r = run(self.home, INSTALLER)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("kept (yours)", r.stdout)
        self.assertEqual(open(os.path.join(self.home, ".claude/skills/score-against-plan/SKILL.md"), "rb").read().split(b"\n")[4], b"my own")
        s = json.load(open(os.path.join(self.home, ".claude/settings.json")))
        self.assertEqual(s["hooks"]["Stop"][0]["hooks"][0]["command"], "echo hi")
        self.assertEqual(len(s["hooks"]["UserPromptSubmit"]), 1)
        self.assertEqual(run(self.home, INSTALLER, "--uninstall").returncode, 0)
        self.assertEqual(tree(self.home), before)

    def test_idempotent_and_dry_run(self):
        self.put("settings.json", b"{}\n")
        before = tree(self.home)
        run(self.home, INSTALLER, "--dry-run")
        self.assertEqual(tree(self.home), before, "dry run must not write")
        run(self.home, INSTALLER)
        once = tree(self.home)
        run(self.home, INSTALLER)
        self.assertEqual(tree(self.home), once, "second install must change nothing")
        s = json.load(open(os.path.join(self.home, ".claude/settings.json")))
        self.assertEqual(sum(len(v) for v in s["hooks"].values()), 2)
        md = open(os.path.join(self.home, ".claude/CLAUDE.md")).read()
        self.assertEqual(md.count("quality-loop-kit:begin"), 1)

    def test_invalid_settings_aborts_untouched(self):
        self.put("settings.json", b"{not json")
        before = tree(self.home)
        r = run(self.home, INSTALLER)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(tree(self.home), before)

    def test_uninstall_after_user_edits_keeps_their_changes(self):
        self.put("settings.json", b"{}\n")
        run(self.home, INSTALLER)
        p = os.path.join(self.home, ".claude/settings.json")
        s = json.load(open(p))
        s["theme"] = "dark"
        s["hooks"]["Stop"] = [{"hooks": [{"type": "command", "command": "mine"}]}]
        json.dump(s, open(p, "w"))
        self.assertEqual(run(self.home, INSTALLER, "--uninstall").returncode, 0)
        s = json.load(open(p))
        self.assertEqual(s["theme"], "dark")
        self.assertEqual(list(s["hooks"]), ["Stop"])
        self.assertFalse(os.path.exists(os.path.join(self.home, ".claude/quality-loop")))

    def test_hooks_and_toolbelt(self):
        run(self.home, INSTALLER)
        kit = os.path.join(self.home, ".claude/quality-loop")
        for py in PYS:
            task = json.dumps({"prompt": "please build the importer and test it end to end"})
            r = run(self.home, os.path.join(kit, "hooks/quality_prompt.py"), py=py, stdin=task)
            self.assertEqual(r.returncode, 0)
            self.assertIn("quality-loop", json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"])
            for quiet in ('{"prompt":"what is a gradient?"}', "", "not json", "[]", '{"prompt":null}', '{"prompt":"/clear"}'):
                r = run(self.home, os.path.join(kit, "hooks/quality_prompt.py"), py=py, stdin=quiet)
                self.assertEqual((r.returncode, r.stdout), (0, ""), quiet)
            g = os.path.join(kit, "hooks/quality_guard.py")
            fire = lambda c: run(self.home, g, py=py, stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": c}})).stdout
            for c in ("git push origin main", "git -C /x commit -m y", "ssh h 'git push'", "sudo rm -rf build", "git clean -fd", "cd x && git commit -am z"):
                self.assertTrue(fire(c), c)
            for c in ("echo git push", "grep -r 'rm -rf' .", "git commit-graph write", "cat <<EOF\ngit push\nEOF", "ls 2>/dev/null", "docker rm x"):
                self.assertEqual(fire(c), "", c)
            self.assertTrue(run(self.home, g, py=py, stdin='{"tool_name":"Agent"}').stdout)
            for bad in ("", "x", "{}", '{"tool_name":null}', '{"tool_name":"Bash","tool_input":null}'):
                self.assertEqual(run(self.home, g, py=py, stdin=bad).returncode, 0)
            r = run(self.home, os.path.join(kit, "toolbelt.py"), "review my plan before shipping", py=py)
            self.assertEqual(r.returncode, 0)
            self.assertIn("score-against-plan", r.stdout)

    def test_toolbelt_ranks_a_fixture_skill_first(self):
        run(self.home, INSTALLER)
        self.put("skills/pdf-wrangler/SKILL.md", b"---\nname: pdf-wrangler\ndescription: Extract tables and text from PDF files\nquality: Execution\n---\nbody\n")
        r = run(self.home, os.path.join(self.home, ".claude/quality-loop/toolbelt.py"), "extract the tables from a pdf")
        self.assertEqual(r.stdout.splitlines()[1].split()[0], "pdf-wrangler")


class Hygiene(unittest.TestCase):
    """The repo must carry no personal string and no secret. The personal denylist lives OUTSIDE the repo."""
    SECRET = re.compile(r"sk-[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|hf_[A-Za-z0-9]{30,}|"
                        r"AIza[0-9A-Za-z_-]{35}|xox[bap]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")

    def texts(self):
        for base, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "dist")]  # dist is scanned through its payload
            for n in names:
                p = os.path.join(base, n)
                yield p, open(p, encoding="utf-8", errors="replace").read()
        # the embedded payload must be scanned too
        sys.path.insert(0, os.path.join(ROOT, "dist"))
        import importlib
        inst = importlib.import_module("install_quality_loop")
        for rel, t in inst.files().items():
            yield "payload:" + rel, t

    def test_no_secret_patterns(self):
        hits = [p for p, t in self.texts() if self.SECRET.search(t)]
        self.assertEqual(hits, [])

    def test_no_personal_strings(self):
        deny = os.environ.get("QL_DENYLIST")
        if not deny or not os.path.exists(deny):
            self.skipTest("set QL_DENYLIST to a file (outside the repo) with one forbidden string per line")
        words = [w.strip().lower() for w in open(deny) if w.strip()]
        hits = [(p, w) for p, t in self.texts() if os.path.basename(p) != "LICENSE" for w in words if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t.lower())]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "pack.py")], check=True)
    unittest.main(verbosity=1)
