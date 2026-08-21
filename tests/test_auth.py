import pytest
from app import create_app
from app.db import db
from app.config import TestingConfig
from app.services.auth_service import AuthService

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_db(app):
    with app.app_context():
        # Tables are already created in create_app()
        yield db
        db.session.remove()
        db.drop_all()

def test_registration_and_login(app, init_db, client):
    # Test sign-up
    response = client.post('/register', data={
        'email': 'jane@company.com',
        'password': 'SecurePassword123',
        'role': 'Employee',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'department': 'Engineering',
        'designation': 'Developer',
        'phone': '1234567890',
        'manager_id': ''
    }, follow_redirects=True)
    
    assert b"Registration successful! Please log in." in response.data

    # Test login - employee is redirected to travel list page
    response = client.post('/login', data={
        'email': 'jane@company.com',
        'password': 'SecurePassword123'
    }, follow_redirects=True)
    
    assert b"Logged in successfully!" in response.data
    assert b"My Travel Requests" in response.data

def test_role_based_access_control(app, init_db, client):
    # Create an employee and a manager
    with app.app_context():
        AuthService.register_user(
            email='employee@company.com', password='password', role='Employee',
            first_name='Emp', last_name='Loyee', department='HR', designation='Staff'
        )
        AuthService.register_user(
            email='manager@company.com', password='password', role='Manager',
            first_name='Man', last_name='Ager', department='HR', designation='Lead'
        )

    # Login as Employee
    client.post('/login', data={'email': 'employee@company.com', 'password': 'password'})

    # /employee/dashboard now redirects to /travel/ (302) - follow redirect and verify travel page
    response = client.get('/employee/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"My Travel Requests" in response.data

    # Try to access manager dashboard as employee - Forbidden (403)
    response = client.get('/manager/dashboard')
    assert response.status_code == 403

    # Logout
    client.get('/logout')

    # Login as Manager
    client.post('/login', data={'email': 'manager@company.com', 'password': 'password'})

    # Try to access employee dashboard as manager - Forbidden
    response = client.get('/employee/dashboard')
    assert response.status_code == 403

    # Try to access manager dashboard as manager - Allowed (dashboard redirects to manager approvals)
    response = client.get('/manager/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Manager Approvals Dashboard" in response.data
