from flask import Blueprint, render_template, request, jsonify, abort
from app.controllers.auth_helper import login_required, current_user
from app.controllers.auth_decorator import role_required
from app.services.analytics_service import AnalyticsService
import json

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

ALLOWED_ROLES = ("Admin", "Finance")
CATEGORIES = ["Accommodation", "Transportation", "Meals", "Flight", "Other"]
STATUSES = ["Draft", "Submitted", "Approved", "Verified", "Rejected"]


def _require_analytics_role():
    if current_user.role not in ALLOWED_ROLES:
        abort(403)


@analytics_bp.route("/")
@login_required
def dashboard():
    _require_analytics_role()

    summary = AnalyticsService.summary_stats()
    by_category = AnalyticsService.spend_by_category()
    by_status = AnalyticsService.spend_by_status()
    by_department = AnalyticsService.spend_by_department()
    monthly = AnalyticsService.monthly_spend_trend(months=6)

    return render_template(
        "analytics/dashboard.html",
        summary=summary,
        by_category_json=json.dumps(by_category),
        by_status_json=json.dumps(by_status),
        by_department_json=json.dumps(by_department),
        monthly_json=json.dumps(monthly),
    )


@analytics_bp.route("/search")
@login_required
def search():
    _require_analytics_role()

    query_str = request.args.get("q", "").strip() or None
    status = request.args.get("status", "").strip() or None
    category = request.args.get("category", "").strip() or None
    employee_name = request.args.get("employee", "").strip() or None

    if status and status not in STATUSES:
        status = None
    if category and category not in CATEGORIES:
        category = None

    claims = AnalyticsService.search_claims(
        query_str=query_str,
        status=status,
        category=category,
        employee_name=employee_name,
    )

    return render_template(
        "analytics/search.html",
        claims=claims,
        q=query_str or "",
        status=status or "",
        category=category or "",
        employee=employee_name or "",
        categories=CATEGORIES,
        statuses=STATUSES,
        total=len(claims),
    )


@analytics_bp.route("/api/summary")
@login_required
def api_summary():
    _require_analytics_role()
    return jsonify(AnalyticsService.summary_stats())


@analytics_bp.route("/api/by-category")
@login_required
def api_by_category():
    _require_analytics_role()
    return jsonify(AnalyticsService.spend_by_category())


@analytics_bp.route("/api/by-department")
@login_required
def api_by_department():
    _require_analytics_role()
    return jsonify(AnalyticsService.spend_by_department())


@analytics_bp.route("/api/monthly-trend")
@login_required
def api_monthly_trend():
    _require_analytics_role()
    return jsonify(AnalyticsService.monthly_spend_trend())
