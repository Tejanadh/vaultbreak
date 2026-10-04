# Vaultbreak

I got tired of incident lists. Date, name, "reentrancy", a link. Fine if you want the news. Useless when I wanted the actual shape of the bug, and a check that fires on that shape and stays quiet on the fix.

This repo is one YAML file per incident. My summary, one class, a small snippet I wrote (not their code), and the links I opened. Some files also have a Semgrep or Slither rule. CI runs it. It has to hit the vulnerable fixture and miss the fixed one.

## Where it stands

21 EVM incidents, 2022 through 2025. I have not reviewed them. Every file still has `needs_review: true`. A lot of the wording started as a model draft from the sources, then had to pass the schema. Passing the schema means the file is complete. It does not mean I signed the root cause.

Radiant, January 2024, is the one I went back to. `VB-2024-0018`. The project postmortem says a new USDC market on Arbitrum was empty and about 1900 WETH got borrowed. I read the transactions off an Arbitrum node. The dollar writeups say $4.5M and $4.6M, so the file keeps both. I have not replayed it.

The other 20 have no addresses and no hashes. Those fields stay empty until I fetch them.

Five detectors. They match a code shape. They do not say a live protocol is safe. The Conic rule does not flag Conic's own snippet. That is written on the entry.

I left out incidents I could not verify, and anything that is not EVM. Missing id numbers are those skips. The list is in `docs/STATUS.md`.

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
solc-select install 0.8.20 && solc-select use 0.8.20

scripts/check_all.sh
python scripts/vb.py search "empty market"
python scripts/vb.py show VB-2024-0018
```

That validates the files, compiles the snippets, runs the detectors, and builds the site. Then:

```bash
cd build/site && python3 -m http.server
```

Link check, when you want it: `python scripts/validate.py --check-links`.

## What gets rejected

Wrong filename, unknown class or tag, only aggregator links, a loss number that cites a link missing from `sources`, a snippet that does not say it is illustrative, a `TODO` left in the text. Fewer than two sources is a warning.

## Layout

```
entries/     one YAML file per incident
schema/      the entry schema
taxonomy/    classes, tags, chains
detectors/   Semgrep rules, one Slither plugin, expected counts
fixtures/    tiny vulnerable and fixed contracts I wrote
scripts/     validate, compile, test detectors, build, vb.py
site/src/    the static site
tests/
docs/        LICENSING.md, STATUS.md
```

## License

Code is MIT (`LICENSE`). The entries are CC-BY-4.0 (`LICENSE-DATA`). I link to Rekt, DefiLlama, SlowMist, and DeFiHackLabs. I do not copy them. Details in `docs/LICENSING.md`. How to add a file: `CONTRIBUTING.md`.

The snippets are illustrations. Loss figures come from the cited pages and they often disagree, so a range is normal. This is not an audit.
