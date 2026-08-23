# Persistent Final Interview Preparation

## 1. TOP 40 - MOST LIKELY QUESTIONS

### Q1. Explain your project in short.

**Answer:**  
My project is a Flask-based Corporate Expense Management System. Employees can create travel requests, submit expense claims with line items and receipts, managers approve or reject those requests, finance verifies approved claims and processes reimbursements, and admins manage users and expense policies.

**Code:**  
`run.py`, `app/__init__.py`, `app/controllers/*`, `app/services/*`

**Follow-up:**  
Why is it realistic?  
Because it models a real multi-level corporate approval workflow: employee submission, manager approval, finance verification, and admin policy control.

### Q2. What is the application entry point?

**Answer:**  
The entry point is `run.py`. It imports `create_app()` from `app` and starts the Flask development server.

**Code:**  
`run.py`

**Follow-up:**  
Why not create the Flask app directly in `run.py`?  
Using `create_app()` keeps initialization reusable for development, testing, and different configurations.

### Q3. What does `create_app()` do?

**Answer:**  
`create_app()` creates the Flask app, loads configuration, initializes SQLAlchemy and JWT, registers all blueprints, configures JWT behavior, creates database tables, and returns the app object.

**Code:**  
`app/__init__.py:create_app`

**Follow-up:**  
What design pattern is this?  
It is the Flask application factory pattern.

### Q4. Why did you use Flask?

**Answer:**  
I used Flask because it is lightweight and flexible. This project needed custom workflows, role-based routing, Jinja2 pages, service classes, DAO classes, SQLAlchemy models, and JWT authentication. Flask allowed me to structure those layers clearly.

**Code:**  
`app/__init__.py`

**Follow-up:**  
Why not Django?  
Django is powerful but heavier and more opinionated. Flask was enough for this project and gave more control over architecture.

### Q5. Explain your architecture.

**Answer:**  
The project is divided into models, DAOs, services, controllers, templates, and static files. Models define database tables. DAOs handle database queries. Services contain business rules. Controllers handle routes. Templates render UI pages.

**Code:**  
`app/models`, `app/dao`, `app/services`, `app/controllers`, `app/templates`

**Follow-up:**  
What is the advantage?  
It improves maintainability because each layer has one clear responsibility.

### Q6. What is the role of controllers?

**Answer:**  
Controllers define Flask routes and handle request/response logic. They read form data, call service methods, flash messages, redirect users, and render templates.

**Code:**  
`app/controllers/expense_controller.py`, `travel_controller.py`, `manager_controller.py`

**Follow-up:**  
Should controllers contain business rules?  
Only minimal validation. Core business rules should stay in the service layer.

### Q7. What is the role of the service layer?

**Answer:**  
The service layer contains business logic like creating claims, validating policy limits, submitting claims, approving requests, and reimbursing claims.

**Code:**  
`app/services/expense_service.py`, `travel_service.py`, `admin_service.py`

**Follow-up:**  
Why not put this logic in controllers?  
Services make the logic reusable and easier to test.

### Q8. What is the role of the DAO layer?

**Answer:**  
The DAO layer centralizes database access. It provides reusable methods like `get_by_id()`, `get_all()`, `get_by_employee_id()`, and manager-specific pending queries.

**Code:**  
`app/dao/base_dao.py`, `expense_dao.py`, `travel_dao.py`, `user_dao.py`

**Follow-up:**  
What benefit does DAO provide?  
It avoids repeated query logic inside route functions.

### Q9. How is authentication implemented?

**Answer:**  
Users log in with email and password. Passwords are hashed using Werkzeug. On successful login, the app creates a JWT token using Flask-JWT-Extended and stores it in cookies for browser pages or returns it as JSON for API requests.

**Code:**  
`app/services/auth_service.py`, `app/controllers/auth_controller.py`

**Follow-up:**  
Where is password checked?  
In `AuthService.authenticate_user()`.

### Q10. How are passwords secured?

**Answer:**  
Passwords are not stored directly. During registration, `generate_password_hash()` creates a secure hash. During login, `check_password_hash()` verifies the entered password.

**Code:**  
`app/services/auth_service.py`

**Follow-up:**  
Why is hashing important?  
If the database is exposed, attackers cannot directly read user passwords.

### Q11. What is JWT used for?

**Answer:**  
JWT is used to identify authenticated users across requests. The token stores the user identity and role claim. Protected routes verify this token before allowing access.

**Code:**  
`app/__init__.py`, `app/controllers/auth_controller.py`, `app/controllers/auth_helper.py`

**Follow-up:**  
What is stored as JWT identity?  
The user's ID as a string.

### Q12. How is `current_user` implemented?

**Answer:**  
`current_user` is a `LocalProxy`. It tries to verify the JWT optionally and returns the loaded user. If no valid user exists, it returns an `AnonymousUser`.

