# Status (2026-10-04)

The corpus started as public EVM incidents. The notes file those marks came from is not in this repo. Source links were HTTP-checked on this date. Two Medium posts return 403 to the checker, so those two links are still unchecked.

## Included (27)

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
| VB-2022-0003 | Wormhole | unchecked_sysvar | semgrep: vb-anchor-account-without-signer (shape only) |
| VB-2022-0004 | Cashio | account_type_confusion | semgrep: vb-anchor-unchecked-account-no-owner (shape only) |
| VB-2022-0007 | Crema Finance | missing_owner_check | - |
| VB-2022-0008 | Nirvana Finance | oracle_manipulation | - |
| VB-2022-0011 | Mango Markets | oracle_manipulation | - |
| VB-2022-0012 | Solend | oracle_manipulation | - |

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
| Loopscale, Cetus | Not verified in the Solana pass. Cetus is Move. No Loopscale signature was fetched. |
| Orbit, Omni replay, Nirvana, Allbridge, Raydium, Aquifer | Report marks them unverified |

## Solana pass (step 2, 2026-10-04)

`chain: solana` was already in `taxonomy/chains.yaml`. Taxonomy v2 adds `missing_signer_check`, `missing_owner_check`, `account_type_confusion`, `pda_seed_collision`, `arbitrary_cpi`, and `unchecked_sysvar`. The address and hash patterns now accept Solana base58 as well as EVM hex.

`getTransaction` on `https://api.mainnet-beta.solana.com` confirmed the stored signatures. `https://solana-rpc.publicnode.com` returned null for the historical signatures it was given, so it is not a second confirmation.

| Entry | What was stored | Left out |
|---|---|---|
| VB-2022-0003 Wormhole | ImmuneBytes signature, slot 119025020, 2022-02-02T17:58:04Z. Class `unchecked_sysvar`. | The signer Semgrep rule is a fixture shape under this id. It does not parse the sysvar bug. |
| VB-2022-0004 Cashio | Five CertiK signatures on 2022-03-23, 08:15:26Z through 08:21:41Z. | CertiK's 08:23:26Z clock time is later than these block times. |
| VB-2022-0007 Crema | Two signatures from the Crema thread. The tick transaction is 2022-07-02T20:07:57Z. | The earlier signature only invokes the System program. No program id was named by Crema, so the invoked program is unlabeled. |
| VB-2022-0008 Nirvana | One signature, slot 143469271, 2022-07-28T05:11:56Z. Accounts match the CertiK labels. | The Block calls it an oracle. CertiK calls it a Buy command. Both notes are on the entry. |
| VB-2022-0011 Mango | Four Sec3 signatures on 2022-10-11, 22:23:40Z through 22:36:34Z. | Sec3 counts 44 transactions on Account1. The other 40 were not fetched. |
| VB-2022-0012 Solend | Incident only. Ackee and The Block say 2022-11-02 and $1.26M bad debt. `attack_txs` is empty. | ImmuneBytes' two signatures are real and are slot 157809596 at 2022-10-28T01:27:35Z, the failed attempt. They are not stored as the November attack. Pool addresses were not in those transactions. |
| `pda_seed_collision`, `arbitrary_cpi` | Classes exist. | No incident with a confirmed signature was added for either class. |

## Detector reliability

* All seven pass their fixtures with exact finding counts (`detectors/expected.yaml`). The two Anchor rules are line-oriented Rust regexes. Semgrep's Rust parser rejected lifetime patterns, which is why the signer or owner token has to sit on the same line as the field.
* `vb-exchange-rate-from-balance` only matches `balanceOf(address(this))` divided by a share supply. It does not understand Aave `liquidityIndex`. The Radiant entry uses it as the code shape, not as a proof about the live pool.
* The three Solidity Semgrep rules also fire on the vulnerable snippet of their own entries and stay silent on
  every fixed snippet and on every other entry's snippets (checked 2026-10-04), except Conic's
  ETH/WETH guard mix-up, which a syntactic rule cannot see. That entry's detector is `draft`.
  The two Anchor rules are not part of that snippet cross-check, because it only runs on Solidity snippets.
* Semgrep's Solidity support is experimental; rules use only simple function-scope patterns and
  do not do data-flow. A struct field passed as a spender (the real Hedgey shape) is missed.
* The Slither plugin overlaps Slither's built-in `reentrancy-eth`; it is kept as a small
  readable detector with fixtures, and is not claimed to be more precise.
* No detector was attempted for rounding, oracle, governance, bridge-config or compiler-bug
  classes; they are not reliably expressible as a single-function pattern.

## On-chain checks (step 1, 2026-10-04)

Receipts were read with `eth_getTransactionByHash` and `eth_getTransactionReceipt` on `https://eth.drpc.org`. `https://rpc.mevblocker.io` returned the same block, from, to, status, and log count for every stored hash. `https://ethereum-rpc.publicnode.com` returned some transactions and null receipts, so it was not used for receipts. `needs_review` was not changed.

