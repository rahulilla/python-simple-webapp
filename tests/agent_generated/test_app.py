from unittest.mock import MagicMock, patch
from flask import Flask
from app import create_app, lookup_user, main

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
    with patch('app.lookup_user') as mock_lookup_user:
        mock_db_conn = MagicMock()
        mock_cursor = mock_db_conn.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [{'id': 1, 'username': 'testuser'}]

        # Normal behavior
        result = lookup_user(mock_db_conn, 'testuser')
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE username = %s", ('testuser',)
        )
        assert result == [{'id': 1, 'username': 'testuser'}]

        # Edge case: empty username
        result = lookup_user(mock_db_conn, '')
        assert result == []

        # Edge case: non-existent user
        mock_cursor.fetchall.return_value = []
        result = lookup_user(mock_db_conn, 'nonexistentuser')
        assert result == []

        # Test for SQL injection attempt
        result = lookup_user(mock_db_conn, "testuser'; DROP TABLE users; --")
        mock_cursor.execute.assert_called_with(
            "SELECT * FROM users WHERE username = %s", ("testuser'; DROP TABLE users; --",)
        )
        assert result == []

def test_main():
    """Test the main function to ensure it runs the app with the correct parameters."""
    with patch('app.run') as mock_run:
        with patch('os.environ.get') as mock_get:
            mock_get.side_effect = lambda key, default=None: {'PORT': '8000'}.get(key, default)
            main()
            mock_run.assert_called_once_with(host="0.0.0.0", port=8000, debug=False)