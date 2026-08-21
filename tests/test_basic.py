import pytest
from app import create_app
from app.config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_app_home_redirects_to_login(client):
    """Root route should redirect unauthenticated users to /login."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_page_loads(client):
    """Login page should load successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data
