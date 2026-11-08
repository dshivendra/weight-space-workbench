from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from apply_safetensors_delta import parse_index  # noqa: E402


class ParseIndexTests(unittest.TestCase):
    def test_parses_scalar_coordinate(self):
        self.assertEqual(parse_index(" 0, 3 "), (0, 3))

    def test_rejects_negative_coordinate(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_index("0,-1")

    def test_rejects_non_integer_coordinate(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_index("0,x")


if __name__ == "__main__":
    unittest.main()
