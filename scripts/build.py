#!/usr/bin/env python3
"""Build derived artefacts from entries/ into build/ (git-ignored).

  build/vaultbreak.json     all entries, normalised (for the site, CLI, other tools)
  build/vaultbreak.sqlite   entries table + FTS5 index (ad-hoc queries)
  build/site/               static site: index.html (search/filter), entries/<slug>.html,
                            taxonomy.html, data.json, app.js, filter.js, style.css

Stdlib + PyYAML only. Runs validate first; refuses to build invalid data.
"""
from __future__ import annotations

import html
import json
import pathlib
import shutil
import sqlite3
import subprocess
import sys

from common import ROOT, TAXONOMY, load_entries, load_yaml

BUILD = ROOT / "build"
SITE_SRC = ROOT / "site" / "src"
SITE_OUT = BUILD / "site"
esc = html.escape


def money(n):
    if n is None:
        return "n/a"
    for div, unit in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if n >= div:
            v = n / div
            return f"${v:.1f}{unit}".replace(".0", "")
    return f"${n:,.0f}"


def loss_text(e):
    lo, hi = e["loss_usd"]["reported_min"], e["loss_usd"]["reported_max"]
    return money(lo) if lo == hi else f"{money(lo)} - {money(hi)}"


def flat(e, classes):
    """Compact record used by the browser."""
    cls = classes[e["vuln_class"]]["name"]
    text = " ".join([e["title"], e["protocol"]["name"], e["root_cause"], cls, " ".join(e["tags"]),
                     " ".join(e["chains"]), " ".join(e.get("preconditions", []))]).lower().replace("_", " ")
    return {
        "id": e["id"], "slug": e["slug"], "title": e["title"], "date": e["date"], "year": int(e["date"][:4]),
        "chains": e["chains"], "language": e["language"], "protocol": e["protocol"]["name"],
        "category": e["protocol"]["category"], "vuln_class": e["vuln_class"], "class_name": cls,
        "severity": e["severity"]["rating"], "scope": e["scope"], "tags": e["tags"],
        "loss_min": e["loss_usd"]["reported_min"], "loss_max": e["loss_usd"]["reported_max"],
        "loss_text": loss_text(e), "has_detector": any(d["status"] in ("validated", "draft") for d in e.get("detectors", [])),
        "detector_validated": any(d["status"] == "validated" for d in e.get("detectors", [])),
        "confidence": e["confidence"]["overall"], "needs_review": e["confidence"]["needs_review"],
        "summary": e["root_cause"], "text": text,
    }


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - Vaultbreak</title><link rel="stylesheet" href="{root}style.css"></head>
<body><header><a class="brand" href="{root}index.html">Vaultbreak</a>
<nav><a href="{root}index.html">Entries</a> <a href="{root}taxonomy.html">Taxonomy</a></nav></header>
<main>{body}</main>
<footer>Draft. Summaries and snippets were written for this repo. Facts point at the source. Data CC-BY-4.0, code MIT.
Entries marked <em>needs review</em> have not been signed off.</footer></body></html>"""


def entry_page(e, classes):
    c = e["confidence"]
    rows = [
        ("Date (UTC)", e["date"]), ("Chains", ", ".join(e["chains"])), ("Language", e["language"]),
        ("Protocol", f"{e['protocol']['name']} ({e['protocol']['category']})"),
        ("Class", classes[e["vuln_class"]]["name"]), ("Scope", e["scope"]),
        ("Severity", f"{e['severity']['rating']} - {e['severity']['rationale']}"),
        ("Reported loss", loss_text(e) + (f" (recovered ~{money(e['loss_usd']['recovered'])})" if e["loss_usd"].get("recovered") else "")),
        ("Confidence", f"overall {c['overall']} (root cause {c['root_cause']}, loss {c['loss']}, date {c['date']})"
                       + ("; needs review" if c["needs_review"] else "")),
    ]
    meta = "".join(f"<tr><th>{esc(k)}</th><td>{esc(str(v))}</td></tr>" for k, v in rows)
    tags = " ".join(f'<span class="tag">{esc(t)}</span>' for t in e["tags"])
    pre = "".join(f"<li>{esc(p.replace('_', ' '))}</li>" for p in e.get("preconditions", []))
    cp = e["code_pattern"]
    det = ""
    for d in e.get("detectors", []):
        det += (f"<li><code>{esc(d['path'])}</code> ({esc(d['engine'])}, <b>{esc(d['status'])}</b>)<br>"
                f"fixtures: <code>{esc(d['true_positive_fixture'])}</code> / <code>{esc(d['false_positive_fixture'])}</code>"
                f"<br><small>{esc(d.get('notes', ''))}</small></li>")
    det = f"<h2>Detectors</h2><ul>{det}</ul>" if det else "<h2>Detectors</h2><p>None yet.</p>"
    srcs = "".join(f'<li><a href="{esc(s["url"])}" rel="noopener nofollow">{esc(s["publisher"])}</a> '
                   f'<small>({esc(s["type"])}, accessed {esc(s["accessed"])})</small></li>' for s in e["sources"])
    poc = "".join(f'<li><a href="{esc(p["url"])}" rel="noopener nofollow">external PoC ({esc(p["framework"])})</a> '
                  f'<small>replay status: {esc(p["replay_status"])}</small></li>' for p in e.get("poc", []))
    dis = "".join(f"<li><b>{esc(d['source'])}</b>: {esc(d['label'])} <small>{esc(d.get('note', ''))}</small></li>"
                  for d in e.get("labels_disagree", []))
    body = f"""<p><a href="index.html">&larr; all entries</a></p>