**Code:**  
`app/controllers/auth_helper.py`

**Follow-up:**  
Why use `LocalProxy`?  
It gives request-specific user access like a global variable without actually being global.

### Q13. How is role-based access control implemented?

**Answer:**  
RBAC is implemented using the `role_required()` decorator. It checks if the current user's role is in the allowed roles before running the route.

**Code:**  
`app/controllers/auth_decorator.py`

**Follow-up:**  
What happens if role is not allowed?  
The app renders `unauthorized.html` with HTTP 403.

### Q14. What roles exist in the system?

**Answer:**  
The roles are `Employee`, `Manager`, `Finance`, and `Admin`. Each role has different permissions and dashboards.

**Code:**  
`app/models/user.py`, `app/controllers/admin_controller.py`

**Follow-up:**  
Where is role stored?  
In the `role` column of the `users` table.

### Q15. Explain the `User` and `Employee` relationship.

**Answer:**  
`User` stores login and role data. `Employee` stores profile data like name, department, designation, phone, and manager. They have a one-to-one relationship.

**Code:**  
`app/models/user.py:User`, `app/models/user.py:Employee`

**Follow-up:**  
Why separate them?  
Authentication data and employee profile data are different concerns.

### Q16. How is the manager-subordinate relationship modeled?

**Answer:**  
The `Employee` table has a self-referencing `manager_id` foreign key pointing to another employee's ID.

**Code:**  
`app/models/user.py:Employee.manager_id`

**Follow-up:**  
How does a manager get subordinate claims?  
DAO queries filter employees where `Employee.manager_id` equals the manager's employee ID.

### Q17. Explain the expense claim workflow.

**Answer:**  
An employee creates a claim in `Draft`, adds items and receipts, then submits it. The status becomes `Submitted`. A manager approves or rejects it. If approved, finance verifies it and creates a reimbursement.

**Code:**  
`app/services/expense_service.py`

**Follow-up:**  
Why use statuses?  
Statuses control what actions are allowed at each workflow step.

### Q18. Why is there a `Draft` status?

**Answer:**  
Draft allows employees to build a claim gradually by adding multiple items and receipts before final submission.

**Code:**  
`ExpenseService.create_expense_claim`

**Follow-up:**  
Can a draft be reimbursed?  
No. Only manager-approved claims can be reimbursed.

### Q19. Why are submitted claims locked?

**Answer:**  
After submission, the claim enters the approval workflow. Locking prevents employees from changing amounts or receipts after the manager starts reviewing it.

**Code:**  
`ExpenseService.add_expense_item`, `expense_controller.delete_item`, `upload_receipt`

**Follow-up:**  
What error is raised?  
`ValueError("Cannot add items to a submitted or processed claim")`.

### Q20. How are policy limits enforced?

**Answer:**  
When adding an item, the service fetches the category policy. If the amount is greater than `max_limit_per_expense`, it raises a `ValueError`.

**Code:**  
`ExpenseService.add_expense_item`, `ExpensePolicyDAO.get_by_category`

**Follow-up:**  
Where are policies managed?  
In admin routes and `AdminService`.

### Q21. What is `ExpenseClaim` vs `ExpenseItem`?

**Answer:**  
`ExpenseClaim` is the main reimbursement request. `ExpenseItem` is a line item inside the claim, such as meals, transportation, flight, or accommodation.

**Code:**  
`app/models/expense.py`

**Follow-up:**  
What relationship exists?  
One claim has many items.

### Q22. Why store `total_amount` in `ExpenseClaim`?

**Answer:**  
It makes dashboards and finance pages faster because totals do not need to be recalculated every time. The app updates it after item changes.

**Code:**  
`ExpenseClaim.update_total_amount`

**Follow-up:**  
What is the risk?  
Denormalized data must be kept in sync.

### Q23. How are receipts uploaded?

**Answer:**  
Employees upload receipt files while the claim is in draft status. The controller checks extension, sanitizes filename, saves the file, records file metadata, and links it to the claim.

**Code:**  
`expense_controller.upload_receipt`, `ExpenseService.attach_receipt`

**Follow-up:**  
Which extensions are allowed?  
`pdf`, `png`, `jpg`, and `jpeg`.

### Q24. What is `secure_filename()` used for?

**Answer:**  
It sanitizes uploaded filenames before saving them to avoid unsafe path characters or path traversal style filenames.

**Code:**  
`app/controllers/expense_controller.py`

**Follow-up:**  
Is this enough for production?  
No. Production should also use unique filenames, content validation, and store files outside public static paths.

### Q25. How does finance download receipts?

**Answer:**  
Finance users access `/finance/receipt/<receipt_id>/download`. The route is protected with login and finance role checks, verifies the file exists, and sends it using `send_file()`.

