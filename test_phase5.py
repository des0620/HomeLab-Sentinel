
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

import app as sentinel


class Phase5Tests(unittest.TestCase):

    # ==========================================
    # TEST SETUP AND CLEANUP
    # ==========================================

    def setUp(self):
        # Create a temporary database for each test.
        # This prevents tests from modifying real demo data.

        self.tmp = tempfile.TemporaryDirectory()

        self.old_db = sentinel.DB_PATH

        sentinel.DB_PATH = (
            Path(self.tmp.name) / "test.db"
        )

        sentinel.init_db()

        self.client = sentinel.app.test_client()

    def tearDown(self):
        # Restore the original database path.

        sentinel.DB_PATH = self.old_db

        self.tmp.cleanup()

    # ==========================================
    # TEST 1: FAILED SSH EVENT
    # ==========================================

    def test_failed_ssh_event(self):

        response = self.client.post(
            "/simulate-log/failed_ssh"
        )

        self.assertEqual(
            response.status_code,
            303
        )

        with sentinel.connect_db() as connection:
            log = connection.execute(
                "SELECT * FROM event_logs"
            ).fetchone()

        self.assertEqual(
            log["source"],
            "Security"
        )

        self.assertEqual(
            log["severity"],
            "CRITICAL"
        )

        self.assertEqual(
            log["category"],
            "Failed SSH Logins"
        )

    # ==========================================
    # TEST 2: SECURITY COUNTERS
    # ==========================================

    def test_security_counters(self):

        self.client.post(
            "/simulate-log/failed_ssh"
        )

        self.client.post(
            "/simulate-log/network_activity"
        )

        response = self.client.get("/")

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            b"Total Simulated Security Events",
            response.data
        )

        self.assertIn(
            b"Critical Security Events",
            response.data
        )

        with sentinel.connect_db() as connection:

            total = connection.execute(
                """
                SELECT COUNT(*)
                FROM event_logs
                WHERE source = 'Security'
                """
            ).fetchone()[0]

            critical = connection.execute(
                """
                SELECT COUNT(*)
                FROM event_logs
                WHERE source = 'Security'
                  AND severity = 'CRITICAL'
                """
            ).fetchone()[0]

        self.assertEqual(total, 2)

        self.assertEqual(critical, 1)

    # ==========================================
    # TEST 3: PLEX ERROR LOG
    # ==========================================

    def test_plex_error_log(self):

        self.client.post(
            "/simulate-log/plex_error"
        )

        with sentinel.connect_db() as connection:
            log = connection.execute(
                "SELECT * FROM event_logs"
            ).fetchone()

        self.assertEqual(
            log["source"],
            "Plex"
        )

        self.assertEqual(
            log["severity"],
            "ERROR"
        )

    # ==========================================
    # TEST 4: INVALID EVENT REJECTED
    # ==========================================

    def test_invalid_event_rejected(self):

        response = self.client.post(
            "/simulate-log/unknown_event"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # ==========================================
    # TEST 5: BRUTE-FORCE DETECTION
    # ==========================================

    def test_brute_force_detection(self):

        # Three failed SSH batches should
        # trigger a critical security finding.

        for _ in range(3):
            self.client.post(
                "/simulate-log/failed_ssh"
            )

        findings = (
            sentinel.detect_security_patterns()
        )

        self.assertEqual(
            len(findings),
            1
        )

        self.assertEqual(
            findings[0]["category"],
            "Possible Brute-Force Activity"
        )

        self.assertEqual(
            findings[0]["severity"],
            "CRITICAL"
        )

    # ==========================================
    # TEST 6: BELOW BRUTE-FORCE THRESHOLD
    # ==========================================

    def test_no_brute_force_below_threshold(self):

        # Two SSH event batches should not
        # trigger the brute-force rule.

        for _ in range(2):
            self.client.post(
                "/simulate-log/failed_ssh"
            )

        findings = (
            sentinel.detect_security_patterns()
        )

        self.assertEqual(
            len(findings),
            0
        )

    # ==========================================
    # TEST 7: SUSPICIOUS NETWORK DETECTION
    # ==========================================

    def test_network_activity_detection(self):

        # Three suspicious network events
        # should trigger a warning.

        for _ in range(3):
            self.client.post(
                "/simulate-log/network_activity"
            )

        findings = (
            sentinel.detect_security_patterns()
        )

        self.assertEqual(
            len(findings),
            1
        )

        self.assertEqual(
            findings[0]["category"],
            "Repeated Suspicious Network Activity"
        )

        self.assertEqual(
            findings[0]["severity"],
            "WARNING"
        )

    # ==========================================
    # TEST 8: UNAUTHORIZED ACCESS DETECTION
    # ==========================================

    def test_unauthorized_access_detection(self):

        # One unauthorized access attempt
        # should trigger a critical finding.

        self.client.post(
            "/simulate-log/unauthorized_access"
        )

        findings = (
            sentinel.detect_security_patterns()
        )

        self.assertEqual(
            len(findings),
            1
        )

        self.assertEqual(
            findings[0]["category"],
            "Unauthorized Access Detected"
        )

        self.assertEqual(
            findings[0]["severity"],
            "CRITICAL"
        )

    # ==========================================
    # TEST 9: AI SECURITY TROUBLESHOOTING
    # ==========================================

    def test_security_troubleshooting_route(self):

        # Generate an unauthorized access event.

        self.client.post(
            "/simulate-log/unauthorized_access"
        )

        # Mock the OpenAI function so the test
        # does not make a real API request.

        with patch.object(
            sentinel,
            "generate_ai_guidance",
            return_value=(
                None,
                "Test mode: local guidance only."
            )
        ):

            response = self.client.get(
                "/troubleshoot/Unauthorized%20Access%20Detected"
            )

        # The troubleshooting page should load.

        self.assertEqual(
            response.status_code,
            200
        )

        # The correct security category
        # should appear on the page.

        self.assertIn(
            b"Unauthorized Access Detected",
            response.data
        )


# ==========================================
# RUN TESTS
# ==========================================

if __name__ == "__main__":
    unittest.main()
