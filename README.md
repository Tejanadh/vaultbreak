# Vaultbreak

One YAML file per public incident. A class, a short summary, a small snippet written for this repo, and the links. Some files have a Semgrep or Slither rule. CI runs the rule. It has to hit the vulnerable fixture and stay quiet on the fixed one.

## Where it stands

27 entries, 2022 through 2025, Ethereum and Solana. All 27 still have `needs_review: true` and `llm_assisted: true`. No root cause has been signed off. A schema pass means the file is complete.

`VB-2024-0018` is Radiant, January 2024. Radiant's postmortem says a new USDC market on Arbitrum was empty and about 1900 WETH was borrowed. On 4 Oct 2026 the hashes in that file were fetched with `eth_getTransactionByHash` against `https://arb1.arbitrum.io/rpc`. Block 166405628 is timestamped 2024-01-02 18:53:23Z, the same minute the postmortem gives. Secondary pages say $4.5M and $4.6M, so the file stores the range.

Ethereum hashes were filled the same day for Euler, Nomad, Bybit, and Ronin, after `eth_getTransactionByHash` and the receipt on `https://eth.drpc.org`, cross-checked on `https://rpc.mevblocker.io`. Solana signatures for Wormhole, Cashio, Crema, Nirvana, and Mango were read with `getTransaction` on `https://api.mainnet-beta.solana.com`. Solend is in the set without a transaction: the two signatures that were fetched are dated 28 Oct 2022, and the write-ups put the drain on 2 Nov 2022.

17 entries still have empty `affected_contracts` and `attack_txs`. That is the 16 older EVM files plus Solend.

Seven detectors. They match a code shape. The Conic entry stays `draft` because `vb-readonly-reentrancy-lp-view` does not flag that entry's own snippet. The two Anchor rules are line checks. Semgrep's Rust parser would not take a lifetime pattern, so the constraint has to be on the same line as the field. The limit is in the entry notes.

Nomad is the one fork replay. On 4 Oct 2026, `forge 1.7.1` ran `replay/nomad/test/NomadReplay.t.sol` against `https://eth.drpc.org` at block 15259100. The test calls `vm.transact` on the process hash and checks the WBTC delta from the receipt. It passed, so that entry's `replay_status` is `verified`. The DeFiHackLabs file is linked and not copied. Every other `replay_status` is still `unverified`. Euler was not replayed.

Incidents that were not verified are not in the set. `pda_seed_collision` and `arbitrary_cpi` are in the taxonomy and have no entry. Missing id numbers are the skips. The list is in `docs/STATUS.md`.

`scripts/check_all.sh` was run on 4 Oct 2026 after these edits. Validation, unit tests, snippet compiles, detector counts, and the site filter tests passed. That script does not run the Foundry replay. The Nomad forge command above was run on its own, and it passed.

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
fixtures/    small vulnerable and fixed files written for this repo
scripts/     validate, compile, test detectors, build, vb.py
replay/      one Foundry fork test (Nomad)
site/src/    the static site
tests/
docs/        LICENSING.md, STATUS.md
```

## License

Code is MIT (`LICENSE`). The entries are CC-BY-4.0 (`LICENSE-DATA`). Rekt, DefiLlama, SlowMist, and DeFiHackLabs are linked. Their text is not copied. `docs/LICENSING.md`. How to add a file: `CONTRIBUTING.md`.

The Slither plugin imports Slither, which is AGPL-3.0. That file is still marked MIT, and that combination is not settled. Do not describe the plugin as clean MIT until it is. The Semgrep rules do not import Slither.

The snippets are illustrations. Loss figures come from the cited pages and often disagree, so a range is normal. This is not an audit.