**Code:**  
`finance_controller.download_receipt`

**Follow-up:**  
Can employees download through this route?  
No, it requires the `Finance` role.

### Q26. How does reimbursement work?

**Answer:**  
Finance can reimburse only an `Approved` claim. The service changes claim status to `Verified`, creates a `Reimbursement` record, and logs an `ApprovalHistory` action.

**Code:**  
`ExpenseService.verify_and_reimburse`

**Follow-up:**  
What amount is reimbursed?  
The claim's `total_amount`.

### Q27. What is `ApprovalHistory`?

**Answer:**  
It is an audit table that records approval, rejection, and verification actions for travel requests and expense claims.

**Code:**  
`app/models/history.py:ApprovalHistory`

**Follow-up:**  
Why is it needed?  
Corporate approval systems need traceability.

### Q28. What is the purpose of `ExpensePolicy`?

**Answer:**  
It stores category-wise limits, such as maximum amount for meals or accommodation. It is used to validate employee expense items.

**Code:**  
`app/models/policy.py`, `app/services/policy_service.py`

**Follow-up:**  
Who manages policies?  
Admin users.

### Q29. How are manager pending requests fetched?

**Answer:**  
The DAO joins request records with `Employee` and filters by `Employee.manager_id`. This ensures managers only see their own subordinates' pending work.

**Code:**  
`TravelDAO.get_pending_by_manager_id`, `ExpenseClaimDAO.get_pending_by_manager_id`

**Follow-up:**  
Why is this important?  
It enforces data ownership and approval hierarchy.

### Q30. How does the finance dashboard filter claims?

**Answer:**  
It allows only `Approved` and `Verified` claims. If an invalid status filter is provided, it ignores it.

**Code:**  
`finance_controller.dashboard`, `ExpenseClaimDAO.get_all_for_finance`

**Follow-up:**  
Why not show `Submitted` claims?  
They are waiting for manager approval and are not ready for finance.

### Q31. How are analytics implemented?

**Answer:**  
Analytics use SQLAlchemy aggregate queries for spend by category, status, department, monthly trend, and summary stats. Only Admin and Finance users can access them.

**Code:**  
`app/services/analytics_service.py`, `app/controllers/analytics_controller.py`

**Follow-up:**  
What SQL concepts are used?  
Joins, grouping, sums, counts, filters, and ordering.

### Q32. What is `TestingConfig` used for?

**Answer:**  
`TestingConfig` switches the database to in-memory SQLite and enables testing mode. This keeps tests isolated from the real MySQL database.

**Code:**  
`app/config.py:TestingConfig`

**Follow-up:**  
Why not use MySQL in tests?  
In-memory SQLite is faster and simpler for automated unit/integration tests.

### Q33. What tests are implemented?

**Answer:**  
Tests cover basic routes, authentication, role-based access, user/admin management, policy management, expense creation, receipt upload, policy enforcement, travel workflow, and reimbursement.

**Code:**  
`tests/test_basic.py`, `test_auth.py`, `test_expense.py`, `test_admin.py`, `test_database.py`

**Follow-up:**  
What important test would you add?  
A test for unauthorized receipt download and inactive user login.

### Q34. What happens when a JWT is expired?

**Answer:**  
For API requests, the app returns JSON with 401. For browser requests, it flashes a message, clears JWT cookies, and redirects to login.

**Code:**  
`app/__init__.py:expired_token_callback`

**Follow-up:**  
How does the app detect API request?  
Using `is_api_request()`.

### Q35. What is the difference between 401 and 403?

**Answer:**  
401 means the user is not authenticated or token is missing/invalid. 403 means the user is authenticated but not authorized for that role or resource.

**Code:**  
`auth_helper.login_required`, `auth_decorator.role_required`

**Follow-up:**  
Where is 403 used?  
Unauthorized role access and ownership checks.

### Q36. How does admin manage users?

**Answer:**  
Admin can view users, update roles, activate/deactivate users, and delete users. The app prevents an admin from deactivating or deleting their own account.

**Code:**  
`app/controllers/admin_controller.py`, `app/services/admin_service.py`

**Follow-up:**  
Is inactive user login blocked?  
Not implemented in the current codebase.

### Q37. How does admin manage policies?

**Answer:**  
Admin can create, update, and delete expense policies. The service validates that category is not empty and limit is a positive number.

**Code:**  
`AdminService.create_or_update_policy`

**Follow-up:**  
What happens if a policy already exists?  
The existing policy is updated.

### Q38. What database relationships are most important?

**Answer:**  
Important relationships are User-Employee one-to-one, Employee self-reference for manager, Employee-TravelRequest one-to-many, Employee-ExpenseClaim one-to-many, ExpenseClaim-ExpenseItem one-to-many, ExpenseClaim-Receipt one-to-many, and ExpenseClaim-Reimbursement one-to-many.

