from flask import Flask, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name('alerts.db')


def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            message TEXT NOT NULL
        )''')


def get_demo_data():
    """Fixed sample data; simulated events will be added in Phase 2."""
    return {
        'name': 'Demo Server',
        'cpu': 24,
        'memory': 42,
        'storage': 61,
        'services': [
            {'name': 'Plex', 'status': 'Running'},
            {'name': 'Sonarr', 'status': 'Running'},
            {'name': 'Radarr', 'status': 'Running'},
        ],
    }


@app.route('/')
def dashboard():
    return render_template('dashboard.html', server=get_demo_data())


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
