HomeLab Sentinel — Phase 3 update

1. Stop Flask (Ctrl+C).
2. Extract this ZIP and copy its contents into your EXISTING project directory, replacing app.py, requirements.txt, and templates/dashboard.html. Keep .git, .venv, alerts.db, and static/.
3. Ensure your existing app.py has the corrected @contextmanager connect_db() with connection.close() in finally. The included app.py uses that fix.
4. In the VS Code terminal (with .venv active), run:
   python -m pip install -r requirements.txt
   python -m unittest -v test_phase2 test_phase3
   python app.py
5. Open http://127.0.0.1:5000, click High CPU, then Troubleshoot.
6. OPTIONAL Gemini setup: copy .env.example to .env, put your real GOOGLE_API_KEY in .env, and restart Flask. Do not paste your key into chat or GitHub.
7. Verify .gitignore contains a line for .env before any git add/commit.

If your Gemini model is unavailable to your API key, change GEMINI_MODEL in .env to a model listed in your Gemini account. Without an API key, the knowledge base still works.
