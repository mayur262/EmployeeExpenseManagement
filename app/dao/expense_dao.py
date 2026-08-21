from app.dao.base_dao import BaseDAO
from app.models.expense import ExpenseClaim, ExpenseItem, ExpenseReceipt
from app.models.user import Employee

class ExpenseClaimDAO(BaseDAO):
    model = ExpenseClaim

    @classmethod
    def get_by_employee_id(cls, employee_id):
        return cls.model.query.filter_by(employee_id=employee_id).order_by(ExpenseClaim.created_at.desc()).all()

    @classmethod
    def get_pending_by_manager_id(cls, manager_id):
        return cls.model.query.join(Employee).filter(
            Employee.manager_id == manager_id,
            ExpenseClaim.status == 'Submitted'
        ).order_by(ExpenseClaim.created_at.desc()).all()

    @classmethod
    def get_verified_or_pending_finance(cls):
        return cls.model.query.filter(
            ExpenseClaim.status.in_(['Approved', 'Verified'])
        ).order_by(ExpenseClaim.created_at.desc()).all()

    @classmethod
    def get_all_for_finance(cls, status_filter=None):
        if status_filter and status_filter in ('Approved', 'Verified'):
            return cls.model.query.filter(
                ExpenseClaim.status == status_filter
            ).order_by(ExpenseClaim.created_at.desc()).all()
        return cls.model.query.filter(
            ExpenseClaim.status.in_(['Approved', 'Verified'])
        ).order_by(ExpenseClaim.created_at.desc()).all()


class ExpenseItemDAO(BaseDAO):
    model = ExpenseItem

class ExpenseReceiptDAO(BaseDAO):
    model = ExpenseReceipt
