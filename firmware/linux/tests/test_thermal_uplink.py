import unittest

from cam4g.thermal import ThermalPolicy
from cam4g.uplink import Uplink, UplinkConfig


class TestThermal(unittest.TestCase):
    def test_charge_inhibit(self):
        t = ThermalPolicy()
        self.assertTrue(t.can_charge(35.0))
        self.assertFalse(t.can_charge(45.0))

    def test_throttle(self):
        t = ThermalPolicy()
        self.assertEqual(t.throttle_level(60.0), "normal")
        self.assertEqual(t.throttle_level(90.0), "reduced")
        self.assertEqual(t.throttle_level(99.0), "shutdown")


class TestUplink(unittest.TestCase):
    def test_batch_and_spool(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            u = Uplink(UplinkConfig(spool_dir=d, max_batch=2))
            for i in range(5):
                u.enqueue("t", {"i": i})
            b = u.next_batch()
            self.assertEqual(len(b), 2)
            u.ack(b)
            self.assertEqual(u.sent, 2)
            self.assertEqual(len(u.pending), 3)
            path = u.spool()
            self.assertTrue(os.path.exists(path))
            u2 = Uplink(UplinkConfig(spool_dir=d))
            u2.load()
            self.assertEqual(len(u2.pending), 3)


if __name__ == "__main__":
    unittest.main()