**Code:**  
`app/models/user.py`, `expense.py`, `travel.py`, `history.py`

**Follow-up:**  
Why use relationships?  
They make related data easier to access through SQLAlchemy objects.

### Q39. How would you improve production security?

**Answer:**  
I would remove default secrets/passwords, enable CSRF protection for cookie JWT flows, store uploads outside `static`, generate unique filenames, validate file content, enforce HTTPS, add rate limiting, check `is_active` during login, and add stronger audit logs.

**Code:**  
`app/config.py`, `expense_controller.py`, `auth_service.py`

**Follow-up:**  
What is the most urgent improvement?  
Move secrets and database passwords fully to environment variables and remove defaults.

### Q40. What was the hardest part of this project?

**Answer:**  
The hardest part was coordinating the workflow between roles while keeping permissions correct: employee ownership, manager-subordinate filtering, finance-only reimbursement, and admin-only policy management.

**Code:**  
`manager_controller.py`, `finance_controller.py`, `auth_decorator.py`

**Follow-up:**  
How did you solve it?  
By combining JWT authentication, role decorators, ownership checks, status checks, and service-level validations.

## 2. PROJECT + ARCHITECTURE

### Q1. What is the project objective?

**Answer:**  
To automate corporate travel and expense reimbursement with employee submissions, manager approval, finance verification, and admin policy management.

### Q2. What are the major modules?

**Answer:**  
Authentication, travel requests, expense claims, manager dashboard, finance dashboard, admin panel, analytics, models, DAOs, services, and tests.

### Q3. What does `run.py` do?

**Answer:**  
It creates the Flask application using `create_app()` and starts it with `app.run(debug=True)`.

### Q4. Why use an application factory?

**Answer:**  
It allows the same application to be created with different configurations, especially `Config` for normal use and `TestingConfig` for tests.

### Q5. How are blueprints used?

**Answer:**  
Each functional area has a blueprint: auth, travel, expense, manager, finance, admin, and analytics. These are registered inside `create_app()`.

### Q6. Explain a typical request flow.

**Answer:**  
For adding an expense item, the browser sends a POST request to the expense controller. The controller checks ownership and extracts form data. The service validates claim status and policy limit. The DAO/model stores data. The controller redirects back with a flash message.

### Q7. Why is the service layer important?

**Answer:**  
Because workflows like approval, submission, policy checks, and reimbursement should not depend on a specific route. The service layer keeps them reusable and testable.

### Q8. Is this project API-based or template-based?

**Answer:**  
Mostly template-based using Jinja2. Login also supports JSON, and analytics exposes some JSON API endpoints.

## 3. JWT + AUTHENTICATION

### Q1. Explain the complete login flow.

**Answer:**  
The `/login` route accepts email and password. `AuthService.authenticate_user()` checks the password hash. If valid, `create_access_token()` creates a JWT with user ID and role. Browser users get the token in cookies; JSON clients receive it in the response.

**Code:**  
`auth_controller.login`, `auth_service.authenticate_user`

### Q2. Where is the password hash created?

**Answer:**  
In `AuthService.register_user()` using `generate_password_hash(password)`.

**Code:**  
`app/services/auth_service.py`

### Q3. Where is the password verified?

**Answer:**  
In `AuthService.authenticate_user()` using `check_password_hash(user.password_hash, password)`.

**Code:**  
`app/services/auth_service.py`

### Q4. What is the JWT identity?

**Answer:**  
The JWT identity is `str(user.id)`. Later, `user_lookup_callback()` converts it back to integer and loads the user using `UserDAO.get_by_id()`.

**Code:**  
`auth_controller.login`, `app/__init__.py:user_lookup_callback`

### Q5. What JWT claims are added?

**Answer:**  
The app adds `{"role": user.role}` as additional claims.

**Code:**  
`auth_controller.login`

### Q6. Is `jwt_required` used directly?

**Answer:**  
Not implemented in the current codebase. Instead, the project uses a custom `login_required` decorator that calls `verify_jwt_in_request()`.

**Code:**  
`app/controllers/auth_helper.py`

### Q7. How do JWT cookies work here?

**Answer:**  
`JWT_TOKEN_LOCATION` is set to `["headers", "cookies"]`. For normal browser login, `set_access_cookies()` stores the access token in cookies, so protected page requests automatically include it.

**Code:**  
`app/__init__.py`, `auth_controller.login`

### Q8. How does Authorization header login work?

**Answer:**  
For JSON login, the server returns `{"access_token": token}`. An API client can send it in the `Authorization` header for protected requests.

**Code:**  
`auth_controller.login`

### Q9. What happens if token is missing?

