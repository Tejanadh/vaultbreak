# Vaultbreak

One YAML file per public EVM incident. A class, a short summary, a small snippet written for this repo, and the links. Some files have a Semgrep or Slither rule. CI runs the rule. It has to hit `vulnerable.sol` and stay quiet on `fixed.sol`.

## Where it stands

21 entries, 2022 through 2025. All 21 still have `needs_review: true` and `llm_assisted: true`. No root cause has been signed off. A schema pass means the file is complete.

`VB-2024-0018` is Radiant, January 2024. Radiant's postmortem says a new USDC market on Arbitrum was empty and about 1900 WETH was borrowed. On 4 Oct 2026 the hashes in that file were fetched with `eth_getTransactionByHash` against `https://arb1.arbitrum.io/rpc`. Block 166405628 is timestamped 2024-01-02 18:53:23Z, the same minute the postmortem gives. Secondary pages say $4.5M and $4.6M, so the file stores the range. Nothing has been replayed on a fork.

The other 20 entries have empty `affected_contracts` and `attack_txs`.

Five detectors. They match a code shape. The Conic entry stays `draft` because `vb-readonly-reentrancy-lp-view` does not flag that entry's own snippet. The limit is in the entry notes.

Incidents that were not verified, and anything that is not EVM, are not in the set. Missing id numbers are those skips. The list is in `docs/STATUS.md`.

`scripts/check_all.sh` was run on 4 Oct 2026. Validation, unit tests, snippet compiles, detector counts, and the site filter tests passed.

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
solc-select install 0.8.20 && solc-select use 0.8.20

scripts/check_all.sh
python scripts/vb.py search "empty market"
python scripts/vb.py show VB-2024-0018
```

Then:

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
fixtures/    small vulnerable and fixed contracts written for this repo
scripts/     validate, compile, test detectors, build, vb.py
site/src/    the static site
tests/
docs/        LICENSING.md, STATUS.md
```

## License

Code is MIT (`LICENSE`). The entries are CC-BY-4.0 (`LICENSE-DATA`). Rekt, DefiLlama, SlowMist, and DeFiHackLabs are linked. Their text is not copied. `docs/LICENSING.md`. How to add a file: `CONTRIBUTING.md`.

The Slither plugin imports Slither, which is AGPL-3.0. That file is still marked MIT, and that combination is not settled. Do not describe the plugin as clean MIT until it is. The Semgrep rules do not import Slither.

The snippets are illustrations. Loss figures come from the cited pages and often disagree, so a range is normal. This is not an audit.
