# Tests Folder Explanation

This file explains every test file inside the `tests` folder of this Flask Corporate Expense Management System.

The project uses `pytest` and Flask's test client. Most tests create the app with `TestingConfig`, which uses an in-memory SQLite database instead of the real MySQL database.

Important common pattern:

```python
@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
```

This creates a test version of the Flask app and gives a `client` object to send fake browser requests like `GET /login` or `POST /expense/new`.

## 1. `test_basic.py`

### Purpose

This file checks the most basic application routes:

- Whether the home page redirects unauthenticated users to login.
- Whether the login page loads correctly.

### Important code

```python
def test_app_home_redirects_to_login(client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
```

### Explanation

This test sends a GET request to `/`. Since the user is not logged in, the app should redirect to `/login`.

Expected result:

- Status code should be `302`.
- Redirect location should contain `/login`.

### Important code

```python
def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data
```

### Explanation

This checks whether the login page is available and contains the text `Sign In`.

## 2. `test_auth.py`

### Purpose

This file tests:

- User registration.
- User login.
- Role-based access between Employee and Manager.

### Setup code

```python
@pytest.fixture
def init_db(app):
    with app.app_context():
        yield db
        db.session.remove()
        db.drop_all()
```

### Explanation

This fixture prepares the database for each test and drops all tables after the test. It keeps tests isolated.

### Test: registration and login

```python
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
```

### Explanation

This submits the registration form. The expected behavior is that a new user and employee profile are created, and the app shows a success message.

Then it logs in:

```python
response = client.post('/login', data={
    'email': 'jane@company.com',
    'password': 'SecurePassword123'
}, follow_redirects=True)

assert b"Logged in successfully!" in response.data
assert b"My Travel Requests" in response.data
```

After employee login, the user is redirected to the travel request page.

### Test: role-based access control

```python
AuthService.register_user(
    email='employee@company.com', password='password', role='Employee',
    first_name='Emp', last_name='Loyee', department='HR', designation='Staff'
)
AuthService.register_user(
    email='manager@company.com', password='password', role='Manager',
    first_name='Man', last_name='Ager', department='HR', designation='Lead'
)
```

### Explanation

The test creates one employee and one manager directly using `AuthService`.

It then verifies:

- Employee can access employee dashboard.
- Employee cannot access manager dashboard.
- Manager cannot access employee dashboard.
- Manager can access manager dashboard.

Important assertion:

```python
response = client.get('/manager/dashboard')
assert response.status_code == 403
```

This proves RBAC is working.

## 3. `test_expense.py`

### Purpose

This file tests the main employee expense claim flow:

- Login as employee.
- Create an expense claim.
- Add an expense item.
- Upload a valid receipt.
- Reject invalid receipt type.
- Submit the claim.
- Prevent item changes after submission.

### Setup code

```python
AuthService.register_user(
    email='emp@company.com', password='password123', role='Employee',
    first_name='John', last_name='Doe', department='Sales', designation='Rep'
)
```

### Explanation

The test database is seeded with an employee. The employee is used to test claim creation and receipt upload.

### Test: create claim

```python
response = client.post('/expense/new', data={
    'title': 'Trip to Mumbai Office',
    'description': 'Meetings with client partners',
    'travel_request_id': ''
}, follow_redirects=True)

assert response.status_code == 200
assert b"Expense claim created successfully" in response.data
```

### Explanation

This checks that an employee can create a new expense claim. The claim starts in `Draft` status.

### Test: add expense item

```python
response = client.post(f'/expense/{claim_id}/item', data={
    'category': 'Meals',
    'amount': '1500.50',
    'expense_date': '2026-08-18',
    'description': 'Team dinner'
}, follow_redirects=True)
```

### Explanation

This adds one line item to the claim. The test later checks that the claim total becomes `1500.50`.

### Test: valid receipt upload

```python
data = {
    'receipt_file': (BytesIO(b"dummy pdf receipt content"), 'invoice.pdf')
}
response = client.post(
    f'/expense/{claim_id}/receipt',
    data=data,
    content_type='multipart/form-data',
    follow_redirects=True
)
```

### Explanation

