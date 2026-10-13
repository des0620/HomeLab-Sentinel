from flask import Flask, render_template, redirect, url_for, request, abort
from contextlib import contextmanager
import sqlite3
from pathlib import Path


app = Flask(__name__)
DB_PATH = Path(__file__).with_name("alerts.db")

# Demo state only: this is not a live server connection.
DEFAULT = {"cpu": 24, "memory": 42, "storage": 61, "plex": "Running", "sonarr": "Running", "radarr": "Running"}
EVENTS = {
    "high_cpu": {"category": "High CPU", "message": "CPU usage is above 90%.", "updates": {"cpu": 95}},
    "disk_warning": {"category": "Disk Warning", "message": "Storage usage is above 90%.", "updates": {"storage": 96}},
    "docker_failure": {"category": "Docker Failure", "message": "Plex container has stopped.", "updates": {"plex": "Stopped"}},
}


@contextmanager
def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_db():
    with connect_db() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            message TEXT NOT NULL
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS demo_state (
            name TEXT PRIMARY KEY, value TEXT NOT NULL
        )""")
        for name, value in DEFAULT.items():
            connection.execute("INSERT OR IGNORE INTO demo_state (name, value) VALUES (?, ?)", (name, str(value)))


def current_state():
    with connect_db() as connection:
        state = {row["name"]: row["value"] for row in connection.execute("SELECT name, value FROM demo_state")}
    return {
        "name": "Demo Server", "cpu": int(state["cpu"]), "memory": int(state["memory"]),
        "storage": int(state["storage"]),
        "services": [{"name": name, "status": state[name.lower()]} for name in ("Plex", "Sonarr", "Radarr")]
    }


def active_alerts(server):
    problems = []
    if server["cpu"] >= 90:
        problems.append({"category": "High CPU", "message": "CPU usage is above 90%."})
    if server["memory"] >= 90:
        problems.append({"category": "High Memory", "message": "Memory usage is above 90%."})
    if server["storage"] >= 90:
        problems.append({"category": "Disk Warning", "message": "Storage usage is above 90%."})
    for service in server["services"]:
        if service["status"] != "Running":
            problems.append({"category": "Docker Failure", "message": f"{service['name']} container has stopped."})
    return problems


@app.route("/")
def dashboard():
    server = current_state()
    with connect_db() as connection:
        history = connection.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 15").fetchall()
    return render_template("dashboard.html", server=server, active_alerts=active_alerts(server), history=history)


@app.post("/simulate/<event>")
def simulate(event):
    # Allow only explicitly supported simulation events.
    if event != "reset" and event not in EVENTS:
        abort(404)
    with connect_db() as connection:
        if event == "reset":
            for name, value in DEFAULT.items():
                connection.execute("UPDATE demo_state SET value = ? WHERE name = ?", (str(value), name))
            connection.execute("INSERT INTO alerts (category, message) VALUES (?, ?)", ("Reset", "Demo server returned to normal."))
        else:
            definition = EVENTS[event]
            for name, value in definition["updates"].items():
                connection.execute("UPDATE demo_state SET value = ? WHERE name = ?", (str(value), name))
            connection.execute("INSERT INTO alerts (category, message) VALUES (?, ?)",
                               (definition["category"], definition["message"]))
    return redirect(url_for("dashboard"), code=303)


# Database setup also runs when Flask imports the app for testing.
init_db()

if __name__ == "__main__":
    app.run(debug=True)