**Answer:**  
For API requests, JSON 401 is returned. For browser requests, the user is redirected to `/login` with a flash message.

**Code:**  
`app/__init__.py:missing_token_callback`

### Q10. What happens if token is invalid or expired?

**Answer:**  
Invalid and expired token handlers return JSON errors for API requests. For browser requests, they redirect to login and clear JWT cookies where needed.

**Code:**  
`invalid_token_callback`, `expired_token_callback`

## 4. RBAC / AUTHORIZATION

### Q1. Authentication vs authorization?

**Answer:**  
Authentication checks who the user is. Authorization checks what that authenticated user is allowed to do.

### Q2. How does `role_required()` work?

**Answer:**  
It checks `current_user.is_authenticated` and verifies whether `current_user.role` is in the allowed roles passed to the decorator.

**Code:**  
`app/controllers/auth_decorator.py`

### Q3. What can an Employee do?

**Answer:**  
Employees can create travel requests, create draft expense claims, add items, upload receipts, submit claims, and view their own records.

### Q4. What can a Manager do?

**Answer:**  
Managers can view pending travel and expense claims from their subordinates and approve or reject them.

**Code:**  
`manager_controller.py`

### Q5. What can Finance do?

**Answer:**  
Finance can view approved and verified claims, download receipts, verify approved claims, and process reimbursements.

**Code:**  
`finance_controller.py`

### Q6. What can Admin do?

**Answer:**  
Admins can manage users, update roles, activate/deactivate users, delete users, and manage expense policies.

**Code:**  
`admin_controller.py`

## 5. PYTHON

### Q1. Where is OOP used?

**Answer:**  
OOP is used in SQLAlchemy model classes, DAO classes, and service classes. Examples are `User`, `ExpenseClaim`, `ExpenseService`, and `BaseDAO`.

### Q2. Why are service methods static?

**Answer:**  
They do not need object-specific state. They work directly with passed arguments and database models, so `@staticmethod` is suitable.

### Q3. What are decorators in this project?

**Answer:**  
Decorators wrap route functions to add authentication and authorization checks. Examples are `@login_required` and `@role_required`.

### Q4. Why use `functools.wraps`?

**Answer:**  
`wraps` preserves the original route function's metadata, which is important for Flask routing and debugging.

**Code:**  
`auth_helper.py`, `auth_decorator.py`

### Q5. Where is exception handling used?

**Answer:**  
Controllers catch service exceptions like `ValueError` and show flash messages instead of crashing the app.

### Q6. Where are sets used?

**Answer:**  
`ALLOWED_EXTENSIONS` is a set used for fast membership checking of allowed receipt file extensions.

**Code:**  
`expense_controller.py`

### Q7. What is `*args` and `**kwargs` used for?

**Answer:**  
They are used inside decorators so the wrapper can forward any route parameters to the original route function.

**Code:**  
`auth_helper.login_required`, `auth_decorator.role_required`

### Q8. What is `LocalProxy`?

**Answer:**  
`LocalProxy` provides request-local access to the current user. It behaves like a global variable, but the value is resolved per request.

**Code:**  
`auth_helper.py`

## 6. SQL + SQLALCHEMY + DATABASE

### Q1. What ORM is used?

**Answer:**  
The project uses Flask-SQLAlchemy, which wraps SQLAlchemy for Flask applications.

### Q2. What is the main database configuration?

**Answer:**  
By default, the app uses MySQL with PyMySQL. In tests, it uses in-memory SQLite through `TestingConfig`.

**Code:**  
`app/config.py`

### Q3. What is a primary key example?

**Answer:**  
Every model has an `id` primary key, such as `User.id`, `Employee.id`, and `ExpenseClaim.id`.

### Q4. What is a foreign key example?

**Answer:**  
`ExpenseClaim.employee_id` references `employees.id`, and `ExpenseItem.expense_claim_id` references `expense_claims.id`.

### Q5. Explain the User-Employee relationship.

**Answer:**  
It is one-to-one. `User.employee` uses `uselist=False`, and `Employee.user_id` references `users.id`.

### Q6. Explain Employee manager self-reference.

**Answer:**  
`Employee.manager_id` points to another row in the same `employees` table. This models reporting hierarchy.

### Q7. Explain ExpenseClaim and ExpenseItem relation.

**Answer:**  
One claim can have many items. Items are deleted automatically if the claim is deleted because of cascade behavior.

### Q8. What does `filter_by()` do?

**Answer:**  
It filters by simple keyword equality, like `filter_by(email=email)`.

**Code:**  
`UserDAO.get_by_email`

### Q9. What does `filter()` do?

**Answer:**  
It supports more complex SQLAlchemy expressions, such as joins, comparisons, and `in_()`.

**Code:**  
`ExpenseClaimDAO.get_all_for_finance`

### Q10. Where are joins used?

