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

    def test_balance_action_parsing(self):
        # Test balancer off (0)
        frame = bytearray(300)
        frame[0:2] = b"\x55\xaa"
        frame[172] = 0
        frame[198] = 1  # charge_mos
        frame[199] = 1  # discharge_mos
        frame[200] = 0  # legacy byte 200
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertFalse(res['balance_mos'])
        self.assertEqual(res['balance_action'], 0)
        self.assertEqual(res['balance_action_text'], 'Off')
        self.assertEqual(res['battery_state'], 0)
        self.assertTrue(res['charge_mos'])
        self.assertTrue(res['discharge_mos'])

        # Test balancer charging (1)
        frame[172] = 1
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertTrue(res['balance_mos'])
        self.assertEqual(res['balance_action'], 1)
        self.assertEqual(res['balance_action_text'], 'Charging')
        self.assertEqual(res['battery_state'], 1)

        # Test balancer discharging (2)
        frame[172] = 2
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertTrue(res['balance_mos'])
        self.assertEqual(res['balance_action'], 2)
        self.assertEqual(res['balance_action_text'], 'Discharging')
        self.assertEqual(res['battery_state'], 2)

        # Test legacy firmware fallback (byte 172 = 0, but byte 200 != 0)
        frame[172] = 0
        frame[200] = 1
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertTrue(res['balance_mos'])
        self.assertEqual(res['balance_action'], 0)
        self.assertEqual(res['battery_state'], 0)


if __name__ == "__main__":
    unittest.main()
