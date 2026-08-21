from app.db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Employee') # Employee, Manager, Finance, Admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True)
    
    manager = db.relationship('Employee', remote_side=[id], backref=db.backref('subordinates', lazy='dynamic'))
    travel_requests = db.relationship('TravelRequest', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    expense_claims = db.relationship('ExpenseClaim', backref='employee', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name} ({self.department})>"
