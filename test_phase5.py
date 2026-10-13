
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
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = sentinel.DB_PATH

        sentinel.DB_PATH = Path(self.tmp.name) / "test.db"
        sentinel.init_db()

        self.client = sentinel.app.test_client()

    def tearDown(self):
        sentinel.DB_PATH = self.old_db
        self.tmp.cleanup()

    # ==========================================
    # TEST 1: FAILED SSH EVENT
    # ==========================================

    def test_failed_ssh_event(self):
        response = self.client.post(
            "/simulate-log/failed_ssh"
        )

        self.assertEqual(response.status_code, 303)

        with sentinel.connect_db() as connection:
            log = connection.execute(
                "SELECT * FROM event_logs"
            ).fetchone()

        self.assertEqual(log["source"], "Security")
        self.assertEqual(log["severity"], "CRITICAL")
        self.assertEqual(log["category"], "Failed SSH Logins")

    # ==========================================
    # TEST 2: SECURITY COUNTERS
    # ==========================================

    def test_security_counters(self):
        self.client.post("/simulate-log/failed_ssh")
        self.client.post("/simulate-log/network_activity")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

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
        self.client.post("/simulate-log/plex_error")

        with sentinel.connect_db() as connection:
            log = connection.execute(
                "SELECT * FROM event_logs"
            ).fetchone()

        self.assertEqual(log["source"], "Plex")
        self.assertEqual(log["severity"], "ERROR")

    # ==========================================
    # TEST 4: INVALID EVENT
    # ==========================================

    def test_invalid_event_rejected(self):
        response = self.client.post(
            "/simulate-log/unknown_event"
        )

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # TEST 5: BRUTE-FORCE DETECTION
    # ==========================================

    def test_brute_force_detection(self):
        for _ in range(3):
            self.client.post("/simulate-log/failed_ssh")

        findings = sentinel.detect_security_patterns()

        self.assertEqual(len(findings), 1)
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
        for _ in range(2):
            self.client.post("/simulate-log/failed_ssh")

        findings = sentinel.detect_security_patterns()

        self.assertEqual(len(findings), 0)

    # ==========================================
    # TEST 7: NETWORK ACTIVITY DETECTION
    # ==========================================

    def test_network_activity_detection(self):
        for _ in range(3):
            self.client.post("/simulate-log/network_activity")

        findings = sentinel.detect_security_patterns()

        self.assertEqual(len(findings), 1)
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
        self.client.post("/simulate-log/unauthorized_access")

        findings = sentinel.detect_security_patterns()

        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0]["category"],
            "Unauthorized Access Detected"
        )
        self.assertEqual(
            findings[0]["severity"],
            "CRITICAL"
        )

    # ==========================================
    # TEST 9: SECURITY TROUBLESHOOTING ROUTE
    # ==========================================

    def test_security_troubleshooting_route(self):
        self.client.post("/simulate-log/unauthorized_access")

        with patch.object(
            sentinel,
            "generate_ai_guidance",
            return_value=(None, "Test mode: local guidance only.")
        ):
            response = self.client.get(
                "/troubleshoot/Unauthorized%20Access%20Detected"
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Unauthorized Access Detected",
            response.data
        )

    # ==========================================
    # TEST 10: BRUTE-FORCE TROUBLESHOOTING
    # ==========================================

    def test_brute_force_troubleshooting(self):
        for _ in range(3):
            self.client.post("/simulate-log/failed_ssh")

        with patch.object(
            sentinel,
            "generate_ai_guidance",
            return_value=(None, "Test mode.")
        ):
            response = self.client.get(
                "/troubleshoot/Possible%20Brute-Force%20Activity"
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Possible Brute-Force Activity",
            response.data
        )

    # ==========================================
    # TEST 11: NETWORK TROUBLESHOOTING
    # ==========================================

    def test_network_troubleshooting(self):
        for _ in range(3):
            self.client.post("/simulate-log/network_activity")

        with patch.object(
            sentinel,
            "generate_ai_guidance",
            return_value=(None, "Test mode.")
        ):
            response = self.client.get(
                "/troubleshoot/Repeated%20Suspicious%20Network%20Activity"
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Repeated Suspicious Network Activity",
            response.data
        )

    # ==========================================
    # TEST 12: EXPIRED SECURITY EVENTS
    # ==========================================

    def test_expired_security_events(self):
        self.client.post("/simulate-log/unauthorized_access")

        with sentinel.connect_db() as connection:
            connection.execute(
                """
                UPDATE event_logs
                SET created_at = datetime(
                    'now', '-10 minutes'
                )
                """
            )

        findings = sentinel.detect_security_patterns()

        self.assertEqual(len(findings), 0)

    # ==========================================
    # TEST 13: INVALID TROUBLESHOOTING CATEGORY
    # ==========================================

    def test_invalid_troubleshooting_category(self):
        response = self.client.get(
            "/troubleshoot/Unknown%20Security%20Threat"
        )

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # TEST 14: INACTIVE SECURITY FINDING
    # ==========================================

    def test_inactive_security_troubleshooting(self):
        response = self.client.get(
            "/troubleshoot/Unauthorized%20Access%20Detected"
        )

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # TEST 15: OPENAI FALLBACK
    # ==========================================

    def test_openai_fallback(self):
        self.client.post("/simulate-log/unauthorized_access")

        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": ""}
        ):
            response = self.client.get(
                "/troubleshoot/Unauthorized%20Access%20Detected"
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"OpenAI API key not configured",
            response.data
        )

    # ==========================================
    # TEST 16: RESET CLEARS SECURITY EVENTS
    # ==========================================

    def test_reset_clears_security_events(self):
        for _ in range(3):
            self.client.post("/simulate-log/failed_ssh")

        self.client.post("/simulate-log/unauthorized_access")

        # Confirm findings exist before reset.
        self.assertGreater(
            len(sentinel.detect_security_patterns()),
            0
        )

        response = self.client.post("/reset-security")

        self.assertEqual(response.status_code, 303)

        with sentinel.connect_db() as connection:
            security_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM event_logs
                WHERE source = 'Security'
                """
            ).fetchone()[0]

            security_history = connection.execute(
                """
                SELECT COUNT(*)
                FROM alerts
                WHERE category IN (
                    'Failed SSH Logins',
                    'Suspicious Network Activity',
                    'Unauthorized Access Attempt'
                )
                """
            ).fetchone()[0]

        self.assertEqual(security_count, 0)
        self.assertEqual(security_history, 0)

        # Active security findings must disappear.
        self.assertEqual(
            sentinel.detect_security_patterns(),
            []
        )

        dashboard = self.client.get("/")

        self.assertEqual(dashboard.status_code, 200)
        self.assertIn(
            b"No suspicious event patterns detected",
            dashboard.data
        )

    # ==========================================
    # TEST 17: RESET PRESERVES OTHER LOGS
    # ==========================================

    def test_reset_preserves_nonsecurity_logs(self):
        self.client.post("/simulate-log/plex_error")
        self.client.post("/simulate-log/docker_crash")
        self.client.post("/simulate-log/disk_io")
        self.client.post("/simulate-log/failed_ssh")

        response = self.client.post("/reset-security")

        self.assertEqual(response.status_code, 303)

        with sentinel.connect_db() as connection:
            logs = connection.execute(
                """
                SELECT source, category
                FROM event_logs
                ORDER BY id
                """
            ).fetchall()

            history = connection.execute(
                """
                SELECT category
                FROM alerts
                ORDER BY id
                """
            ).fetchall()

        self.assertEqual(len(logs), 3)

        categories = {log["category"] for log in logs}

        self.assertEqual(
            categories,
            {
                "Plex Playback Error",
                "Docker Container Crash",
                "Disk I/O Warning"
            }
        )

        history_categories = {
            item["category"] for item in history
        }

        self.assertIn(
            "Plex Playback Error",
            history_categories
        )
        self.assertIn(
            "Docker Container Crash",
            history_categories
        )
        self.assertNotIn(
            "Failed SSH Logins",
            history_categories
        )

    # ==========================================
    # TEST 18: RESET PRESERVES SERVER STATE
    # ==========================================

    def test_reset_preserves_server_state(self):
        # Put the simulated server into a warning state.
        self.client.post("/simulate/high_cpu")
        self.client.post("/simulate/disk_warning")
        self.client.post("/simulate/docker_failure")

        # Generate a security event to clear.
        self.client.post("/simulate-log/unauthorized_access")

        before = sentinel.current_state()

        response = self.client.post("/reset-security")

        after = sentinel.current_state()

        self.assertEqual(response.status_code, 303)

        # Security reset must not change server metrics.
        self.assertEqual(before, after)

        self.assertEqual(after["cpu"], 95)
        self.assertEqual(after["storage"], 96)

        plex = next(
            service
            for service in after["services"]
            if service["name"] == "Plex"
        )

        self.assertEqual(plex["status"], "Stopped")

        # Server warnings must still be active.
        categories = {
            alert["category"]
            for alert in sentinel.active_alerts(after)
        }

        self.assertIn("High CPU", categories)
        self.assertIn("Disk Warning", categories)
        self.assertIn("Docker Failure", categories)


# ==========================================
# RUN TESTS
# ==========================================

if __name__ == "__main__":
    unittest.main()
