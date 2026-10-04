# Vaultbreak

A searchable, machine-checkable database of real smart-contract exploit patterns.
One YAML file per incident, validated against a schema in CI. Each entry has our own
root-cause summary, a normalised class, a minimal *illustrative* code shape, source links
and a confidence rating. Some entries also ship a Semgrep or Slither detector with passing
and failing fixtures that CI runs.

## Why

Incident lists already exist and are plentiful. What was missing, as far as we could tell
from the research behind this project (`docs/STATUS.md`), is a record that links, in one
validated place: a normalised root-cause class, the vulnerable code shape, a detector that
is *proven* to fire on the vulnerable fixture and stay silent on the fixed one, and
provenance (including where aggregators disagree). Quality over volume.

## Status (honest)

Early draft, **Phase 0/1 of the plan**. The repo is public at
https://github.com/Tejanadh/vaultbreak. Entries are still unreviewed.

* **21 EVM entries**, from incidents the research report marked as verified (2022-2025), plus
  Radiant Capital (January 2024), which that report had verified and then deferred.
  Entries are **LLM-drafted and not yet human-reviewed**:
  every entry carries `confidence.needs_review: true` and `provenance.human_reviewed_by: null`.
* **Counts:** 6 reentrancy, 4 donation/inflation, 2 rounding, 2 arbitrary external call,
  2 bridge verification, 1 each governance, delegatecall, access control, proxy/init, oracle.
  13 critical, 8 high. Overall confidence: 6 high, 15 medium.
* **5 detectors** with fixtures and exact expected results (4 Semgrep, 1 Slither); 7 entries
  reference one. They are **heuristic, syntactic checks of a code shape**, not proofs that
  a codebase is safe or vulnerable. Limits are written in each entry's `detectors[].notes`.
* **On-chain data:** only Radiant (`VB-2024-0018`) has addresses and tx hashes, and those were
  read from an Arbitrum node. Every other entry leaves `affected_contracts` and `attack_txs`
  empty. We do not invent addresses or hashes.
* **PoCs are links only** (DeFiHackLabs). `replay_status` is `unverified` everywhere; nothing
  has been replayed on a fork.
* **Not covered yet:** Solana/Move/Cairo entries, Foundry mainnet replay, bytecode matching,
  a `labels_disagree` page, Pagefind full-text index (the site uses a tiny client-side filter).
  A query CLI does exist: `python scripts/vb.py`.
* Incidents the report marked partial or unverified (Cork, Texture, Bunni mechanism, Tectonic,
  Truebit, Orbit, Omni replay) are **deliberately skipped**. So are non-EVM incidents.
* The research report's ID numbers are kept (e.g. `VB-2023-0013` is Sentiment) so gaps in the
  sequence are the skipped incidents.

## Layout

```
entries/      one YAML per incident (source of truth)
schema/       entry.schema.yaml (authoring) + entry.schema.json (generated)
taxonomy/     vuln_class.yaml, tags.yaml, chains.yaml
detectors/    semgrep/*.yaml, slither/*.py, expected.yaml (exact expected results)
fixtures/     <entry id>/{vulnerable,fixed}.sol  (original, tiny)
scripts/      validate.py, compile_snippets.py, test_detectors.py, build.py, vb.py
site/src/     static site sources (plain HTML/JS, no framework)
tests/        validator negative tests, site filter test
docs/         LICENSING.md, STATUS.md
.github/      ci.yml, PR template (committed, never pushed)
```

## Quick start

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
solc-select install 0.8.20 && solc-select use 0.8.20

scripts/check_all.sh   # validate, unit tests, compile snippets, detector tests, build site, site tests
python scripts/vb.py search "empty market"
python scripts/vb.py show VB-2024-0018
python scripts/validate.py --check-links   # network: HEAD/GET every source URL
cd build/site && python3 -m http.server    # then open http://localhost:8000
```

`build/` gets `vaultbreak.json`, `vaultbreak.sqlite` (with FTS5) and the static site (entry
pages, taxonomy page, search/filter by class, chain, severity, date range, text, has-detector;
filter state lives in the URL hash).

## What validation enforces

JSON Schema; file name = slug; ids and slugs unique; id year = date year; no future dates;
`vuln_class`, tags and chains exist in `taxonomy/`; at least one postmortem/analysis/primary source
(aggregators alone are rejected); `loss_usd.sources` and `fix.reference_url` appear in `sources[]`;
no `TODO` placeholders; snippets carry an `ILLUSTRATIVE` comment; detector and fixture files exist.
It warns when an entry has fewer than two sources.

## Sourcing and licensing

Code is MIT (`LICENSE`); data is CC-BY-4.0 (`LICENSE-DATA`). We store our own summaries,
facts with links, and our own minimal code. We link to Rekt, DefiLlama, SlowMist, DeFiHackLabs
and others but never copy or mirror them. Details and an open question about the Slither plugin:
`docs/LICENSING.md`. Contributions: `CONTRIBUTING.md`.

## Disclaimer

Illustrative snippets are not the affected projects' code. Loss figures are as reported by the
cited sources and often disagree; ranges are shown. Nothing here is audit advice.
