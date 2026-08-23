# Corporate Expense Management System - Interview Questions and Answers

## Project Overview and Architecture

1. Can you explain the main objective of your corporate expense management system?

   Answer: The main objective of this project is to build a Flask-based corporate expense management system where employees can create travel requests, submit expense claims, upload receipts, and track reimbursement status. The system also allows managers to approve or reject claims, finance users to verify approved claims and process reimbursements, and admins to manage users and company expense policies.

2. What problem does this project solve for employees, managers, finance admins, and system admins?

   Answer: The project solves the problem of handling business expenses manually through emails, paper receipts, and spreadsheets. Employees get a structured way to submit travel and expense claims. Managers get a dashboard to review only their subordinates' pending requests. Finance users can verify approved claims and download receipts. Admins can manage users, roles, and expense limits from one place.

3. Why did you choose Flask for this project instead of Django or FastAPI?

   Answer: I chose Flask because it is lightweight, flexible, and suitable for building a custom web application with clear layers. Flask does not force a fixed project structure, so I could organize the app into controllers, services, DAOs, and models. Django would provide many built-in features but may be heavier for this project, while FastAPI is more API-focused. Since this project uses Jinja2 templates and server-rendered pages, Flask was a good fit.

4. Can you explain the folder structure of your project, especially the purpose of `controllers`, `services`, `dao`, `models`, `templates`, and `static`?

   Answer: The `controllers` folder contains Flask blueprints and route handlers. The `services` folder contains business logic such as claim submission, approval, reimbursement, and policy validation. The `dao` folder contains database access classes. The `models` folder defines SQLAlchemy database tables. The `templates` folder contains Jinja2 HTML pages. The `static` folder stores CSS files and uploaded receipt files.

5. How does your application follow separation of concerns?

   Answer: The project separates responsibilities into different layers. Controllers handle HTTP requests and responses. Services handle business rules. DAOs handle database queries. Models define database structure. Templates handle presentation. This makes the code easier to understand, test, and maintain because each layer has a clear responsibility.

6. What is the purpose of the `create_app()` function in `app/__init__.py`?

   Answer: The `create_app()` function follows the Flask application factory pattern. It creates the Flask app, loads configuration, initializes SQLAlchemy and JWT, registers blueprints, defines JWT error handlers, and creates database tables. This pattern also makes testing easier because the app can be created with `TestingConfig`.

7. Why did you use Flask blueprints, and how are they organized in your project?

   Answer: I used blueprints to divide the application into modules. For example, authentication routes are in `auth_bp`, travel routes are in `travel_bp`, expenses are in `expense_bp`, manager approvals are in `manager_bp`, finance workflows are in `finance_bp`, admin features are in `admin_bp`, and reports are in `analytics_bp`. This keeps routes organized instead of putting everything in one large file.

8. What is the role of the service layer in your application?

   Answer: The service layer contains the main business logic. For example, `ExpenseService` creates claims, adds items, validates policy limits, submits claims, approves or rejects claims, and creates reimbursement records. `TravelService` validates travel dates and handles approval actions. This keeps business rules outside the controllers.

9. What is the role of the DAO layer, and why did you not directly query the database from every controller?

   Answer: The DAO layer centralizes database operations. For example, `ExpenseClaimDAO.get_by_employee_id()` and `TravelDAO.get_pending_by_manager_id()` are reusable query methods. This avoids repeating SQLAlchemy query logic in controllers and makes the code cleaner. If query logic changes later, I can update it in one DAO method instead of many routes.

10. How does the request flow work when an employee creates and submits an expense claim?

    Answer: The employee logs in and opens the new expense claim page. The `/expense/new` route receives the form data and calls `ExpenseService.create_expense_claim()`, which creates a claim in `Draft` status. The employee then adds expense items through `ExpenseService.add_expense_item()`, which also updates the total amount. Receipts can be uploaded while the claim is still draft. Finally, the employee submits the claim through `ExpenseService.submit_claim()`, which changes the status from `Draft` to `Submitted`.