**Answer:**  
Joins are used to fetch manager-specific pending requests and analytics grouped by department/category.

**Code:**  
`travel_dao.py`, `expense_dao.py`, `analytics_service.py`

### Q11. Where are commits used?

**Answer:**  
Commits are used after saving, deleting, updating statuses, adding receipts, creating policies, and reimbursement processing.

**Code:**  
`BaseDAO.save`, `ExpenseService`, `AdminService`

### Q12. Is rollback implemented?

**Answer:**  
Not implemented in the current codebase. A production improvement would be to add transaction handling with rollback on exceptions.

### SQL Coding Q13. Second highest salary.

**Solution:**
```sql
SELECT MAX(salary) AS second_highest_salary
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

**Explanation:**  
First find the maximum salary, then find the maximum below it.

### SQL Coding Q14. Find duplicate emails.

**Solution:**
```sql
SELECT email, COUNT(*) AS count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Explanation:**  
`GROUP BY` groups same emails and `HAVING` filters duplicate groups.

### SQL Coding Q15. JOIN users and employees.

**Solution:**
```sql
SELECT u.email, e.first_name, e.last_name, e.department
FROM users u
JOIN employees e ON e.user_id = u.id;
```

**Explanation:**  
This combines login data from `users` with profile data from `employees`.

### SQL Coding Q16. Total spend by department.

**Solution:**
```sql
SELECT e.department, SUM(c.total_amount) AS total_spend
FROM employees e
JOIN expense_claims c ON c.employee_id = e.id
GROUP BY e.department;
```

**Explanation:**  
This is similar to the analytics department spend query.

### SQL Coding Q17. Departments with spend above 10000.

**Solution:**
```sql
SELECT e.department, SUM(c.total_amount) AS total_spend
FROM employees e
JOIN expense_claims c ON c.employee_id = e.id
GROUP BY e.department
HAVING SUM(c.total_amount) > 10000;
```

**Explanation:**  
`HAVING` filters aggregated results.

### SQL Coding Q18. ROW_NUMBER example.

**Solution:**
```sql
SELECT employee_id, total_amount,
       ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY total_amount DESC) AS rn
FROM expense_claims;
```

**Explanation:**  
It numbers claims for each employee by amount.

### SQL Coding Q19. RANK vs DENSE_RANK.

**Solution:**
```sql
SELECT employee_id, total_amount,
       RANK() OVER (ORDER BY total_amount DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY total_amount DESC) AS dense_rnk
FROM expense_claims;
```

**Explanation:**  
`RANK` leaves gaps after ties. `DENSE_RANK` does not.

## 7. BUSINESS WORKFLOW

### Q1. Explain employee workflow.

**Answer:**  
Employee creates a draft claim, adds expense items, uploads receipts, and submits it for manager approval.

### Q2. Explain manager workflow.

**Answer:**  
Manager dashboard shows pending travel requests and submitted claims from subordinates. Manager can approve or reject with comments.

### Q3. Explain finance workflow.

**Answer:**  
Finance sees manager-approved claims, checks receipt documents, verifies the claim, and creates a reimbursement record.

### Q4. Explain admin workflow.

**Answer:**  
Admin manages users, roles, active status, deletion, and expense policies.

### Q5. What happens if invalid approval action is sent?

**Answer:**  
The service checks allowed actions. If action is not `Approved` or `Rejected`, it raises `ValueError("Invalid action")`.

### Q6. Why can finance process only approved claims?

**Answer:**  
Because finance reimbursement should happen only after managerial validation.

### Q7. What happens during reimbursement?

**Answer:**  
Claim status becomes `Verified`, reimbursement status becomes `Processed`, payment date is set, transaction reference is stored, and history is recorded.

## 8. SECURITY

### Q1. What security is implemented for passwords?

**Answer:**  
Passwords are hashed using Werkzeug before storing and verified using hash comparison during login.

### Q2. What security is implemented for routes?

**Answer:**  
Routes use JWT verification through `login_required`, role checks through `role_required`, and ownership checks inside controllers.

### Q3. What security exists for file uploads?

**Answer:**  
Allowed extensions are restricted, filenames are sanitized, upload size is limited, and only claim owners can upload before submission.

### Q4. What is `MAX_CONTENT_LENGTH`?

**Answer:**  
It limits upload size to 16 MB.

**Code:**  
`app/config.py`

### Q5. Are environment variables used?

**Answer:**  
Yes, configuration loads `.env` values using `load_dotenv()`. However, default secrets and database passwords exist in the code and should be removed for production.

### Q6. Is CSRF protection implemented?

**Answer:**  
Flask-WTF is installed, but JWT cookie CSRF protection is disabled with `JWT_COOKIE_CSRF_PROTECT = False`. Stronger CSRF protection should be enabled for production.

