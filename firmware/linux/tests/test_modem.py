import unittest

from cam4g.modem import ATClient, ATError


class MockTransport:
    def __init__(self, responses):
        self.responses = list(responses)

    def write(self, data):
        pass

    def readline(self):
        if not self.responses:
            return b""
        return self.responses.pop(0).encode()


class TestModem(unittest.TestCase):
    def test_alive(self):
        c = ATClient(MockTransport(["OK", ""]))
        self.assertTrue(c.alive())

    def test_sim_ready(self):
        c = ATClient(MockTransport(["+CPIN: READY", "OK"]))
        self.assertTrue(c.sim_ready())

    def test_signal_and_registration(self):
        c = ATClient(MockTransport(["+CSQ: 18,99", "OK"]))
        self.assertEqual(c.signal_quality(), 18)
        c = ATClient(MockTransport(["+CREG: 0,1", "OK"]))
        self.assertEqual(c.registration(), 1)

    def test_error_raises(self):
        c = ATClient(MockTransport(["ERROR"]))
        with self.assertRaises(ATError):
            c.command("AT+CPIN?")

    def test_set_apn(self):
        c = ATClient(MockTransport(["OK"]))
        c.set_apn("v-internet")


if __name__ == "__main__":
    unittest.main()