## Authentication and Authorization

11. How is user authentication implemented in your project?

    Answer: Authentication is implemented using email and password login. During registration, passwords are hashed using Werkzeug's `generate_password_hash()`. During login, `AuthService.authenticate_user()` retrieves the user by email and checks the password using `check_password_hash()`. If valid, the app creates a JWT access token.

12. Why did you use password hashing instead of storing plain-text passwords?

    Answer: Password hashing is important because plain-text passwords are unsafe. If the database is leaked, attackers should not be able to directly read user passwords. Werkzeug hashing stores a secure hash instead of the original password, and login checks compare the submitted password against that hash.

13. Which function is responsible for checking a user's email and password during login?

    Answer: The `AuthService.authenticate_user(email, password)` function is responsible for login validation. It uses `UserDAO.get_by_email()` to find the user and then uses `check_password_hash()` to verify the password.

14. How does your application use JWT tokens for login sessions?

    Answer: After successful login, the app creates a JWT access token using `create_access_token()`. The token contains the user's identity and role as an additional claim. For browser login, the token is stored in cookies using `set_access_cookies()`. For JSON/API login, the token is returned in the JSON response.

15. Why does your JWT setup support both headers and cookies?

    Answer: The app supports both because it can handle browser-based pages and API-style requests. Cookies are convenient for server-rendered Jinja pages because the browser automatically sends them. Headers are useful for API clients such as Postman or frontend apps that send an `Authorization` header.

16. How does your application behave differently for API-style requests and browser/template requests when a JWT token is missing, invalid, or expired?

    Answer: In `app/__init__.py`, JWT error handlers check whether the request looks like an API request using `is_api_request()`. If it is an API request, the app returns JSON error messages with status code 401. If it is a browser request, the app redirects the user to the login page, flashes a message, and clears invalid JWT cookies when needed.

17. What is the purpose of `current_user` in `auth_helper.py`?

    Answer: `current_user` is a `LocalProxy` that gives access to the currently authenticated JWT user. It calls `verify_jwt_in_request(optional=True)` and returns the user loaded by the JWT user lookup callback. If no valid user is found, it returns an `AnonymousUser`. This allows templates and routes to easily check `current_user.role` and `current_user.is_authenticated`.

18. How does your custom `login_required` decorator work?

    Answer: The custom `login_required` decorator wraps a route function and calls `verify_jwt_in_request()`. If a valid JWT is present, the route continues. If not, Flask-JWT-Extended triggers the appropriate missing or invalid token handler.

19. How does your `role_required` decorator restrict access to specific roles?

    Answer: The `role_required()` decorator accepts allowed roles such as `Manager`, `Finance`, or `Admin`. It checks whether `current_user` is authenticated and whether the user's role is in the allowed list. If the role is not allowed, it returns the `unauthorized.html` page with a 403 status.

20. What routes or features are protected so that only Manager, Finance, or Admin users can access them?

    Answer: Manager routes under `/manager` are protected with `@role_required('Manager')`. Finance routes under `/finance` are protected with `@role_required('Finance')`. Admin routes under `/admin` are protected with `@role_required('Admin')`. Analytics routes allow only Admin and Finance users through an internal role check.

## Database Design and Models

21. Can you explain the relationship between the `User` and `Employee` models?

    Answer: The `User` model stores authentication and role information, while the `Employee` model stores profile details like first name, last name, department, designation, phone, and manager. The relationship is one-to-one because each user has one employee profile.

22. Why did you separate user login information from employee profile information?

    Answer: Separating them improves design and security. Login-related data such as email, password hash, role, and active status belongs in `User`. Business profile data belongs in `Employee`. This separation makes the system more maintainable and allows profile details to evolve without mixing them with authentication logic.

23. How is the employee-manager relationship represented in your database?

    Answer: The `Employee` model has a `manager_id` field that references another employee's `id`. This is a self-referential relationship. It allows one employee to be assigned as the manager of another employee, and it also allows the system to fetch subordinates for manager approval workflows.

