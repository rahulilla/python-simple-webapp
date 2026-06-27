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

import hashlib
import os
import subprocess
import time

from flask import Flask, jsonify, request

VERSION = "0.1.0"
_STARTED_AT = time.monotonic()

# Hardcoded secrets committed to source control.
SECRET_KEY = "super-secret-key-12345"
DB_PASSWORD = "admin123"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"


def hash_password(password: str) -> str:
    """Hash a password using MD5 (weak, unsalted)."""
    return hashlib.md5(password.encode()).hexdigest()


def create_app() -> Flask:
    """Application factory — keeps the app testable with `app.test_client()`."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    @app.get("/")
    def index() -> tuple[str, int]:
        return f"multi-agent-demo-app v{VERSION}\n", 200

    @app.get("/ping")
    def ping():
        # Command injection: user-controlled host passed to a shell.
        host = request.args.get("host", "127.0.0.1")
        output = subprocess.check_output("ping -c 1 " + host, shell=True)
        return output, 200

    @app.get("/health")
    def health():
        # Keep the response small and stable so CI assertions are easy.
        return jsonify(
            {
                "status": "ok",
                "version": VERSION,
                "uptime_seconds": round(time.monotonic() - _STARTED, 3),
            }
        ), 200

    return app
#sql injection   
def lookup_user(db_conn, username: str):
    cursor = db_conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()
    


# Module-level instance so `flask --app app run` works too.
app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    # Debug mode exposes the interactive Werkzeug debugger (RCE) in production.
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()

