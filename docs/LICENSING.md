# Licensing and content policy

| What | License | Where |
|---|---|---|
| Code (scripts, site, detectors, tests, CI) | MIT | `LICENSE` |
| Data (entries, taxonomy, schema, fixtures, illustrative snippets) | CC-BY-4.0 | `LICENSE-DATA` |

CC-BY-4.0 text was fetched from creativecommons.org (legalcode.txt) on 2026-10-04.
This is a policy summary, not legal advice.

## Content rules every entry follows

* **Our own words.** `root_cause`, `explanation`, `fix.summary` are written by us. No pasted
  passages from Rekt, DefiLlama, SlowMist, Code4rena, Solodit, OAK or any write-up.
* **Facts and links only from sources.** Dates, amounts, chains and names are facts; each is tied
  to a link in `sources[]`. Rekt is all rights reserved, so it is linked, never mirrored.
* **Our own code.** Snippets and fixtures are minimal, original and labelled ILLUSTRATIVE.
  They are not the projects' real code. DeFiHackLabs PoCs are linked, not copied (sampled files
  carry `SPDX: UNLICENSED`).
* **Not used as input:** Code4rena content (ToS bars scraping and AI use), DefiLlama's `/hacks`
  dump (ToS bars republishing), Solodit raw findings (no mirroring), OAK text (CC-BY-SA would
  impose share-alike on this dataset), Decurity rules (CC BY-NC-SA). Our three Semgrep rules were
  written from the exploit class. Decurity rule *names* appear in the research report; their rule
  contents were not read or copied.
* **No LLM was fed Code4rena content.**

## Open question for the owner

`detectors/slither/vb_eth_send_before_write.py` imports `slither`, which is AGPL-3.0. Whether a
plugin that imports an AGPL library must itself be AGPL is a genuine legal grey area. The file is
self-contained and trivially separable. Options: keep MIT (current), or relicense that one file
as AGPL-3.0. Semgrep rules are plain YAML run by Semgrep and are not affected. Decide before
publishing.
