import subprocess
import sys
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "warehouse.cli", *args],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )

    def test_quotes(self):
        for zone, standard, express in (
            ("local", "$8.00\n", "$15.00\n"),
            ("regional", "$11.00\n", "$18.00\n"),
        ):
            for options, expected in (
                ((), standard),
                (("--service", "standard"), standard),
                (("--service", "express"), express),
            ):
                with self.subTest(zone=zone, options=options):
                    result = self.run_cli("2", zone, *options)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, expected)
                    self.assertEqual(result.stderr, "")

    def test_unknown_service_is_rejected(self):
        result = self.run_cli("2", "local", "--service", "overnight")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid choice", result.stderr)
        self.assertIn("overnight", result.stderr)
