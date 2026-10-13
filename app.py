from flask import Flask, render_template, redirect, url_for, abort

from contextlib import contextmanager

from pathlib import Path

import os

import re

import sqlite3

import markdown

import bleach

from dotenv import load_dotenv

# ==========================================

# APPLICATION CONFIGURATION

# ==========================================

load_dotenv()

app = Flask(__name__)

KB_PATH = (

    Path(__file__).with_name("knowledge_base")

    / "troubleshooting.txt"

)

DB_PATH = Path(__file__).with_name("alerts.db")

# ==========================================

# SIMULATED SERVER CONFIGURATION

# ==========================================

# Demo data only. No live server connection.

DEFAULT = {

    "cpu": 24,

    "memory": 42,

    "storage": 61,

    "plex": "Running",

    "sonarr": "Running",

    "radarr": "Running"

}

EVENTS = {

    "high_cpu": {

        "category": "High CPU",

        "message": "CPU usage is above 90%.",

        "updates": {"cpu": 95}

    },

    "disk_warning": {

        "category": "Disk Warning",

        "message": "Storage usage is above 90%.",

        "updates": {"storage": 96}

    },

    "docker_failure": {

        "category": "Docker Failure",

        "message": "Plex container has stopped.",

        "updates": {"plex": "Stopped"}

    }

}

# ==========================================

# SIMULATED LOG AND SECURITY EVENTS

# ==========================================

LOG_EVENTS = {

    "plex_error": {

        "source": "Plex",

        "severity": "ERROR",

        "category": "Plex Playback Error",

        "message": "Plex failed to play a media file."

    },

    "docker_crash": {

        "source": "Docker",

        "severity": "ERROR",

        "category": "Docker Container Crash",

        "message": (

            "A simulated Docker container exited unexpectedly."

        )

    },

    "disk_io": {

        "source": "System",

        "severity": "WARNING",

        "category": "Disk I/O Warning",

        "message": (

            "Simulated disk read/write latency exceeded "

            "the warning threshold."

        )

    },

    "failed_ssh": {

        "source": "Security",

        "severity": "CRITICAL",

        "category": "Failed SSH Logins",

        "message": (

            "Five failed SSH login attempts detected "

            "from a simulated remote address."

        )

    },

    "network_activity": {

        "source": "Security",

        "severity": "WARNING",

        "category": "Suspicious Network Activity",

        "message": (

            "Unusual simulated inbound connection "

            "activity detected."

        )

    },

    "unauthorized_access": {

        "source": "Security",

        "severity": "CRITICAL",

        "category": "Unauthorized Access Attempt",

        "message": (

            "A simulated unauthorized access attempt "

            "was detected."

        )

    }

}

# ==========================================

# DATABASE CONNECTION

# ==========================================

@contextmanager

def connect_db():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    try:

        with connection:

            yield connection

    finally:

        connection.close()

# ==========================================

# DATABASE INITIALIZATION

# ==========================================

def init_db():

    with connect_db() as connection:

        # Alert history

        connection.execute("""

            CREATE TABLE IF NOT EXISTS alerts (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                category TEXT NOT NULL,

                message TEXT NOT NULL

            )

        """)

        # Simulated server state

        connection.execute("""

            CREATE TABLE IF NOT EXISTS demo_state (

                name TEXT PRIMARY KEY,

                value TEXT NOT NULL

            )

        """)

        for name, value in DEFAULT.items():

            connection.execute(

                """

                INSERT OR IGNORE INTO demo_state

                    (name, value)

                VALUES (?, ?)

                """,

                (name, str(value))

            )

        # Simulated system and security event logs

        connection.execute("""

            CREATE TABLE IF NOT EXISTS event_logs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                source TEXT NOT NULL,

                severity TEXT NOT NULL,

                category TEXT NOT NULL,

                message TEXT NOT NULL

            )

        """)

# ==========================================

# CURRENT SERVER STATE

