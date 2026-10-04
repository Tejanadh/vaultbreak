# Status (2026-10-04)

I only kept incidents I had already marked verified, and only EVM. The notes file those marks came from is not in this repo. I HTTP-checked the source links on this date. Two Medium posts return 403 to the checker, so those two links are still unchecked.

## Included (21)

| ID | Incident | Class | Detector |
|---|---|---|---|
| VB-2022-0002 | Qubit Finance | bridge_verification | - |
| VB-2022-0005 | Beanstalk | governance_flashloan | - |
| VB-2022-0006 | Fei Rari (Fuse) | reentrancy | slither: vb-eth-send-before-write |
| VB-2022-0009 | Nomad Bridge | bridge_verification | - |
| VB-2022-0010 | Transit Swap | arbitrary_external_call | semgrep: vb-arbitrary-transferfrom-approve |
| VB-2023-0012 | Euler Finance | donation_inflation | - |
| VB-2023-0013 | Sentiment | reentrancy | semgrep: vb-readonly-reentrancy-lp-view |
| VB-2023-0014 | Hundred Finance (2023) | donation_inflation | - |
| VB-2023-0015 | Conic Finance | reentrancy | semgrep (draft; does not flag its own snippet) |
| VB-2023-0016 | Curve / Vyper | reentrancy | none possible from source (compiler bug) |
| VB-2023-0017 | KyberSwap Elastic | rounding_arithmetic | - |
| VB-2024-0018 | Radiant Capital (Jan 2024) | donation_inflation | semgrep: vb-exchange-rate-from-balance |
| VB-2024-0019 | Hedgey Finance | arbitrary_external_call | semgrep: vb-arbitrary-transferfrom-approve (partial) |
| VB-2024-0020 | Sonne Finance | donation_inflation | - |
| VB-2024-0021 | UwU Lend | oracle_manipulation | - |
| VB-2024-0022 | Ronin Bridge (2024) | proxy_upgrade_init | - |
| VB-2024-0023 | Penpie | reentrancy | - |
| VB-2025-0025 | Bybit | delegatecall (hybrid) | semgrep: vb-delegatecall-user-target |
| VB-2025-0026 | KiloEx | access_control | - |
| VB-2025-0031 | GMX V1 | reentrancy | - |
| VB-2025-0033 | Balancer v2 | rounding_arithmetic | - |

## Skipped on purpose

| Incident | Reason |
|---|---|
| Cork Protocol, Texture, Tectonic | Report marks them partial (`P`) |
| Bunni v2 | Report: mechanism detail unverified |
| Truebit | Report notes the source page was not read in full |
| Audius | Report: exact date unverified (2022-07-23..25) |
| Multichain/AnySwap | Report evidence was a search synthesis plus DefiLlama only |
| Radiant (Jan 2024) | Added as VB-2024-0018. Still `needs_review: true`. Tx hashes were read from an Arbitrum node on 2026-10-04. |
| Kelp, Drift, zkLend | Operational/hybrid, or not EVM (Starknet), or beyond this phase's scope |
| Wormhole, Cashio, Crema, Mango, Loopscale, Cetus | Solana / Move, not EVM |
| Orbit, Omni replay, Nirvana, Allbridge, Raydium, Aquifer | Report marks them unverified |

## Detector reliability

* All five pass their fixtures with exact finding counts (`detectors/expected.yaml`).
* `vb-exchange-rate-from-balance` only matches `balanceOf(address(this))` divided by a share supply. It does not understand Aave `liquidityIndex`. The Radiant entry uses it as the code shape, not as a proof about the live pool.
* The three Semgrep rules also fire on the vulnerable snippet of their own entries and stay silent on
  every fixed snippet and on every other entry's snippets (checked 2026-10-04), except Conic's
  ETH/WETH guard mix-up, which a syntactic rule cannot see. That entry's detector is `draft`.
* Semgrep's Solidity support is experimental; rules use only simple function-scope patterns and
  do not do data-flow. A struct field passed as a spender (the real Hedgey shape) is missed.
* The Slither plugin overlaps Slither's built-in `reentrancy-eth`; it is kept as a small
  readable detector with fixtures, and is not claimed to be more precise.
* No detector was attempted for rounding, oracle, governance, bridge-config or compiler-bug
  classes; they are not reliably expressible as a single-function pattern.

## Known data gaps

* Radiant (VB-2024-0018) is the only entry with node-checked tx hashes and contract addresses. Every other `affected_contracts` / `attack_txs` list is still empty. No Foundry mainnet replay (`replay_status: unverified` everywhere, including Radiant).
* `python scripts/vb.py` queries `build/vaultbreak.sqlite` (`list`, `show`, `search`).
* Dates differ by about a day between DeFiHackLabs and other sources for several incidents; the
  entry's `confidence.notes` says so.
* `date_source` is `aggregator` or `postmortem`, never `tx`, because no tx hashes were verified.
* OAK taxonomy mapping not done (not verified).

## Next steps (suggested)

1. Human review of all 21 entries (set `needs_review: false`, fill `human_reviewed_by`).
2. Explorer-verified addresses and tx hashes for the other 20 entries. Radiant is the pattern: read the node, do not copy a hash you have not fetched.
3. More detectors where a reliable shape exists (e.g. zero-value root in initialisers).
4. Foundry replay harness for ~10 entries; Pagefind for full-text search.
