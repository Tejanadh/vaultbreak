"""Shared helpers: YAML loading (dates stay strings) and repo paths."""
from __future__ import annotations

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "entries"
SCHEMA_YAML = ROOT / "schema" / "entry.schema.yaml"
SCHEMA_JSON = ROOT / "schema" / "entry.schema.json"
TAXONOMY = ROOT / "taxonomy"


class _StrDateLoader(yaml.SafeLoader):
    """SafeLoader that leaves ISO dates as plain strings (JSON-Schema friendly)."""


_StrDateLoader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path: pathlib.Path):
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=_StrDateLoader)


def load_entries():
    """Return [(path, data)] sorted by file name."""
    return [(p, load_yaml(p)) for p in sorted(ENTRIES.glob("*.yaml"))]