# ==========================================

def current_state():

    with connect_db() as connection:

        state = {

            row["name"]: row["value"]

            for row in connection.execute(

                "SELECT name, value FROM demo_state"

            )

        }

    return {

        "name": "Demo Server",

        "cpu": int(state["cpu"]),

        "memory": int(state["memory"]),

        "storage": int(state["storage"]),

        "services": [

            {

                "name": name,

                "status": state[name.lower()]

            }

            for name in ("Plex", "Sonarr", "Radarr")

        ]

    }

# ==========================================

# ACTIVE SERVER ALERTS

# ==========================================

def active_alerts(server):

    problems = []

    if server["cpu"] >= 90:

        problems.append({

            "category": "High CPU",

            "message": "CPU usage is above 90%."

        })

    if server["memory"] >= 90:

        problems.append({

            "category": "High Memory",

            "message": "Memory usage is above 90%."

        })

    if server["storage"] >= 90:

        problems.append({

            "category": "Disk Warning",

            "message": "Storage usage is above 90%."

        })

    for service in server["services"]:

        if service["status"] != "Running":

            problems.append({

                "category": "Docker Failure",

                "message": (

                    f"{service['name']} container has stopped."

                )

            })

    return problems

# ==========================================

# SECURITY PATTERN DETECTION

# ==========================================

def detect_security_patterns():

    """

    Analyze simulated security logs.

    Rules:

    - 3 failed SSH event batches in 5 minutes

    - 3 suspicious network events in 5 minutes

    - 1 unauthorized access event in 5 minutes

    No real network activity is monitored.

    """

    findings = []

    rules = [

        {

            "event": "Failed SSH Logins",

            "threshold": 3,

            "category": "Possible Brute-Force Activity",

            "severity": "CRITICAL",

            "description": "failed-SSH event batches"

        },

        {

            "event": "Suspicious Network Activity",

            "threshold": 3,

            "category": "Repeated Suspicious Network Activity",

            "severity": "WARNING",

            "description": "suspicious network events"

        },

        {

            "event": "Unauthorized Access Attempt",

            "threshold": 1,

            "category": "Unauthorized Access Detected",

            "severity": "CRITICAL",

            "description": "unauthorized access attempts"

        }

    ]

    with connect_db() as connection:

        for rule in rules:

            result = connection.execute(

                """

                SELECT COUNT(*) AS attempts

                FROM event_logs

                WHERE category = ?

                  AND created_at >= datetime(

                      'now', '-5 minutes'

                  )

                """,

                (rule["event"],)

            ).fetchone()

            count = result["attempts"]

            if count >= rule["threshold"]:

                event_word = (

                    "event" if count == 1 else "events"

                )

                findings.append({

                    "category": rule["category"],

                    "severity": rule["severity"],

                    "message": (

                        f"{count} simulated "

                        f"{rule['description']} "

                        f"{event_word} recorded within "

                        "the last five minutes."

                    )

                })

    return findings

# ==========================================

# MAIN DASHBOARD

# ==========================================

@app.route("/")

def dashboard():

    server = current_state()

    with connect_db() as connection:

        # Recent alert history

        history = connection.execute(

            """

            SELECT *

            FROM alerts

            ORDER BY id DESC

            LIMIT 15

            """

        ).fetchall()

        # Recent simulated event logs

        event_logs = connection.execute(

            """

            SELECT *

            FROM event_logs

            ORDER BY id DESC

            LIMIT 20

            """

        ).fetchall()

        # Total simulated security events

        security_count = connection.execute(

            """

            SELECT COUNT(*)

            FROM event_logs

            WHERE source = ?

            """,

            ("Security",)

        ).fetchone()[0]

        # Critical simulated security events

        critical_count = connection.execute(

            """

            SELECT COUNT(*)

            FROM event_logs

            WHERE source = ?

              AND severity = ?

            """,

            ("Security", "CRITICAL")

        ).fetchone()[0]

    return render_template(

        "dashboard.html",

        server=server,

        active_alerts=active_alerts(server),

        history=history,

        event_logs=event_logs,

        security_count=security_count,

        critical_count=critical_count,

        security_findings=detect_security_patterns()

    )