<h1>{esc(e['title'])}</h1><p class="id">{esc(e['id'])}</p>
<table class="meta">{meta}</table><p>{tags}</p>
<h2>Root cause (our summary)</h2><p>{esc(e['root_cause'])}</p>
<h2>Preconditions</h2><ul>{pre}</ul>
<h2>Code shape <span class="badge">illustrative, not the project's code</span></h2>
<h3>Vulnerable</h3><pre>{esc(cp['vulnerable_snippet'])}</pre>
<h3>Fixed</h3><pre>{esc(cp['fixed_snippet'])}</pre><p>{esc(cp['explanation'])}</p>
{det}
<h2>Fix</h2><p>{esc(e.get('fix', {}).get('summary', ''))}</p>
<h2>Sources</h2><ul>{srcs}</ul>
{('<h2>Proofs of concept</h2><ul>' + poc + '</ul>') if poc else ''}
{('<h2>Where other labels disagree</h2><ul>' + dis + '</ul>') if dis else ''}
{('<p><small>Confidence notes: ' + esc(c.get('notes', '')) + '</small></p>') if c.get('notes') else ''}"""
    return PAGE.format(title=esc(e["title"]), root="../", body=body)


def taxonomy_page(classes, counts):
    rows = "".join(f"<tr><td><a href=\"index.html#class={esc(k)}\">{esc(v['name'])}</a></td><td>{counts.get(k, 0)}</td>"
                   f"<td>{esc(v['description'])}</td><td>{esc(', '.join(v.get('defillama', [])))}</td>"
                   f"<td>{esc(', '.join(v.get('swc', [])))}</td></tr>" for k, v in classes.items())
    body = ("<h1>Taxonomy</h1><p>One primary root-cause class per entry. Mappings are our own judgement.</p>"
            f"<table class='meta'><tr><th>Class</th><th>Entries</th><th>Meaning</th><th>DefiLlama label(s)</th><th>SWC</th></tr>{rows}</table>")
    return PAGE.format(title="Taxonomy", root="", body=body)


def build_sqlite(entries, flats, path):
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.execute("""create table entries(id text primary key, slug text, title text, date text, chains text, language text,
                  protocol text, vuln_class text, severity text, scope text, loss_min real, loss_max real,
                  has_detector int, confidence text, root_cause text, tags text, json text)""")
    for e, f in zip(entries, flats):
        db.execute("insert into entries values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (e["id"], e["slug"], e["title"], e["date"], ",".join(e["chains"]), e["language"], e["protocol"]["name"],
                    e["vuln_class"], f["severity"], e["scope"], f["loss_min"], f["loss_max"], int(f["has_detector"]),
                    f["confidence"], e["root_cause"], ",".join(e["tags"]), json.dumps(e)))
    try:
        # A normal FTS5 table, not contentless: content='' stores no column values,
        # so a later SELECT of id comes back NULL and the query CLI cannot join.
        db.execute("create virtual table entries_fts using fts5(id, title, root_cause, tags)")
        for e, f in zip(entries, flats):
            db.execute("insert into entries_fts values (?,?,?,?)", (e["id"], e["title"], e["root_cause"], f["text"]))
        fts = True
    except sqlite3.OperationalError:
        fts = False  # SQLite build without FTS5
    db.commit()
    db.close()
    return fts


def main() -> int:
    here = pathlib.Path(__file__).parent
    if subprocess.run([sys.executable, str(here / "validate.py"), "--quiet"]).returncode:
        print("build aborted: validation failed")
        return 1
    classes = load_yaml(TAXONOMY / "vuln_class.yaml")["classes"]
    entries = [e for _, e in load_entries()]
    entries.sort(key=lambda e: e["date"], reverse=True)
    flats = [flat(e, classes) for e in entries]

    if BUILD.exists():
        shutil.rmtree(BUILD)
    (SITE_OUT / "entries").mkdir(parents=True)
    (BUILD / "vaultbreak.json").write_text(json.dumps({"version": 1, "count": len(entries), "entries": entries}, indent=1))
    fts = build_sqlite(entries, flats, BUILD / "vaultbreak.sqlite")

    for f in ("app.js", "filter.js", "style.css"):
        shutil.copy(SITE_SRC / f, SITE_OUT / f)
    options = {
        "classes": [{"id": k, "name": v["name"]} for k, v in classes.items() if any(e["vuln_class"] == k for e in entries)],
        "chains": sorted({c for e in entries for c in e["chains"]}),
        "severities": [s for s in ("critical", "high", "medium", "low") if any(e["severity"]["rating"] == s for e in entries)],
        "years": sorted({int(e["date"][:4]) for e in entries}),
    }
    (SITE_OUT / "data.json").write_text(json.dumps({"entries": flats, "options": options}))
    shutil.copy(SITE_SRC / "index.html", SITE_OUT / "index.html")
    for e in entries:
        (SITE_OUT / "entries" / f"{e['slug']}.html").write_text(entry_page(e, classes))
    counts = {}
    for e in entries:
        counts[e["vuln_class"]] = counts.get(e["vuln_class"], 0) + 1
    (SITE_OUT / "taxonomy.html").write_text(taxonomy_page(classes, counts))
    print(f"built {len(entries)} entries -> {BUILD.relative_to(ROOT)}/ (json, sqlite{' + FTS5' if fts else ', no FTS5'}, site with "
          f"{len(entries) + 2} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
