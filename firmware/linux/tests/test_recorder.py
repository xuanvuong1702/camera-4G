import os
import tempfile
import unittest

from cam4g.recorder import RecorderConfig, SegmentRecorder


class TestRecorder(unittest.TestCase):
    def test_segments_and_fsync(self):
        with tempfile.TemporaryDirectory() as d:
            rec = SegmentRecorder(RecorderConfig(root=d, segment_seconds=1.0, fsync_frames=2))
            for i in range(10):
                rec.write_frame(b"\xff\xd8" + bytes([i]) * 100, i * 0.2)
            rec.stop()
            files = os.listdir(os.path.join(d, "video"))
            self.assertGreaterEqual(len(files), 1)
            self.assertEqual(rec.bytes_written, 10 * 102)

    def test_stop_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            rec = SegmentRecorder(RecorderConfig(root=d))
            rec.start(0.0)
            rec.stop()
            rec.stop()


if __name__ == "__main__":
    unittest.main()
