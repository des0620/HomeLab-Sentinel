from flask import Flask, render_template, redirect, url_for, abort
from contextlib import contextmanager
import markdown
import bleach
import sqlite3
from pathlib import Path
import os
import re
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
KB_PATH = Path(__file__).with_name("knowledge_base") / "troubleshooting.txt"
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




def retrieve_guidance(category):
    """Retrieve the best matching local runbook section (no external service needed)."""
    sections = [section.strip() for section in KB_PATH.read_text(encoding="utf-8").split("\n---\n") if section.strip()]
    query = set(re.findall(r"[a-z0-9]+", category.lower()))
    ranked = []
    for section in sections:
        title = section.splitlines()[0].removeprefix("# ").strip()
        words = set(re.findall(r"[a-z0-9]+", title.lower()))
        score = len(query & words)
        if score:
            ranked.append((score, title, section))
    if not ranked:
        return None
    _, title, content = max(ranked, key=lambda item: item[0])
    return {"title": title, "content": content}


def generate_ai_guidance(category, evidence):
    """Generate troubleshooting guidance using OpenAI, with a local fallback."""

    key = os.getenv("OPENAI_API_KEY", "").strip()

    if not key:
        return None, "OpenAI API key not configured. Showing local runbook guidance."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, timeout=30.0, max_retries=1)

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "You are a cautious home server troubleshooting assistant. "
                "Use ONLY the provided local runbook. "
                "Do not invent commands or causes. "
                "Explain the issue and give numbered, non-destructive troubleshooting steps. "
                "If the runbook lacks information, say so. "
                "Never suggest automatic repairs."
            ),
            input=(
                f"Alert: {category}\n\n"
                f"Trusted local runbook:\n{evidence}"
            ),
            max_output_tokens=500
        )

        answer = (response.output_text or "").strip()

        if answer:
            return answer, None

        return None, "AI returned no response. Showing local guidance."

    except Exception:
        app.logger.exception("OpenAI troubleshooting request failed")
        return None, "AI service unavailable. Showing local runbook guidance."


@app.get("/troubleshoot/<category>")
def troubleshoot(category):
    # Only allow advice for a currently active alert.
    server = current_state()
    categories = {alert["category"] for alert in active_alerts(server)}

    if category not in categories:
        abort(404)

    guidance = retrieve_guidance(category)

    if guidance is None:
        return render_template(
            "troubleshoot.html",
            category=category,
            guidance=None,
            ai_text=None,
            notice="No matching local troubleshooting guide was found."
        )

    ai_text, notice = generate_ai_guidance(category, guidance["content"])

    # Convert OpenAI's Markdown into safe, formatted HTML.
    if ai_text:
        ai_text = bleach.clean(
            markdown.markdown(
                ai_text,
                extensions=["extra", "sane_lists"]
            ),
            tags=[
                "p", "h1", "h2", "h3", "h4",
                "strong", "em", "ul", "ol", "li",
                "code", "pre", "blockquote", "hr"
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


# Database setup also runs when Flask imports the app for testing.
init_db()

if __name__ == "__main__":
    app.run(debug=True)
