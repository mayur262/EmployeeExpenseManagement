import pytest
from datetime import date, datetime
from app import create_app
from app.db import db
from app.config import TestingConfig
from app.services.auth_service import AuthService
from app.services.travel_service import TravelService
from app.services.expense_service import ExpenseService
from app.services.policy_service import PolicyService
from app.dao.user_dao import UserDAO, EmployeeDAO
from app.dao.travel_dao import TravelDAO
from app.dao.expense_dao import ExpenseClaimDAO

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
       
        PolicyService.create_policy('Meals', 50.00)
        PolicyService.create_policy('Accommodation', 200.00)
        yield db
        db.session.remove()
        db.drop_all()

def test_user_employee_creation(app, init_database):
    with app.app_context():
       
        manager_user = AuthService.register_user(
            email='manager@company.com',
            password='Password123',
            role='Manager',
            first_name='John',
            last_name='Doe',
            department='Engineering',
            designation='Engineering Manager'
        )
        
        manager_emp = EmployeeDAO.get_by_user_id(manager_user.id)
        assert manager_emp is not None
        assert manager_emp.first_name == 'John'
        
        
        employee_user = AuthService.register_user(
            email='emp@company.com',
            password='Password123',
            role='Employee',
            first_name='Jane',
            last_name='Smith',
            department='Engineering',
            designation='Software Engineer',
            manager_id=manager_emp.id
        )
        
        emp = EmployeeDAO.get_by_user_id(employee_user.id)
        assert emp is not None
        assert emp.manager_id == manager_emp.id
        assert emp.manager.first_name == 'John'

def test_travel_request_workflow(app, init_database):
    with app.app_context():
        manager_user = AuthService.register_user(
            email='manager@company.com', password='Password123', role='Manager',
            first_name='John', last_name='Doe', department='HR', designation='Manager'
        )
        manager_emp = EmployeeDAO.get_by_user_id(manager_user.id)
        
        employee_user = AuthService.register_user(
            email='emp@company.com', password='Password123', role='Employee',
            first_name='Jane', last_name='Smith', department='HR', designation='Associate',
            manager_id=manager_emp.id
        )
        emp = EmployeeDAO.get_by_user_id(employee_user.id)

        
        req = TravelService.create_travel_request(
            employee_id=emp.id,
            destination='New York',
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 5),
            purpose='Client Meeting',
            estimated_budget=1500.00
        )
        
        assert req.id is not None
        assert req.status == 'Pending'

        
        TravelService.approve_or_reject_travel_request(
            request_id=req.id,
            approver_user=manager_user,
            action='Approved',
            comments='Approved for business travel'
        )
        
        updated_req = TravelDAO.get_by_id(req.id)
        assert updated_req.status == 'Approved'

def test_expense_claims_reimbursement(app, init_database):
    with app.app_context():
        
        emp_user = AuthService.register_user(
            email='emp@company.com', password='Password123', role='Employee',
            first_name='Jane', last_name='Smith', department='Sales', designation='Sales Lead'
        )
        emp = EmployeeDAO.get_by_user_id(emp_user.id)

        
        claim = ExpenseService.create_expense_claim(
            employee_id=emp.id,
            title='Q3 Sales Conference'
        )
        assert claim.status == 'Draft'
        assert claim.total_amount == 0.00

       
        ExpenseService.add_expense_item(
            claim_id=claim.id,
            category='Meals',
            amount=45.00,
            expense_date=date(2026, 8, 1),
            description='Client lunch'
        )
        
        ExpenseService.add_expense_item(
            claim_id=claim.id,
            category='Accommodation',
            amount=180.00,
            expense_date=date(2026, 8, 1),
            description='Hotel stay'
        )

        assert claim.total_amount == 225.00

      
        ExpenseService.submit_claim(claim.id)
        assert claim.status == 'Submitted'

        
        mgr_user = AuthService.register_user(
            email='mgr@company.com', password='Password123', role='Manager',
            first_name='Manager', last_name='One', department='Sales', designation='VP'
        )
        ExpenseService.approve_or_reject_claim(claim.id, mgr_user, 'Approved', 'Looks valid')
        assert claim.status == 'Approved'

        
        fin_user = AuthService.register_user(
            email='fin@company.com', password='Password123', role='Finance',
            first_name='Finance', last_name='One', department='Finance', designation='Accountant'
        )
        reimbursement = ExpenseService.verify_and_reimburse(
            claim_id=claim.id,
            finance_user=fin_user,
            transaction_reference='TXN987654'
        )
        
        assert reimbursement.status == 'Processed'
        assert reimbursement.amount_paid == 225.00
        assert claim.status == 'Verified'
