#!/usr/bin/env python3
"""Validate every entry in entries/ against schema/entry.schema.yaml plus repo rules.

Checks
  1. JSON Schema (structure, enums, formats).
  2. Identity: file name == slug.yaml, ids/slugs unique, id year == date year,
     date is a real, non-future calendar date.
  3. Vocabulary: vuln_class, tags and chains exist in taxonomy/.
  4. Sources: >=1 required (schema); a link per source; loss_usd.sources and
     fix.reference_url must appear in sources[]; warning if fewer than 2 sources.
  5. No 'TODO' placeholders anywhere in an entry.
  6. code_pattern snippets are labelled ILLUSTRATIVE (comment) and are ours.
  7. Detectors: files exist; 'validated' status needs both fixtures.
  8. Address/hash formats (schema) and low-level consistency (min <= max).
Optional: --check-links does an HTTP HEAD/GET on every source URL (network).
Exit status 1 if any error; warnings never fail the run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request

from jsonschema import Draft202012Validator

from common import ENTRIES, ROOT, SCHEMA_JSON, SCHEMA_YAML, TAXONOMY, load_entries, load_yaml


def vocab():
    classes = set(load_yaml(TAXONOMY / "vuln_class.yaml")["classes"])
    tags = set(load_yaml(TAXONOMY / "tags.yaml")["tags"])
    chains = set(load_yaml(TAXONOMY / "chains.yaml")["chains"])
    return classes, tags, chains


def walk_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_strings(v)


def check_entry(path, e, validator, classes, tags, chains, today):
    errs, warns = [], []
    for err in sorted(validator.iter_errors(e), key=lambda x: list(x.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errs.append(f"schema: {loc}: {err.message[:200]}")
    if errs:  # structure is broken; semantic checks would only add noise
        return errs, warns

    if path.stem != e["slug"]:
        errs.append(f"file name '{path.name}' must equal slug '{e['slug']}.yaml'")
    try:
        d = dt.date.fromisoformat(e["date"])
        if d > today:
            errs.append(f"date {e['date']} is in the future")
        if e["id"].split("-")[1] != str(d.year):
            errs.append(f"id year {e['id']} does not match date year {d.year}")
    except ValueError:
        errs.append(f"date {e['date']!r} is not a real calendar date")

    if e["vuln_class"] not in classes:
        errs.append(f"vuln_class '{e['vuln_class']}' not in taxonomy/vuln_class.yaml")
    for t in e["tags"]:
        if t not in tags:
            errs.append(f"tag '{t}' not in taxonomy/tags.yaml")
    for c in e["chains"]:
        if c not in chains:
            errs.append(f"chain '{c}' not in taxonomy/chains.yaml")

    # sources
    src_urls = {s["url"] for s in e["sources"]}
    if len(src_urls) != len(e["sources"]):
        errs.append("duplicate source url")
    for u in e["loss_usd"]["sources"]:
        if u not in src_urls:
            errs.append(f"loss_usd source not listed in sources[]: {u}")
    ref = e.get("fix", {}).get("reference_url")
    if ref and ref not in src_urls:
        errs.append(f"fix.reference_url not listed in sources[]: {ref}")
    if not any(s["type"] in ("postmortem", "analysis", "primary") for s in e["sources"]):
        errs.append("needs at least one postmortem/analysis/primary source (not only aggregators)")
    if len(e["sources"]) < 2:
        warns.append("only 1 source (Phase 1 exit criterion asks for >= 2)")

    lo, hi = e["loss_usd"]["reported_min"], e["loss_usd"]["reported_max"]
    if lo is not None and hi is not None and lo > hi:
        errs.append("loss_usd.reported_min > reported_max")

    # placeholders
    for s in walk_strings(e):
        if re.search(r"\bTODO\b", s, re.I):
            errs.append(f"contains TODO placeholder: {s[:60]!r}")
            break

    # snippets
    cp = e["code_pattern"]
    for k in ("vulnerable_snippet", "fixed_snippet"):
        if not re.search(r"(//|#).*illustrative", cp[k], re.I):
            errs.append(f"code_pattern.{k} must carry an 'ILLUSTRATIVE' comment")

    # detectors
    for i, det in enumerate(e.get("detectors", [])):
        for k in ("path", "true_positive_fixture", "false_positive_fixture"):
            if not (ROOT / det[k]).is_file():
                errs.append(f"detectors[{i}].{k} missing file: {det[k]}")

    if e["confidence"]["overall"] == "high" and "low" in (e["confidence"]["root_cause"], e["confidence"]["loss"], e["confidence"]["date"]):
        warns.append("overall=high but a sub-confidence is low")
    return errs, warns


# Hosts that answer bot traffic (CI runners included) with 403/429 while the page is live
# in a browser. A 403/429 from one of these is a warning ("not verified"), not an error.
BOT_BLOCK_HOSTS = {
    "medium.com": "Medium blocks bots",
    "blog.save.finance": "Medium-hosted; Medium blocks bots",
    "theblock.co": "The Block blocks bots",
}


def bot_block_reason(url):
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    for domain, why in BOT_BLOCK_HOSTS.items():
        if host == domain or host.endswith("." + domain):
            return why
    return None


def check_link(url, timeout=20):
    hdr = {"User-Agent": "Mozilla/5.0 (vaultbreak link check)"}
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as ex:
            if method == "GET" or ex.code not in (403, 405, 400):
                return ex.code
        except Exception as ex:  # noqa: BLE001
            if method == "GET":
                return f"ERR {type(ex).__name__}"
    return "ERR"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-links", action="store_true", help="HTTP-check every source URL (network)")
    ap.add_argument("--write-json-schema", action="store_true", help="regenerate schema/entry.schema.json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    schema = load_yaml(SCHEMA_YAML)
    Draft202012Validator.check_schema(schema)
    if args.write_json_schema:
        SCHEMA_JSON.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {SCHEMA_JSON.relative_to(ROOT)}")
    elif SCHEMA_JSON.exists() and json.loads(SCHEMA_JSON.read_text()) != schema:
        print("ERROR: schema/entry.schema.json is out of date; run validate.py --write-json-schema")
        return 1

    validator = Draft202012Validator(schema)
    classes, tags, chains = vocab()
    today = dt.date.today()

    entries = load_entries()
    if not entries:
        print("ERROR: no entries found")
        return 1
    ids, slugs = {}, {}
    total_err = total_warn = 0
    for path, e in entries:
        if not isinstance(e, dict):
            print(f"FAIL {path.name}: not a mapping")
            total_err += 1
            continue
        errs, warns = check_entry(path, e, validator, classes, tags, chains, today)
        for key, seen, label in (("id", ids, "id"), ("slug", slugs, "slug")):
            v = e.get(key)
            if v in seen:
                errs.append(f"duplicate {label} also in {seen[v]}")
            seen[v] = path.name
        if args.check_links and not errs:
            for s in e["sources"]:
                st = check_link(s["url"])
                if st == 200:
                    continue
                why = bot_block_reason(s["url"])
                if st in (403, 429) and why:
                    warns.append(f"link check {st} ({why}; not verified): {s['url']}")
                else:
                    errs.append(f"link check {st}: {s['url']}")
        total_err += len(errs)
        total_warn += len(warns)
        if errs or warns or not args.quiet:
            print(f"{'FAIL' if errs else 'ok  '} {path.name}")
        for m in errs:
            print(f"     ERROR: {m}")
        for m in warns:
            print(f"     warn : {m}")
    print(f"\n{len(entries)} entries, {total_err} errors, {total_warn} warnings")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
