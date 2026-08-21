from app.db import db
from datetime import datetime

class TravelRequest(db.Model):
    __tablename__ = 'travel_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    estimated_budget = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    expense_claims = db.relationship('ExpenseClaim', backref='travel_request', lazy='dynamic')

    def __repr__(self):
        return f"<TravelRequest to {self.destination} for Employee {self.employee_id}>"
