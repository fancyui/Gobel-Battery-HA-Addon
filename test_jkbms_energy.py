import logging
import struct
import unittest
from unittest.mock import patch

from jkbms_rs485 import JKBMS485


class JKBMSEnergyTest(unittest.TestCase):
    def setUp(self):
        self.bms = JKBMS485.__new__(JKBMS485)
        self.bms.logger = logging.getLogger(__name__)
        self.bms.pack_energy = {}

    def parse_power(self, power_mw, current_ma):
        frame = bytearray(300)
        frame[0:2] = b"\x55\xaa"
        struct.pack_into("<I", frame, 154, power_mw)
        struct.pack_into("<i", frame, 158, current_ma)
        return self.bms.parse_jkbms_55aa_frame(frame)["power_kw"]

    def test_positive_current_produces_positive_power(self):
        self.assertEqual(self.parse_power(1_500_000, 30_000), 1.5)

    def test_negative_current_produces_negative_power(self):
        self.assertEqual(self.parse_power(1_500_000, -30_000), -1.5)

    def test_positive_power_accumulates_charged_energy(self):
        with patch("time.time", side_effect=[100.0, 160.0]):
            self.bms.calculate_cumulative_energy(0, 1.0)
            charged, discharged = self.bms.calculate_cumulative_energy(0, 1.0)

        self.assertAlmostEqual(charged, 1000 / 60)
        self.assertEqual(discharged, 0.0)

    def test_negative_power_accumulates_discharged_energy(self):
        with patch("time.time", side_effect=[100.0, 160.0]):
            self.bms.calculate_cumulative_energy(0, -1.0)
            charged, discharged = self.bms.calculate_cumulative_energy(0, -1.0)

        self.assertEqual(charged, 0.0)
        self.assertAlmostEqual(discharged, 1000 / 60)


if __name__ == "__main__":
    unittest.main()
