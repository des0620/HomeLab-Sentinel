import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app as sentinel


class Phase3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = sentinel.DB_PATH
        sentinel.DB_PATH = Path(self.tmp.name) / "test.db"
        sentinel.init_db()
        self.client = sentinel.app.test_client()

    def tearDown(self):
        sentinel.DB_PATH = self.old_db
        self.tmp.cleanup()

    def test_no_alert_not_troubleshootable(self):
        self.assertEqual(self.client.get("/troubleshoot/High CPU").status_code, 404)

    def test_retrieval(self):
        guide = sentinel.retrieve_guidance("Disk Warning")
        self.assertEqual(guide["title"], "Disk Warning")
        self.assertIn("df -h", guide["content"])

    def test_cpu_troubleshooting_without_api(self):
        self.client.post("/simulate/high_cpu")
        with patch.dict("os.environ", {"GOOGLE_API_KEY": ""}):
            response = self.client.get("/troubleshoot/High CPU")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Plex library scanning", response.data)
        self.assertIn(b"API key not configured", response.data)

    def test_no_match(self):
        self.assertIsNone(sentinel.retrieve_guidance("Nonexistent Alert"))


if __name__ == "__main__":
    unittest.main()
