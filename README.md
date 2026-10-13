# HomeLab Sentinel — Phase 1

A Flask-based server monitoring dashboard using simulated server data.

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Stop with Ctrl+C.

## Current features
- Simulated CPU, memory, storage, and service status
- SQLite database initialization for later alert history
- Responsive dashboard using Bootstrap

## Coming next
- Simulated failure events and alert rules
- Alert history
- AI-assisted troubleshooting using RAG

The sample values are fixed placeholders, not live readings.
