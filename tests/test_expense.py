import pytest
from io import BytesIO
from datetime import date
from app import create_app
from app.db import db
from app.config import TestingConfig
from app.services.auth_service import AuthService
from app.services.travel_service import TravelService
from app.services.expense_service import ExpenseService
from app.dao.user_dao import EmployeeDAO
from app.dao.expense_dao import ExpenseClaimDAO

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def init_db(app):
    with app.app_context():
        db.create_all()
        # Seed employee and manager
        AuthService.register_user(
            email='emp@company.com', password='password123', role='Employee',
            first_name='John', last_name='Doe', department='Sales', designation='Rep'
        )
        yield db
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login_client(client, email, password):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

def test_create_and_manage_expense_claim(app, init_db, client):
    login_client(client, 'emp@company.com', 'password123')
    
    # 1. Create a claim via POST
    response = client.post('/expense/new', data={
        'title': 'Trip to Mumbai Office',
        'description': 'Meetings with client partners',
        'travel_request_id': '' # Standalone
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Expense claim created successfully" in response.data
    assert b"Trip to Mumbai Office" in response.data

    # Fetch claim to get its id
    with app.app_context():
        employee = EmployeeDAO.get_by_user_id(1)
        claims = ExpenseClaimDAO.get_by_employee_id(employee.id)
        assert len(claims) == 1
        claim_id = claims[0].id
        assert claims[0].status == 'Draft'
        assert float(claims[0].total_amount) == 0.00

    # 2. Add an expense item line
    response = client.post(f'/expense/{claim_id}/item', data={
        'category': 'Meals',
        'amount': '1500.50',
        'expense_date': '2026-08-18',
        'description': 'Team dinner'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Line item added successfully" in response.data
    assert b"1500.50" in response.data

    with app.app_context():
        claims = ExpenseClaimDAO.get_by_employee_id(employee.id)
        assert float(claims[0].total_amount) == 1500.50

    # 3. Simulate file upload of a valid receipt (PDF)
    data = {
        'receipt_file': (BytesIO(b"dummy pdf receipt content"), 'invoice.pdf')
    }
    response = client.post(f'/expense/{claim_id}/receipt', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"Receipt uploaded successfully" in response.data
    assert b"invoice.pdf" in response.data

    # 4. Simulate file upload of an invalid receipt type (.txt)
    data_invalid = {
        'receipt_file': (BytesIO(b"dummy text content"), 'receipt.txt')
    }
    response = client.post(f'/expense/{claim_id}/receipt', data=data_invalid, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid file type" in response.data

    # 5. Submit the claim
    response = client.post(f'/expense/{claim_id}/submit', follow_redirects=True)
    assert response.status_code == 200
    assert b"Expense claim submitted successfully for approval" in response.data

    with app.app_context():
        claims = ExpenseClaimDAO.get_by_employee_id(employee.id)
        assert claims[0].status == 'Submitted'

    # 6. Try adding item to a submitted claim (should fail/redirect/prevent)
    response = client.post(f'/expense/{claim_id}/item', data={
        'category': 'Flight',
        'amount': '5000.00',
        'expense_date': '2026-08-18',
        'description': 'Flight to Mumbai'
    }, follow_redirects=True)
    assert b"Cannot add items to a submitted or processed claim" in response.data
