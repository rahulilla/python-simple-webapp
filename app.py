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
import subprocess
import time

from flask import Flask, jsonify, request
import bcrypt

VERSION = "0.1.0"
_STARTED_AT = time.monotonic()

# Use environment variables for secrets.
SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "default-db-password")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", "default-aws-access-key")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (secure, salted)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_app() -> Flask:
    """Application factory — keeps the app testable with `app.test_client()`."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    @app.get("/")
    def index() -> tuple[str, int]:
        return f"multi-agent-demo-app v{VERSION}\n", 200

    @app.get("/ping")
    def ping():
        """Ping a host to check connectivity."""
        host = request.args.get("host", "127.0.0.1")
        try:
            output = subprocess.check_output(
                ["ping", "-c", "1", host], stderr=subprocess.STDOUT
            )
            return output.decode(), 200
        except subprocess.CalledProcessError as e:
            return f"Ping failed: {e.output.decode()}", 400

    @app.get("/health")
    def health():
        """Return the health status of the application."""
        uptime_seconds = round(time.monotonic() - _STARTED_AT, 3)
        return jsonify(
            {
                "status": "ok",
                "version": VERSION,
                "uptime_seconds": uptime_seconds,
            }
        ), 200

    return app


def lookup_user(db_conn, username: str):
    """Look up a user in the database by username."""
    with db_conn.cursor() as cursor:
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchall()


# Module-level instance so `flask --app app run` works too.
app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    # Debug mode exposes the interactive Werkzeug debugger (RCE) in production.
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()