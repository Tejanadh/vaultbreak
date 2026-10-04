# Contributing

Thanks for helping. Quality beats volume: a short, correct, well-sourced entry is better than
ten fast ones.

## Ground rules

1. **Your own words.** No copying text from write-ups, aggregators, contest reports or other
   datasets. Facts (date, amount, chain) are fine when linked. See `docs/LICENSING.md`.
2. **Never use Code4rena content** (their terms forbid scraping and AI/ML use), and do not
   paste DefiLlama, Rekt, Solodit or OAK text.
3. **Two sources minimum** where possible, at least one a postmortem, analysis or primary
   source. Say in `confidence.notes` what is uncertain. If you cannot verify it, leave it out.
4. **No invented data.** Addresses and tx hashes only if you checked them on a block explorer
   (`verified_on_explorer`). No `TODO` placeholders; CI rejects them.
5. **Original code only.** `code_pattern` snippets are minimal, written by you, start with an
   `// ILLUSTRATIVE` comment, and must compile (`python scripts/compile_snippets.py`).
6. **Pick one `vuln_class`** from `taxonomy/vuln_class.yaml`. Flash loans are a tag
   (`capital_amplifier:flash_loan`), not a class. If aggregators label it differently, record
   that in `labels_disagree`.

## Adding an entry

1. Copy an existing file in `entries/` to `entries/<slug>.yaml` (slug = `name-YYYY-MM`).
2. Use the next free id `VB-<year>-<NNNN>`; ids are never reused.
3. Fill every required field (see `schema/entry.schema.yaml`). Set `confidence.needs_review: true`
   until a human who is not the author has checked the root cause against the sources.
4. If you used an LLM, set `provenance.llm_assisted: true`. Do not let it supply addresses,
   amounts or dates that are not in a source you opened.
5. Run `scripts/check_all.sh` (and `python scripts/validate.py --check-links` if you have network).

## Adding a detector

1. Write the **fixtures first**: `fixtures/<entry id>/vulnerable.sol` and `fixed.sol`, both
   original and compiling. `fixed.sol` should include at least one near-miss that a sloppy
   rule would flag.
2. Add the Semgrep rule (`detectors/semgrep/`) or Slither plugin (`detectors/slither/`). Write
   it from the exploit class, not by copying another project's rule (check their license).
3. Add an entry to `detectors/expected.yaml` with the exact expected finding counts.
4. Reference it from the entry's `detectors[]`. Use `status: validated` only when it fires on
   the vulnerable fixture and is silent on the fixed one (`python scripts/test_detectors.py`).
   Write the limits into `notes`. If a detector cannot be made reliable, do not ship one; say
   so in the entry instead (see the Curve/Vyper entry).

## Pull request checklist

See `.github/pull_request_template.md`.
