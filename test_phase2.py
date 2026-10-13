import unittest
import tempfile
from pathlib import Path
import app as sentinel


class Phase2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = sentinel.DB_PATH
        sentinel.DB_PATH = Path(self.tmp.name) / "test.db"
        sentinel.init_db()
        self.client = sentinel.app.test_client()

    def tearDown(self):
        sentinel.DB_PATH = self.old_db
        self.tmp.cleanup()

    def test_initial_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"24%", response.data)
        self.assertIn(b"No active problems", response.data)

    def test_high_cpu_and_reset(self):
        self.assertEqual(self.client.post("/simulate/high_cpu").status_code, 303)
        response = self.client.get("/")
        self.assertIn(b"95%", response.data)
        self.assertIn(b"CPU usage is above 90%", response.data)
        self.client.post("/simulate/reset")
        response = self.client.get("/")
        self.assertIn(b"24%", response.data)
        self.assertIn(b"returned to normal", response.data)

    def test_disk_and_docker(self):
        self.client.post("/simulate/disk_warning")
        self.client.post("/simulate/docker_failure")
        response = self.client.get("/")
        self.assertIn(b"96%", response.data)
        self.assertIn(b"Stopped", response.data)

    def test_invalid_event(self):
        self.assertEqual(self.client.post("/simulate/not_real").status_code, 404)


if __name__ == "__main__":
    unittest.main()
