import unittest

from pymlokit.utils.arg_utils import parse_arguments


class TestArgUtils(unittest.TestCase):
    def test_parse_arguments_slash_prefix(self):
        args = ["/platform:azureml", "/credential:abc", "/region:eastus"]
        parsed = parse_arguments(args)
        self.assertEqual(parsed["platform"], "azureml")
        self.assertEqual(parsed["credential"], "abc")
        self.assertEqual(parsed["region"], "eastus")

    def test_parse_arguments_dash_prefix(self):
        args = ["-platform:mlflow", "-credential:user;pass", "-url:http://x"]
        parsed = parse_arguments(args)
        self.assertEqual(parsed["platform"], "mlflow")
        self.assertEqual(parsed["credential"], "user;pass")
        self.assertEqual(parsed["url"], "http://x")

    def test_parse_arguments_flag(self):
        args = ["/help"]
        parsed = parse_arguments(args)
        self.assertIn("help", parsed)
        self.assertEqual(parsed["help"], "")


if __name__ == "__main__":
    unittest.main()
