from app.dao.expense_dao import ExpenseClaimDAO, ExpenseItemDAO, ExpenseReceiptDAO
from app.models.expense import ExpenseClaim, ExpenseItem, ExpenseReceipt
from app.models.history import ApprovalHistory, Reimbursement
from app.dao.policy_dao import ExpensePolicyDAO
from app.db import db
from datetime import datetime, timezone

class ExpenseService:
    @staticmethod
    def create_expense_claim(employee_id, title, description=None, travel_request_id=None):
        claim = ExpenseClaim(
            employee_id=employee_id,
            travel_request_id=travel_request_id,
            title=title,
            description=description,
            status="Draft",
            total_amount=0.00
        )
        return ExpenseClaimDAO.save(claim)

    @staticmethod
    def add_expense_item(claim_id, category, amount, expense_date, description=None):
        claim = ExpenseClaimDAO.get_by_id(claim_id)
        if not claim:
            raise ValueError("Expense claim not found")
        if claim.status != "Draft":
            raise ValueError("Cannot add items to a submitted or processed claim")

        policy = ExpensePolicyDAO.get_by_category(category)
        if policy and float(amount) > float(policy.max_limit_per_expense):
            raise ValueError(
                f"Amount {amount} exceeds the policy limit of "
                f"{policy.max_limit_per_expense} for category '{category}'."
            )

        item = ExpenseItem(
            expense_claim_id=claim_id,
            category=category,
            amount=amount,
            expense_date=expense_date,
            description=description
        )
        db.session.add(item)
        db.session.flush()

        claim.update_total_amount()
        return item

    @staticmethod
    def attach_receipt(claim_id, filename, filepath, file_type, file_size):
        claim = ExpenseClaimDAO.get_by_id(claim_id)
        if not claim:
            raise ValueError("Expense claim not found")

        receipt = ExpenseReceipt(
            expense_claim_id=claim_id,
            filename=filename,
            filepath=filepath,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(receipt)
        db.session.commit()
        return receipt

    @staticmethod
    def submit_claim(claim_id):
        claim = ExpenseClaimDAO.get_by_id(claim_id)
        if not claim:
            raise ValueError("Expense claim not found")
        if claim.status != "Draft":
            raise ValueError("Only draft claims can be submitted")
        if claim.total_amount <= 0:
            raise ValueError("Cannot submit an empty expense claim")

        claim.status = "Submitted"
        db.session.commit()
        return claim

    @staticmethod
    def approve_or_reject_claim(claim_id, approver_user, action, comments=None):
        if action not in ["Approved", "Rejected"]:
            raise ValueError("Invalid action")

        claim = ExpenseClaimDAO.get_by_id(claim_id)
        if not claim:
            raise ValueError("Expense claim not found")
        if claim.status != "Submitted":
            raise ValueError("Only submitted claims can be approved or rejected")

        claim.status = action

        history = ApprovalHistory(
            request_type="Expense",
            request_id=claim_id,
            approver_id=approver_user.id,
            action=action,
            comments=comments
        )
        db.session.add(history)
        db.session.commit()
        return claim

    @staticmethod
    def verify_and_reimburse(claim_id, finance_user, transaction_reference=None):
        claim = ExpenseClaimDAO.get_by_id(claim_id)
        if not claim:
            raise ValueError("Expense claim not found")
        if claim.status != "Approved":
            raise ValueError("Only approved claims can be verified/reimbursed")

        claim.status = "Verified"

        reimbursement = Reimbursement(
            expense_claim_id=claim.id,
            status="Processed",
            payment_date=datetime.now(timezone.utc).date(),
            transaction_reference=transaction_reference,
            amount_paid=claim.total_amount
        )

        history = ApprovalHistory(
            request_type="Expense",
            request_id=claim_id,
            approver_id=finance_user.id,
            action="Verified",
            comments="Verified and reimbursement initiated."
        )

        db.session.add(reimbursement)
        db.session.add(history)
        db.session.commit()
        return reimbursement