# ==========================================

# SIMULATE SERVER EVENTS

# ==========================================

@app.post("/simulate/<event>")

def simulate(event):

    # Reject unsupported events

    if event != "reset" and event not in EVENTS:

        abort(404)

    with connect_db() as connection:

        if event == "reset":

            for name, value in DEFAULT.items():

                connection.execute(

                    """

                    UPDATE demo_state

                    SET value = ?

                    WHERE name = ?

                    """,

                    (str(value), name)

                )

            connection.execute(

                """

                INSERT INTO alerts

                    (category, message)

                VALUES (?, ?)

                """,

                (

                    "Reset",

                    "Demo server returned to normal."

                )

            )

        else:

            definition = EVENTS[event]

            for name, value in definition["updates"].items():

                connection.execute(

                    """

                    UPDATE demo_state

                    SET value = ?

                    WHERE name = ?

                    """,

                    (str(value), name)

                )

            connection.execute(

                """

                INSERT INTO alerts

                    (category, message)

                VALUES (?, ?)

                """,

                (

                    definition["category"],

                    definition["message"]

                )

            )

    return redirect(

        url_for("dashboard"),

        code=303

    )

# ==========================================

# SIMULATE LOG AND SECURITY EVENTS

# ==========================================

@app.post("/simulate-log/<event>")

def simulate_log(event):

    # Only allow predefined simulation events

    if event not in LOG_EVENTS:

        abort(404)

    definition = LOG_EVENTS[event]

    with connect_db() as connection:

        connection.execute(

            """

            INSERT INTO event_logs

                (source, severity, category, message)

            VALUES (?, ?, ?, ?)

            """,

            (

                definition["source"],

                definition["severity"],

                definition["category"],

                definition["message"]

            )

        )

        # ERROR and CRITICAL events also enter

        # the existing alert history.

        if definition["severity"] in (

            "ERROR",

            "CRITICAL"

        ):

            connection.execute(

                """

                INSERT INTO alerts

                    (category, message)

                VALUES (?, ?)

                """,

                (

                    definition["category"],

                    definition["message"]

                )

            )

    return redirect(

        url_for("dashboard"),

        code=303

    )

# ==========================================

# LOCAL KNOWLEDGE BASE RETRIEVAL

# ==========================================

@app.post("/reset-security")
def reset_security_events():
    """Remove simulated security logs and associated history only."""
    categories = tuple(
        definition["category"]
        for definition in LOG_EVENTS.values()
        if definition["source"] == "Security"
    )
    placeholders = ", ".join("?" for _ in categories)

    with connect_db() as connection:
        connection.execute(
            "DELETE FROM event_logs WHERE source = ?", ("Security",)
        )
        connection.execute(
            f"DELETE FROM alerts WHERE category IN ({placeholders})",
            categories
        )

    return redirect(url_for("dashboard"), code=303)


def retrieve_guidance(category):

    """

    Retrieve a relevant local troubleshooting

    guide without using an external service.

    """

    sections = [

        section.strip()

        for section in KB_PATH.read_text(

            encoding="utf-8"

        ).split("\n---\n")

        if section.strip()

    ]

    query = set(

        re.findall(

            r"[a-z0-9]+",

            category.lower()

        )

    )

    ranked = []

    for section in sections:

        title = (

            section.splitlines()[0]

            .removeprefix("# ")

            .strip()

        )

        words = set(

            re.findall(

                r"[a-z0-9]+",

                title.lower()

            )

        )

        score = len(query & words)

        if score:

            ranked.append(

                (score, title, section)

            )

    if not ranked:

        return None

    _, title, content = max(

        ranked,

        key=lambda item: item[0]

    )

    return {

        "title": title,

        "content": content

    }

