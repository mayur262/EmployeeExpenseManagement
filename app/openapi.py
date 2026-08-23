from flask import Blueprint, jsonify, render_template_string


openapi_bp = Blueprint("openapi", __name__, url_prefix="/api")


def _response(description, content_type="text/html"):
    return {
        "description": description,
        "content": {
            content_type: {
                "schema": {
                    "type": "object" if content_type == "application/json" else "string"
                }
            }
        },
    }


def build_openapi_spec():
    auth_errors = {
        "401": _response("Missing, invalid, or expired authentication token.", "application/json"),
        "403": _response("Authenticated user does not have permission for this resource."),
    }

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Corporate Expense Management API",
            "version": "1.0.0",
            "description": (
                "OpenAPI documentation for the Flask corporate expense management "
                "system. The application primarily uses Jinja2 pages with form "
                "submissions, plus JSON endpoints for login/logout errors and "
                "analytics data."
            ),
        },
        "servers": [{"url": "/"}],
        "tags": [
            {"name": "Authentication"},
            {"name": "Travel Requests"},
            {"name": "Expense Claims"},
            {"name": "Manager"},
            {"name": "Finance"},
            {"name": "Admin"},
            {"name": "Analytics"},
            {"name": "Documentation"},
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
                "cookieAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "access_token_cookie",
                },
            },
            "schemas": {
                "LoginRequest": {
                    "type": "object",
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string", "format": "password"},
                    },
                },
                "LoginResponse": {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                    },
                },
                "MessageResponse": {
                    "type": "object",
                    "properties": {
                        "msg": {"type": "string"},
                        "error": {"type": "string"},
                    },
                },
                "SummaryStats": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "ChartSeries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": True,
                    },
                },
            },
        },
        "paths": {
            "/": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Redirect user to the correct dashboard or login page.",
                    "responses": {"302": {"description": "Redirect response."}},
                }
            },
            "/login": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Render the login page.",
                    "responses": {"200": _response("Login HTML page.")},
                },
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Authenticate a user.",
                    "description": (
                        "Accepts JSON credentials for API clients or form data from "
                        "the login page. JSON requests receive a JWT access token."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            },
                            "application/x-www-form-urlencoded": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            },
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Authenticated successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginResponse"}
                                },
                                "text/html": {"schema": {"type": "string"}},
                            },
                        },
                        "401": _response("Invalid email or password.", "application/json"),
                    },
                },
            },
            "/register": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Render the registration page.",
                    "responses": {"200": _response("Registration HTML page.")},
                },
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Register a new user and employee profile from form data.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "format": "password"},
                                        "role": {"type": "string"},
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"},
                                        "department": {"type": "string"},
                                        "designation": {"type": "string"},
                                        "phone": {"type": "string"},
                                        "manager_id": {"type": "integer"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect after registration."}},
                },
            },
            "/logout": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Log out the current user.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {
                        "200": _response("JSON logout response.", "application/json"),
                        "302": {"description": "Redirect to login for browser users."},
                        **auth_errors,
                    },
                }
            },
            "/employee/dashboard": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Redirect an employee to their travel request list.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"302": {"description": "Redirect response."}, **auth_errors},
                }
            },
            "/manager/dashboard": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Redirect a manager to the manager dashboard.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"302": {"description": "Redirect response."}, **auth_errors},
                }
            },
            "/finance/dashboard": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Redirect a finance user to the finance dashboard.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"302": {"description": "Redirect response."}, **auth_errors},
                }
            },
            "/admin/dashboard": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Redirect an admin user to the admin dashboard.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"302": {"description": "Redirect response."}, **auth_errors},
                }
            },
            "/travel/": {
                "get": {
                    "tags": ["Travel Requests"],
                    "summary": "List travel requests for the current user.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "minimum": 1},
                            "description": "Pagination page number.",
                        }
                    ],
                    "responses": {"200": _response("Travel request list page."), **auth_errors},
                }
            },
            "/travel/new": {
                "get": {
                    "tags": ["Travel Requests"],
                    "summary": "Render the travel request form.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"200": _response("Travel request form."), **auth_errors},
                },
                "post": {
                    "tags": ["Travel Requests"],
                    "summary": "Create a travel request from form data.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "required": [
                                        "destination",
                                        "start_date",
                                        "end_date",
                                        "purpose",
                                        "estimated_budget",
                                    ],
                                    "properties": {
                                        "destination": {"type": "string"},
                                        "start_date": {"type": "string", "format": "date"},
                                        "end_date": {"type": "string", "format": "date"},
                                        "purpose": {"type": "string"},
                                        "estimated_budget": {"type": "number", "format": "float"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect after create."}, **auth_errors},
                },
            },
            "/travel/{request_id}": {
                "get": {
                    "tags": ["Travel Requests"],
                    "summary": "View travel request details.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {
                            "name": "request_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": _response("Travel request detail page."),
                        "404": _response("Travel request not found."),
                        **auth_errors,
                    },
                }
            },
            "/expense/": {
                "get": {
                    "tags": ["Expense Claims"],
                    "summary": "List expense claims visible to the current user.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "minimum": 1},
                            "description": "Pagination page number.",
                        }
                    ],
                    "responses": {"200": _response("Expense claim list page."), **auth_errors},
                }
            },
            "/expense/new": {
                "get": {
                    "tags": ["Expense Claims"],
                    "summary": "Render the expense claim form.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"200": _response("Expense claim form."), **auth_errors},
                },
                "post": {
                    "tags": ["Expense Claims"],
                    "summary": "Create an expense claim draft.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "travel_request_id": {"type": "integer", "nullable": True},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect to claim details."}, **auth_errors},
                },
            },
            "/expense/{claim_id}": {
                "get": {
                    "tags": ["Expense Claims"],
                    "summary": "View expense claim details.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {
                            "name": "claim_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": _response("Expense claim detail page."),
                        "404": _response("Expense claim not found."),
                        **auth_errors,
                    },
                }
            },
            "/expense/{claim_id}/item": {
                "post": {
                    "tags": ["Expense Claims"],
                    "summary": "Add a line item to an expense claim.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "required": ["category", "amount", "expense_date"],
                                    "properties": {
                                        "category": {"type": "string"},
                                        "amount": {"type": "number", "format": "float"},
                                        "expense_date": {"type": "string", "format": "date"},
                                        "description": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect back to claim details."}, **auth_errors},
                }
            },
            "/expense/{claim_id}/item/{item_id}/delete": {
                "post": {
                    "tags": ["Expense Claims"],
                    "summary": "Delete a draft claim line item.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "item_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    ],
                    "responses": {"302": {"description": "Redirect back to claim details."}, **auth_errors},
                }
            },
            "/expense/{claim_id}/receipt": {
                "post": {
                    "tags": ["Expense Claims"],
                    "summary": "Upload a receipt attachment for a draft claim.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["receipt_file"],
                                    "properties": {
                                        "receipt_file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "PDF, PNG, JPG, or JPEG receipt.",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect back to claim details."}, **auth_errors},
                }
            },
            "/expense/{claim_id}/receipt/{receipt_id}/delete": {
                "post": {
                    "tags": ["Expense Claims"],
                    "summary": "Delete a draft claim receipt.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "receipt_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    ],
                    "responses": {"302": {"description": "Redirect back to claim details."}, **auth_errors},
                }
            },
            "/expense/{claim_id}/submit": {
                "post": {
                    "tags": ["Expense Claims"],
                    "summary": "Submit a draft expense claim for manager approval.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"302": {"description": "Redirect back to claim details."}, **auth_errors},
                }
            },
            "/manager/": {
                "get": {
                    "tags": ["Manager"],
                    "summary": "Display pending travel requests and expense claims for manager approval.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "travel_page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                        {"name": "expense_page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    ],
                    "responses": {"200": _response("Manager dashboard page."), **auth_errors},
                }
            },
            "/manager/travel/{request_id}": {
                "get": {
                    "tags": ["Manager"],
                    "summary": "View a travel request awaiting manager action.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "request_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": _response("Manager travel detail page."), **auth_errors},
                }
            },
            "/manager/travel/{request_id}/action": {
                "post": {
                    "tags": ["Manager"],
                    "summary": "Approve or reject a travel request.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "request_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "required": ["action"],
                                    "properties": {
                                        "action": {"type": "string", "enum": ["Approved", "Rejected"]},
                                        "comments": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect to manager dashboard."}, **auth_errors},
                }
            },
            "/manager/expense/{claim_id}": {
                "get": {
                    "tags": ["Manager"],
                    "summary": "View an expense claim awaiting manager action.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": _response("Manager expense detail page."), **auth_errors},
                }
            },
            "/manager/expense/{claim_id}/action": {
                "post": {
                    "tags": ["Manager"],
                    "summary": "Approve or reject an expense claim.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "required": ["action"],
                                    "properties": {
                                        "action": {"type": "string", "enum": ["Approved", "Rejected"]},
                                        "comments": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect to manager dashboard."}, **auth_errors},
                }
            },
            "/finance/": {
                "get": {
                    "tags": ["Finance"],
                    "summary": "Display finance verification queue.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["Approved", "Verified"]}},
                        {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    ],
                    "responses": {"200": _response("Finance dashboard page."), **auth_errors},
                }
            },
            "/finance/claim/{claim_id}": {
                "get": {
                    "tags": ["Finance"],
                    "summary": "View a claim for finance verification.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": _response("Finance claim detail page."), **auth_errors},
                }
            },
            "/finance/receipt/{receipt_id}/download": {
                "get": {
                    "tags": ["Finance"],
                    "summary": "Download a receipt attachment.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "receipt_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Receipt file download.",
                            "content": {
                                "application/pdf": {"schema": {"type": "string", "format": "binary"}},
                                "image/png": {"schema": {"type": "string", "format": "binary"}},
                                "image/jpeg": {"schema": {"type": "string", "format": "binary"}},
                            },
                        },
                        **auth_errors,
                    },
                }
            },
            "/finance/claim/{claim_id}/reimburse": {
                "post": {
                    "tags": ["Finance"],
                    "summary": "Verify an approved claim and create reimbursement record.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "claim_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "transaction_reference": {"type": "string"}
                                    },
                                }
                            }
                        }
                    },
                    "responses": {"302": {"description": "Redirect to finance dashboard."}, **auth_errors},
                }
            },
            "/admin/": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "Display admin dashboard.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"200": _response("Admin dashboard page."), **auth_errors},
                }
            },
            "/admin/users": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "List users for administration.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}}
                    ],
                    "responses": {"200": _response("User management page."), **auth_errors},
                }
            },
            "/admin/users/{user_id}/edit": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "Render user role edit form.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": _response("User edit page."), **auth_errors},
                },
                "post": {
                    "tags": ["Admin"],
                    "summary": "Update user role.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"role": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect to users list."}, **auth_errors},
                },
            },
            "/admin/users/{user_id}/toggle": {
                "post": {
                    "tags": ["Admin"],
                    "summary": "Activate or deactivate a user account.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"302": {"description": "Redirect to users list."}, **auth_errors},
                }
            },
            "/admin/users/{user_id}/delete": {
                "post": {
                    "tags": ["Admin"],
                    "summary": "Delete a user account.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"302": {"description": "Redirect to users list."}, **auth_errors},
                }
            },
            "/admin/policies": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "List expense policies.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}}
                    ],
                    "responses": {"200": _response("Policy management page."), **auth_errors},
                }
            },
            "/admin/policies/new": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "Render policy creation form.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"200": _response("Policy edit page."), **auth_errors},
                },
                "post": {
                    "tags": ["Admin"],
                    "summary": "Create an expense policy.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "category": {"type": "string"},
                                        "max_limit": {"type": "number", "format": "float"},
                                        "role_restriction": {"type": "string", "nullable": True},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect to policies list."}, **auth_errors},
                },
            },
            "/admin/policies/{policy_id}/edit": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "Render policy edit form.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "policy_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": _response("Policy edit page."), **auth_errors},
                },
                "post": {
                    "tags": ["Admin"],
                    "summary": "Update an expense policy.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "policy_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "category": {"type": "string"},
                                        "max_limit": {"type": "number", "format": "float"},
                                        "role_restriction": {"type": "string", "nullable": True},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"302": {"description": "Redirect to policies list."}, **auth_errors},
                },
            },
            "/admin/policies/{policy_id}/delete": {
                "post": {
                    "tags": ["Admin"],
                    "summary": "Delete an expense policy.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "policy_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"302": {"description": "Redirect to policies list."}, **auth_errors},
                }
            },
            "/analytics/": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Render analytics dashboard.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {"200": _response("Analytics dashboard page."), **auth_errors},
                }
            },
            "/analytics/search": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Search claims with filters.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "parameters": [
                        {"name": "q", "in": "query", "schema": {"type": "string"}},
                        {"name": "status", "in": "query", "schema": {"type": "string"}},
                        {"name": "category", "in": "query", "schema": {"type": "string"}},
                        {"name": "employee", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {"200": _response("Analytics search page."), **auth_errors},
                }
            },
            "/analytics/api/summary": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Return summary expense statistics as JSON.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Summary statistics.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SummaryStats"}
                                }
                            },
                        },
                        **auth_errors,
                    },
                }
            },
            "/analytics/api/by-category": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Return spend grouped by category.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Category spend series.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ChartSeries"}
                                }
                            },
                        },
                        **auth_errors,
                    },
                }
            },
            "/analytics/api/by-department": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Return spend grouped by department.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Department spend series.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ChartSeries"}
                                }
                            },
                        },
                        **auth_errors,
                    },
                }
            },
            "/analytics/api/monthly-trend": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Return monthly spend trend data.",
                    "security": [{"bearerAuth": []}, {"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Monthly trend series.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ChartSeries"}
                                }
                            },
                        },
                        **auth_errors,
                    },
                }
            },
            "/api/openapi.json": {
                "get": {
                    "tags": ["Documentation"],
                    "summary": "Return this OpenAPI specification.",
                    "responses": {
                        "200": {
                            "description": "OpenAPI specification.",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
            "/api/docs": {
                "get": {
                    "tags": ["Documentation"],
                    "summary": "Render Swagger UI for this API.",
                    "responses": {"200": _response("Swagger UI HTML page.")},
                }
            },
        },
    }


@openapi_bp.route("/openapi.json")
def openapi_json():
    return jsonify(build_openapi_spec())


@openapi_bp.route("/docs")
def swagger_ui():
    return render_template_string(
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Corporate Expense Management API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
      body { margin: 0; background: #f7f8fb; }
      .swagger-ui .topbar { display: none; }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = function () {
        SwaggerUIBundle({
          url: "{{ url_for('openapi.openapi_json') }}",
          dom_id: "#swagger-ui",
          deepLinking: true,
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout"
        });
      };
    </script>
  </body>
</html>
        """
    )
