# HomeLab Sentinel — Phase 2

Flask dashboard with simulated server events, rule-based alerts, and SQLite alert history. No live server connection or AI integration yet.

## Windows setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Press Ctrl+C to stop.

## Try it
1. Click **High CPU**: CPU goes to 95%, a red alert appears, and a history entry is saved.
2. Click **Disk Warning**: storage goes to 96% and an alert appears.
3. Click **Docker Failure**: Plex becomes Stopped.
4. Click **Reset Server**: all current values return to normal. History remains for review.

## Notes
- All data is simulated. Changes persist locally in `alerts.db` until that file is deleted.
- The database is ignored by Git. Never commit API keys or `.env` files.
- The web app is for local development only; don't expose Flask's debug server to the internet.
- Phase 3 will add RAG-based AI troubleshooting.