24. What are the main fields in the `TravelRequest` model, and why are they needed?

    Answer: The `TravelRequest` model contains `employee_id`, `destination`, `start_date`, `end_date`, `purpose`, `estimated_budget`, `status`, and `created_at`. These fields capture who is travelling, where, when, why, the expected cost, the approval status, and when the request was created.

25. What is the difference between an `ExpenseClaim` and an `ExpenseItem`?

    Answer: An `ExpenseClaim` is the main reimbursement request, such as "Trip to Mumbai Office." An `ExpenseItem` is an individual line item inside that claim, such as meals, flight, accommodation, or transportation. One claim can have many expense items.

26. Why does an expense claim store `total_amount` if the total can be calculated from expense items?

    Answer: Storing `total_amount` makes it faster to display and query claim totals, especially on dashboards and finance pages. The system updates this value whenever items are added or deleted. It is a denormalized value, so it must be kept in sync carefully.

27. How does the system update the total claim amount after adding or deleting an expense item?

    Answer: The `ExpenseClaim.update_total_amount()` method calculates the sum of all related `ExpenseItem.amount` values and updates the claim's `total_amount`. This method is called after adding an item in `ExpenseService.add_expense_item()` and after deleting an item in the expense controller.

28. What is the purpose of the `ExpenseReceipt` model?

    Answer: The `ExpenseReceipt` model stores metadata about uploaded supporting documents. It stores the claim ID, original filename, file path, MIME type, file size, and upload time. This allows the system to connect receipts to claims and allows finance users to download the supporting documents.

29. Why did you create a separate `ApprovalHistory` table?

    Answer: `ApprovalHistory` creates an audit trail. It records who approved, rejected, or verified a travel request or expense claim, along with comments and action date. This is important in a corporate system because approval decisions should be traceable.

30. What is stored in the `Reimbursement` table, and when is a reimbursement record created?

    Answer: The `Reimbursement` table stores the expense claim ID, reimbursement status, payment date, transaction reference, amount paid, and creation time. A reimbursement record is created when a finance user verifies an approved claim using `ExpenseService.verify_and_reimburse()`.

## Business Workflow

31. What are the possible statuses of a travel request, and how do they change?

    Answer: A travel request starts with `Pending` status when an employee creates it. A manager can then change it to `Approved` or `Rejected`. The action is recorded in `ApprovalHistory`.

32. What are the possible statuses of an expense claim, and what does each status mean?

    Answer: The main statuses are `Draft`, `Submitted`, `Approved`, `Rejected`, and `Verified`. `Draft` means the employee can still edit the claim. `Submitted` means it is waiting for manager review. `Approved` means the manager has accepted it. `Rejected` means it was denied. `Verified` means finance has checked it and processed reimbursement.

33. Why are expense claims first created in `Draft` status?

    Answer: Draft status allows employees to build a claim step by step. They can add multiple items and receipts before final submission. This is realistic because employees may not have all receipt details ready at the moment they create the claim.

34. Why does your system prevent employees from adding or deleting items after a claim is submitted?

    Answer: Once a claim is submitted, it enters the approval workflow. Allowing changes after submission could create confusion or fraud risk because the manager might approve one version while the employee later changes the amount or receipts. Locking submitted claims keeps the approval process consistent.

35. How does a manager see only the travel requests or expense claims of their own subordinates?

    Answer: The DAO queries join travel requests or expense claims with the `Employee` table and filter by `Employee.manager_id`. For example, `TravelDAO.get_pending_by_manager_id()` and `ExpenseClaimDAO.get_pending_by_manager_id()` return only records where the employee's manager matches the logged-in manager's employee ID.

36. What validation is performed before a travel request is created?

    Answer: In `TravelService.create_travel_request()`, the system checks that the start date is not after the end date. If the start date is greater than the end date, it raises a `ValueError`. This prevents invalid travel periods.

