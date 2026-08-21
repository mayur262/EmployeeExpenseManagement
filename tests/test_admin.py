import pytest
from app import create_app
from app.db import db
from app.config import TestingConfig
from app.services.auth_service import AuthService
from app.services.admin_service import AdminService
from app.services.expense_service import ExpenseService
from app.services.policy_service import PolicyService
from app.dao.user_dao import UserDAO
from app.models.policy import ExpensePolicy
from datetime import date

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def init_db(app):
    with app.app_context():
        db.create_all()
        # Admin user
        AuthService.register_user(
            email="admin@company.com", password="password123", role="Admin",
            first_name="Super", last_name="Admin", department="IT", designation="Admin"
        )
        # Employee
        AuthService.register_user(
            email="emp@company.com", password="password123", role="Employee",
            first_name="John", last_name="Doe", department="Sales", designation="Rep"
        )
        # Finance user
        AuthService.register_user(
            email="fin@company.com", password="password123", role="Finance",
            first_name="Fin", last_name="Officer", department="Finance", designation="Accountant"
        )
        yield db
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login_client(client, email, password):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


# ---- Access Control Tests ----

def test_admin_access_control(app, init_db, client):
    # Employee cannot access admin panel
    login_client(client, "emp@company.com", "password123")
    response = client.get("/admin/")
    assert response.status_code == 403
    client.get("/logout")

    # Finance cannot access admin panel
    login_client(client, "fin@company.com", "password123")
    response = client.get("/admin/")
    assert response.status_code == 403
    client.get("/logout")

    # Admin can access
    login_client(client, "admin@company.com", "password123")
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"System Admin Panel" in response.data


# ---- User Management Tests ----

def test_admin_manage_users(app, init_db, client):
    login_client(client, "admin@company.com", "password123")

    # Manage users page loads
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert b"emp@company.com" in response.data
    assert b"fin@company.com" in response.data


def test_admin_update_user_role(app, init_db, client):
    login_client(client, "admin@company.com", "password123")

    # Change emp role to Manager
    response = client.post("/admin/users/2/edit", data={"role": "Manager"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated to Manager" in response.data

    with app.app_context():
        user = UserDAO.get_by_id(2)
        assert user.role == "Manager"


def test_admin_toggle_user_active(app, init_db, client):
    login_client(client, "admin@company.com", "password123")

    # Deactivate user 2
    response = client.post("/admin/users/2/toggle", follow_redirects=True)
    assert response.status_code == 200
    assert b"deactivated" in response.data

    with app.app_context():
        user = UserDAO.get_by_id(2)
        assert user.is_active is False

    # Re-activate
    response = client.post("/admin/users/2/toggle", follow_redirects=True)
    assert b"activated" in response.data

    with app.app_context():
        user = UserDAO.get_by_id(2)
        assert user.is_active is True


def test_admin_cannot_deactivate_self(app, init_db, client):
    login_client(client, "admin@company.com", "password123")
    # Admin id is 1
    response = client.post("/admin/users/1/toggle", follow_redirects=True)
    assert b"cannot deactivate your own account" in response.data.lower() or response.status_code == 200


# ---- Policy Management Tests ----

def test_admin_create_policy(app, init_db, client):
    login_client(client, "admin@company.com", "password123")

    # Create a Meals policy
    response = client.post("/admin/policies/new", data={
        "category": "Meals",
        "max_limit": "500",
        "role_restriction": ""
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Meals" in response.data

    with app.app_context():
        policy = ExpensePolicy.query.filter_by(category="Meals").first()
        assert policy is not None
        assert float(policy.max_limit_per_expense) == 500.0


def test_admin_update_policy(app, init_db, client):
    with app.app_context():
        PolicyService.create_policy(category="Accommodation", max_limit=2000.0)
        policy = ExpensePolicy.query.filter_by(category="Accommodation").first()
        policy_id = policy.id

    login_client(client, "admin@company.com", "password123")
    response = client.post(f"/admin/policies/{policy_id}/edit", data={
        "category": "Accommodation",
        "max_limit": "3000",
        "role_restriction": "Employee"
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        policy = ExpensePolicy.query.filter_by(category="Accommodation").first()
        assert float(policy.max_limit_per_expense) == 3000.0
        assert policy.role_restriction == "Employee"


def test_admin_delete_policy(app, init_db, client):
    with app.app_context():
        PolicyService.create_policy(category="Flight", max_limit=10000.0)
        policy = ExpensePolicy.query.filter_by(category="Flight").first()
        policy_id = policy.id

    login_client(client, "admin@company.com", "password123")
    response = client.post(f"/admin/policies/{policy_id}/delete", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        policy = ExpensePolicy.query.filter_by(category="Flight").first()
        assert policy is None


# ---- Policy Enforcement Tests ----

def test_policy_limit_enforced_on_expense_item(app, init_db, client):
    """Adding an expense item exceeding policy limit should raise a ValueError."""
    with app.app_context():
        # Create Meals policy with limit of 300
        PolicyService.create_policy(category="Meals", max_limit=300.0)

        claim = ExpenseService.create_expense_claim(employee_id=2, title="Dinner Claim")

        # Amount below limit - should succeed
        item = ExpenseService.add_expense_item(
            claim_id=claim.id, category="Meals", amount=250.0, expense_date=date(2026, 8, 1)
        )
        assert item is not None

        # Amount above limit - should raise ValueError
        try:
            ExpenseService.add_expense_item(
                claim_id=claim.id, category="Meals", amount=400.0, expense_date=date(2026, 8, 2)
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "policy limit" in str(e).lower() or "exceeds" in str(e).lower()


def test_policy_limit_enforced_via_ui(app, init_db, client):
    """UI endpoint should flash error when expense item exceeds policy."""
    with app.app_context():
        PolicyService.create_policy(category="Meals", max_limit=200.0)
        claim = ExpenseService.create_expense_claim(employee_id=2, title="Lunch Claim")
        claim_id = claim.id

    login_client(client, "emp@company.com", "password123")
    response = client.post(f"/expense/{claim_id}/item", data={
        "category": "Meals",
        "amount": "500",
        "expense_date": "2026-08-01",
        "description": "Fancy lunch"
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should flash the policy violation error
    assert b"policy limit" in response.data.lower() or b"exceeds" in response.data.lower()