This simulates uploading a PDF receipt. `BytesIO` is used to fake a file in memory.

### Test: invalid receipt upload

```python
data_invalid = {
    'receipt_file': (BytesIO(b"dummy text content"), 'receipt.txt')
}
response = client.post(
    f'/expense/{claim_id}/receipt',
    data=data_invalid,
    content_type='multipart/form-data',
    follow_redirects=True
)

assert b"Invalid file type" in response.data
```

### Explanation

The application allows only PDF and image files. A `.txt` file should be rejected.

### Test: submit claim and lock it

```python
response = client.post(f'/expense/{claim_id}/submit', follow_redirects=True)
assert b"Expense claim submitted successfully for approval" in response.data
```

After submission, the test tries to add another item:

```python
assert b"Cannot add items to a submitted or processed claim" in response.data
```

This verifies that submitted claims cannot be edited.

## 4. `test_database.py`

### Purpose

This file tests database-level and service-level workflows:

- User and employee creation.
- Manager relationship.
- Travel request workflow.
- Expense claim reimbursement workflow.

### Setup code

```python
PolicyService.create_policy('Meals', 50.00)
PolicyService.create_policy('Accommodation', 200.00)
```

### Explanation

The test database starts with two expense policies. These are used when testing expense items.

### Test: user and employee creation

```python
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
```

### Explanation

This verifies that registration creates both:

- A `User` record.
- An `Employee` profile record.

Then it creates an employee reporting to the manager:

```python
assert emp.manager_id == manager_emp.id
assert emp.manager.first_name == 'John'
```

This checks the self-referencing manager relationship.

### Test: travel request workflow

```python
req = TravelService.create_travel_request(
    employee_id=emp.id,
    destination='New York',
    start_date=date(2026, 9, 1),
    end_date=date(2026, 9, 5),
    purpose='Client Meeting',
    estimated_budget=1500.00
)

assert req.status == 'Pending'
```

### Explanation

When an employee creates a travel request, it starts as `Pending`.

Manager approval:

```python
TravelService.approve_or_reject_travel_request(
    request_id=req.id,
    approver_user=manager_user,
    action='Approved',
    comments='Approved for business travel'
)

updated_req = TravelDAO.get_by_id(req.id)
assert updated_req.status == 'Approved'
```

This verifies the travel request status changes after approval.

### Test: expense claim reimbursement

```python
claim = ExpenseService.create_expense_claim(
    employee_id=emp.id,
    title='Q3 Sales Conference'
)
assert claim.status == 'Draft'
```

The test adds items, submits the claim, gets manager approval, and then finance reimburses it.

Important final assertions:

```python
assert reimbursement.status == 'Processed'
assert reimbursement.amount_paid == 225.00
assert claim.status == 'Verified'
```

This verifies the full reimbursement workflow.

## 5. `test_admin.py`

### Purpose

This file tests admin functionality:

- Admin access control.
- Manage users page.
- Update user role.
- Activate/deactivate user.
- Prevent admin self-deactivation.
- Create, update, delete policies.
- Policy limit enforcement through service and UI.

### Setup code

```python
AuthService.register_user(
    email="admin@company.com", password="password123", role="Admin",
    first_name="Super", last_name="Admin", department="IT", designation="Admin"
)
AuthService.register_user(
    email="emp@company.com", password="password123", role="Employee",
    first_name="John", last_name="Doe", department="Sales", designation="Rep"
)
AuthService.register_user(
    email="fin@company.com", password="password123", role="Finance",
    first_name="Fin", last_name="Officer", department="Finance", designation="Accountant"
)
```

### Explanation

The test creates Admin, Employee, and Finance users to check role restrictions.

### Test: admin access control

```python
login_client(client, "emp@company.com", "password123")
response = client.get("/admin/")
assert response.status_code == 403
```

### Explanation

Employee should not access admin panel.

Finance also gets blocked:

```python
assert response.status_code == 403
```

Admin is allowed:

```python
assert response.status_code == 200
assert b"System Admin Panel" in response.data
```

### Test: update user role

```python
response = client.post("/admin/users/2/edit", data={"role": "Manager"}, follow_redirects=True)
assert b"updated to Manager" in response.data

with app.app_context():
    user = UserDAO.get_by_id(2)
    assert user.role == "Manager"
```

