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

        # Test byte 200 (UserAlarm2) does not trigger balance_mos when balancer is off
        frame[172] = 0
        frame[200] = 1
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertFalse(res['balance_mos'])
        self.assertEqual(res['balance_action'], 0)
        self.assertEqual(res['battery_state'], 0)

    def test_charge_status_and_dry_contacts(self):
        frame = bytearray(300)
        frame[0:2] = b"\x55\xaa"
        struct.pack_into("<H", frame, 278, 3600)  # 1 hour
        frame[280] = 0  # Bulk
        frame[281] = 0x02  # Dry 1 on, Dry 2 off

        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertEqual(res['charge_status_time'], 3600)
        self.assertEqual(res['charge_status'], 0)
        self.assertEqual(res['charge_status_text'], "Bulk")
        self.assertTrue(res['dry1_contact'])
        self.assertFalse(res['dry2_contact'])

        # Absorption & Dry 2 on
        frame[280] = 1
        frame[281] = 0x04
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertEqual(res['charge_status'], 1)
        self.assertEqual(res['charge_status_text'], "Absorption")
        self.assertFalse(res['dry1_contact'])
        self.assertTrue(res['dry2_contact'])

        # Float & Both dry contacts on
        frame[280] = 2
        frame[281] = 0x06
        res = self.bms.parse_jkbms_55aa_frame(frame)
        self.assertEqual(res['charge_status'], 2)
        self.assertEqual(res['charge_status_text'], "Float")
        self.assertTrue(res['dry1_contact'])
        self.assertTrue(res['dry2_contact'])

        # Test boundary frame lengths do not throw IndexError/struct.error
        short_frame_279 = bytearray(279)
        short_frame_279[0:2] = b"\x55\xaa"
        res279 = self.bms.parse_jkbms_55aa_frame(short_frame_279)
        self.assertNotIn('charge_status_time', res279)
        self.assertNotIn('charge_status', res279)
        self.assertNotIn('dry1_contact', res279)

        short_frame_280 = bytearray(280)
        short_frame_280[0:2] = b"\x55\xaa"
        res280 = self.bms.parse_jkbms_55aa_frame(short_frame_280)
        self.assertIn('charge_status_time', res280)
        self.assertNotIn('charge_status', res280)
        self.assertNotIn('dry1_contact', res280)

        short_frame_281 = bytearray(281)
        short_frame_281[0:2] = b"\x55\xaa"
        res281 = self.bms.parse_jkbms_55aa_frame(short_frame_281)
        self.assertIn('charge_status_time', res281)
        self.assertIn('charge_status', res281)
        self.assertNotIn('dry1_contact', res281)


if __name__ == "__main__":
    unittest.main()
