import unittest
from datetime import datetime, timezone

from pymlokit.utils.azure_storage import canonicalized_headers, canonicalized_resource, storage_headers_common


class TestAzureStorage(unittest.TestCase):
    def test_canonicalized_headers(self):
        headers = {"x-ms-date": "x", "X-Ms-Version": "y", "Content-Type": "z"}
        s = canonicalized_headers(headers)
        self.assertIn("x-ms-date:x\n", s)
        self.assertIn("x-ms-version:y\n", s)
        self.assertNotIn("content-type", s.lower())

    def test_canonicalized_resource_sorts_query(self):
        url = "https://acct.blob.core.windows.net/container/blob?b=2&a=1"
        s = canonicalized_resource(url, "acct")
        self.assertEqual(s.split("\n")[0], "/acct/container/blob")
        self.assertEqual(s.split("\n")[1], "a:1")
        self.assertEqual(s.split("\n")[2], "b:2")

    def test_storage_headers_common(self):
        now = datetime(2020, 1, 1, tzinfo=timezone.utc)
        h = storage_headers_common(now)
        self.assertIn("x-ms-date", h)
        self.assertEqual(h["x-ms-version"], "2021-08-06")


if __name__ == "__main__":
    unittest.main()
