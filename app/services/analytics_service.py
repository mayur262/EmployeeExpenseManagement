from app.db import db
from app.models.expense import ExpenseClaim, ExpenseItem
from app.models.travel import TravelRequest
from app.models.user import Employee, User
from sqlalchemy import func, case
from collections import defaultdict
from datetime import datetime, timedelta, timezone


class AnalyticsService:

    @staticmethod
    def spend_by_category():
        rows = (
            db.session.query(
                ExpenseItem.category,
                func.sum(ExpenseItem.amount).label("total")
            )
            .join(ExpenseClaim, ExpenseClaim.id == ExpenseItem.expense_claim_id)
            .filter(ExpenseClaim.status.in_(["Approved", "Verified"]))
            .group_by(ExpenseItem.category)
            .order_by(func.sum(ExpenseItem.amount).desc())
            .all()
        )
        return [{"category": r.category, "total": float(r.total)} for r in rows]

    @staticmethod
    def spend_by_status():
        rows = (
            db.session.query(
                ExpenseClaim.status,
                func.count(ExpenseClaim.id).label("count"),
                func.sum(ExpenseClaim.total_amount).label("total")
            )
            .group_by(ExpenseClaim.status)
            .all()
        )
        return [
            {"status": r.status, "count": int(r.count), "total": float(r.total or 0)}
            for r in rows
        ]

    @staticmethod
    def spend_by_department():
        rows = (
            db.session.query(
                Employee.department,
                func.sum(ExpenseClaim.total_amount).label("total")
            )
            .join(ExpenseClaim, ExpenseClaim.employee_id == Employee.id)
            .filter(ExpenseClaim.status.in_(["Approved", "Verified"]))
            .group_by(Employee.department)
            .order_by(func.sum(ExpenseClaim.total_amount).desc())
            .all()
        )
        return [{"department": r.department, "total": float(r.total or 0)} for r in rows]

    @staticmethod
    def monthly_spend_trend(months=6):
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)
        rows = (
            db.session.query(
                func.strftime("%Y-%m", ExpenseClaim.created_at).label("month"),
                func.sum(ExpenseClaim.total_amount).label("total")
            )
            .filter(
                ExpenseClaim.status.in_(["Submitted", "Approved", "Verified"]),
                ExpenseClaim.created_at >= cutoff
            )
            .group_by(func.strftime("%Y-%m", ExpenseClaim.created_at))
            .order_by(func.strftime("%Y-%m", ExpenseClaim.created_at))
            .all()
        )
        return [{"month": r.month, "total": float(r.total or 0)} for r in rows]

    @staticmethod
    def summary_stats():
        rows = (
            db.session.query(
                ExpenseClaim.status,
                func.count(ExpenseClaim.id).label("cnt"),
                func.sum(ExpenseClaim.total_amount).label("amt")
            )
            .group_by(ExpenseClaim.status)
            .all()
        )
        stats = {
            "total_claims": 0,
            "total_spend": 0.0,
            "Draft": 0, "Submitted": 0, "Approved": 0,
            "Verified": 0, "Rejected": 0
        }
        for r in rows:
            stats["total_claims"] += int(r.cnt)
            stats["total_spend"] += float(r.amt or 0)
            stats[r.status] = int(r.cnt)

        travel_total = db.session.query(func.count(TravelRequest.id)).scalar() or 0
        stats["total_travel_requests"] = travel_total
        return stats



    @staticmethod
    def search_claims(query_str=None, status=None, category=None, employee_name=None):
        q = db.session.query(ExpenseClaim).join(
            Employee, Employee.id == ExpenseClaim.employee_id
        )

        if query_str:
            try:
                claim_id = int(query_str)
                q = q.filter(
                    db.or_(
                        ExpenseClaim.title.ilike(f"%{query_str}%"),
                        ExpenseClaim.id == claim_id
                    )
                )
            except (ValueError, TypeError):
                q = q.filter(ExpenseClaim.title.ilike(f"%{query_str}%"))

        if status:
            q = q.filter(ExpenseClaim.status == status)

        if employee_name:
            q = q.filter(
                db.or_(
                    Employee.first_name.ilike(f"%{employee_name}%"),
                    Employee.last_name.ilike(f"%{employee_name}%"),
                    func.concat(Employee.first_name, " ", Employee.last_name).ilike(f"%{employee_name}%")
                )
            )

        if category:
            q = q.join(ExpenseItem, ExpenseItem.expense_claim_id == ExpenseClaim.id).filter(
                ExpenseItem.category == category
            ).distinct()

        return q.order_by(ExpenseClaim.created_at.desc()).all()

