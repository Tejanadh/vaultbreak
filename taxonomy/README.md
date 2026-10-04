# Taxonomy

* `vuln_class.yaml` - the primary root-cause vocabulary (one class per entry).
* `tags.yaml` - secondary tags (preconditions, mechanisms, capital amplifiers).
* `chains.yaml` - allowed chain identifiers.

Mappings to DefiLlama labels and SWC ids in `vuln_class.yaml` are our own judgement.
Mapping to OAK is **not done yet** (not verified; see docs/STATUS.md).
Flash loans are not a root cause: tag them as `capital_amplifier:flash_loan`.
