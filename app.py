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
import logging

# Ensure these packages are installed via requirements.txt
from flask import Flask, jsonify
from psycopg2 import DatabaseError

VERSION = os.environ.get("APP_VERSION")
if not VERSION:
    VERSION = "unknown-version"
    logging.warning("APP_VERSION environment variable not set, using default version: %s", VERSION)

_STARTED_AT = time.monotonic()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Application factory — keeps the app testable with `app.test_client()`."""
    application = Flask(__name__)

    @application.get("/")
    def index() -> tuple[str, int]:
        """Return the index banner."""
        return f"multi-agent-demo-app v{VERSION}\n", 200

    @application.get("/health")
    def health():
        """Return the health status of the application."""
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
    """
    Look up a user in the database by username.

    Note: The caller is responsible for managing the lifecycle of the db_conn
    connection, including closing it when done.
    """
    if not username:
        logger.warning("Empty username provided.")
        return None

    try:
        with db_conn.cursor() as cursor:
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            return cursor.fetchall()
    except DatabaseError as e:
        logger.error("Database error occurred: %s", e)
        raise  # Re-raise the exception to ensure it is not silently ignored

# Module-level instance so `flask --app app run` works too.
app = create_app()

def main() -> None:
    """Run the Flask application."""
    port = os.environ.get("PORT")
    if port is None:
        logging.warning("PORT environment variable not set, using default port 8000 for local development.")
        port = 8000
    else:
        try:
            port = int(port)
        except ValueError:
            logging.error("Invalid PORT environment variable value, using default port 8000.")
            port = 8000
    # host=0.0.0.0 so the GitHub Actions runner can curl it; debug stays off.
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()