### Explanation

This verifies that admin can change an employee's role to Manager.

### Test: toggle active status

```python
response = client.post("/admin/users/2/toggle", follow_redirects=True)
assert b"deactivated" in response.data
```

### Explanation

Admin can deactivate and reactivate another user.

### Test: admin cannot deactivate own account

```python
response = client.post("/admin/users/1/toggle", follow_redirects=True)
assert b"cannot deactivate your own account" in response.data.lower() or response.status_code == 200
```

### Explanation

This prevents the logged-in admin from locking themselves out.

### Test: create policy

```python
response = client.post("/admin/policies/new", data={
    "category": "Meals",
    "max_limit": "500",
    "role_restriction": ""
}, follow_redirects=True)
```

### Explanation

This verifies admin can create an expense policy for a category.

### Test: policy limit enforcement

```python
PolicyService.create_policy(category="Meals", max_limit=300.0)

ExpenseService.add_expense_item(
    claim_id=claim.id, category="Meals", amount=250.0, expense_date=date(2026, 8, 1)
)
```

This succeeds because `250 <= 300`.

Then:

```python
ExpenseService.add_expense_item(
    claim_id=claim.id, category="Meals", amount=400.0, expense_date=date(2026, 8, 2)
)
```

This should raise a `ValueError` because `400 > 300`.

## 6. `test_manager.py`

### Purpose

This file tests manager-specific workflows:

- Employee cannot access manager dashboard.
- Manager sees only their subordinate's travel requests.
- Manager cannot access non-subordinate requests.
- Manager approves travel requests.
- Manager sees only subordinate expense claims.
- Manager rejects expense claims.
- Approval history is created.

### Setup code

```python
manager_user = AuthService.register_user(
    email='manager@company.com', password='password123', role='Manager',
    first_name='Boss', last_name='Man', department='Sales', designation='Director'
)
```

Then:

```python
AuthService.register_user(
    email='emp1@company.com', password='password123', role='Employee',
    first_name='John', last_name='Doe', department='Sales', designation='Rep',
    manager_id=1
)
```

### Explanation

The manager has employee ID `1`. Employee 1 reports to this manager. Employee 2 does not report to this manager.

### Test: manager dashboard and travel workflow

```python
response = client.get('/manager/')
assert b"Paris" in response.data
assert b"London" not in response.data
```

### Explanation

The manager should see the Paris request from their subordinate, but not the London request from another employee.

### Test: non-report access blocked

```python
response = client.get(f'/manager/travel/{req2_id}')
assert response.status_code == 403
```

### Explanation

The manager cannot open another employee's travel request if that employee does not report to them.

### Test: approve travel request

```python
response = client.post(f'/manager/travel/{req1_id}/action', data={
    'action': 'Approved',
    'comments': 'Approved conference trip'
}, follow_redirects=True)
```

### Explanation

This verifies manager approval. The database is checked after the request:

```python
assert req.status == 'Approved'
assert history.action == 'Approved'
assert history.comments == 'Approved conference trip'
```

### Test: manager expense claim workflow

```python
claim1 = ExpenseService.create_expense_claim(employee_id=2, title='Client Lunch Claim')
ExpenseService.add_expense_item(
    claim_id=claim1.id, category='Meals', amount=150.00, expense_date=date(2026, 8, 1)
)
ExpenseService.submit_claim(claim1.id)
```

### Explanation

This creates a submitted claim for a subordinate.

The manager rejects it:

```python
response = client.post(f'/manager/expense/{claim1_id}/action', data={
    'action': 'Rejected',
    'comments': 'Please attach missing meal receipts'
}, follow_redirects=True)
```

Final checks:

```python
assert claim.status == 'Rejected'
assert history.action == 'Rejected'
assert history.comments == 'Please attach missing meal receipts'
```

## 7. `test_finance.py`

### Purpose

This file tests finance workflows:

- Employee and Manager cannot access finance dashboard.
- Finance can access finance dashboard.
- Finance can view approved claims.
- Finance can reimburse approved claims.
- Finance can download receipt files.

