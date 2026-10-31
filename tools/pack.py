#!/usr/bin/env python3
"""Build dist/install_quality_loop.py: the installer template with every file under src/ embedded."""
import base64
import json
import os
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = {}
for base, _, names in os.walk(os.path.join(ROOT, "src")):
    for n in names:
        p = os.path.join(base, n)
        files[os.path.relpath(p, os.path.join(ROOT, "src")).replace(os.sep, "/")] = open(p, encoding="utf-8").read()
blob = base64.b64encode(zlib.compress(json.dumps(files, sort_keys=True).encode(), 9)).decode()
tpl = open(os.path.join(ROOT, "tools", "installer_template.py"), encoding="utf-8").read()
assert tpl.count('"__PAYLOAD__"') == 1
os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
out = os.path.join(ROOT, "dist", "install_quality_loop.py")
open(out, "w", encoding="utf-8").write(tpl.replace('"__PAYLOAD__"', '"%s"' % blob))
os.chmod(out, 0o755)
print(f"{len(files)} files, {os.path.getsize(out)} bytes -> dist/install_quality_loop.py")
