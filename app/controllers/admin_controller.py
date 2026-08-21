from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.controllers.auth_helper import login_required, current_user
from app.controllers.auth_decorator import role_required
from app.services.admin_service import AdminService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

CATEGORIES = ["Accommodation", "Transportation", "Meals", "Flight", "Other"]
ROLES = ["Employee", "Manager", "Finance", "Admin"]


@admin_bp.route("/")
@login_required
@role_required("Admin")
def dashboard():
    users = AdminService.get_all_users()
    policies = AdminService.get_all_policies()
    return render_template(
        "admin/dashboard.html",
        users=users,
        policies=policies
    )




@admin_bp.route("/users")
@login_required
@role_required("Admin")
def manage_users():
    users = AdminService.get_all_users()
    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_user(user_id):
    user = AdminService.get_user_by_id(user_id)
    if not user:
        abort(404)

    if request.method == "POST":
        new_role = request.form.get("role", "").strip()
        try:
            AdminService.update_user_role(user_id, new_role)
            flash(f"Role for {user.email} updated to {new_role}.", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("admin.manage_users"))

    return render_template("admin/edit_user.html", user=user, roles=ROLES)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("Admin")
def toggle_user(user_id):
    if user_id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("admin.manage_users"))
    try:
        user = AdminService.toggle_user_active(user_id)
        status = "activated" if user.is_active else "deactivated"
        flash(f"User {user.email} has been {status}.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.manage_users"))
    try:
        AdminService.delete_user(user_id)
        flash("User deleted successfully.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_users"))




@admin_bp.route("/policies")
@login_required
@role_required("Admin")
def manage_policies():
    policies = AdminService.get_all_policies()
    return render_template("admin/manage_policies.html", policies=policies)


@admin_bp.route("/policies/new", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def new_policy():
    if request.method == "POST":
        category = request.form.get("category", "").strip()
        max_limit = request.form.get("max_limit", "").strip()
        role_restriction = request.form.get("role_restriction", "").strip() or None
        try:
            AdminService.create_or_update_policy(
                category=category,
                max_limit=max_limit,
                role_restriction=role_restriction
            )
            flash(f"Policy for category '{category}' saved.", "success")
            return redirect(url_for("admin.manage_policies"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "admin/edit_policy.html",
        policy=None,
        categories=CATEGORIES,
        roles=ROLES,
        form_action=url_for("admin.new_policy")
    )


@admin_bp.route("/policies/<int:policy_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_policy(policy_id):
    policy = AdminService.get_policy_by_id(policy_id)
    if not policy:
        abort(404)

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        max_limit = request.form.get("max_limit", "").strip()
        role_restriction = request.form.get("role_restriction", "").strip() or None
        try:
            AdminService.create_or_update_policy(
                category=category,
                max_limit=max_limit,
                role_restriction=role_restriction,
                policy_id=policy_id
            )
            flash(f"Policy for '{category}' updated.", "success")
            return redirect(url_for("admin.manage_policies"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "admin/edit_policy.html",
        policy=policy,
        categories=CATEGORIES,
        roles=ROLES,
        form_action=url_for("admin.edit_policy", policy_id=policy_id)
    )


@admin_bp.route("/policies/<int:policy_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_policy(policy_id):
    try:
        AdminService.delete_policy(policy_id)
        flash("Policy deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_policies"))
