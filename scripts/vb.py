#!/usr/bin/env python3
"""Query the built Vaultbreak database.

  python scripts/vb.py list [--class donation_inflation] [--chain arbitrum] [--severity high]
  python scripts/vb.py show VB-2024-0018
  python scripts/vb.py search "empty market"

Reads build/vaultbreak.sqlite. Run scripts/build.py first.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys

from common import ROOT

DB = ROOT / "build" / "vaultbreak.sqlite"


def connect():
    if not DB.is_file():
        raise SystemExit(f"no database at {DB}. Run: python scripts/build.py")
    return sqlite3.connect(DB)


def _where(args):
    clauses, params = [], []
    if args.vuln_class:
        clauses.append("vuln_class = ?")
        params.append(args.vuln_class)
    if args.chain:
        clauses.append("(',' || chains || ',') LIKE ?")
        params.append(f"%,{args.chain},%")
    if args.severity:
        clauses.append("severity = ?")
        params.append(args.severity)
    sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return sql, params


def cmd_list(args) -> int:
    db = connect()
    sql, params = _where(args)
    rows = db.execute(
        "SELECT id, date, vuln_class, severity, title FROM entries" + sql + " ORDER BY date DESC, id",
        params,
    ).fetchall()
    if not rows:
        print("no entries")
        return 1
    for row in rows:
        print(f"{row[0]}  {row[1]}  {row[2]:22} {row[3]:8}  {row[4]}")
    print(f"{len(rows)} entries")
    return 0


def cmd_show(args) -> int:
    db = connect()
    row = db.execute("SELECT json FROM entries WHERE id = ? OR slug = ?", (args.id, args.id)).fetchone()
    if not row:
        print(f"not found: {args.id}", file=sys.stderr)
        return 1
    e = json.loads(row[0])
    loss = e["loss_usd"]
    print(f"{e['id']}  {e['title']}")
    print(f"date: {e['date']} ({e['date_source']})")
    print(f"class: {e['vuln_class']}   severity: {e['severity']['rating']}   chains: {', '.join(e['chains'])}")
    print(f"loss: {loss['reported_min']} .. {loss['reported_max']} USD")
    print()
    print(e["root_cause"])
    print()
    if e.get("attack_txs"):
        print("transactions:")
        for tx in e["attack_txs"]:
            print(f"  {tx['chain']}  {tx['hash']}")
    if e.get("affected_contracts"):
        print("contracts:")
        for c in e["affected_contracts"]:
            mark = "verified" if c["verified_on_explorer"] else "unverified"
            print(f"  {c['chain']}  {c['address']}  {c['role']}  ({mark})")
    print("sources:")
    for s in e["sources"]:
        print(f"  [{s['type']}] {s['publisher']}  {s['url']}")
    return 0


def search_terms(query: str) -> list[str]:
    terms = []
    for raw in query.lower().replace("_", " ").split():
        term = "".join(ch for ch in raw if ch.isalnum())
        if term:
            terms.append(term)
    return terms


def cmd_search(args) -> int:
    terms = search_terms(args.query)
    if not terms:
        print("empty search", file=sys.stderr)
        return 2
    db = connect()
    has_fts = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='entries_fts'").fetchone()
    if has_fts:
        match = " AND ".join(terms)
        rows = db.execute(
            """SELECT e.id, e.date, e.title FROM entries e
               JOIN entries_fts f ON f.id = e.id
               WHERE entries_fts MATCH ?
               ORDER BY e.date DESC""",
            (match,),
        ).fetchall()
    else:
        sql = "SELECT id, date, title FROM entries WHERE " + " AND ".join(
            ["lower(root_cause || ' ' || title) LIKE ?"] * len(terms)
        ) + " ORDER BY date DESC"
        rows = db.execute(sql, [f"%{t}%" for t in terms]).fetchall()
    if not rows:
        print("no matches")
        return 1
    for row in rows:
        print(f"{row[0]}  {row[1]}  {row[2]}")
    print(f"{len(rows)} matches")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Query the Vaultbreak sqlite build")
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list")
    pl.add_argument("--class", dest="vuln_class")
    pl.add_argument("--chain")
    pl.add_argument("--severity")
    pl.set_defaults(func=cmd_list)
    ps = sub.add_parser("show")
    ps.add_argument("id")
    ps.set_defaults(func=cmd_show)
    pq = sub.add_parser("search")
    pq.add_argument("query")
    pq.set_defaults(func=cmd_search)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