37. What validation is performed before an expense claim can be submitted?

    Answer: `ExpenseService.submit_claim()` checks that the claim exists, that its status is `Draft`, and that the `total_amount` is greater than zero. This prevents empty claims and prevents already submitted or processed claims from being submitted again.

38. Why can finance users only process claims that are already approved by a manager?

    Answer: Finance should not reimburse unapproved claims. The manager approval step confirms that the claim is valid from the employee's reporting hierarchy. Finance then performs the financial verification and reimbursement step. This creates a multi-level approval workflow.

39. What happens in the database when finance verifies and reimburses an approved claim?

    Answer: `ExpenseService.verify_and_reimburse()` changes the claim status from `Approved` to `Verified`, creates a `Reimbursement` record with status `Processed`, payment date, transaction reference, and amount paid, and adds an `ApprovalHistory` entry with action `Verified`.

40. How would you handle a case where a manager approves a claim by mistake?

    Answer: Currently, the project does not have a reversal workflow. A good improvement would be to add a `Reopened`, `Cancelled`, or `Finance Rejected` status before reimbursement. Finance could return the claim to the manager or employee with comments. The system should also record that reversal in `ApprovalHistory` for audit purposes.

## Policies, File Handling, and Security

41. How are company expense policies represented in your application?

    Answer: Company policies are represented by the `ExpensePolicy` model. Each policy has a category, a maximum limit per expense, and an optional role restriction. Admins can manage these policies through the admin panel.

42. How does the system validate an expense item against a category limit?

    Answer: When an employee adds an expense item, `ExpenseService.add_expense_item()` fetches the policy for that category using `ExpensePolicyDAO.get_by_category()`. If a policy exists and the submitted amount is greater than the allowed limit, the service raises a `ValueError`.

43. What happens if an employee enters an expense amount greater than the allowed policy limit?

    Answer: The system rejects the item and shows an error message. In the service layer, a `ValueError` is raised with a message explaining that the amount exceeds the policy limit for that category. The controller catches the exception and flashes the error on the page.

44. How can an admin create, update, or delete expense policies?

    Answer: Admins use the `/admin/policies` routes. The controller calls methods in `AdminService`, such as `create_or_update_policy()` and `delete_policy()`. These methods validate the category and limit, then create, update, or delete the corresponding `ExpensePolicy` record.

45. What file types are allowed for receipt uploads?

    Answer: The allowed receipt file extensions are `pdf`, `png`, `jpg`, and `jpeg`. This is defined in the `ALLOWED_EXTENSIONS` set inside `expense_controller.py`.

46. How does your project reduce file upload security risks?

    Answer: The project restricts allowed file extensions, uses `secure_filename()` before saving files, stores upload metadata in the database, and limits request size using `MAX_CONTENT_LENGTH`. It also only allows receipts to be added while the claim is in `Draft` status and only by the owner of the claim.

47. Why did you use `secure_filename()` before saving uploaded receipt files?

    Answer: `secure_filename()` sanitizes the uploaded filename. It helps prevent unsafe filenames, path traversal attempts, or special characters from being used to write files outside the intended upload directory.

48. How does your application prevent unauthorized users from viewing another employee's claim details?

    Answer: In the claim detail route, the system checks the logged-in user's employee profile. If the user is an employee, the claim's `employee_id` must match that employee's ID. Otherwise, the route aborts with 403. Manager and finance routes also have role checks and workflow-specific validations.

49. Why is receipt downloading restricted to finance users?

    Answer: Receipts contain sensitive financial and business information. In this project, finance users need to download receipts to verify expenses before reimbursement. Restricting downloads to finance users reduces unnecessary exposure of uploaded documents.

50. What additional security improvements would you add before deploying this project to production?

    Answer: I would use a strong secret key from environment variables, remove default database passwords from config, enable CSRF protection for cookie-based JWT flows, validate MIME content more deeply, use unique stored filenames to avoid overwriting files, store uploads outside the public static folder, add antivirus scanning for uploaded files, enforce HTTPS, add rate limiting on login, check `is_active` during authentication, and add more detailed audit logs.

