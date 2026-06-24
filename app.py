"""
Tiny Flask web app with a /health endpoint.

This is the **target** repo for the multi-agent PR-review demo: open a PR
against this app, the agent reviews it (in the separate MultiAgentCodeReview
repo) and suggests fixes, and this repo's GitHub Actions workflow verifies the
app still boots and `/health` returns 200 after the change.

Run locally:
    pip install -r requirements.txt
    python app.py                    # serves on http://127.0.0.1:8000

Endpoints:
    GET /          -> index banner (text/plain)
    GET /health    -> {"status": "ok", "version": "...", "uptime_seconds": N}
"""

from __future__ import annotations

import os
import time

from flask import Flask, jsonify

VERSION = "0.1.0"
_STARTED_AT = time.monotonic()


def create_app() -> Flask:
    """Application factory — keeps the app testable with `app.test_client()`."""
    application = Flask(__name__)

    @application.get("/")
    def index() -> tuple[str, int]:
        return f"multi-agent-demo-app v{VERSION}\n", 200

    @application.get("/health")
    def health():
        # Keep the response small and stable so CI assertions are easy.
        return jsonify(
            {
                "status": "ok",
                "version": VERSION,
                "uptime_seconds": round(time.monotonic() - _STARTED_AT, 3),
            }
        ), 200

    return application
    
def lookup_user(db_conn, username: str):
    """Fetch user details from the database by username."""
    with db_conn.cursor() as cursor:
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchall()


# Module-level instance so `flask --app app run` works too.
app = create_app()


def main() -> None:
    """Run the Flask application."""
    port = int(os.environ.get("PORT", "8000"))
    # host=0.0.0.0 so the GitHub Actions runner can curl it; debug stays off.
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()