### Setup code

```python
AuthService.register_user(
    email="fin@company.com", password="password123", role="Finance",
    first_name="Fin", last_name="Officer", department="Finance", designation="Accountant"
)
```

### Test: finance access control

```python
login_client(client, "emp@company.com", "password123")
response = client.get("/finance/")
assert response.status_code == 403
```

Manager is also blocked:

```python
assert response.status_code == 403
```

Finance is allowed:

```python
assert response.status_code == 200
assert b"Finance Admin Dashboard" in response.data
```

### Test: finance reimbursement flow

The test creates a claim:

```python
claim = ExpenseService.create_expense_claim(employee_id=3, title="Client Dinner")
ExpenseService.add_expense_item(
    claim_id=claim.id, category="Meals", amount=250.00, expense_date=date(2026, 8, 15)
)
ExpenseService.submit_claim(claim.id)
```

Then manager approves it:

```python
ExpenseService.approve_or_reject_claim(
    claim_id=claim.id, approver_user=mgr_user, action="Approved", comments="Approved by manager"
)
```

Finance reimburses:

```python
response = client.post(f"/finance/claim/{claim_id}/reimburse", data={
    "transaction_reference": "TXN-FIN-12345"
}, follow_redirects=True)
```

Final checks:

```python
assert claim_db.status == "Verified"
assert reimb.status == "Processed"
assert reimb.transaction_reference == "TXN-FIN-12345"
assert float(reimb.amount_paid) == 250.00
```

### Explanation

This verifies the complete finance step:

- Approved claim becomes `Verified`.
- Reimbursement row is created.
- Payment amount equals claim total.
- Approval history records finance verification.

### Test: receipt download

```python
tmp_file = tempfile.NamedTemporaryFile(
    suffix=".pdf",
    dir=app.config["UPLOAD_FOLDER"],
    delete=False
)
tmp_file.write(b"Fake PDF content")
```

### Explanation

The test creates a temporary fake PDF receipt file.

Then it links the file to a claim:

```python
receipt = ExpenseService.attach_receipt(
    claim_id=claim.id,
    filename=filename,
    filepath=filepath,
    file_type="application/pdf",
    file_size=16
)
```

Download check:

```python
with client.get(f"/finance/receipt/{receipt_id}/download") as dl:
    assert dl.status_code == 200
    assert dl.data == b"Fake PDF content"
```

This proves finance can download supporting receipt documents.

## 8. `test_analytics.py`

### Purpose

This file tests analytics/reporting features:

- Analytics access control.
- Summary statistics.
- Spend by category.
- Spend by department.
- Monthly trend.
- Search and filters.
- Analytics UI page.
- Analytics JSON API endpoints.

### Setup code

```python
AuthService.register_user(
    email="admin@company.com", password="pass", role="Admin",
    first_name="Super", last_name="Admin", department="IT", designation="Admin"
)
AuthService.register_user(
    email="finance@company.com", password="pass", role="Finance",
    first_name="Fin", last_name="User", department="Finance", designation="Accountant"
)
AuthService.register_user(
    email="mgr@company.com", password="pass", role="Manager",
    first_name="Manager", last_name="One", department="Sales", designation="Manager"
)
```

### Explanation

The test creates Admin, Finance, Manager, and Employee users. Analytics should only be accessible to Admin and Finance.

### Test: analytics access control

```python
def test_analytics_blocked_for_employee(app, init_db, client):
    login(client, "emp@company.com")
    r = client.get("/analytics/")
    assert r.status_code == 403
```

Manager is also blocked:

```python
assert r.status_code == 403
```

Admin is allowed:

```python
assert r.status_code == 200
assert b"Analytics Dashboard" in r.data
```

Finance is also allowed:

```python
assert r.status_code == 200
assert b"Analytics Dashboard" in r.data
```

### Test: summary stats

```python
stats = AnalyticsService.summary_stats()
assert stats["total_claims"] == 0
assert stats["total_spend"] == 0.0
assert stats["total_travel_requests"] == 0
```

### Explanation

This verifies that empty analytics returns zero values.

With data:

