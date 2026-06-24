from unittest.mock import MagicMock, patch
import pytest
from app import create_app, lookup_user, main
from psycopg2 import DatabaseError

@pytest.fixture
def flask_app_fixture():
    """Fixture to create a Flask app for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def test_client(flask_app_fixture):
    """Fixture to create a test client for the Flask app."""
    return flask_app_fixture.test_client()

def test_create_app(test_client):
    """Test the create_app function and its endpoints."""
    # Test the index endpoint
    response = test_client.get('/')
    assert response.status_code == 200
    assert response.data.decode() == "multi-agent-demo-app vunknown-version\n"

    # Test the health endpoint
    response = test_client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['version'] == 'unknown-version'
    assert isinstance(data['uptime_seconds'], float)

def test_lookup_user_valid_user():
    """Test lookup_user with a valid username."""
    mock_db_conn = MagicMock()
    with mock_db_conn.cursor() as mock_cursor:
        mock_cursor.fetchall.return_value = [{'username': 'testuser'}]

        result = lookup_user(mock_db_conn, 'testuser')
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = %s", ('testuser',))
        assert result == [{'username': 'testuser'}]

def test_lookup_user_empty_username():
    """Test lookup_user with an empty username."""
    mock_db_conn = MagicMock()

    result = lookup_user(mock_db_conn, '')
    assert result == []

def test_lookup_user_database_error():
    """Test lookup_user when a DatabaseError is raised."""
    mock_db_conn = MagicMock()
    mock_db_conn.cursor.side_effect = DatabaseError("Database connection error")

    with pytest.raises(DatabaseError):
        lookup_user(mock_db_conn, 'testuser')

@patch('app.run')
def test_main(mock_run):
    """Test the main function."""
    with patch.dict('os.environ', {}, clear=True):
        main()
        mock_run.assert_called_once_with(host="0.0.0.0", port=8000, debug=False)

    with patch.dict('os.environ', {'PORT': '5000'}, clear=True):
        main()
        mock_run.assert_called_with(host="0.0.0.0", port=5000, debug=False)