### Q7. How would you improve this project for production?

**Answer:**  
Use strong environment-only secrets, enable CSRF, use HTTPS, rate limit login, check inactive users at login, validate file content, store files outside `static`, use unique filenames, add rollback handling, and improve audit logs.

## 9. CODEBASE / CODE-READING QUESTIONS

### Q1. What does `create_app()` do?

**Answer:**  
It initializes the Flask application, extensions, JWT callbacks, blueprints, and database tables.

**Why:**  
It centralizes app setup and supports testing with different configs.

**Follow-up:**  
Why use app factory?  
For flexible app creation and testing.

### Q2. What does `is_api_request()` do?

**Answer:**  
It detects whether a request expects API behavior by checking Authorization header, JSON body, or JSON Accept header.

**Why:**  
JWT errors should return JSON for APIs and redirects for browser pages.

**Follow-up:**  
Where is it used?  
JWT error handlers in `app/__init__.py`.

### Q3. What does `user_lookup_callback()` do?

**Answer:**  
It loads the current user from the JWT subject using `UserDAO.get_by_id()`.

**Why:**  
It allows `get_current_user()` and `current_user` to return a real `User` object.

**Follow-up:**  
What is `sub`?  
The JWT subject, which stores user identity.

### Q4. What does `AuthService.register_user()` do?

**Answer:**  
It checks duplicate email, hashes password, creates a `User`, flushes to get user ID, creates an `Employee`, and commits.

**Why:**  
Registration must create both login and profile records.

**Follow-up:**  
Why use `flush()`?  
To get `new_user.id` before committing.

### Q5. What does `AuthService.authenticate_user()` do?

**Answer:**  
It finds the user by email and validates the password hash.

**Why:**  
It keeps login verification logic outside the controller.

**Follow-up:**  
Does it check `is_active`?  
Not implemented in the current codebase.

### Q6. What does `login_required()` do?

**Answer:**  
It verifies that a valid JWT is present before allowing the route to execute.

**Why:**  
Protected pages should not be accessible anonymously.

**Follow-up:**  
Which function verifies JWT?  
`verify_jwt_in_request()`.

### Q7. What does `role_required()` do?

**Answer:**  
It restricts a route to specific user roles.

**Why:**  
Manager, Finance, and Admin should access different features.

**Follow-up:**  
What if user has wrong role?  
It returns 403 with unauthorized template.

### Q8. What does `ExpenseService.add_expense_item()` do?

**Answer:**  
It checks claim exists, ensures claim is draft, checks category policy limit, creates an item, and updates total amount.

**Why:**  
Expense item creation has important business rules.

**Follow-up:**  
Can it add item to submitted claim?  
No.

### Q9. What does `ExpenseService.submit_claim()` do?

**Answer:**  
It validates that the claim exists, is in draft, has positive amount, and then changes status to `Submitted`.

**Why:**  
Submission starts manager approval workflow.

**Follow-up:**  
Can empty claim be submitted?  
No.

### Q10. What does `verify_and_reimburse()` do?

**Answer:**  
It verifies approved claims, creates reimbursement, logs history, and changes status to `Verified`.

**Why:**  
It represents the finance completion step.

**Follow-up:**  
What status is required?  
`Approved`.

### Q11. What does `TravelService.create_travel_request()` do?

**Answer:**  
It validates dates and creates a pending travel request.

**Why:**  
Employees need manager approval before business travel.

**Follow-up:**  
What date validation exists?  
Start date must not be after end date.

### Q12. What does `AnalyticsService.search_claims()` do?

**Answer:**  
It searches claims by title/id, status, category, and employee name.

**Why:**  
Finance/Admin need claim filtering and reporting.

**Follow-up:**  
Which SQL concepts are used?  
Joins, filters, `ilike`, and `distinct`.

## 10. LIVE CODING

### Q1. Find duplicates in a list.

**Solution:**
```python
def duplicates(nums):
    seen = set()
    dup = set()
    for n in nums:
        if n in seen:
            dup.add(n)
        else:
            seen.add(n)
    return list(dup)
```

**Short explanation:**  
Track seen numbers and collect repeated ones.

**Complexity:**  
Time O(n), space O(n).

### Q2. Count frequency of characters.

**Solution:**
```python
def frequency(s):
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    return freq
```

**Short explanation:**  
Use a dictionary to count each character.

**Complexity:**  
Time O(n), space O(k).

### Q3. First non-repeating character.

**Solution:**
```python
def first_unique(s):
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    for ch in s:
        if freq[ch] == 1:
            return ch
    return None
```

**Short explanation:**  
Count first, then scan in original order.

**Complexity:**  
Time O(n), space O(k).

### Q4. Check palindrome.

