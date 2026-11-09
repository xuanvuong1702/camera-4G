import unittest

from cam4g.power import PowerManager, State


class TestPower(unittest.TestCase):
    def setUp(self):
        self.p = PowerManager()
        self.p.boot(0.0)

    def test_boot_connected(self):
        self.assertEqual(self.p.state, State.SLEEP_CONNECTED)
        self.assertTrue(self.p.modem_on)
        self.assertFalse(self.p.soc_on)

    def test_motion_records_then_sleeps(self):
        self.p.on_motion(10.0)
        self.assertEqual(self.p.state, State.RECORD)
        self.assertTrue(self.p.recording)
        self.p.tick(10.0 + self.p.cfg.clip_seconds - 0.1)
        self.assertEqual(self.p.state, State.RECORD)
        self.p.tick(10.0 + self.p.cfg.clip_seconds + 0.1)
        self.assertEqual(self.p.state, State.SLEEP_DEEP)
        self.assertFalse(self.p.soc_on)

    def test_live_then_back_to_record(self):
        self.p.on_motion(0.0)
        self.p.on_live_request(1.0, True)
        self.assertEqual(self.p.state, State.RECORD_LIVE)
        self.assertTrue(self.p.modem_on)
        self.p.tick(1.0 + self.p.cfg.live_hold_seconds + 1)
        self.assertEqual(self.p.state, State.RECORD)

    def test_thermal_fault_latches(self):
        self.p.on_thermal_fault(True, 5.0)
        self.assertEqual(self.p.state, State.FAULT)
        self.assertFalse(self.p.soc_on)
        self.p.on_thermal_fault(False, 6.0)
        self.assertEqual(self.p.state, State.SLEEP_DEEP)

    def test_critical_battery(self):
        self.p.on_motion(0.0)
        self.p.on_battery(3.0, 1.0)
        self.assertEqual(self.p.state, State.FAULT)


if __name__ == "__main__":
    unittest.main()