# ==========================================

# OPENAI TROUBLESHOOTING

# ==========================================

def generate_ai_guidance(category, evidence):

    """

    Generate AI troubleshooting guidance

    grounded in the local knowledge base.

    Falls back to local guidance if OpenAI

    is unavailable.

    """

    key = os.getenv(

        "OPENAI_API_KEY",

        ""

    ).strip()

    if not key:

        return (

            None,

            "OpenAI API key not configured. "

            "Showing local runbook guidance."

        )

    try:

        from openai import OpenAI

        client = OpenAI(

            api_key=key,

            timeout=30.0,

            max_retries=1

        )

        response = client.responses.create(

            model=os.getenv(

                "OPENAI_MODEL",

                "gpt-4.1-mini"

            ),

            instructions=(

                "You are a cautious home server and "

                "cybersecurity troubleshooting assistant. "

                "Use ONLY the provided local runbook. "

                "Do not invent commands, evidence, "

                "or causes. "

                "Explain the issue and provide numbered, "

                "non-destructive investigation steps. "

                "Distinguish suspected activity from "

                "confirmed compromise. "

                "If the runbook lacks information, "

                "say so. "

                "Never suggest automatic repairs, "

                "automatic blocking, or destructive actions. "

                "The events are simulated."

            ),

            input=(

                f"Alert: {category}\n\n"

                f"Trusted local runbook:\n{evidence}"

            ),

            max_output_tokens=500

        )

        answer = (

            response.output_text or ""

        ).strip()

        if answer:

            return answer, None

        return (

            None,

            "AI returned no response. "

            "Showing local guidance."

        )

    except Exception:

        app.logger.exception(

            "OpenAI troubleshooting request failed"

        )

        return (

            None,

            "AI service unavailable. "

            "Showing local runbook guidance."

        )

# ==========================================

# AI TROUBLESHOOTING ROUTE

# ==========================================

@app.get("/troubleshoot/<category>")

def troubleshoot(category):

    """

    Allow troubleshooting for currently active

    server alerts and detected security patterns.

    """

    # Existing active server alerts

    server = current_state()

    server_alerts = active_alerts(server)

    # New: detected security patterns

    security_alerts = detect_security_patterns()

    # Build the list of allowed categories

    allowed_categories = {

        alert["category"]

        for alert in server_alerts

    }

    allowed_categories.update(

        finding["category"]

        for finding in security_alerts

    )

    # Prevent troubleshooting inactive or

    # unsupported alert categories.

    if category not in allowed_categories:

        abort(404)

    # Retrieve local knowledge-base guidance

    guidance = retrieve_guidance(category)

    if guidance is None:

        return render_template(

            "troubleshoot.html",

            category=category,

            guidance=None,

            ai_text=None,

            notice=(

                "No matching local troubleshooting "

                "guide was found."

            )

        )

    # Generate AI explanation using the runbook

    ai_text, notice = generate_ai_guidance(

        category,

        guidance["content"]

    )

    # Convert AI Markdown to safe HTML

    if ai_text:

        ai_text = bleach.clean(

            markdown.markdown(

                ai_text,

                extensions=[

                    "extra",

                    "sane_lists"

                ]

            ),

            tags=[

                "p",

                "h1",

                "h2",

                "h3",

                "h4",

                "strong",

                "em",

                "ul",

                "ol",

                "li",

                "code",

                "pre",

                "blockquote",

                "hr"

            ],

            attributes={},

            strip=True

        )

    return render_template(

        "troubleshoot.html",

        category=category,

        guidance=guidance,

        ai_text=ai_text,

        notice=notice

    )

# ==========================================

# APPLICATION STARTUP

# ==========================================

# Initialize the database when imported

# by Flask or the automated test suite.

init_db()

if __name__ == "__main__":

    app.run(debug=True)
