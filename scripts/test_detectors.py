#!/usr/bin/env python3
"""Run every detector referenced by an entry against its fixtures.

Pass criteria (per detector): the vulnerable fixture yields exactly the expected number
of findings (detectors/expected.yaml) and the fixed fixture yields zero. Also checks that
each entry's detector paths/fixtures agree with detectors/expected.yaml and that every
detector file on disk is referenced by at least one entry.

Needs: semgrep, slither-analyzer, solc (solc-select, 0.8.20) on PATH.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

from common import ROOT, load_entries, load_yaml


def run_semgrep(rule: str, fixture: str):
    r = subprocess.run(["semgrep", "--metrics=off", "--quiet", "--json", "--config", rule, fixture],
                       capture_output=True, text=True, cwd=ROOT)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"semgrep produced no JSON: {r.stderr[-500:]}")
    if d.get("errors"):
        raise RuntimeError("semgrep errors: " + "; ".join(e["message"][:200] for e in d["errors"]))
    return [f"{x['path']}:{x['start']['line']}" for x in d["results"]]


def run_slither(plugin: str, fixture: str):
    from slither import Slither
    spec = importlib.util.spec_from_file_location("vb_plugin", ROOT / plugin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cls = [v for v in vars(mod).values() if isinstance(v, type) and getattr(v, "ARGUMENT", "").startswith("vb-")][0]
    sl = Slither(str(ROOT / fixture), compile_force_framework="solc")
    sl.register_detector(cls)
    res = sl.run_detectors()[0]
    out = []
    for r in res:
        fn = [e["name"] for e in r["elements"] if e.get("type") == "function"]
        out.append(f"{fixture}:{','.join(fn)}")
    return out


def main() -> int:
    expected = load_yaml(ROOT / "detectors" / "expected.yaml")
    used = {}
    for _, e in load_entries():
        for d in e.get("detectors", []):
            used.setdefault(d["path"], set()).add((d["engine"], d["true_positive_fixture"], d["false_positive_fixture"]))
    problems = 0
    on_disk = {str(p.relative_to(ROOT)) for p in (ROOT / "detectors").rglob("*") if p.suffix in (".yaml", ".py") and p.name != "expected.yaml"}
    for p in sorted(on_disk - set(used)):
        print(f"FAIL detector not referenced by any entry: {p}")
        problems += 1
    print(f"{'detector':58} {'engine':8} {'TP':>3} {'FP':>3}  result")
    for path, variants in sorted(used.items()):
        exp = expected.get(path)
        if not exp:
            print(f"FAIL {path}: missing from detectors/expected.yaml")
            problems += 1
            continue
        for engine, tp_fix, fp_fix in sorted(variants):
            fd = exp["fixture_dir"]
            if not tp_fix.startswith(fd) or not fp_fix.startswith(fd):
                print(f"FAIL {path}: entry fixtures {tp_fix}/{fp_fix} not under {fd}")
                problems += 1
                continue
        engine, tp_fix, fp_fix = sorted(variants)[0]
        try:
            run = run_semgrep if engine == "semgrep" else run_slither
            tp, fp = run(path, tp_fix), run(path, fp_fix)
        except Exception as ex:  # noqa: BLE001
            print(f"FAIL {path}: {ex}")
            problems += 1
            continue
        ok = len(tp) == exp["tp"] and len(fp) == exp["fp"]
        print(f"{path.split('/')[-1]:58} {engine:8} {len(tp):>3} {len(fp):>3}  {'PASS' if ok else 'FAIL'}")
        if not ok:
            problems += 1
            print("   TP hits:", tp, "\n   FP hits:", fp, f"\n   expected tp={exp['tp']} fp={exp['fp']}")
    # Cross-check: run each entry's semgrep detectors on the entry's own snippets.
    # A flagged fixed_snippet is a failure; an unflagged vulnerable_snippet is reported only
    # (e.g. Conic's ETH/WETH guard mix-up is documented as out of reach for this rule).
    import pathlib
    import tempfile
    print("\nsnippet cross-check (semgrep detectors vs. each entry's own snippets):")
    for _, e in load_entries():
        if e["code_pattern"]["language"] != "solidity":
            continue
        for d in e.get("detectors", []):
            if d["engine"] != "semgrep":
                continue
            with tempfile.TemporaryDirectory() as td:
                res = {}
                for key in ("vulnerable_snippet", "fixed_snippet"):
                    f = pathlib.Path(td) / f"{key}.sol"
                    f.write_text(e["code_pattern"][key])
                    res[key] = len(run_semgrep(d["path"], str(f)))
            bad = res["fixed_snippet"] > 0
            problems += bad
            note = "FAIL fixed snippet flagged" if bad else ("flagged" if res["vulnerable_snippet"] else "NOT flagged (see detector notes)")
            print(f"  {e['id']} {d['path'].split('/')[-1]:44} vulnerable_snippet: {note}")
    print(f"\n{len(used)} detectors, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
