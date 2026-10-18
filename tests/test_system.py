import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netpulse.system import format_bytes, format_uptime


class SystemFormattingTests(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(format_bytes(0), "0.0 B")
        self.assertEqual(format_bytes(1024), "1.0 KiB")
        self.assertEqual(format_bytes(1048576), "1.0 MiB")

    def test_uptime(self):
        self.assertEqual(format_uptime(0), "0d 0h 0m")
        self.assertEqual(format_uptime(90061), "1d 1h 1m")

    def test_negative_uptime(self):
        self.assertEqual(format_uptime(-10), "0d 0h 0m")


if __name__ == "__main__":
    unittest.main()