| Entry | Stored, with block time (UTC) | Left out |
|---|---|---|
| VB-2023-0012 Euler | DAI `0xc310a0af…111d` block 16817996, 2023-03-13T08:50:59Z; WETH `0x47ac3527…088f` block 16818024, 2023-03-13T08:56:35Z; wstETH `0x62bd3d31…18c4` block 16818062, 2023-03-13T09:04:23Z | eDAI, eWETH, ewstETH are receipt logs. CertiK's attack contract `0x583c2163…6c72` is not from, to, or a log on these three, so it is omitted. BlockSec's WBTC, USDC, and stETH hashes are shorter than 32 bytes and were not queried. CertiK's eWBTC and eUSDC addresses have no confirmed tx here. |
| VB-2022-0009 Nomad | setup `0xed26708a…35f0` block 15258799, 2022-08-01T20:24:53Z; process `0xa5fe9d04…5460` block 15259101, 2022-08-01T21:32:31Z | Replica and BridgeRouter proxies and WBTC are on the receipts. Replica logic and BridgeRouter logic are not receipt logs, and the Replica EIP-1967 implementation slot at block 15259101 was zero, so those two addresses are omitted. `0x53fd9277…24cad` is a 2022-06-21 transaction, not stored as an August attack tx. |
| VB-2025-0025 Bybit | masterCopy `0x46deef0f…7882` block 21895238, 2025-02-21T14:13:35Z; four later hashes in block 21895251, 2025-02-21T14:16:11Z | Safe, trojan input address, backdoor (slot 0 at end of 21895238), previous masterCopy (slot 0 at end of 21895237). The ETH-labeled hash has msg.value 0 and no logs. Token symbols on the later logs were not read. |
| VB-2024-0022 Ronin | `0x26195700…a6cb` block 20468679, 2024-08-06T09:37:23Z; `0xbce5b854…60ad8` block 20468848, 2024-08-06T10:11:47Z | Bridge is a log on both. The second receipt's USDC Transfer is 1,998,046.875 USDC. Beosin audit-transaction hashes were not stored. |

## Fork replay (step 3, 2026-10-04)

`replay/nomad/test/NomadReplay.t.sol` passed on 2026-10-04: `forge 1.7.1 test --fork-url https://eth.drpc.org --fork-block-number 15259100`. One test, `test_process_tx_moves_wbtc`, passed. It replays process hash `0xa5fe9d04…5460` with `vm.transact` and expects the receipt's WBTC delta of 10000000000 raw units. The DeFiHackLabs file is linked from the test and from the Nomad entry. Its body is not in this repo. `replay_status: verified` on VB-2022-0009 means that test passed. Every other entry is still `unverified`. `https://eth.drpc.org` and `https://rpc.mevblocker.io` returned code at block 15259100. `https://1rpc.io/eth` and `https://rpc.flashbots.net` said historical state was unavailable. Euler was not replayed. `scripts/check_all.sh` does not run this Foundry test.

## Known data gaps

* Radiant (VB-2024-0018) is the only Arbitrum node check. Euler, Nomad, Bybit, and Ronin have Ethereum hashes from the calls above. Wormhole, Cashio, Crema, Nirvana, and Mango have Solana signatures from `getTransaction`. Seventeen entries still have empty `affected_contracts` and `attack_txs`: the 16 older EVM files, plus Solend.
* `python scripts/vb.py` queries `build/vaultbreak.sqlite` (`list`, `show`, `search`).
* Dates differ by about a day between DeFiHackLabs and other sources for several incidents; the
  entry's `confidence.notes` says so. Nomad's stored blocks are 2022-08-01 UTC.
* `date_source: tx` is set where a confirmed block timestamp falls on the entry date: Euler, Nomad, Bybit, Ronin, Wormhole, Cashio, Crema, Nirvana, and Mango. Radiant's `date_source` was left as it was. Solend stays `postmortem` because no November transaction was confirmed.
* OAK taxonomy mapping not done (not verified).
* Five entries have `needs_review: false`: VB-2022-0009 Nomad, VB-2022-0003 Wormhole, VB-2022-0004 Cashio, VB-2023-0012 Euler, and VB-2025-0025 Bybit. The check used the node notes already in each file. On 2026-10-04 one stored transaction per entry was read again and matched: Nomad process on `https://rpc.mevblocker.io` (block 15259101), Wormhole on `https://api.mainnet-beta.solana.com` (slot 119025020), Cashio mint (slot 126266822), Euler DAI (block 16817996), Bybit masterCopy (block 21895238). `https://eth.drpc.org` returned HTTP 403 on that pass. `human_reviewed_by` is still empty. The other 22 entries, including Solend, still have `needs_review: true`. Solend's two October signatures are still not attack transactions.

## Next steps (suggested)

1. Review of the other 22 entries. The five above have `needs_review: false` and `human_reviewed_by` still empty.
2. Addresses and tx hashes for the 17 entries that are still empty. Read the node. Do not copy a hash that was not fetched.
3. More detectors where a reliable shape exists (e.g. zero-value root in initialisers). A confirmed incident for `pda_seed_collision` or `arbitrary_cpi` if one is found.
4. Foundry replay for more than Nomad. Pagefind for full-text search.