```python
claim = ExpenseService.create_expense_claim(employee_id=emp.id, title="Test Claim")
ExpenseService.add_expense_item(claim.id, "Meals", 300.0, date(2026, 8, 1))

stats = AnalyticsService.summary_stats()
assert stats["total_claims"] == 1
assert stats["Draft"] == 1
```

This verifies that summary counts draft claims correctly.

### Test: spend by category

```python
result = AnalyticsService.spend_by_category()
categories = [r["category"] for r in result]
assert "Flight" in categories or "Meals" in categories
```

### Explanation

This checks that approved claim items are grouped by category.

### Test: spend by department

```python
result = AnalyticsService.spend_by_department()
depts = [r["department"] for r in result]
assert "Sales" in depts
```

### Explanation

This verifies department-wise spending analytics.

### Test: search by title

```python
ExpenseService.create_expense_claim(emp.id, "Singapore Business Trip")
ExpenseService.create_expense_claim(emp.id, "Local Office Supplies")

results = AnalyticsService.search_claims(query_str="Singapore")
assert len(results) == 1
assert results[0].title == "Singapore Business Trip"
```

### Explanation

This verifies claim search by title.

### Test: search by claim ID

```python
results = AnalyticsService.search_claims(query_str=str(claim.id))
assert any(r.id == claim.id for r in results)
```

### Explanation

This verifies that numeric search can match claim IDs.

### Test: search by status

```python
submitted = AnalyticsService.search_claims(status="Submitted")
draft = AnalyticsService.search_claims(status="Draft")
assert all(c.status == "Submitted" for c in submitted)
assert all(c.status == "Draft" for c in draft)
```

### Explanation

This verifies filtering claims by status.

### Test: search by category

```python
meals = AnalyticsService.search_claims(category="Meals")
assert all(
    any(item.category == "Meals" for item in c.items.all())
    for c in meals
)
```

### Explanation

This verifies filtering claims by line-item category.

### Test: analytics API endpoints

```python
r = client.get("/analytics/api/summary")
assert r.status_code == 200
data = r.get_json()
assert "total_claims" in data
assert "total_spend" in data
```

Other endpoints tested:

- `/analytics/api/by-category`
- `/analytics/api/by-department`
- `/analytics/api/monthly-trend`

These should return JSON lists or summary dictionaries.

## Quick Summary of All Test Files

| File | What it tests |
| --- | --- |
| `test_basic.py` | Home redirect and login page load |
| `test_auth.py` | Registration, login, basic RBAC |
| `test_expense.py` | Employee expense claim creation, items, receipts, submission lock |
| `test_database.py` | Model/service workflows, relationships, travel approval, reimbursement |
| `test_admin.py` | Admin access, user management, policy management, policy enforcement |
| `test_manager.py` | Manager dashboard, subordinate filtering, approve/reject workflows |
| `test_finance.py` | Finance access, reimbursement, receipt download |
| `test_analytics.py` | Analytics access, reports, search, JSON APIs |

## Question: If I delete `test_analytics.md`, will there be an error?

There is no `test_analytics.md` file in the current `tests` folder. The actual file is:

```text
tests/test_analytics.py
```

So if you delete a file named `test_analytics.md`, there will be no effect because that file does not exist.

## Question: If I delete `test_analytics.py`, will there be an error?

If you simply run:

```bash
pytest
```

then deleting `tests/test_analytics.py` will usually not cause an import error, because no other test file imports it. Pytest will just run fewer tests.

But there are important consequences:

- Analytics features will no longer be tested.
- Bugs in `/analytics/`, `/analytics/search`, and analytics API endpoints may go unnoticed.
- Access control for analytics will no longer be verified.
- Search/filter/reporting functions in `AnalyticsService` will lose direct test coverage.

Also, if you run a command that specifically targets the deleted file:

```bash
pytest tests/test_analytics.py
```

then pytest will show an error because the file no longer exists.

Best answer in interview:

"Deleting `test_analytics.py` will not break the application runtime, and normal pytest discovery may still run the remaining tests. But it will reduce test coverage because analytics access control, summary stats, search filters, and JSON API endpoints will no longer be verified. If pytest is run specifically against that deleted file, then pytest will report that the file is missing."

