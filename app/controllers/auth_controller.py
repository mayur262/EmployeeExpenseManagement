from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from app.controllers.auth_helper import login_required, current_user
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from app.services.auth_service import AuthService
from app.dao.user_dao import UserDAO, EmployeeDAO
import os

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == "Employee":
            return redirect(url_for("auth.employee_dashboard"))
        elif current_user.role == "Manager":
            return redirect(url_for("auth.manager_dashboard"))
        elif current_user.role == "Finance":
            return redirect(url_for("auth.finance_dashboard"))
        elif current_user.role == "Admin":
            return redirect(url_for("auth.admin_dashboard"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({"msg": "Already authenticated"}), 200
        return redirect(url_for("auth.home"))

    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        else:
            email = request.form.get("email")
            password = request.form.get("password")

        user = AuthService.authenticate_user(email, password)
        if user:
           
            additional_claims = {"role": user.role}
            access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
            
            if request.is_json:
                return jsonify({"access_token": access_token}), 200
                
            response = redirect(url_for("auth.home"))
            set_access_cookies(response, access_token)
            flash("Logged in successfully!", "success")
            return response
        else:
            if request.is_json:
                return jsonify({"msg": "Invalid email or password"}), 401
            flash("Invalid email or password", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    employees = EmployeeDAO.get_all()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "Employee")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        department = request.form.get("department")
        designation = request.form.get("designation")
        phone = request.form.get("phone")
        manager_id = request.form.get("manager_id")

        if not manager_id or manager_id == "":
            manager_id = None
        else:
            manager_id = int(manager_id)

        try:
            AuthService.register_user(
                email=email,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name,
                department=department,
                designation=designation,
                phone=phone,
                manager_id=manager_id
            )
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("register.html", employees=employees)

@auth_bp.route("/logout")
@login_required
def logout():
    if request.is_json:
        response = jsonify({"msg": "Logged out successfully"})
        unset_jwt_cookies(response)
        return response, 200
        
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    flash("Logged out successfully!", "info")
    return response

@auth_bp.route("/employee/dashboard")
@login_required
def employee_dashboard():
    if current_user.role != "Employee":
        return abort(403)
    return redirect(url_for("travel.list_requests"))

@auth_bp.route("/manager/dashboard")
@login_required
def manager_dashboard():
    if current_user.role != "Manager":
        return abort(403)
    return redirect(url_for("manager.dashboard"))

@auth_bp.route("/finance/dashboard")
@login_required
def finance_dashboard():
    if current_user.role != "Finance":
        return abort(403)
    return redirect(url_for("finance.dashboard"))

@auth_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        return abort(403)
    return redirect(url_for("admin.dashboard"))
