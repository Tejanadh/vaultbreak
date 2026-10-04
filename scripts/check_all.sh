#!/usr/bin/env bash
# Everything CI runs, in the same order. Assumes the venv is active and solc 0.8.20 is selected.
#   python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
#   solc-select install 0.8.20 && solc-select use 0.8.20
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/validate.py --quiet
python -m unittest discover -s tests
python scripts/compile_snippets.py
python scripts/test_detectors.py
python scripts/build.py
node tests/site_filter.test.js
echo "ALL CHECKS PASSED"
