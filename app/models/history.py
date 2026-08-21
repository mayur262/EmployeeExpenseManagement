from app.db import db
from datetime import datetime

class ApprovalHistory(db.Model):
    __tablename__ = 'approval_history'
    
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), nullable=False) # 'Travel' or 'Expense'
    request_id = db.Column(db.Integer, nullable=False) # ID of travel_request or expense_claim
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(20), nullable=False) # Approved, Rejected, Verified
    comments = db.Column(db.Text, nullable=True)
    action_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    approver = db.relationship('User', backref='approvals_done')

    def __repr__(self):
        return f"<ApprovalHistory for {self.request_type} #{self.request_id} by User {self.approver_id}>"

class Reimbursement(db.Model):
    __tablename__ = 'reimbursements'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_claim_id = db.Column(db.Integer, db.ForeignKey('expense_claims.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, Processed
    payment_date = db.Column(db.Date, nullable=True)
    transaction_reference = db.Column(db.String(100), nullable=True)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Reimbursement for Claim {self.expense_claim_id}: {self.status}>"
