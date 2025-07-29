import pytest
from main import app, db
from models import User

@pytest.fixture(scope='module')
def test_client():
    """
    Sets up a test client for the Flask application.
    This fixture configures the app for testing, uses an in-memory SQLite
    database, and creates all database tables. It yields a client to run
    requests against the app.
    """
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key" # A secret key is needed for session management
    })

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
        yield testing_client
        with app.app_context():
            db.drop_all()

@pytest.fixture(autouse=True)
def cleanup_db(test_client):
    """
    A fixture that automatically cleans up the database after each test.
    This ensures that tests are independent of each other.
    """
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

def test_create_user_success(test_client):
    """Test creating a new user successfully."""
    response = test_client.post('/api/users', json={'username': 'testuser', 'email': 'test@example.com'})
    assert response.status_code == 201
    assert response.json['username'] == 'testuser'
    assert response.json['email'] == 'test@example.com'

def test_create_user_duplicate(test_client):
    """Test creating a user with a duplicate username or email."""
    test_client.post('/api/users', json={'username': 'testuser', 'email': 'test@example.com'})
    response = test_client.post('/api/users', json={'username': 'testuser', 'email': 'another@example.com'})
    assert response.status_code == 409
    assert 'error' in response.json

@pytest.mark.parametrize("payload, expected_error", [
    ({'username': 'testuser'}, 'email must be a non-empty string'),
    ({'email': 'test@example.com'}, 'username must be a non-empty string'),
    ({}, 'username must be a non-empty string'), # username is checked first
    ({'username': '', 'email': 'test@example.com'}, 'username must be a non-empty string'),
    ({'username': 'testuser', 'email': '  '}, 'email must be a non-empty string'),
    ({'username': 'testuser', 'email': 123}, 'email must be a non-empty string'),
    ({'username': None, 'email': 'test@example.com'}, 'username must be a non-empty string'),
])
def test_create_user_invalid_data(test_client, payload, expected_error):
    """Test creating a user with various invalid or missing data payloads."""
    response = test_client.post('/api/users', json=payload)
    assert response.status_code == 400
    assert expected_error in response.json['error']

def test_get_all_users(test_client):
    """Test retrieving all users."""
    test_client.post('/api/users', json={'username': 'user1', 'email': 'user1@example.com'})
    test_client.post('/api/users', json={'username': 'user2', 'email': 'user2@example.com'})
    response = test_client.get('/api/users')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_get_single_user(test_client):
    """Test retrieving a single user by ID."""
    res = test_client.post('/api/users', json={'username': 'testuser', 'email': 'test@example.com'})
    user_id = res.json['id']
    response = test_client.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    assert response.json['username'] == 'testuser'

def test_get_nonexistent_user(test_client):
    """Test retrieving a user that does not exist."""
    response = test_client.get('/api/users/999')
    assert response.status_code == 404

def test_update_user(test_client):
    """Test updating an existing user's details."""
    res = test_client.post('/api/users', json={'username': 'testuser', 'email': 'test@example.com'})
    user_id = res.json['id']
    response = test_client.put(f'/api/users/{user_id}', json={'username': 'updateduser'})
    assert response.status_code == 200
    assert response.json['username'] == 'updateduser'
    assert response.json['email'] == 'test@example.com' # Email should be unchanged

def test_update_user_conflict(test_client):
    """Test updating a user to an email that already exists."""
    test_client.post('/api/users', json={'username': 'user1', 'email': 'user1@example.com'})
    res2 = test_client.post('/api/users', json={'username': 'user2', 'email': 'user2@example.com'})
    user2_id = res2.json['id']
    
    response = test_client.put(f'/api/users/{user2_id}', json={'email': 'user1@example.com'})
    assert response.status_code == 409

def test_delete_user(test_client):
    """Test deleting a user."""
    res = test_client.post('/api/users', json={'username': 'testuser', 'email': 'test@example.com'})
    user_id = res.json['id']
    
    # Delete the user
    delete_response = test_client.delete(f'/api/users/{user_id}')
    assert delete_response.status_code == 204
    
    # Verify the user is gone
    get_response = test_client.get(f'/api/users/{user_id}')
    assert get_response.status_code == 404