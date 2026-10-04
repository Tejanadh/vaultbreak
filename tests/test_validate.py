"""Negative tests: the validator must reject broken entries. Run: python -m unittest discover -s tests"""
import copy
import datetime as dt
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from jsonschema import Draft202012Validator  # noqa: E402

import validate as V  # noqa: E402
from common import SCHEMA_YAML, load_entries, load_yaml  # noqa: E402

VALIDATOR = Draft202012Validator(load_yaml(SCHEMA_YAML))
CLASSES, TAGS, CHAINS = V.vocab()
BASE_PATH, BASE = next((p, e) for p, e in load_entries() if e["slug"] == "sentiment-2023-04")


def check(mutate):
    e = copy.deepcopy(BASE)
    mutate(e)
    return V.check_entry(BASE_PATH, e, VALIDATOR, CLASSES, TAGS, CHAINS, dt.date(2026, 10, 4))


class ValidatorRejects(unittest.TestCase):
    def assertRejects(self, mutate, needle):
        errs, _ = check(mutate)
        self.assertTrue(any(needle in x for x in errs), f"expected an error containing {needle!r}, got {errs}")

    def test_baseline_is_valid(self):
        self.assertEqual(check(lambda e: None)[0], [])

    def test_missing_sources(self):
        self.assertRejects(lambda e: e.update(sources=[]), "sources")

    def test_aggregator_only_sources(self):
        def m(e):
            for s in e["sources"]:
                s["type"] = "aggregator"
        self.assertRejects(m, "postmortem/analysis/primary")

    def test_loss_source_must_be_listed(self):
        self.assertRejects(lambda e: e["loss_usd"].update(sources=["https://example.com/x"]), "loss_usd source not listed")

    def test_unknown_class(self):
        self.assertRejects(lambda e: e.update(vuln_class="made_up"), "vuln_class")

    def test_unknown_tag(self):
        self.assertRejects(lambda e: e["tags"].append("not_in_taxonomy"), "tag 'not_in_taxonomy'")

    def test_todo_placeholder(self):
        self.assertRejects(lambda e: e.update(root_cause=e["root_cause"] + " TODO verify address"), "TODO")

    def test_bad_address(self):
        self.assertRejects(lambda e: e.update(affected_contracts=[{"chain": "arbitrum", "address": "0x123", "role": "x", "verified_on_explorer": False}]), "address")

    def test_future_date(self):
        self.assertRejects(lambda e: e.update(date="2030-01-01"), "future")

    def test_snippet_must_be_labelled_illustrative(self):
        self.assertRejects(lambda e: e["code_pattern"].update(vulnerable_snippet="contract A { function f() external {} }"), "ILLUSTRATIVE")

    def test_missing_detector_fixture(self):
        def m(e):
            e["detectors"][0]["true_positive_fixture"] = "fixtures/nope.sol"
        self.assertRejects(m, "missing file")

    def test_non_https_source(self):
        self.assertRejects(lambda e: e["sources"][0].update(url="http://insecure.example"), "url")

    def test_slug_filename_mismatch(self):
        self.assertRejects(lambda e: e.update(slug="other-slug"), "must equal slug")

    def test_min_greater_than_max(self):
        self.assertRejects(lambda e: e["loss_usd"].update(reported_min=9, reported_max=1), "reported_min")


if __name__ == "__main__":
    unittest.main()
