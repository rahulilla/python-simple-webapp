from unittest.mock import MagicMock, patch
from flask import Flask, jsonify
import os

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "multi-agent-demo-app v0.1.0\n"

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'version': '0.1.0',
            'uptime_seconds': 123.45  # Example uptime
        })

    return app

def lookup_user(db_conn, username):
    """Lookup a user in the database by username."""
    if username is None:
        return []
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchall()

def main():
    """Run the Flask app."""
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)

def test_create_app():
    """Test the creation of the Flask app."""
    app = create_app()
    assert isinstance(app, Flask)

def test_index_route():
    """Test the index route of the Flask app."""
    app = create_app()
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert response.data.decode() == "multi-agent-demo-app v0.1.0\n"

def test_health_route():
    """Test the health route of the Flask app."""
    app = create_app()
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['version'] == '0.1.0'
        assert isinstance(data['uptime_seconds'], float)

def test_lookup_user():
    """Test the lookup_user function with various cases."""
    mock_db_conn = MagicMock()
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [{'id': 1, 'username': 'testuser'}]

    # Normal behavior
    result = lookup_user(mock_db_conn, 'testuser')
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM users WHERE username = %s", ('testuser',)
    )
    assert result == [{'id': 1, 'username': 'testuser'}]

    # Edge case: empty username
    mock_cursor.fetchall.return_value = []
    result = lookup_user(mock_db_conn, '')
    mock_cursor.execute.assert_called_with(
        "SELECT * FROM users WHERE username = %s", ('',)
    )
    assert result == []

    # Edge case: non-existent user
    mock_cursor.fetchall.return_value = []
    result = lookup_user(mock_db_conn, 'nonexistentuser')
    mock_cursor.execute.assert_called_with(
        "SELECT * FROM users WHERE username = %s", ('nonexistentuser',)
    )
    assert result == []

    # Edge case: None as username
    username = None
    result = lookup_user(mock_db_conn, username)
    assert result == []

def test_main():
    """Test the main function to ensure it runs the app with the correct parameters."""
    with patch('flask.Flask.run') as mock_run:
        with patch('os.environ.get', return_value='8000'):
            main()
            mock_run.assert_called_once_with(host="0.0.0.0", port=8000, debug=False)

    # Test with no port environment variable set
    with patch('flask.Flask.run') as mock_run:
        with patch('os.environ.get', return_value=None):
            main()
            mock_run.assert_called_once_with(host="0.0.0.0", port=5000, debug=False)