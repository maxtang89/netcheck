import unittest
from netcheck import ping, speed, dns_lookup, traceroute, start_iperf_server, stop_iperf_server

class TestNetCheck(unittest.TestCase):

    def test_ping(self):
        """Test the ping function with a valid host."""
        result = ping("8.8.8.8", count=3, warmup=1, timeout=2)
        self.assertIsInstance(result, dict)
        self.assertIn("min", result)
        self.assertIn("max", result)
        self.assertIn("avg", result)
        self.assertIn("loss", result)

    def test_ping_invalid_host(self):
        """Test the ping function with an invalid host."""
        result = ping("invalid.host", count=3, warmup=1, timeout=2)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["min"], -1)
        self.assertEqual(result["max"], -1)
        self.assertEqual(result["avg"], -1)
        self.assertEqual(result["loss"], 100)

    def test_speed(self):
        """Test the speed function."""
        result = speed()
        self.assertIsInstance(result, dict)
        self.assertIn("download", result)
        self.assertIn("upload", result)
        self.assertTrue(result["download"] >= 0)
        self.assertTrue(result["upload"] >= 0)

    def test_dns_lookup(self):
        """Test DNS resolution for a valid domain."""
        result = dns_lookup("google.com")
        self.assertIsInstance(result, dict)
        self.assertIn("domain", result)
        self.assertIn("records", result)
        self.assertTrue(len(result["records"]) > 0)

    def test_dns_lookup_invalid(self):
        """Test DNS resolution for an invalid domain."""
        result = dns_lookup("invalid.domain.test")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_traceroute(self):
        """Test traceroute to a valid domain."""
        result = traceroute("8.8.8.8")
        if "error" in result and "timed out" in result["error"]:
            self.skipTest("Skipping due to traceroute timeout in CI")
        self.assertIsInstance(result, dict)

    def test_traceroute_invalid(self):
        """Test traceroute to an invalid domain."""
        result = traceroute("invalid.host")
        if "error" in result and "timed out" in result["error"]:
            self.skipTest("Skipping due to traceroute timeout in CI")
        self.assertIsInstance(result, dict)

    def test_iperf_server_start_stop(self):
        """Test starting and stopping the iPerf server."""
        start_result = start_iperf_server(port=5201)
        self.assertIsInstance(start_result, dict)
        self.assertIn("message", start_result)

        stop_result = stop_iperf_server()
        self.assertIsInstance(stop_result, dict)
        self.assertIn("message", stop_result)

if __name__ == "__main__":
    unittest.main()