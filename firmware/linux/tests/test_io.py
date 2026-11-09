import os
import unittest

from cam4g.camera import SimCamera
from cam4g.gpio import SysfsGPIO


class TestCamera(unittest.TestCase):
    def test_sim_returns_jpeg(self):
        frame = SimCamera().capture()
        self.assertTrue(frame.startswith(b"\xff\xd8"))
        self.assertTrue(frame.endswith(b"\xff\xd9"))


class TestGPIO(unittest.TestCase):
    def test_paths(self):
        g = SysfsGPIO(base="/tmp/gpio")
        self.assertEqual(g._path(12, "value"), os.path.join("/tmp/gpio", "gpio12", "value"))


if __name__ == "__main__":
    unittest.main()
