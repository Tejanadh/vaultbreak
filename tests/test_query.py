"""CLI query tests. Builds the sqlite database, then checks list/show/search."""
import io
import pathlib
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build  # noqa: E402
import vb  # noqa: E402


def run_vb(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = vb.main(argv)
    return code, buf.getvalue()


class Query(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if build.main() != 0:
            raise RuntimeError("build failed")

    def test_list_donation_includes_radiant_and_hundred(self):
        rows = vb.connect().execute(
            "SELECT id FROM entries WHERE vuln_class = ? ORDER BY id", ("donation_inflation",)
        ).fetchall()
        ids = [r[0] for r in rows]
        self.assertIn("VB-2023-0014", ids)
        self.assertIn("VB-2024-0018", ids)

    def test_search_finds_radiant(self):
        code, out = run_vb(["search", "empty reserve"])
        self.assertEqual(code, 0, out)
        self.assertIn("VB-2024-0018", out)

    def test_show_prints_verified_tx(self):
        code, out = run_vb(["show", "VB-2024-0018"])
        self.assertEqual(code, 0, out)
        self.assertIn("0x0e5330ad77b9b806cb9f6ea595d58552f341dbad0691e0599ab5f1caf214c247", out)
        self.assertIn("verified", out)

    def test_show_missing_is_an_error(self):
        self.assertEqual(vb.main(["show", "VB-1999-0001"]), 1)

    def test_cli_list_chain(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "vb.py"), "list", "--chain", "arbitrum"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("VB-2024-0018", r.stdout)


if __name__ == "__main__":
    unittest.main()