**Solution:**
```python
def is_palindrome(s):
    s = ''.join(ch.lower() for ch in s if ch.isalnum())
    return s == s[::-1]
```

**Short explanation:**  
Normalize string and compare with reverse.

**Complexity:**  
Time O(n), space O(n).

### Q5. Longest common prefix.

**Solution:**
```python
def longest_common_prefix(words):
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
```

**Short explanation:**  
Shrink prefix until every word starts with it.

**Complexity:**  
Time O(n*m), space O(1).

### Q6. Simple Flask GET API.

**Solution:**
```python
@app.get("/api/health")
def health():
    return {"status": "ok"}, 200
```

**Short explanation:**  
Defines a GET endpoint returning JSON.

### Q7. Simple Flask POST API.

**Solution:**
```python
@app.post("/api/claims")
def create_claim():
    data = request.get_json()
    return {"title": data["title"]}, 201
```

**Short explanation:**  
Reads JSON request data and returns a created response.

### Q8. JWT protected endpoint.

**Solution:**
```python
@app.get("/api/profile")
@login_required
def profile():
    return {"user_id": current_user.id, "email": current_user.email}
```

**Short explanation:**  
Uses the project's custom JWT-based `login_required`.

### Q9. Role-protected endpoint.

**Solution:**
```python
@app.get("/api/admin-only")
@login_required
@role_required("Admin")
def admin_only():
    return {"message": "admin access"}
```

**Short explanation:**  
Combines authentication with role authorization.

### Q10. SQL top N claims by amount.

**Solution:**
```sql
SELECT id, title, total_amount
FROM expense_claims
ORDER BY total_amount DESC
LIMIT 5;
```

**Short explanation:**  
Sorts claims by amount and returns top five.

## 11. DEBUGGING / SCENARIO QUESTIONS

### Q1. Flask returns 500.

**Likely cause -> How to debug -> Fix:**  
Unhandled exception -> Check traceback and logs -> Validate inputs and handle service exceptions.

### Q2. Database connection fails.

**Likely cause -> How to debug -> Fix:**  
Wrong MySQL credentials or server not running -> Check `.env`, `Config`, and MySQL service -> Correct credentials/start database.

### Q3. JWT returns 401.

**Likely cause -> How to debug -> Fix:**  
Missing/expired/invalid token -> Check cookies or Authorization header -> Login again or send valid token.

### Q4. User gets 403.

**Likely cause -> How to debug -> Fix:**  
Wrong role or ownership failure -> Check `current_user.role` and resource owner -> Use correct account or fix role assignment.

### Q5. Query returns `None`.

**Likely cause -> How to debug -> Fix:**  
Record does not exist or wrong ID -> Print/query database records -> Validate ID and seed data.

### Q6. Changes are not saved.

**Likely cause -> How to debug -> Fix:**  
Missing `db.session.commit()` -> Check service/DAO method -> Add commit after update.

### Q7. Invalid file upload rejected.

**Likely cause -> How to debug -> Fix:**  
Extension not in `ALLOWED_EXTENSIONS` -> Check filename -> Upload PDF/PNG/JPG/JPEG.

### Q8. Policy limit exceeded.

**Likely cause -> How to debug -> Fix:**  
Amount is greater than category limit -> Check `ExpensePolicy` row -> Reduce amount or admin updates policy.

## 12. HR / PROJECT QUESTIONS

### Q1. Tell me about yourself.

**Answer:**  
I am a Python and Flask learner focused on building practical backend projects. In this project, I built a corporate expense system using Flask, SQLAlchemy, MySQL, JWT authentication, RBAC, file uploads, and automated tests.

### Q2. Explain your project.

**Answer:**  
It is a role-based expense management app. Employees submit travel and expense claims, managers approve them, finance verifies and reimburses them, and admins manage users and policies.

### Q3. What was your contribution?

**Answer:**  
I implemented the main backend structure, models, controllers, service layer, DAO layer, authentication, RBAC, workflows, file upload logic, admin policy management, and tests.

### Q4. What was the hardest part?

**Answer:**  
The hardest part was maintaining correct workflow rules and permissions across four roles.

### Q5. What bug did you face?

**Answer:**  
A common issue was making sure claim totals update correctly after adding or deleting items. I handled it using `ExpenseClaim.update_total_amount()`.

### Q6. Why Flask?

**Answer:**  
Flask gave me flexibility to design my own architecture while still supporting templates, routing, SQLAlchemy, and JWT integration.

### Q7. What did you learn?

**Answer:**  
I learned how to design a layered Flask application, implement JWT authentication, enforce RBAC, model database relationships, handle uploads, and test workflows.

### Q8. How would you scale it?

**Answer:**  
I would add migrations, background jobs for reimbursement emails, cloud storage for receipts, pagination, indexes, better audit logs, role permissions table, and stronger production security.

