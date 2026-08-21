from decimal import Decimal
from app.db import db
from datetime import datetime

class ExpenseClaim(db.Model):
    __tablename__ = 'expense_claims'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    travel_request_id = db.Column(db.Integer, db.ForeignKey('travel_requests.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Draft') # Draft, Submitted, Approved, Verified, Rejected
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('ExpenseItem', backref='claim', lazy='dynamic', cascade='all, delete-orphan')
    receipts = db.relationship('ExpenseReceipt', backref='claim', lazy='dynamic', cascade='all, delete-orphan')
    reimbursements = db.relationship('Reimbursement', backref='claim', lazy='dynamic', cascade='all, delete-orphan')

    def update_total_amount(self):
        self.total_amount = sum((Decimal(str(item.amount)) for item in self.items.all()), Decimal('0.00'))
        db.session.commit()

    def __repr__(self):
        return f"<ExpenseClaim {self.title} - Status: {self.status}>"

class ExpenseItem(db.Model):
    __tablename__ = 'expense_items'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_claim_id = db.Column(db.Integer, db.ForeignKey('expense_claims.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Accommodation, Transportation, Meals, Flight, Other
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<ExpenseItem {self.category}: {self.amount}>"

class ExpenseReceipt(db.Model):
    __tablename__ = 'expense_receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_claim_id = db.Column(db.Integer, db.ForeignKey('expense_claims.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False) # e.g. application/pdf, image/png
    file_size = db.Column(db.Integer, nullable=False) # size in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ExpenseReceipt {self.filename}>"
