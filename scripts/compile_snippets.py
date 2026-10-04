#!/usr/bin/env python3
"""Compile every Solidity snippet in entries/ and every fixture in fixtures/ with solc.

Proves the illustrative code is at least syntactically and type correct. Needs `solc`
on PATH (solc-select, 0.8.20). Vyper/other snippets are skipped and listed.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

from common import ROOT, load_entries


def compile_src(text: str, name: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / name
        p.write_text(text)
        r = subprocess.run(["solc", "--bin", "-o", d + "/out", str(p)], capture_output=True, text=True)
        return r.returncode == 0, (r.stderr or r.stdout)[-1500:]


def main() -> int:
    fails, ok, skipped = 0, 0, []
    for path, e in load_entries():
        cp = e["code_pattern"]
        for key in ("vulnerable_snippet", "fixed_snippet"):
            if cp["language"] != "solidity":
                skipped.append(f"{e['id']}.{key} ({cp['language']})")
                continue
            good, msg = compile_src(cp[key], f"{e['slug']}_{key}.sol")
            if good:
                ok += 1
            else:
                fails += 1
                print(f"FAIL {e['id']} {key}\n{msg}")
    for f in sorted((ROOT / "fixtures").glob("*/*.sol")):
        good, msg = compile_src(f.read_text(), f.name)
        if good:
            ok += 1
        else:
            fails += 1
            print(f"FAIL {f.relative_to(ROOT)}\n{msg}")
    print(f"compiled ok: {ok}, failed: {fails}, skipped: {len(skipped)}")
    for s in skipped:
        print("  skipped:", s)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
